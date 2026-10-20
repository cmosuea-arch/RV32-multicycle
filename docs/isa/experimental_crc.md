# Matriz experimental CRC — contrato CMOS, 2026-10-13

Esta matriz complementa `coverage.csv`, sem declarar conformidade oficial.
Baseline: **41/47 (87,23%)**. Perfil experimental: 41 + 3 operações testadas.

| Instrução | Opcode / funct3 / funct7 | Módulo | Unitário | Core integrado | Regressão | Firmware próprio |
|---|---|---|---|---|---|---|
| CRCB | 0x33 / 0 / 0x40 | crc | PASS | PASS | PASS | PASS |
| CRCH | 0x33 / 1 / 0x40 | crc | PASS | PASS | PASS | PASS |
| CRCW | 0x33 / 2 / 0x40 | crc | PASS | PASS | PASS | PASS |

Contrato: [crc_provisional.md](../architecture/crc_provisional.md).
Commit do bloco: `05fd114`. Evidências de unidade/core:
[CRC](../../results/experiments/crc/README.md). Firmware e regressão posterior:
[simple_system](../../results/experiments/simple/README.md), identificados por SHA256.

`EXPERIMENTAL_XICRC=0` é o padrão em decoder/core/riscv_top; simple_system usa 1.
Firmware oficial e homologação das três instruções: **PENDENTES**.

Atualização de 20/10/2026: a mensagem encaminhada identifica CRC-16-CCITT-FALSE
para as três operações, em acordo com o algoritmo atual com seed `0xFFFF`.
A [comparação registrada](../architecture/clarifications_20261020.md) distingue
essa confirmação da semântica ainda aberta de rs1/rs2 e da ordem dos bytes.
Os resultados acima continuam históricos do contrato CMOS; esta revisão não
executou nova regressão nem promoveu as três linhas à matriz oficial.
Recebimento dos detalhes e promoção do contrato seguem o
[formulário/checklist CRC](../architecture/crc_official_confirmation.md).
