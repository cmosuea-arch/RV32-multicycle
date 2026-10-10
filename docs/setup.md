# Instalação e atualização em outra máquina

## Plataforma suportada

O instalador de pacotes suporta **Ubuntu 24.04**, nativo ou dentro do WSL2.
O fluxo físico com a imagem UNIC-CASS é validado em **x86_64**. Em Windows,
execute os scripts no terminal Ubuntu/WSL2, com o clone no filesystem Linux.
macOS e outras distribuições não têm instalador de pacotes automatizado aqui;
podem usar `--skip-system` após instalar ferramentas equivalentes.

É necessário ter Git para clonar, acesso à rede para baixar pacotes e permissão
sudo para instalar dependências do sistema. Execute o instalador como seu usuário
normal; ele chama sudo somente para o APT. Não copie `.venv/` de outra máquina.

## Primeiro clone

```bash
git clone https://github.com/cmosuea-arch/RV32-multicycle.git
cd RV32-multicycle
bash scripts/setup/install.sh
make doctor
make regression
```

O instalador pode ser executado novamente. Ele instala/atualiza os pacotes
declarados, cria `.venv`, aplica `requirements.txt` e verifica executáveis e o
suporte real do GCC a RV32I_Zmmul/ILP32. A regressão é o teste funcional final.

O Makefile usa `.venv/bin/python` quando disponível, sem exigir ativação manual.
Para executar scripts Python diretamente nesse mesmo ambiente, use:

```bash
source .venv/bin/activate
python scripts/sim/vectors.py
```

## Dependências por camada

| Dependência | Instalação / finalidade |
|---|---|
| Python 3.9+ | geradores, executor e relatórios |
| `requirements.txt` | sem pacotes externos atualmente; XLSX usa zipfile/XML da biblioteca padrão |
| `python3-venv`, `python3-pip` | ambiente Python isolado |
| Icarus (`iverilog`, `vvp`) | compilação e simulação SystemVerilog |
| Verilator | lint do RTL |
| Make e Git | receitas e versionamento |
| GCC/binutils `riscv64-unknown-elf-*` | compilação, conversão e inspeção do firmware RV32 |
| GTKWave, opcional | visualização de VCD |
| Docker + imagem UNIC-CASS, opcionais | LibreLane, ferramentas físicas e SKY130A |

A lista de pacotes APT é [packages-ubuntu.txt](../scripts/setup/packages-ubuntu.txt).
O firmware atual usa `-nostdlib` e fornece seu startup: não requer picolibc.
`pip install -r requirements.txt` sozinho não instala as ferramentas EDA do sistema.

Para incluir GTKWave:

```bash
bash scripts/setup/install.sh --with-gui
```

O visualizador precisa de uma sessão gráfica (WSLg no Windows). Para um ambiente
que já tem as ferramentas:

```bash
bash scripts/setup/install.sh --skip-system
```

## Ambiente OpenLane/LibreLane

Prepare Docker primeiro:

- No WSL2, instale/abra Docker Desktop no Windows e habilite a distribuição em
  Settings → Resources → WSL Integration, conforme a
  [documentação oficial](https://docs.docker.com/desktop/features/wsl/).
- No Ubuntu nativo, siga a
  [instalação do Docker Engine](https://docs.docker.com/engine/install/ubuntu/)
  e configure acesso ao daemon para o usuário que executa o projeto.

`docker info` precisa funcionar no mesmo terminal. O instalador deste projeto não
altera permissões do socket, grupos ou serviços Docker. Depois:

```bash
make setup-openlane
make openlane-env-check
make openlane-env-smoke
```

Ou inclua o download da imagem na instalação base:

```bash
bash scripts/setup/install.sh --with-openlane
```

A imagem `isaiassh/unic-cass-tools:1.1.0` inclui ferramentas e PDK. Reserve dezenas
de GB; a imagem local original ocupa aproximadamente 34 GB descompactada. `install`
faz `docker pull` e verifica o ambiente; o smoke valida o fluxo completo e é uma
etapa explícita. Não é necessário clonar o repositório pai UNIC-CASS.

O wrapper monta este clone em `/home/designer/shared/cmos-riscv`, independente de
seu nome no host. Usa o UID/GID do usuário para as gravações no projeto.
Adiciona o grupo 1000 dentro do contêiner para permitir a leitura do ambiente
`designer` da imagem, sem alterar permissões dos arquivos no host.
Dentro de `make openlane-shell`, use:

```bash
bash scripts/openlane/librelane.sh --version
bash scripts/openlane/librelane.sh --help
```

## Atualizar

Atualizar dependências declaradas (sem puxar código):

```bash
make update
# Equivalente:
bash scripts/setup/update.sh
```

Atualizar o código e depois as dependências:

```bash
bash scripts/setup/update.sh --pull
make regression
```

`--pull` exige árvore limpa e upstream e usa `git pull --ff-only`. Alterações
locais e divergências são informadas; o script não faz reset, stash ou merge
automático. Logs versionados alterados por testes também contam como alterações:
revise-os antes de atualizar. A opção `--skip-system` evita APT;
`--with-openlane` também puxa novamente a tag configurada da imagem.

O APT atualiza somente os pacotes solicitados e suas dependências; não executamos
um upgrade geral da distribuição. A tag Docker é fixa, mas tags podem ser
republicadas: para reprodução imutável pode-se fornecer uma referência por digest
em `UNICCASS_DOCKER_IMAGE`. Uma troca de ferramentas exige nova regressão.

## Diagnóstico

```bash
make doctor
```

O diagnóstico lista versões e caminhos efetivamente usados e retorna erro se
faltar uma ferramenta ou se o GCC não aceitar o alvo. Ferramentas antigas no PATH
podem ter prioridade sobre as instaladas pelo APT. O diagnóstico não substitui
`make regression` nem `make openlane-env-smoke`.

| Erro | Ação |
|---|---|
| pacote APT não encontrado | confira rede, Ubuntu 24.04 e repositório Universe habilitado |
| erro em `python3 -m venv` | instale `python3-venv`; confira a versão do Python |
| comando ausente / opção Zmmul rejeitada | execute o instalador e confira os caminhos de `make doctor` |
| Docker inacessível | confira serviço/integração WSL e acesso do usuário com `docker info` |
| imagem ausente | execute `make setup-openlane` |
| regressão falhou | leia `results/logs/`; confira versão, diagnóstico e primeiro teste com erro |

O objetivo é detectar dependências faltantes antes dos testes. A instalação não
garante ausência de erros de rede, incompatibilidades futuras ou falhas funcionais
no RTL. A lista de requisitos e os testes dão um caminho reproduzível de diagnóstico.

Referências de pacotes: [GCC RISC-V](https://packages.ubuntu.com/noble/gcc-riscv64-unknown-elf),
[Icarus](https://packages.ubuntu.com/noble/iverilog),
[Verilator](https://packages.ubuntu.com/noble/verilator).

Evidências da instalação limpa e da regressão: [validação](../results/setup/validation.md).
