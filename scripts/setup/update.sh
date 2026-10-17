#!/usr/bin/env bash
# Atualiza os pacotes declarados; --pull também atualiza o checkout por fast-forward.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)"
pull=0
args=()
for arg in "$@"; do
    case "$arg" in
        --pull) pull=1 ;;
        --skip-system|--with-gui|--with-openlane) args+=("$arg") ;;
        -h|--help)
            echo 'Uso: bash scripts/setup/update.sh [--pull] [--skip-system] [--with-gui] [--with-openlane]'
            echo '--pull exige checkout limpo e upstream configurado; nunca força ou apaga alterações.'
            exit 0 ;;
        *) echo "Opção desconhecida: $arg" >&2; exit 2 ;;
    esac
done
if (( pull )); then
    # Só atualiza código com árvore limpa e upstream; --ff-only recusa divergências.
    [[ -z "$(git -C "$root" status --porcelain)" ]] || {
        echo 'Checkout com alterações. Revise e registre seu trabalho antes de usar --pull.' >&2; exit 1;
    }
    git -C "$root" rev-parse --abbrev-ref '@{upstream}' >/dev/null || {
        echo 'Configure o upstream da branch antes de usar --pull.' >&2; exit 1;
    }
    git -C "$root" pull --ff-only
fi
# Reinstalação idempotente: apt atualiza somente os pacotes solicitados/dependências.
exec bash "$root/scripts/setup/install.sh" "${args[@]}"
