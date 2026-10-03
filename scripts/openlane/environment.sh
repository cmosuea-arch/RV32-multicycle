#!/usr/bin/env bash
set -euo pipefail

# Localiza o workspace compartilhado e a imagem usada nesta instalação UNIC-CASS.
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
project_dir="$(cd -- "$script_dir/../.." && pwd -P)"
shared_dir="$(cd -- "$project_dir/.." && pwd -P)"
image="${UNICCASS_DOCKER_IMAGE:-isaiassh/unic-cass-tools:1.1.0}"
action="${1:-check}"

command -v docker >/dev/null 2>&1 || {
    echo "ERRO: Docker não encontrado." >&2
    exit 1
}
docker info >/dev/null 2>&1 || {
    echo "ERRO: daemon Docker inacessível. Inicie o Docker Desktop e habilite a integração WSL." >&2
    exit 1
}

# A montagem preserva arquivos do projeto; --rm remove o contêiner após a execução.
common_args=(
    --rm
    --entrypoint /bin/bash
    --mount "type=bind,source=$shared_dir,target=/home/designer/shared"
    --workdir /home/designer/shared/cmos-riscv
    --env PDK=sky130A
    --env PDK_ROOT=/opt/pdks
)

# check verifica ferramentas; smoke executa um exemplo; shell abre sessão interativa.
case "$action" in
    check)
        exec docker run "${common_args[@]}" "$image" \
            -lc '/home/designer/shared/bin/verificar-ambiente-unicass'
        ;;
    smoke)
        exec docker run "${common_args[@]}" "$image" \
            -lc 'cd /tmp && /home/designer/shared/bin/librelane-local --smoke-test'
        ;;
    shell)
        exec docker run -it "${common_args[@]}" "$image"
        ;;
    *)
        echo "Uso: $0 {check|smoke|shell}" >&2
        exit 2
        ;;
esac
