# Program Counter
## Objetivo
Manter endereço da instrução; Block Guide §3.1.4.
## Entradas
clk_i, rst_i, we_i, next_i[31:0]; parâmetro RESET_PC.
## Saídas
pc_o e plus4_o[31:0].
## Comportamento
Atualização síncrona com enable; reset em 0x00400000.
## Dependências
Seleção de next_i pertence ao datapath/controle.
## Casos especiais
Soma modular; desalinhamento validado no core, não no registrador PC.
## Diagrama
```mermaid
flowchart LR
 NEXT[next_i] --> REG[PC com enable/reset]
 REG --> PC[pc_o]
 PC --> ADD[mais 4]
 ADD --> P4[plus4_o]
```
## Testbench
tb_pc e tb_pc_alu.
## Casos testados
Sequência, retenção, alvos positivos/negativos, wrap, reset sobre enable.
## Resultado
results/logs/tb_pc.log e regressão PASS.
## Integração
PC → ALU com imediato J → PC; seleção sequencial/redirect.
## Commit validado
Tag block-pc-v1.
## Pendências
Branches/jumps integrados e verificados em isa-29-v1 e isa-41-v1; ChipInventor pendente.
