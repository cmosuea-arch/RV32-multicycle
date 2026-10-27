# Decoder
## Objetivo
Gerar controles a partir da instrução (RISC-V oficial e guia).
## Entradas
instr_i[31:0]; parâmetro EXPERIMENTAL_XICRC=1 por padrão (nome histórico preservado).
## Saídas
alu_op_o e seletores/enables descritos na baseline, incluindo crc_o.
## Comportamento
Reconhece as instruções de docs/isa/enabled.json; demais palavras ilegais.
Com EXPERIMENTAL_XICRC=1, reconhece CRCB/CRCH/CRCW sob o
[contrato oficial implementado](../architecture/crc.md). Valor 0 desabilita as três.
## Dependências
ALU e FSM.
## Casos especiais
Checagem de funct3/funct7; ilegal desabilita RF.
## Diagrama
```mermaid
flowchart LR
 IR --> F[opcode / funct3 / funct7]
 F --> CTRL[seletores e enables]
 F --> ILLEGAL[illegal]
```
## Testbench
tb_decoder: varredura opcode/funct3/funct7 em dois perfis; tb_isa, tb_core_smoke e tb_core_crc.
## Casos testados
131072 combinações de campos por perfil, instruções válidas e inválidas; operandos limite
e aleatórios, x0 e sobreposição rd/rs1 no core.
## Resultado
results/logs/tb_decoder.log e tb_core_smoke.log. Evidência dos dois perfis:
`results/experiments/crc/tb_decoder.log`.
## Integração
Decoder → muxes de operandos / RF / FSM.
## Commit validado
Tags core-smoke-v1, isa-rtype-v1 e marcos seguintes em git log.
## Pendências
Definição de sistema e diagramas ChipInventor para submissão.
