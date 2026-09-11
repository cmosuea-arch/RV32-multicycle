# RISC-V Core
## Objetivo
Integrar datapath e FSM multiciclo.
## Entradas
clk_i/rst_i, data_i e bus_fault_i.
## Saídas
Barramento address/data/oe/we/bw e sinais de aposentadoria commit_*.
## Comportamento
Uma instrução por vez; PC e RF escrevem em WRITEBACK, IR em FETCH.
## Dependências
PC, IR, RF, Immediate, ALU, decoder e control_unit.
## Casos especiais
FAULT diagnóstico CMOS persistente; x0 sempre zero, inclusive na observação.
## Diagrama
Ver architecture/block_diagram.md; CRC/memória ainda não implementados neste marco.
## Testbench
tb_core_smoke.
## Casos testados
ADD/SUB/ADDI em programa encadeado, PC, dados aposentados e escrita física no RF.
## Resultado
results/logs/tb_core_smoke.log e regressão PASS.
## Integração
Primeiro núcleo executável. Barramento simples sem handshake externo.
## Commit validado
Tag core-smoke-v1.
## Pendências
Famílias adicionais, memórias, CRC, sistema e interface física oficial.
