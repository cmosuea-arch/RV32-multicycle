#!/usr/bin/env bash
set -euo pipefail
# Executar dentro da imagem UNIC-CASS, usando o PDK que ela já contém.
exec librelane --manual-pdk --pdk-root "${PDK_ROOT:-/opt/pdks}" --pdk "${PDK:-sky130A}" "$@"
