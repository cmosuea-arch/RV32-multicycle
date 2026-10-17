#!/usr/bin/env bash
set -euo pipefail

# Monta somente este clone; não depende de scripts ou diretórios do repositório pai.
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
project_dir="$(cd -- "$script_dir/../.." && pwd -P)"
image="${UNICCASS_DOCKER_IMAGE:-isaiassh/unic-cass-tools:1.1.0}"
action="${1:-check}"
case "$action" in
    install|check|smoke|shell) ;;
    -h|--help) echo "Uso: $0 {install|check|smoke|shell}"; exit 0 ;;
    *) echo "Uso: $0 {install|check|smoke|shell}" >&2; exit 2 ;;
esac
if [[ "$(uname -m)" != x86_64 ]]; then
    echo 'A imagem padrão foi validada somente em Linux x86_64 (nativo ou WSL2).' >&2
    exit 1
fi

command -v docker >/dev/null 2>&1 || {
    echo "ERRO: Docker não encontrado. Veja docs/setup.md (Docker Engine ou Desktop/WSL2)." >&2
    exit 1
}
docker info >/dev/null 2>&1 || {
    echo "ERRO: daemon Docker inacessível. Confira docker info e docs/setup.md." >&2
    exit 1
}

# Somente install acessa o registry; outros modos exigem a imagem já disponível.
if [[ "$action" == install ]]; then
    docker pull "$image"
    action=check
elif ! docker image inspect "$image" >/dev/null 2>&1; then
    echo 'Imagem ausente. Execute make setup-openlane para baixá-la.' >&2
    exit 1
fi

# A montagem preserva arquivos do projeto; --rm remove o contêiner após a execução.
common_args=(
    --rm
    --pull never
    --entrypoint /bin/bash
    --user "$(id -u):$(id -g)"
    # O home das ferramentas na imagem é 0750, grupo designer (1000).
    --group-add 1000
    --env HOME=/home/designer
    --env XDG_CACHE_HOME=/tmp/cmos-cache
    --mount "type=bind,source=$project_dir,target=/home/designer/shared/cmos-riscv"
    --workdir /home/designer/shared/cmos-riscv
    --env PDK=sky130A
    --env PDK_ROOT=/opt/pdks
)

# check verifica ferramentas; smoke executa um exemplo; shell abre sessão interativa.
case "$action" in
    check)
        exec docker run "${common_args[@]}" "$image" \
            -lc 'bash scripts/openlane/check.sh'
        ;;
    smoke)
        # O exemplo roda em /tmp do contêiner; não é o layout do processador CMOS.
        exec docker run "${common_args[@]}" "$image" \
            -lc 'cd /tmp && bash /home/designer/shared/cmos-riscv/scripts/openlane/librelane.sh --smoke-test'
        ;;
    shell)
        exec docker run -it "${common_args[@]}" "$image"
        ;;
    *)
        echo "Uso: $0 {check|smoke|shell}" >&2
        exit 2
        ;;
esac
