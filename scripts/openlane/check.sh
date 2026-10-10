#!/usr/bin/env bash
set -euo pipefail
failed=0
for tool in librelane openroad yosys magic netgen klayout; do
    if command -v "$tool"; then :; else
        echo "FALTA: $tool" >&2
        failed=1
    fi
done
pdk_dir="${PDK_ROOT:-/opt/pdks}/${PDK:-sky130A}"
for file in libs.tech/openlane/config.tcl libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib; do
    if [[ ! -r "$pdk_dir/$file" ]]; then
        echo "FALTA: $pdk_dir/$file" >&2
        failed=1
    fi
done
(( failed == 0 )) || exit 1
librelane --version
echo 'AMBIENTE COMPLETO: LibreLane e SKY130A. Execute o smoke para validar o fluxo.'
