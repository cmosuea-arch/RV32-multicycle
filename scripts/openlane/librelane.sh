#!/usr/bin/env bash
set -euo pipefail
# Executar dentro da imagem UNIC-CASS, usando o PDK que ela já contém.
# Repassa as opções recebidas ao LibreLane; exec preserva seu código de saída.
exec librelane --manual-pdk --pdk-root "${PDK_ROOT:-/opt/pdks}" --pdk "${PDK:-sky130A}" "$@"
