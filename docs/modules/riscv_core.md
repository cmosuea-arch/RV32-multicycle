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
PC, IR, RF, Immediate, ALU, branch_comp, LSU, multiplier, decoder e control_unit.
## Casos especiais
FAULT diagnóstico CMOS persistente; x0 sempre zero, inclusive na observação.
## Diagrama
Ver architecture/block_diagram.md para o datapath e a FSM integrados.
## Testbench
tb_core_smoke, tb_isa (trace arquitetural Python por aposentadoria), tb_core_faults,
tb_memory_faults e tb_firmware.
## Casos testados
Operações habilitadas em docs/isa/enabled.json; PC, dados aposentados, escrita
física no RF, dependências, limites e branches tomados/não tomados para frente/trás.
JAL/JALR: link PC+4, offsets positivos/negativos, rd=rs1, bit 0 removido.
Erros: instruções inválidas/não suportadas, alvos desalinhados e erro de fetch,
sem efeitos colaterais; branch não tomado não valida o alvo.
## Resultado
results/logs/tb_core_smoke.log e regressão PASS.
## Integração
Núcleo executável de 41 instruções. Barramento simples sem handshake externo;
IMEM combinacional e DMEM síncrona conectadas pelo top. Loads/stores acrescentam
o estado MEMORY. Multiplicação combinacional selecionada em EXECUTE.
## Commit validado
Tag isa-41-v1; firmware e evidências finais em rtl-subset-v0.1.
## Pendências
CRC, sistema, firmware oficial e interface física oficial.
