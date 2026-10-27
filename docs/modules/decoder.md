# Decoder
## Objetivo
Gerar controles a partir da instrução (RISC-V oficial e guia).
## Entradas
instr_i[31:0]; parâmetro EXPERIMENTAL_XICRC=1 por padrão (nome histórico preservado).
## Saídas
alu_op_o e seletores/enables descritos na baseline, incluindo crc_o e trap_o.
## Comportamento
Reconhece as instruções de docs/isa/enabled.json; demais palavras ilegais.
Com EXPERIMENTAL_XICRC=1, reconhece CRCB/CRCH/CRCW sob o
[contrato oficial implementado](../architecture/crc.md). Valor 0 desabilita as três.
## Dependências
ALU e FSM.
## Casos especiais
Checagem de funct3/funct7; ilegal desabilita RF.
FENCE aceita funct3=000, ignora campos reservados e não gera escrita.
ECALL/EBREAK exigem a palavra completa e geram apenas trap_o; SYSTEM vizinhas
e FENCE.I permanecem ilegais. Ver [EEI CMOS](../architecture/system.md).
## Diagrama
```mermaid
flowchart LR
 IR --> F[opcode / funct3 / funct7]
 F --> CTRL[seletores e enables]
 F --> ILLEGAL[illegal]
 F --> TRAP[trap solicitado: ECALL / EBREAK]
```
## Testbench
tb_decoder: varredura opcode/funct3/funct7 em dois perfis; tb_isa, tb_core_smoke e tb_core_crc.
## Casos testados
131138 palavras por perfil (131072 combinações e 66 SYSTEM/vizinhas), válidas e inválidas; operandos limite
e aleatórios, x0 e sobreposição rd/rs1 no core.
## Resultado
results/logs/tb_decoder.log e tb_core_smoke.log. Evidência dos dois perfis:
`results/experiments/crc/tb_decoder.log`.
## Integração
Decoder → muxes de operandos / RF / FSM.
## Commit validado
Tags core-smoke-v1, isa-rtype-v1 e marcos seguintes em git log.
## Pendências
Diagramas ChipInventor para submissão. Fechamento funcional: tag isa-47-v1 e
`results/experiments/isa-47-20261027/logs/regression.json`.
