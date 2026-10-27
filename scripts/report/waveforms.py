#!/usr/bin/env python3
"""Valida a captura VCD do smoke próprio e exporta janelas reais em SVG/PNG."""
# Usa a captura real de make wave; não inventa transições nem executa nova simulação.
import argparse
from bisect import bisect_left, bisect_right
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[2]
CORE = 'tb_firmware.dut.core.'
# Lista das redes obrigatórias, nomes de exibição e larguras esperadas no VCD.
ROWS = [
    ('clk_i', 'clk', 1), ('rst_i', 'reset', 1), ('state', 'FSM', 3),
    ('current_pc', 'PC [31:0]', 32), ('instruction', 'instrução [31:0]', 32),
    ('commit_valid_o', 'commit_valid', 1), ('commit_rd_o', 'commit_rd [4:0]', 5),
    ('commit_data_o', 'commit_data [31:0]', 32), ('oe_o', 'oe', 1),
    ('we_o', 'we', 1), ('address_o', 'endereço [31:0]', 32),
    ('data_o', 'dado store [31:0]', 32), ('bw_o', 'bw [3:0]', 4),
    ('fault_o', 'fault', 1),
]


def load_vcd(path, core=CORE):
    """Lê escala, hierarquia e mudanças das redes selecionadas; preserva X/Z."""
    events, widths, codes, scope = {}, {}, {}, []
    timestamp, last, header = 0, 0, True
    opener = gzip.open if path.suffix == '.gz' else open
    scale = None
    with opener(path, 'rt') as stream:
        for raw in stream:
            line = raw.strip()
            if not line:
                continue
            # Cabeçalho associa identificadores VCD a redes e define a escala de tempo.
            if header:
                if line.startswith('$timescale'):
                    declaration = line
                    while '$end' not in declaration:
                        declaration += ' ' + next(stream).strip()
                    match = re.search(r'(\d+)\s*(s|ms|us|ns|ps|fs)\b', declaration)
                    if not match:
                        raise ValueError('Escala de tempo VCD inválida')
                    scale = int(match[1]) * {'s': 1e9, 'ms': 1e6, 'us': 1e3,
                                             'ns': 1, 'ps': 1e-3, 'fs': 1e-6}[match[2]]
                elif line.startswith('$scope'):
                    scope.append(line.split()[2])
                elif line.startswith('$upscope'):
                    scope.pop()
                elif line.startswith('$var'):
                    fields = line.split()
                    full = '.'.join([*scope, fields[4]])
                    if full in {core + name for name, _, _ in ROWS}:
                        name = full.removeprefix(core)
                        widths[name] = int(fields[2])
                        codes[fields[3]] = name
                        events[name] = []
                elif line.startswith('$enddefinitions'):
                    header = False
                continue
            # Corpo contém timestamps e mudanças; só guardamos as redes selecionadas.
            if line.startswith('#'):
                timestamp = int(line[1:])
                if timestamp < last:
                    raise ValueError('Tempo VCD fora de ordem')
                last = timestamp
                continue
            if line.startswith('$'):
                continue
            if line[0].lower() == 'b':
                value, code = line[1:].split()
            elif line[0].lower() in '01xz':
                value, code = line[0], line[1:]
            else:
                continue
            if code not in codes:
                continue
            name = codes[code]
            value = value.lower()
            if not re.fullmatch('[01xz]+', value) or len(value) > widths[name]:
                raise ValueError(f'Valor VCD inválido: {name}')
            value = value.rjust(widths[name], value[0] if value[0] in 'xz' else '0')
            history = events[name]
            if history and history[-1][0] == timestamp:
                history[-1] = (timestamp, value)  # Último valor após deltas desse instante.
            elif not history or history[-1][1] != value:
                history.append((timestamp, value))
    for name, _, width in ROWS:
        if name not in events or not events[name] or widths[name] != width:
            raise ValueError(f'Rede obrigatória ausente/vazia ou largura incorreta: {name}')
    if scale is None:
        raise ValueError('VCD sem escala de tempo')
    return events, scale, last


def sample(events, name, time, before=False):
    # Busca binária obtém o último valor, incluindo ou excluindo o instante da borda.
    history = events[name]
    times = [t for t, _ in history]
    idx = (bisect_left(times, time) if before else bisect_right(times, time)) - 1
    return history[idx][1] if idx >= 0 else 'x' * len(history[0][1])


def number(bits):
    # X/Z podem ser desenhados, mas não servem como valores válidos de verificação.
    if any(c in bits for c in 'xz'):
        raise ValueError(f'Valor indefinido em amostra de verificação: {bits}')
    return int(bits, 2)


def verify(events, log):
    """A escrita síncrona e o commit usam valores anteriores à borda, antes dos NBAs."""
    match = re.search(r'PASS firmware: signature 600dc0de, (\d+) retirements, (\d+) cycles', log)
    if not match or '$fatal' in log or 'FATAL:' in log:
        raise ValueError('Log não comprova término válido do firmware')
    release = next((t for t, v in events['rst_i'] if v == '0'), None)
    if release is None:
        raise ValueError('Reset não foi liberado')
    cycles, retired, writes = 0, 0, []
    previous_clock = 'x'
    # Reconta ciclos/commits e valida a escrita da assinatura contra o log do TB.
    for time, clock in events['clk_i']:
        rising = previous_clock == '0' and clock == '1'
        previous_clock = clock
        if not rising or time <= release:
            continue
        get = lambda name: number(sample(events, name, time, before=True))
        if get('rst_i') != 0 or get('fault_o') != 0:
            raise ValueError('Reset/falha inesperado após início da execução')
        cycles += 1
        retired += get('commit_valid_o')
        if get('we_o') and get('address_o') == 0x10011ff0:
            if get('data_o') != 0x600dc0de or get('bw_o') != 15 or get('state') != 4:
                raise ValueError('Escrita de assinatura inválida no VCD')
            writes.append(time)
    if len(writes) != 1 or [retired, cycles] != list(map(int, match.groups())):
        raise ValueError(f'VCD/log divergem: {retired} commits, {cycles} ciclos, {writes}')
    return {'signature_edge_tick': writes[0], 'reset_release_tick': release,
            'retirements': retired, 'cycles': cycles, 'signature_address': '0x10011ff0',
            'signature_data': '0x600dc0de', 'signature_bw': '0xf'}


def label(d, x, y, text, size=10, color='#223e50'):
    # Aplica a mesma fonte e cor aos rótulos das figuras.
    d.add(String(x, y, text, fontName='Wave', fontSize=size, fillColor=HexColor(color)))


def value_label(bits, name):
    # FSM usa letras dos estados; buses usam hexadecimal; indefinidos mantêm X/Z.
    if name == 'state' and not any(c in bits for c in 'xz'):
        return {0: 'F', 1: 'D', 2: 'E', 3: 'W', 4: 'M', 5: 'FAULT'}.get(int(bits, 2), '?')
    return bits.upper() if any(c in bits for c in 'xz') else f'{int(bits, 2):0{(len(bits)+3)//4}x}'


def draw(events, scale, start, end, title, subtitle, marker=None):
    """Traça patamares e buses por mudanças efetivas do VCD, sem interpolar valores."""
    d = Drawing(700, 580)
    d.add(Rect(0, 0, 700, 580, fillColor=white, strokeColor=None))
    label(d, 12, 556, title, 15)
    label(d, 12, 538, subtitle, 10)
    x0, x1, top, row_h = 165, 685, 485, 29
    xpos = lambda t: x0 + (t - start) / (end - start) * (x1 - x0)
    start_ns, end_ns = start * scale, end * scale
    step_ns = 25 if end_ns - start_ns > 100 else 20
    ticks_ns = range(math.ceil(start_ns / step_ns)*step_ns,
                     math.floor(end_ns / step_ns)*step_ns + 1, step_ns)
    for time_ns in ticks_ns:
        time = time_ns / scale
        x = xpos(time)
        d.add(Line(x, 80, x, top + 15, strokeColor=HexColor('#dce4e9'), strokeWidth=0.5))
        label(d, min(max(x - 15, x0), x1 - 42), 510, f'{time*scale:.0f}', 9)
    label(d, 12, 510, 'Tempo de simulação (ns)', 9)
    # Divide cada linha em intervalos constantes: patamares para bits e caixas para buses.
    for i, (name, display, width) in enumerate(ROWS):
        y = top - i * row_h
        label(d, 12, y - 4, display, 10.5)
        history = events[name]
        cuts = [start, *(t for t, _ in history if start < t < end), end]
        previous_y = None
        for a, b in zip(cuts, cuts[1:]):
            bits = sample(events, name, a)
            left, right = xpos(a), xpos(b)
            unknown = any(c in bits for c in 'xz')
            color = '#a15c12' if unknown else '#244f70'
            if width == 1 and not unknown:
                level = y + (7 if bits == '1' else -7)
                d.add(Line(left, level, right, level, strokeColor=HexColor(color), strokeWidth=1.1))
                if previous_y is not None:
                    d.add(Line(left, previous_y, left, level, strokeColor=HexColor(color), strokeWidth=1.1))
                previous_y = level
            else:
                fill = '#fff4df' if unknown else '#edf5fa'
                d.add(Polygon([left, y, left + min(2, (right-left)/3), y+9,
                               right-min(2, (right-left)/3), y+9, right, y,
                               right-min(2, (right-left)/3), y-9,
                               left+min(2, (right-left)/3), y-9],
                              fillColor=HexColor(fill), strokeColor=HexColor(color), strokeWidth=0.6))
                value = value_label(bits, name)
                needed = pdfmetrics.stringWidth(value, 'Wave', 10)
                if right - left >= needed + 6:
                    label(d, (left + right - needed)/2, y - 3.5, value, 10, color)
                previous_y = None
    if marker is not None:
        x = xpos(marker)
        d.add(Line(x, 79, x, top+17, strokeColor=HexColor('#ad3333'), strokeWidth=1.1))
        label(d, 400, 522, f'SW na borda: {marker*scale:g} ns', 10, '#ad3333')
    label(d, 12, 55, 'FSM: F=FETCH(0), D=DECODE(1), E=EXECUTE(2), W=WRITEBACK(3), M=MEMORY(4).', 9)
    label(d, 12, 38, 'Buses em hexadecimal; X/Z preservados. Valores sem espaço para rótulo são omitidos.', 9)
    label(d, 12, 21, 'commit_rd/data só têm significado com commit_valid=1; we/bw qualificam o store.', 9)
    return d


def main():
    # Recebe captura/log, valida ambos e recorta as janelas de boot e assinatura.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vcd', type=Path, default=ROOT/'results/waveforms/smoke.vcd')
    parser.add_argument('--log', type=Path, default=ROOT/'results/logs/tb_firmware.wave.log')
    parser.add_argument('--output', type=Path, default=ROOT/'results/experiments/firmware-wave')
    args = parser.parse_args()
    events, scale, last = load_vcd(args.vcd)
    result = verify(events, args.log.read_text())
    edge = result['signature_edge_tick']
    windows = [
        ('firmware-boot', 0, int(150/scale), 'F20-A — Boot do firmware próprio',
         'Reset, busca e primeiras instruções; captura real de tb_firmware.'),
        ('firmware-signature', edge-int(85/scale), last, 'F20-B — Término do firmware próprio',
         'SW: endereço 10011ff0, dado 600dc0de, máscara f; fault permanece zero.'),
    ]
    if last < windows[0][2] or edge < int(85/scale):
        raise ValueError('Captura curta demais para as janelas previstas')
    pdfmetrics.registerFont(TTFont('Wave', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    args.output.mkdir(parents=True, exist_ok=True)
    figures = {}
    for name, start, end, title, subtitle in windows:
        drawing = draw(events, scale, start, end, title, subtitle,
                       marker=edge if name == 'firmware-signature' else None)
        svg = args.output/f'{name}.svg'
        renderSVG.drawToFile(drawing, str(svg))
        svg.write_text(svg.read_text().replace('font-family: Wave;', 'font-family: DejaVu Sans;'))
        intermediate = ROOT/'build'/f'{name}.pdf'
        intermediate.parent.mkdir(exist_ok=True)
        renderPDF.drawToFile(drawing, str(intermediate))
        subprocess.run(['gs','-q','-dSAFER','-dBATCH','-dNOPAUSE','-sDEVICE=png16m','-r180',
                        f'-sOutputFile={args.output/(name+".png")}',str(intermediate)],check=True)
        figures[name] = {'start_ns': start*scale, 'end_ns': end*scale}
    # Hashes vinculam as imagens à captura, ao log e à versão deste renderizador.
    summary = {'status': 'PASS', 'scope': 'own smoke firmware; RTL simulation; not official firmware',
               **result, 'signature_edge_ns': edge*scale, 'timescale_ns_per_tick': scale,
               'end_ns': last*scale, 'windows': figures,
               'vcd_content_sha256': hashlib.sha256(
                   gzip.decompress(args.vcd.read_bytes()) if args.vcd.suffix=='.gz'
                   else args.vcd.read_bytes()).hexdigest(),
               'log_sha256': hashlib.sha256(args.log.read_bytes()).hexdigest(),
               'renderer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output/'waveform.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(f'PASS waveform: {result["cycles"]} ciclos, {result["retirements"]} commits; SW em {edge*scale:g} ns')


if __name__ == '__main__':
    main()
