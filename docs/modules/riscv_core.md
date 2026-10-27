# RISC-V Core
## Objetivo
Integrar datapath e FSM multiciclo.
## Entradas
clk_i/rst_i, data_i e bus_fault_i. Parâmetro EXPERIMENTAL_XICRC=1 por padrão (nome histórico preservado).
## Saídas
Barramento address/data/oe/we/bw e sinais de aposentadoria commit_*.
trap_o, trap_ebreak_o e trap_pc_o conforme [EEI CMOS](../architecture/system.md).
## Comportamento
Uma instrução por vez; PC e RF escrevem em WRITEBACK, IR em FETCH.
## Dependências
PC, IR, RF, Immediate, ALU, branch_comp, LSU, multiplier, decoder e control_unit.
Com EXPERIMENTAL_XICRC=1, inclui o [Xicrc oficial](crc.md).
## Casos especiais
FAULT diagnóstico CMOS persistente; x0 sempre zero, inclusive na observação.
FENCE ordenada sem escritas; ECALL/EBREAK entram em TRAP preciso até reset,
sem aposentadoria nem alteração de PC/RF/memória. A interface foi ampliada para
expor o pedido ao ambiente; não implementa modos privilegiados/CSRs.
## Diagrama
Ver architecture/block_diagram.md para o datapath e a FSM integrados.
## Testbench
tb_core_smoke, tb_isa (trace arquitetural Python por aposentadoria), tb_core_faults,
tb_memory_faults, tb_firmware, tb_core_crc, tb_core_system, tb_simple_system e tb_official_firmware.
## Casos testados
Operações habilitadas em docs/isa/enabled.json; PC, dados aposentados, escrita
física no RF, dependências, limites e branches tomados/não tomados para frente/trás.
JAL/JALR: link PC+4, offsets positivos/negativos, rd=rs1, bit 0 removido.
Erros: instruções inválidas/não suportadas, alvos desalinhados e erro de fetch,
sem efeitos colaterais; branch não tomado não valida o alvo.
## Resultado
results/logs/tb_core_smoke.log e regressão PASS.
## Integração
Núcleo de 47 instruções sob o EEI CMOS. Barramento simples sem handshake externo;
IMEM combinacional e DMEM síncrona conectadas pelo top. Loads/stores acrescentam
o estado MEMORY. Multiplicação combinacional selecionada em EXECUTE.
CRC habilitado também é combinacional e usa EXECUTE/WRITEBACK sem novos estados.
## Commit validado
Tag isa-41-v1; firmware e evidências finais em rtl-subset-v0.1.
Perfil CRC provisório em 05fd114; sistema experimental em 2e87e0e, com evidências
em `results/experiments/`. As tags anteriores descrevem a baseline histórica.
## Pendências
Interface física final, diagramas ChipInventor e síntese da versão atual.
Tag isa-47-v1: 33 TBs/lint e firmware oficial PASS (44 tipos) na rodada
`results/experiments/isa-47-20261027/`.
