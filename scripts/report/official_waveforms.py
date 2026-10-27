#!/usr/bin/env python3
"""Confere término do firmware oficial no VCD e exporta uma janela real para o relatório."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.shapes import Line
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from waveforms import ROOT, draw, label, load_vcd, number, sample


def verify(events, log, success_pc):
    # Valores anteriores à borda são os mesmos usados pelo TB e pelo register file.
    match = re.search(r'PASS official_firmware: x4=00000000, (\d+) retirements, (\d+) cycles, CRC=(\d+), ISA=44, terminal loop verified', log)
    if not match or 'FATAL:' in log:
        raise ValueError('Log não comprova execução oficial completa')
    release = next((t for t, value in events['rst_i'] if value == '0'), None)
    if release is None:
        raise ValueError('VCD sem liberação do reset')
    cycles = retired = crc_count = loops = 0
    success = None
    previous = 'x'
    for time, value in events['clk_i']:
        rising = previous == '0' and value == '1'
        previous = value
        if not rising or time <= release:
            continue
        get = lambda name: number(sample(events, name, time, before=True))
        if get('rst_i') or get('fault_o'):
            raise ValueError('Reset/fault inesperado durante a validação oficial')
        cycles += 1
        if not get('commit_valid_o'):
            continue
        retired += 1
        pc, instr, rd, data = (get(name) for name in
                               ('current_pc', 'instruction', 'commit_rd_o', 'commit_data_o'))
        if instr & 127 == 0x33 and instr >> 25 == 0x40:
            crc_count += 1
        if rd == 4:
            if success is not None or pc != success_pc or data or instr != 0x00000213:
                raise ValueError('Escrita inválida de término em x4')
            success = time
        elif success is not None:
            if pc != success_pc + 4 or instr != 0x0000006f or rd:
                raise ValueError('Loop final oficial não confirmado no VCD')
            loops += 1
    if success is None or loops != 3 or crc_count != 16 or [retired, cycles, crc_count] != list(map(int, match.groups())):
        raise ValueError('VCD/log oficial divergem em término, ciclos, commits ou CRC')
    return {'success_edge_tick': success, 'retirements': retired, 'cycles': cycles,
            'crc_retirements': crc_count, 'terminal_loop_retirements': loops}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vcd', type=Path, default=ROOT/'results/waveforms/official.vcd')
    parser.add_argument('--log', type=Path, default=ROOT/'results/logs/tb_official_firmware.wave.log')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = json.loads((ROOT/'firmware/official/source.json').read_text())
    events, scale, last = load_vcd(args.vcd, core='tb_official_firmware.dut.core.')
    result = verify(events, args.log.read_text(), int(source['termination']['success_write_pc'], 16))
    edge = result['success_edge_tick']
    start = edge - int(55/scale)
    if start < 0:
        raise ValueError('Captura curta demais para a janela de término')
    pdfmetrics.registerFont(TTFont('Wave', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    drawing = draw(events, scale, start, last, 'F21 — Término do firmware oficial',
                   f'x4=00000000 em WRITEBACK; {result["retirements"]} commits, {result["cycles"]} ciclos, três commits no loop final.')
    # Marca a escrita no RF; não usa a marcação de store do renderer do smoke próprio.
    x = 165 + (edge-start)/(last-start)*520
    drawing.add(Line(x, 79, x, 502, strokeColor=HexColor('#ad3333'), strokeWidth=1.1))
    label(drawing, 400, 522, f'x4=0 na borda: {edge*scale:g} ns', 10, '#ad3333')
    args.output.mkdir(parents=True, exist_ok=True)
    svg = args.output/'official-success.svg'
    renderSVG.drawToFile(drawing, str(svg))
    svg.write_text(svg.read_text().replace('font-family: Wave;', 'font-family: DejaVu Sans;'))
    intermediate = ROOT/'build/official-success.pdf'
    intermediate.parent.mkdir(exist_ok=True)
    renderPDF.drawToFile(drawing, str(intermediate))
    subprocess.run(['gs', '-q', '-dSAFER', '-dBATCH', '-dNOPAUSE', '-sDEVICE=png16m', '-r180',
                    f'-sOutputFile={args.output/"official-success.png"}', str(intermediate)], check=True)
    raw = gzip.decompress(args.vcd.read_bytes()) if args.vcd.suffix == '.gz' else args.vcd.read_bytes()
    result.update(status='PASS', scope='official firmware RTL waveform; no physical timing',
                  source_commit=source['commit'], success_edge_ns=edge*scale,
                  timescale_ns_per_tick=scale, start_ns=start*scale, end_ns=last*scale,
                  vcd_sha256=hashlib.sha256(raw).hexdigest(),
                  log_sha256=hashlib.sha256(args.log.read_bytes()).hexdigest(),
                  renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  shared_renderer_sha256=hashlib.sha256((ROOT/'scripts/report/waveforms.py').read_bytes()).hexdigest())
    (args.output/'waveform.json').write_text(json.dumps(result, indent=2)+'\n')
    print(f'PASS official waveform: x4=0 at {edge*scale:g} ns, {result["retirements"]} commits, {result["cycles"]} cycles')


if __name__ == '__main__':
    main()
