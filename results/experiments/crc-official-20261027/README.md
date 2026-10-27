# CRC e firmware oficial — 27/10/2026

Execução em cópia isolada do projeto; os logs da prática no workspace foram
preservados. Revisão upstream: `edc7d5990d2185942081ee8a6899aa603cc91569`.
[Origem e SHA-256](../../../firmware/official/source.json).

| Verificação | Resultado |
|---|---|
| Regressão RTL | 32/32 TBs PASS: 14 unitários e 18 integrações |
| Lint | riscv_top e simple_system PASS |
| ISA integrada | 88.727 aposentadorias, 45 stores e 12 bytes finais |
| CRC isolado | 18.304 vetores e respostas conhecidas 29B1/1E82 |
| Core CRC | 32.930 aposentadorias, 2.146 CRCs, aliases/x0/memória/reset |
| Firmware próprio baseline | 598 aposentadorias, 2.579 ciclos, assinatura 600dc0de |
| Firmware oficial | 252 aposentadorias, 1.026 ciclos, 16 CRCs, 44 tipos de instrução |
| Término oficial | Escrita de x4=0 em 10145 ns; três commits no loop final |
| Teste negativo | CRC anterior resulta em falha oficial x4=FFFFFFFF, PC 004003F0 |
| Síntese / implementação física | Não executadas; reservadas ao usuário |

[regression.json](logs/regression.json) identifica fontes por SHA-256.
[official_firmware.json](logs/official_firmware.json) identifica origem, ROM e RTL
da execução oficial. A captura com onda usa os mesmos arquivos e resultado;
[waveform.json](waveform.json) reconcilia log/VCD, ciclos, commits e término.
O [log negativo](logs/negative_old_crc.log) é uma falha esperada de uma versão
deliberadamente anterior do CRC, não uma regressão falha da versão corrigida.

O VCD está comprimido em [official.vcd.gz](official.vcd.gz). Figura real:
[SVG](official-success.svg) / [PNG](official-success.png). O SHA do conteúdo
descomprimido está em capture.json e waveform.json.

Comandos de reprodução no WSL:

```bash
make official-fetch  # uma vez, download fixado por revisão e SHA-256
make regression     # gera entradas e executa todos os TBs/lint, sem síntese
make official-wave  # gera uma nova captura local em results/waveforms/official.vcd
```

O cache original fica em external/championchip-firmware e é ignorado pelo Git.
O converter também aceita `--source firmware.txt` para uma cópia local com o mesmo
SHA-256. A imagem completa e suas constantes são preservadas sem remontagem.

Exportação da captura arquivada, com as dependências editoriais do relatório:

```bash
python scripts/report/official_waveforms.py \
  --vcd results/experiments/crc-official-20261027/official.vcd.gz \
  --log results/experiments/crc-official-20261027/logs/tb_official_firmware.wave.log \
  --output results/experiments/crc-official-20261027
```

A cobertura é 44/47, não 47/47. O firmware recebido não enumera as três instruções
de sistema/sincronização da tabela do guia; a interface final e o fluxo físico
também permanecem pendentes. A simulação usa clock de 10 ns, sem demonstrar
frequência máxima física ou viabilidade de área/timing em SKY130A.
