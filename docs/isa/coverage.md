# Cobertura ISA

**44/47 instruções (93,62%)** com testes unitários, integração e regressão PASS registrados.

Os estados abaixo são resultados preservados; uma nova validação exige executar `make regression`.
Abra a [planilha Excel](coverage.xlsx) para filtrar, ordenar e consultar todos os campos.
Esta página apresenta os mesmos resultados registrados em [coverage.csv](coverage.csv).
As codificações abaixo estão em binário; **—** indica campo não aplicável ou ainda não definido.

## Resumo por categoria

| Categoria | Implementadas | Cobertura |
|---|---:|---:|
| Aritmética e lógica — registradores | 10/10 | 100,00% |
| Aritmética e lógica — imediatos | 9/9 | 100,00% |
| Imediatos superiores | 2/2 | 100,00% |
| Desvios condicionais | 6/6 | 100,00% |
| Saltos | 2/2 | 100,00% |
| Leitura de memória | 5/5 | 100,00% |
| Escrita de memória | 3/3 | 100,00% |
| Multiplicação — Zmmul | 4/4 | 100,00% |
| CRC — Xicrc | 3/3 | 100,00% |
| Sistema/Sincronização | 0/3 | 0,00% |
| **Total** | **44/47** | **93,62%** |

**Firmware oficial:** PASS, PENDENTE. A evidência da execução fica em `official_firmware.json` junto aos logs.
Slots de sistema são pendências, não nomes oficiais de instruções.

## Aritmética e lógica — registradores

**Módulos:** [alu](../modules/alu.md).
**Commit/tag validado:** `isa-44-v1`.

| Instrução | Opcode | Funct3 | Funct7 | Unitário | Integrado | Regressão | Execuções¹ |
|---|---|---|---|---|---|---|---:|
| `ADD` | `0110011` | `000` | `0000000` | PASS | PASS | PASS | 74.378 |
| `SUB` | `0110011` | `000` | `0100000` | PASS | PASS | PASS | 74 |
| `SLL` | `0110011` | `001` | `0000000` | PASS | PASS | PASS | 74 |
| `SLT` | `0110011` | `010` | `0000000` | PASS | PASS | PASS | 74 |
| `SLTU` | `0110011` | `011` | `0000000` | PASS | PASS | PASS | 74 |
| `XOR` | `0110011` | `100` | `0000000` | PASS | PASS | PASS | 74 |
| `SRL` | `0110011` | `101` | `0000000` | PASS | PASS | PASS | 74 |
| `SRA` | `0110011` | `101` | `0100000` | PASS | PASS | PASS | 74 |
| `OR` | `0110011` | `110` | `0000000` | PASS | PASS | PASS | 74 |
| `AND` | `0110011` | `111` | `0000000` | PASS | PASS | PASS | 74 |

**Evidências:** [tb_decoder](../../results/experiments/crc-official-20261027/logs/tb_decoder.log), [tb_alu](../../results/experiments/crc-official-20261027/logs/tb_alu.log), [tb_isa](../../results/experiments/crc-official-20261027/logs/tb_isa.log), [tb_official_firmware](../../results/experiments/crc-official-20261027/logs/tb_official_firmware.log).

## Aritmética e lógica — imediatos

**Módulos:** [alu](../modules/alu.md), [imm_ext](../modules/imm_ext.md).
**Commit/tag validado:** `isa-44-v1`.

| Instrução | Opcode | Funct3 | Funct7 | Unitário | Integrado | Regressão | Execuções¹ |
|---|---|---|---|---|---|---|---:|
| `ADDI` | `0010011` | `000` | — | PASS | PASS | PASS | 12.507 |
| `SLTI` | `0010011` | `010` | — | PASS | PASS | PASS | 62 |
| `SLTIU` | `0010011` | `011` | — | PASS | PASS | PASS | 62 |
| `XORI` | `0010011` | `100` | — | PASS | PASS | PASS | 62 |
| `ORI` | `0010011` | `110` | — | PASS | PASS | PASS | 62 |
| `ANDI` | `0010011` | `111` | — | PASS | PASS | PASS | 62 |
| `SLLI` | `0010011` | `001` | `0000000` | PASS | PASS | PASS | 38 |
| `SRLI` | `0010011` | `101` | `0000000` | PASS | PASS | PASS | 38 |
| `SRAI` | `0010011` | `101` | `0100000` | PASS | PASS | PASS | 38 |

**Evidências:** [tb_decoder](../../results/experiments/crc-official-20261027/logs/tb_decoder.log), [tb_imm_ext](../../results/experiments/crc-official-20261027/logs/tb_imm_ext.log), [tb_alu](../../results/experiments/crc-official-20261027/logs/tb_alu.log), [tb_isa](../../results/experiments/crc-official-20261027/logs/tb_isa.log), [tb_official_firmware](../../results/experiments/crc-official-20261027/logs/tb_official_firmware.log).

## Imediatos superiores

**Módulos:** [alu](../modules/alu.md), [pc](../modules/pc.md), [imm_ext](../modules/imm_ext.md).
**Commit/tag validado:** `isa-44-v1`.

| Instrução | Opcode | Funct3 | Funct7 | Unitário | Integrado | Regressão | Execuções¹ |
|---|---|---|---|---|---|---|---:|
| `LUI` | `0110111` | — | — | PASS | PASS | PASS | 6 |
| `AUIPC` | `0010111` | — | — | PASS | PASS | PASS | 6 |

**Evidências:** [tb_decoder](../../results/experiments/crc-official-20261027/logs/tb_decoder.log), [tb_imm_ext](../../results/experiments/crc-official-20261027/logs/tb_imm_ext.log), [tb_pc](../../results/experiments/crc-official-20261027/logs/tb_pc.log), [tb_isa](../../results/experiments/crc-official-20261027/logs/tb_isa.log), [tb_official_firmware](../../results/experiments/crc-official-20261027/logs/tb_official_firmware.log).

## Desvios condicionais

**Módulos:** [branch_comp](../modules/branch_comp.md).
**Commit/tag validado:** `isa-44-v1`.

| Instrução | Opcode | Funct3 | Funct7 | Unitário | Integrado | Regressão | Execuções¹ |
|---|---|---|---|---|---|---|---:|
| `BEQ` | `1100011` | `000` | — | PASS | PASS | PASS | 7 |
| `BNE` | `1100011` | `001` | — | PASS | PASS | PASS | 7 |
| `BLT` | `1100011` | `100` | — | PASS | PASS | PASS | 7 |
| `BGE` | `1100011` | `101` | — | PASS | PASS | PASS | 7 |
| `BLTU` | `1100011` | `110` | — | PASS | PASS | PASS | 7 |
| `BGEU` | `1100011` | `111` | — | PASS | PASS | PASS | 7 |

**Evidências:** [tb_decoder](../../results/experiments/crc-official-20261027/logs/tb_decoder.log), [tb_branch_comp](../../results/experiments/crc-official-20261027/logs/tb_branch_comp.log), [tb_isa](../../results/experiments/crc-official-20261027/logs/tb_isa.log), [tb_official_firmware](../../results/experiments/crc-official-20261027/logs/tb_official_firmware.log).

## Saltos

**Módulos:** [pc](../modules/pc.md), [alu](../modules/alu.md).
**Commit/tag validado:** `isa-44-v1`.

| Instrução | Opcode | Funct3 | Funct7 | Unitário | Integrado | Regressão | Execuções¹ |
|---|---|---|---|---|---|---|---:|
| `JAL` | `1101111` | — | — | PASS | PASS | PASS | 4 |
| `JALR` | `1100111` | `000` | — | PASS | PASS | PASS | 4 |

**Evidências:** [tb_decoder](../../results/experiments/crc-official-20261027/logs/tb_decoder.log), [tb_pc](../../results/experiments/crc-official-20261027/logs/tb_pc.log), [tb_imm_ext](../../results/experiments/crc-official-20261027/logs/tb_imm_ext.log), [tb_isa](../../results/experiments/crc-official-20261027/logs/tb_isa.log), [tb_official_firmware](../../results/experiments/crc-official-20261027/logs/tb_official_firmware.log).

## Leitura de memória

**Módulos:** [lsu](../modules/lsu.md), [dmem](../modules/dmem.md).
**Commit/tag validado:** `isa-44-v1`.

| Instrução | Opcode | Funct3 | Funct7 | Unitário | Integrado | Regressão | Execuções¹ |
|---|---|---|---|---|---|---|---:|
| `LB` | `0000011` | `000` | — | PASS | PASS | PASS | 31 |
| `LH` | `0000011` | `001` | — | PASS | PASS | PASS | 21 |
| `LW` | `0000011` | `010` | — | PASS | PASS | PASS | 23 |
| `LBU` | `0000011` | `100` | — | PASS | PASS | PASS | 31 |
| `LHU` | `0000011` | `101` | — | PASS | PASS | PASS | 21 |

**Evidências:** [tb_decoder](../../results/experiments/crc-official-20261027/logs/tb_decoder.log), [tb_lsu](../../results/experiments/crc-official-20261027/logs/tb_lsu.log), [tb_dmem](../../results/experiments/crc-official-20261027/logs/tb_dmem.log), [tb_isa](../../results/experiments/crc-official-20261027/logs/tb_isa.log), [tb_official_firmware](../../results/experiments/crc-official-20261027/logs/tb_official_firmware.log).

## Escrita de memória

**Módulos:** [lsu](../modules/lsu.md), [dmem](../modules/dmem.md).
**Commit/tag validado:** `isa-44-v1`.

| Instrução | Opcode | Funct3 | Funct7 | Unitário | Integrado | Regressão | Execuções¹ |
|---|---|---|---|---|---|---|---:|
| `SB` | `0100011` | `000` | — | PASS | PASS | PASS | 6 |
| `SH` | `0100011` | `001` | — | PASS | PASS | PASS | 4 |
| `SW` | `0100011` | `010` | — | PASS | PASS | PASS | 35 |

**Evidências:** [tb_decoder](../../results/experiments/crc-official-20261027/logs/tb_decoder.log), [tb_lsu](../../results/experiments/crc-official-20261027/logs/tb_lsu.log), [tb_dmem](../../results/experiments/crc-official-20261027/logs/tb_dmem.log), [tb_isa](../../results/experiments/crc-official-20261027/logs/tb_isa.log), [tb_official_firmware](../../results/experiments/crc-official-20261027/logs/tb_official_firmware.log).

## Multiplicação — Zmmul

**Módulos:** [multiplier](../modules/multiplier.md).
**Commit/tag validado:** `isa-44-v1`.

| Instrução | Opcode | Funct3 | Funct7 | Unitário | Integrado | Regressão | Execuções¹ |
|---|---|---|---|---|---|---|---:|
| `MUL` | `0110011` | `000` | `0000001` | PASS | PASS | PASS | 74 |
| `MULH` | `0110011` | `001` | `0000001` | PASS | PASS | PASS | 74 |
| `MULHSU` | `0110011` | `010` | `0000001` | PASS | PASS | PASS | 74 |
| `MULHU` | `0110011` | `011` | `0000001` | PASS | PASS | PASS | 74 |

**Evidências:** [tb_decoder](../../results/experiments/crc-official-20261027/logs/tb_decoder.log), [tb_multiplier](../../results/experiments/crc-official-20261027/logs/tb_multiplier.log), [tb_isa](../../results/experiments/crc-official-20261027/logs/tb_isa.log), [tb_official_firmware](../../results/experiments/crc-official-20261027/logs/tb_official_firmware.log).

## CRC — Xicrc

**Módulos:** [crc](../modules/crc.md).
**Commit/tag validado:** `isa-44-v1`.

| Instrução | Opcode | Funct3 | Funct7 | Unitário | Integrado | Regressão | Execuções¹ |
|---|---|---|---|---|---|---|---:|
| `CRCB` | `0110011` | `000` | `1000000` | PASS | PASS | PASS | 74 |
| `CRCH` | `0110011` | `001` | `1000000` | PASS | PASS | PASS | 74 |
| `CRCW` | `0110011` | `010` | `1000000` | PASS | PASS | PASS | 74 |

**Evidências:** [tb_decoder](../../results/experiments/crc-official-20261027/logs/tb_decoder.log), [tb_crc](../../results/experiments/crc-official-20261027/logs/tb_crc.log), [tb_isa](../../results/experiments/crc-official-20261027/logs/tb_isa.log), [tb_official_firmware](../../results/experiments/crc-official-20261027/logs/tb_official_firmware.log).

## Sistema/Sincronização

**Módulos:** PENDENTE.
**Commit/tag validado:** PENDENTE.

| Instrução | Opcode | Funct3 | Funct7 | Unitário | Integrado | Regressão | Execuções¹ |
|---|---|---|---|---|---|---|---:|
| `PENDENTE_1` | — | — | — | PENDENTE | PENDENTE | PENDENTE | — |
| `PENDENTE_2` | — | — | — | PENDENTE | PENDENTE | PENDENTE | — |
| `PENDENTE_3` | — | — | — | PENDENTE | PENDENTE | PENDENTE | — |

**Pendência:** Definição oficial pendente. Ver [definições oficiais necessárias](../architecture/official_questions.md).

## Como interpretar

¹ Execuções são aposentadorias verificadas no teste próprio por instrução, incluindo instruções auxiliares que preparam operandos.
PASS representa os testes disponíveis, não prova formal nem certificação da competição.
A tag identifica o marco RTL; Manifesto preservado junto aos caminhos da matriz: [regression.json](../../results/experiments/crc-official-20261027/logs/regression.json). Confira a identificação da rodada antes de combinar logs de exercícios individuais.
Cada tag incremental conserva os logs da respectiva regressão. Esta tabela é atualizada automaticamente pela regressão.
Para apenas reformatar os resultados existentes: `python3 scripts/regression/coverage.py --render-only`.
