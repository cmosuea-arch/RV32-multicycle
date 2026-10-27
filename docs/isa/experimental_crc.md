# Matriz experimental CRC — contrato CMOS, 2026-10-13

**Histórico substituído em 27/10.** O contrato oficial foi implementado e as três
instruções agora pertencem ao perfil padrão de [47/47](coverage.md). Veja
[crc.md](../architecture/crc.md) e a
[rodada atual](../../results/experiments/isa-47-20261027/README.md).
O conteúdo abaixo descreve a implementação anterior, sem misturar as evidências.

Esta matriz complementa `coverage.csv`, sem declarar conformidade oficial.
Baseline: **41/47 (87,23%)**. Perfil experimental: 41 + 3 operações testadas.

**Revisão de 27/10:** o [firmware oficial](../architecture/crc_official_20261027.md)
demonstrou que operandos e ordem dos bytes do contrato CMOS precisam ser
corrigidos. Os PASS abaixo são históricos desse contrato e não do oficial.

| Instrução | Opcode / funct3 / funct7 | Módulo | Unitário | Core integrado | Regressão | Firmware próprio |
|---|---|---|---|---|---|---|
| CRCB | 0x33 / 0 / 0x40 | crc | PASS | PASS | PASS | PASS |
| CRCH | 0x33 / 1 / 0x40 | crc | PASS | PASS | PASS | PASS |
| CRCW | 0x33 / 2 / 0x40 | crc | PASS | PASS | PASS | PASS |

Contrato: [crc_provisional.md](../architecture/crc_provisional.md).
Commit do bloco: `05fd114`. Evidências de unidade/core:
[CRC](../../results/experiments/crc/README.md). Firmware e regressão posterior:
[simple_system](../../results/experiments/simple/README.md), identificados por SHA256.

Na versão histórica abaixo, `EXPERIMENTAL_XICRC=0` era o padrão e o firmware
oficial estava pendente. Hoje o padrão é 1, com contrato oficial e firmware PASS.

Atualização de 20/10/2026: a mensagem encaminhada identifica CRC-16-CCITT-FALSE
para as três operações, em acordo com o algoritmo atual com seed `0xFFFF`.
A [comparação registrada](../architecture/clarifications_20261020.md) distingue
essa confirmação da semântica ainda aberta de rs1/rs2 e da ordem dos bytes.
Os resultados acima continuam históricos do contrato CMOS; esta revisão não
executou nova regressão nem promoveu as três linhas à matriz oficial.
Recebimento dos detalhes e promoção do contrato seguem o
[formulário/checklist CRC](../architecture/crc_official_confirmation.md).
Esse registro foi preenchido com a fonte de 27/10. A adequação foi executada em
`isa-44-v1`; o fechamento posterior de sistema está em `isa-47-v1`.
