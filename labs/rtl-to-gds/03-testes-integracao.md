# 3 — Integração: das conexões ao programa executado

[Anterior](02-testes-unitarios.md) · [Índice](README.md) · [Próxima](04-scripts-python.md)

## Objetivo e arquivos

Entender o que muda ao conectar blocos. Abra
[tb_rf_alu.sv](../../tb/integration/tb_rf_alu.sv),
[tb_isa.sv](../../tb/integration/tb_isa.sv) e
[tb_firmware.sv](../../tb/integration/tb_firmware.sv).

## Primeira integração: RF + imediato + ALU

`tb_rf_alu` conecta também `imm_ext`: o imediato entra pelo operando B da ALU,
e o resultado da ALU alimenta a escrita do Register File. A bancada controla os
seletores diretamente; ela ainda não executa a FSM inteira do processador.

```text
instrução → imm_ext ───┐
                      mux → ALU → escrita no RF
RF: leitura de rs2 ───┘       ↑
RF: leitura de rs1 ───────────┘
```

O teste grava -1 em x1 e 1 em x2 por PASS_B, soma os dois e verifica zero em x3.
Depois subtrai x2 de x1 e verifica `0xfffffffe` em x1. Isso exercita leitura,
seleção de operandos, escrita e dependência entre operações.

O clock tem período de 10 ns. Os estímulos mudam na descida; o RF escreve na subida.
O `#1` após a subida permite observar o valor já atualizado pelo registrador.

## Execução manual e automatizada

```bash
mkdir -p build
iverilog -g2012 -Wall -s tb_rf_alu -o build/lab_tb_rf_alu rtl/alu.sv rtl/regfile.sv rtl/imm_ext.sv tb/integration/tb_rf_alu.sv
vvp build/lab_tb_rf_alu
make tb TB=tb_rf_alu
```

Resultado: `PASS rf_alu: source reads, overflow and dependent writeback`.
Se o unitário da ALU passa e essa bancada falha, investigue também seleção,
endereços de registradores e instante de escrita.

## Percurso incremental

Execute os comandos da tabela, de cima para baixo, na raiz do projeto:

| Comando | Conexão/comportamento em foco |
|---|---|
| `make tb TB=tb_pc_alu` | cálculo do endereço de redirecionamento |
| `make tb TB=tb_ir_imm` | captura da instrução e imediato correspondente |
| `make tb TB=tb_fetch` | PC, ROM e IR na busca sequencial |
| `make tb TB=tb_datapath` | seleção de operandos e writeback |
| `make tb TB=tb_branch_pc` | decisão de branch e atualização do PC |
| `make tb TB=tb_lsu_rf` | formatação de loads/stores ligada aos registradores |
| `make tb TB=tb_lsu_dmem` | máscaras e preservação dos bytes de memória |
| `make tb TB=tb_memory_bus` | seleção ROM/RAM e proteção de escrita |
| `make tb TB=tb_mult_rf` | produto e escrita da parte selecionada |
| `make tb TB=tb_core_smoke` | ADD/SUB/ADDI percorrendo a FSM |
| `make tb TB=tb_core_faults` | instruções inválidas, efeitos bloqueados e reset |
| `make tb TB=tb_memory_faults` | endereços inválidos/desalinhados e cancelamento |
| `make tb TB=tb_isa` | programa e aposentadorias comparados ao modelo Python |
| `make tb TB=tb_firmware` | programa C/assembly compilado, executado até assinatura |
| `make tb TB=tb_core_crc` | trace Xicrc oficial, dependências e armazenamento |
| `make simple-system` | sistema pequeno: firmware com CRC, reset, sucesso e falha |
| `make official-run` | imagem oficial, 44 tipos, x4 final e loop de término |

Com `tb_rf_alu`, são os 18 testes da suíte. Antes da primeira execução oficial,
use `make official-fetch` para obter a imagem fixada por SHA-256. Depois,
`make integration` executa todos em ordem alfabética e prepara entradas offline.

## Como reconhecer a execução completa

Em `tb_isa`, aposentadoria significa que uma instrução terminou seus efeitos
arquiteturais. A referência fornece PC, instrução, destino e dado esperado para
comparar com `commit_*`. Há também checagens de RF e memória.
Na baseline, espere 88.727 aposentadorias, 45 stores e 12 bytes finais comparados.

No firmware próprio, o código de startup prepara memória e pilha. O C executa
cálculos e escreve `0x600dc0de` em `0x10011ff0`. O TB verifica a escrita e seu
armazenamento. Espere 598 aposentadorias e 2.579 ciclos na baseline.
Essas contagens podem mudar com uma alteração legítima do firmware/toolchain.

Para executar somente esse programa no processador:

```bash
make firmware
make run
cat results/logs/tb_firmware.log
```

O primeiro comando só compila; `run` recompila o necessário e executa `tb_firmware`.
Você pode chamar `make run` diretamente, sem executar `make firmware` antes.

## Sistema pequeno e Xicrc

```bash
make simple-system
cat results/logs/simple_build.log
cat results/logs/tb_simple_system.log
```

Essa prática usa [outro firmware](../../firmware/simple/README.md), ROM de 2 KiB,
RAM de 1 KiB e assinatura em 0x100103f0. O programa exercita CRCB/CRCH/CRCW; o TB
verifica boot, reset, assinatura ruim e instrução inválida. A baseline continua
47/47 sob o EEI CMOS, com o CRC validado conforme [contrato oficial](../../docs/architecture/crc.md).

O sistema já testado será a entrada da [aula de síntese](07-sintese.md).
O teste da netlist é adicional às 19 integrações RTL.

## FENCE e pedidos de trap

```bash
make system
cat results/logs/tb_core_system.log
cat results/logs/system.json
```

Leia [tb_core_system](../../tb/integration/tb_core_system.sv) nesta ordem:
`prepare` monta store/FENCE/load e uma instrução ECALL ou EBREAK;
`run_to_trap` compara os seis commits anteriores, verifica o PC e o motivo do
trap e confirma que o store posterior não ocorre; `reset_core` recupera FETCH.
O teste varia máscaras/campos FENCE e repete os dois tipos de trap. Compare
`commit_valid_o` com `trap_o`: a instrução que gera trap não aposenta.
O [contrato EEI CMOS](../../docs/architecture/system.md) encerra a execução até
reset, sem serviços de sistema/CSRs. O firmware oficial exercita 44 tipos;
esses testes próprios completam o perfil de 47.

## Observar o firmware em forma de onda

```bash
make wave
gtkwave results/waveforms/smoke.vcd
```

O GTKWave é opcional. A onda gerada cobre `dut.core`; procure clock, reset, estado,
PC e sinais de aposentadoria. A inspeção visual complementa as comparações automáticas.

## Exercício e critério para avançar

Por que PC + 4 não ocorre a cada clock? Porque uma instrução usa vários estados;
neste core, PC e RF atualizam na aposentadoria. Consulte o contrato em
[interfaces.md](../../docs/architecture/interfaces.md).
Avance após interpretar a integração RF/ALU e obter `make integration` em PASS.
