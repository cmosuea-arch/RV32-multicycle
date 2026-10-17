#!/usr/bin/env bash
# Execute como usuário normal; sudo é usado somente para pacotes do sistema.
# -e interrompe erros; -u rejeita variáveis ausentes; pipefail observa falhas em pipelines.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)"
# As opções separam pacotes do sistema, visualizador e ambiente físico opcional.
system=1
gui=0
physical=0
for arg in "$@"; do
    case "$arg" in
        --skip-system) system=0 ;;
        --with-gui) gui=1 ;;
        --with-openlane) physical=1 ;;
        -h|--help)
            echo 'Uso: bash scripts/setup/install.sh [--skip-system] [--with-gui] [--with-openlane]'
            echo 'Instala dependências, cria .venv e verifica ferramentas. Não altera o RTL.'
            exit 0 ;;
        *) echo "Opção desconhecida: $arg" >&2; exit 2 ;;
    esac
done
if (( system )); then
    # Esta lista APT foi preparada para Ubuntu 24.04; não adapta outra distribuição.
    [[ -r /etc/os-release ]] || { echo 'Use Ubuntu 24.04 ou --skip-system com ferramentas instaladas.' >&2; exit 1; }
    . /etc/os-release
    [[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 ]] || {
        echo 'Instalação automática suportada: Ubuntu 24.04 (nativo ou WSL2).' >&2
        echo 'Em outros sistemas, instale os pacotes equivalentes e use --skip-system.' >&2
        exit 1
    }
    elevate=()
    if (( EUID != 0 )); then
        command -v sudo >/dev/null || { echo 'sudo necessário para instalar os pacotes.' >&2; exit 1; }
        elevate=(sudo)
    fi
    # Lê o manifesto ignorando comentários; instala só pacotes declarados/dependências.
    mapfile -t packages < <(sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d' "$root/scripts/setup/packages-ubuntu.txt")
    if (( gui )); then packages+=(gtkwave); fi
    "${elevate[@]}" apt-get update
    "${elevate[@]}" apt-get install -y --no-install-recommends "${packages[@]}"
elif (( gui )); then
    echo '--with-gui requer instalação dos pacotes; remova --skip-system.' >&2
    exit 2
fi
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else "Python >= 3.9 necessário")'
# Reexecutar venv também recupera uma criação interrompida antes da instalação do pip.
python3 -m venv "$root/.venv"
# pip cuida do Python; Icarus, GCC e outras ferramentas EDA vêm dos pacotes do sistema.
"$root/.venv/bin/python" -m pip install --disable-pip-version-check -r "$root/requirements.txt"
"$root/.venv/bin/python" "$root/scripts/setup/check.py"
# Baixar/verificar a imagem física é opcional e não executa o fluxo do processador.
if (( physical )); then bash "$root/scripts/openlane/environment.sh" install; fi
echo 'Preparação concluída. Execute make regression na raiz do repositório.'
