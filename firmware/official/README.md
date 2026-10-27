# Firmware oficial — execução RTL PASS em 27/10/2026

Recebido para análise em **27/10/2026** pelo link fornecido pelo usuário:
[CCX_Brasil_Edition_Firmware_Stage_2](https://github.com/championchip-experience-community/CCX_Brasil_Edition_Firmware_Stage_2).
Revisão consultada: `edc7d5990d2185942081ee8a6899aa603cc91569`.

- [source.json](source.json) registra URLs fixas, SHA-256 e características da imagem.
- [receipt.md](receipt.md) registra formato, entrada e protocolo de término conhecidos.
- [Análise do CRC](../../docs/architecture/crc_official_20261027.md) registra as
  diferenças que precisam ser corrigidas no projeto antes da validação.

O repositório upstream contém `firmware.s`, `firmware.txt` e o README de integração.
O README recomenda usar a imagem completa de `firmware.txt` na validação funcional;
para teste físico rápido, apresenta um mock pequeno, sem exigir embutir o programa
completo na síntese. Os arquivos originais permanecem identificados pelas URLs e
hashes; não foram incorporados integralmente a este diretório.

A imagem inicia em `0x00400000` e contém 259 palavras consecutivas, incluindo
cinco constantes usadas por loads. É necessário converter os pares endereço/palavra
para o formato de carga da nossa IMEM, preservando esses valores.

No término, o programa escreve x4=0 (sucesso) ou x4=FFFFFFFF (falha) e entra em
loop. O zero inicial de x4 após reset não é sucesso: o TB deve observar a escrita
de término/loop final. Isso substitui a hipótese anterior de reutilizar uma
assinatura na DMEM; a assinatura CMOS continua exclusiva dos programas próprios.

O CRC foi adequado, a imagem foi integrada e o teste completo passou:

```text
PASS official_firmware: x4=00000000, 252 retirements, 1026 cycles,
CRC=16, ISA=44, terminal loop verified
```

[Logs, VCD e figura real](../../results/experiments/crc-official-20261027/README.md).
A imagem publicada exercita 44 tipos. O perfil integrado atingiu 47/47 com
[testes próprios de sistema](../../docs/architecture/system.md), sem modificar
a imagem oficial. [Rodada atual](../../results/experiments/isa-47-20261027/README.md).
Esse PASS não constitui síntese ou signoff físico.

```bash
make official-fetch  # primeira preparação: download explícito com revisão/SHA
make official-run
make official-wave
```

O cache original é ignorado pelo Git e sobrevive a make clean. O converter
`build_official.py` também aceita `--source firmware.txt`; sem --fetch não acessa
a rede. A regressão inclui o teste oficial e verifica 44 tipos em execução,
16 CRCs, a escrita de término e três commits no loop. O CRC anterior foi usado
como teste negativo e o firmware detectou a falha. Síntese reservada ao usuário.
