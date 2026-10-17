#!/usr/bin/env python3
"""Desenha o datapath documentado; não extrai automaticamente nem modifica o RTL."""
from pathlib import Path
import subprocess

from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.shapes import Drawing, Rect, String, PolyLine, Polygon
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/architecture/figures'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BLUE = '#315d78'
PURPLE = '#705285'


def text(d, x, y, lines, size=11, color=BLUE):
    for i, line in enumerate(lines.split('\n')):
        d.add(String(x, y - i * (size + 4), line, fontName='Diagram',
                     fontSize=size, fillColor=HexColor(color)))


def box(d, x, y, w, h, title, lines, fill='#edf5fa', color=BLUE):
    d.add(Rect(x, y, w, h, rx=6, ry=6, fillColor=HexColor(fill),
               strokeColor=HexColor(color), strokeWidth=1))
    text(d, x + 10, y + h - 18, title, 12, color)
    text(d, x + 10, y + h - 36, lines, 10, color)


def arrow(d, points, label='', at=None, color=BLUE):
    d.add(PolyLine([c for p in points for c in p], strokeColor=HexColor(color),
                   strokeWidth=1, fillColor=None))
    x, y = points[-1]
    px, py = points[-2]
    dx, dy = x - px, y - py
    length = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / length, dy / length
    d.add(Polygon([x, y, x - 7 * ux + 3 * uy, y - 7 * uy - 3 * ux,
                   x - 7 * ux - 3 * uy, y - 7 * uy + 3 * ux],
                  fillColor=HexColor(color), strokeColor=None))
    if label:
        text(d, *at, label, 9, color)


def canvas(title, subtitle):
    d = Drawing(600, 660)
    d.add(Rect(0, 0, 600, 660, fillColor=white, strokeColor=None))
    text(d, 16, 638, title, 15)
    text(d, 16, 618, subtitle, 9)
    return d


def execution():
    d = canvas('F01-A — Operandos, execução e writeback',
               'Painéis A–C usam redes nomeadas: mesmo nome significa o mesmo fio.')
    box(d, 20, 535, 245, 60, 'IR → instruction[31:0]',
        'Entrada do painel B\nÍndices rs1/rs2/rd: 5 bits cada')
    box(d, 335, 535, 245, 60, 'Immediate Extension',
        'instruction → immediate[31:0]\nFormatos I / S / B / U / J')
    arrow(d, [(265, 565), (335, 565)], '32', (289, 573))
    box(d, 20, 425, 245, 80, 'Register File — 32 × 32',
        'instruction: índices; entrada: writeback_data\nSaídas a = rs1 e b = rs2 (32 bits)\nWE = retire && reg_we; x0 = 0', '#d9ebdf')
    arrow(d, [(140, 535), (140, 505)], 'índices', (148, 516))
    box(d, 335, 425, 245, 80, 'Branch Comparator',
        'Entradas: a, b e funct3[2:0]\nSaída: branch_taken (1 bit)\nDestino: seleção de PC no painel B')
    text(d, 335, 408, 'a / b / funct3 são redes nomeadas do RF e IR.', 9)
    box(d, 20, 315, 245, 65, 'MUX A',
        'a_pc ? current_pc : a\nSaída A[31:0] para a ALU')
    box(d, 335, 315, 245, 65, 'MUX B',
        'b_imm ? immediate : b\nSaída B[31:0] para a ALU')
    arrow(d, [(140, 425), (140, 380)], 'a[31:0]', (148, 390))
    text(d, 335, 390, 'current_pc vem do painel B.', 9)
    box(d, 20, 210, 175, 65, 'ALU', 'A, B, alu_op[3:0]\nalu_result[31:0]')
    box(d, 215, 210, 175, 65, 'Multiplicador', 'a, b, {0, funct3}\nproduct[31:0]')
    box(d, 410, 210, 170, 65, 'CRC experimental',
        'a, b, {0, funct3}\ncrc_result[31:0]', '#fff4df', '#a15c12')
    arrow(d, [(100, 315), (100, 275)], 'A[31:0]', (25, 291))
    arrow(d, [(450, 315), (450, 295), (170, 295), (170, 275)],
          'B[31:0]', (247, 301))
    box(d, 20, 105, 560, 65, 'MUX de execução → result_q[31:0]',
        'Prioridade: (jal || jalr) ? plus4 : crc_op ? CRC : mul ? MULT : ALU\nCaptura em EXECUTE; reset zera. plus4 vem do PC (painel B).', '#d9ebdf')
    for x in (110, 300, 490):
        arrow(d, [(x, 210), (x, 170)], '32', (x + 7, 184))
    box(d, 20, 10, 560, 60, 'MUX writeback → writeback_data[31:0] → RF',
        'load ? load_data : result_q; load_data vem da LSU (painel B).\nCRC existe somente com EXPERIMENTAL_XICRC=1; padrão é 0.')
    arrow(d, [(300, 105), (300, 70)], 'result_q[31:0]', (310, 83))
    return d


def memory():
    d = canvas('F01-B — Próximo PC, LSU e memórias',
               'Redes alu_result, result_q, a e b vêm do painel A; enables no painel C.')
    box(d, 20, 520, 260, 75, 'Alvo e seleção do próximo PC',
        'redirect_target = jalr ?\n  {alu_result[31:1], 0} : alu_result\nredirect = (branch && taken) || jal || jalr')
    box(d, 330, 520, 250, 75, 'next_pc_q[31:0]',
        'Captura em EXECUTE:\nredirect ? redirect_target : plus4\nReset zera.', '#d9ebdf')
    arrow(d, [(280, 555), (330, 555)], '32', (296, 564))
    box(d, 330, 410, 250, 75, 'PC — habilitado por retire',
        'WE: captura next_pc_q\nReset: current_pc = 0x00400000\nplus4 = current_pc + 4', '#d9ebdf')
    arrow(d, [(455, 520), (455, 485)], '32', (464, 496))
    text(d, 20, 481, 'taken = branch_taken do painel A.', 10)
    text(d, 20, 463, 'current_pc / plus4 também alimentam A.', 10)
    text(d, 20, 445, 'plus4 retorna ao mux next_pc acima.', 10)
    box(d, 20, 290, 260, 90, 'MUX endereço → address[31:0]',
        'result_q durante MEMORY ou\nWRITEBACK de load/store;\ncurrent_pc nos demais casos.\nSeleção gerada a partir do estado.')
    box(d, 330, 290, 250, 90, 'LSU — formatação / alinhamento',
        'Entradas: result_q, b, rdata,\nfunct3[2:0], store_op\nSaídas: load_data, store_data (32),\nstore_bw[3:0], misaligned, invalid')
    arrow(d, [(390, 410), (390, 397), (150, 397), (150, 380)],
          'current_pc[31:0]', (180, 402))
    box(d, 20, 165, 560, 80, 'Address Decoder + mux de retorno',
        'Entradas: address, store_data, oe, we, bw; saídas: rdata e bus_fault.\nmem_address = {address[31:2], 00}; ROM sem escrita; regiões parametrizadas.\nRoteia mem_address/mem_data/oe/we/bw; seleciona idata/ddata no retorno.')
    arrow(d, [(150, 290), (150, 245)], 'address[31:0]', (23, 263))
    arrow(d, [(455, 290), (455, 245)], 'store_data / bw (painel C)', (335, 263))
    box(d, 20, 55, 260, 70, 'IMEM — combinacional',
        'Base 0x00400000; mem_address / oe\nSaída idata[31:0]\nCapacidade e arquivo parametrizáveis')
    box(d, 330, 55, 250, 70, 'DMEM — síncrona',
        'Base 0x10010000; endereço / dados\noe / we / bw[3:0]; saída ddata[31:0]\nLeitura/escrita na borda de subida')
    arrow(d, [(110, 165), (110, 125)], 'addr / oe', (23, 139))
    arrow(d, [(220, 125), (220, 165)], 'idata', (228, 139))
    arrow(d, [(400, 165), (400, 125)], 'addr / dados / controles', (408, 147))
    arrow(d, [(550, 125), (550, 165)], 'ddata', (552, 139))
    text(d, 20, 29, 'rdata[31:0] → IR em FETCH e entrada mem_i da LSU; load_data → WB (A).', 10)
    text(d, 20, 12, 'IR captura rdata quando FETCH && !local_fault && !rst; retém nos demais estados.', 10)
    return d


def control():
    d = canvas('F01-C — Decode, FSM, enables e observação',
               'Controles associados às redes de dados dos painéis A e B; estado não é dado de WB.')
    box(d, 20, 495, 260, 100, 'Decoder — instruction[31:0]',
        'opcode / funct3 / funct7\nalu_op, a_pc, b_imm, reg_we\nbranch, jal, jalr, load, store_op\nmul, crc_op, illegal', '#f3f0fa', PURPLE)
    box(d, 330, 495, 250, 100, 'Control Unit / FSM',
        'FETCH → DECODE → EXECUTE\n→ [MEMORY] → WRITEBACK → FETCH\nDECODE ilegal ou fault → FAULT\nReset síncrono leva a FETCH.', '#f3f0fa', PURPLE)
    arrow(d, [(280, 550), (330, 550)], 'classes', (284, 564), PURPLE)
    box(d, 20, 350, 560, 100, 'local_fault → fault_i da FSM',
        'FETCH: bus_fault || current_pc[1:0] != 0\nEXECUTE: redirect && redirect_target[1:0] != 0\nMEMORY: bus_fault || misaligned || lsu_invalid\nDemais estados: sem novo local_fault. FAULT permanece até reset.', '#fbeaea', '#985151')
    arrow(d, [(455, 450), (455, 495)], 'fault_i', (465, 469), '#985151')
    box(d, 20, 190, 560, 115, 'Lógica de enables em riscv_core',
        'retire = (state == WRITEBACK) && !rst; WE do RF = retire && reg_we.\nWE do PC = retire. WE do IR = FETCH && !local_fault && !rst.\nresult_q / next_pc_q capturam em EXECUTE; reset tem prioridade.\noe = !rst && (FETCH || ((MEMORY || WRITEBACK) && load && válido)).\nwe = !rst && MEMORY && store_op && válido; bw = we ? store_bw : 0.', '#f3f0fa', PURPLE)
    arrow(d, [(570, 495), (590, 495), (590, 325), (460, 325), (460, 305)],
          'state[2:0]', (470, 331), PURPLE)
    box(d, 20, 65, 560, 80, 'Observação e sincronização',
        'commit_valid = retire; commit_pc = current_pc; commit_instr = instruction.\ncommit_rd = reg_we ? rd : 0; commit_data = commit_rd == 0 ? 0 : WB.\nfault_o = (state == FAULT); interfaces commit são de verificação, não pinagem final.')
    arrow(d, [(300, 190), (300, 145)], 'retire / dados arquiteturais', (310, 165))
    text(d, 20, 40, 'válido = !misaligned && !lsu_invalid. Address Decoder também bloqueia escrita fora da RAM.', 9)
    text(d, 20, 23, 'Clock/reset: PC, IR, RF, result_q, next_pc_q e FSM. DMEM usa clock e não é apagada por reset.', 9)
    text(d, 20, 6, 'Fonte: rtl/riscv_core.sv, riscv_top.sv, address_decoder.sv e control_unit.sv; revisão 17/10/2026.', 9)
    return d


def main():
    pdfmetrics.registerFont(TTFont('Diagram', FONT))
    OUT.mkdir(parents=True, exist_ok=True)
    for name, drawing in [('datapath-execution', execution()),
                          ('datapath-memory', memory()),
                          ('datapath-control', control())]:
        svg = OUT / f'{name}.svg'
        renderSVG.drawToFile(drawing, str(svg))
        # O alias interno ReportLab não é um nome de fonte instalado no navegador.
        svg.write_text(svg.read_text().replace('font-family: Diagram;',
                                               'font-family: DejaVu Sans;'))
        # PDF vetorial intermediário fica em build; PNG deriva do mesmo desenho.
        temp = ROOT / 'build' / f'{name}.pdf'
        temp.parent.mkdir(exist_ok=True)
        renderPDF.drawToFile(drawing, str(temp))
        subprocess.run(['gs', '-q', '-dSAFER', '-dBATCH', '-dNOPAUSE',
                        '-sDEVICE=png16m', '-r180',
                        f'-sOutputFile={OUT / (name + ".png")}', str(temp)], check=True)
        print(f'PASS figura: {name} (SVG + PNG)')


if __name__ == '__main__':
    main()
