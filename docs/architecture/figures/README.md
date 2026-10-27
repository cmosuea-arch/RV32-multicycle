# Datapath e controle — figuras do relatório

Revisão: **2026-10-27**. Escopo: `riscv_core`, `riscv_top` e blocos conectados,
com Xicrc oficial: a=rs1/dados e b=rs2/CRC anterior, habilitado por padrão.
O desenho está dividido em três painéis;
nomes iguais identificam o mesmo fio entre blocos/painéis.

| Painel | SVG vetorial | PNG usado no PDF |
|---|---|---|
| F01-A — operandos, execução e writeback | [SVG](datapath-execution.svg) | [PNG](datapath-execution.png) |
| F01-B — PC, LSU e memórias | [SVG](datapath-memory.svg) | [PNG](datapath-memory.png) |
| F01-C — decode, FSM e enables | [SVG](datapath-control.svg) | [PNG](datapath-control.png) |

## Conferência com o RTL

| Caminho desenhado | Fonte conferida | Comportamento preservado |
|---|---|---|
| IR → RF/imediato/decoder | `rtl/riscv_core.sv` | Índices de 5 bits, formatos I/S/B/U/J, campos de decode |
| RF/PC/imediato → ALU | `rtl/riscv_core.sv` | a_pc e b_imm selecionam operandos de 32 bits |
| RF → MULT/CRC/Branch | `rtl/riscv_core.sv` | a/b e funct3; comparador fornece branch_taken |
| Execução → result_q | `rtl/riscv_core.sv` | Prioridade link, CRC, MULT, ALU; captura em EXECUTE |
| Load/resultado → RF | `rtl/riscv_core.sv` | load_data ou result_q; WE = retire && reg_we |
| Alvo → next_pc_q → PC | `rtl/riscv_core.sv`, `rtl/pc.sv` | JALR limpa bit 0; branch condicionado; PC atualiza em retire |
| result_q/PC → endereço | `rtl/riscv_core.sv` | Endereço de dados mantido também em WRITEBACK de load/store |
| LSU ↔ barramento | `rtl/lsu.sv`, `rtl/riscv_core.sv` | Extensões, posicionamento, alinhamento e bw condicionado por we |
| Decoder de endereços ↔ IMEM/DMEM | `rtl/riscv_top.sv`, `rtl/address_decoder.sv` | Bases, alinhamento, seleção do retorno e proteção de ROM |
| Classificação/erros → FSM | `rtl/control_unit.sv`, `rtl/riscv_core.sv` | MEMORY só para load/store; FAULT até reset |
| Estado → enables/observação | `rtl/riscv_core.sv` | IR/PC/RF, oe/we/bw e sinais commit_* |

Verde identifica armazenamento arquitetural/intermediário; azul identifica
funções e caminhos de dados; roxo identifica controle; laranja identifica CRC
e vermelho identifica diagnóstico. Alguns blocos combinam mux e
registrador na mesma caixa, com a equação e o instante de captura explícitos.
O painel A representa o IR e sua saída; o painel B detalha sua captura de rdata.

São figuras arquiteturais autorais. Não são esquemáticos extraídos da síntese
nem diagramas produzidos no ChipInventor. A exigência específica de diagramas
por módulo no ChipInventor continua pendente. Mudanças de RTL exigem revisão
manual das figuras: o gerador não verifica equivalência automática.

## Reproduzir

Preparar o ambiente opcional conforme [relatório](../../report/README.md).
O gerador usa ReportLab/fontes DejaVu e Ghostscript (`gs`):

```bash
build/report-venv/bin/python scripts/report/figures.py
build/report-venv/bin/python scripts/report/build.py
```

Execute na raiz. A fonte editável é `scripts/report/figures.py`; SVG e PNG são
versionados para visualização imediata. PDFs vetoriais intermediários ficam
em `build/`, ignorados pelo Git. A prévia do relatório incorpora os três painéis
nas páginas 5–7. O gerador do PDF aceita figuras PNG/JPEG locais em parágrafos
próprios, mantendo proporção e limitando as dimensões à página.
