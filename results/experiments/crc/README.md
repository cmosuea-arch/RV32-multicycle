# CRC provisório — validação em 2026-10-13

Executados em cópia isolada para preservar os logs locais do usuário:

```bash
python3 scripts/regression/run.py --test tb_crc
python3 scripts/regression/run.py --test tb_decoder
python3 scripts/regression/run.py --test tb_core_crc
make regression
```

Resultado: **30 testbenches PASS + lint PASS**, incluindo os 28 da baseline.
CRC isolado: 18304 vetores e check `123456789 -> 29b1`.
Programa CRC: 32147 aposentadorias, das quais 2127 são CRCB/CRCH/CRCW.
Decoder: 131072 combinações em cada configuração (CRC desabilitado/habilitado).

Os logs selecionados e `regression.json` são cópias da execução isolada; caminhos
absolutos `/tmp/cmos-crc-*` identificam o diretório usado naquela execução.
Hashes identificam o código testado. A cobertura oficial permanece 41/47.
Não há alegação de firmware oficial, síntese ou validação física nesta etapa.
