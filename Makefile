# Execute na raiz do projeto. Consulte os comandos com: make help
# Para estudar a receita sem executá-la: make -n run
# Execute um comando por vez: os testes compartilham build/ e results/logs/.
# Fluxo de simulação: receita -> run.py -> geradores -> Icarus/vvp -> logs.
# Fluxo de síntese: receita -> synth/simple.py -> Yosys -> teste da netlist.
# O percurso entre arquivos está explicado em docs/code_guide.md.

# Mantém make sem argumentos equivalente a make test, mesmo com help no início.
.DEFAULT_GOAL := test

# Usa o Python da .venv quando disponível. Aceita make run PYTHON=/caminho/python.
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

# .PHONY faz os comandos executarem mesmo se existir um arquivo com o nome do alvo.
.PHONY: help clean setup update doctor setup-openlane \
        tb unit integration smoke lint test regression system \
        firmware run wave simple-firmware simple-system simple-synth \
        official-fetch official-image official-run official-wave \
        openlane-env-check openlane-env-smoke openlane-shell \
        simple-openlane-synth simple-openlane-floorplan simple-openlane

# Ajuda gerada a partir das descrições após ##; $$ passa um $ literal ao awk.
help: ## Lista os comandos disponíveis e sua finalidade.
	@printf 'Uso: make <comando>\nExemplo de bancada: make tb TB=tb_branch_pc\n\n'
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Reinicia a prática arquivando saídas. Prévia: python3 scripts/setup/clean.py --dry-run
clean: ## Arquiva build, logs e ondas em results/archive/ para recomeçar.
	$(PYTHON) scripts/setup/clean.py

# 1. Preparar a máquina. Sem make instalado, use: bash scripts/setup/install.sh
setup: ## Instala dependências e prepara o ambiente Python (Ubuntu 24.04).
	bash scripts/setup/install.sh
update: ## Atualiza as dependências declaradas; não baixa código do Git.
	bash scripts/setup/update.sh
doctor: ## Confere ferramentas, versões e compilador RISC-V.
	$(PYTHON) scripts/setup/check.py


# 2. Testar os circuitos. O Python prepara entradas, chama Icarus/vvp e salva logs.
# TB é o nome do módulo de teste, sem caminho: make tb TB=tb_alu
# unit/integration selecionam suítes; test/regression também publicam a matriz ISA.
tb: ## Executa uma bancada: make tb TB=tb_alu
	$(if $(strip $(TB)),,$(error Informe a bancada: make tb TB=tb_alu))
	$(PYTHON) scripts/regression/run.py --test "$(TB)"

unit: ## Testa os 14 blocos isolados, incluindo Xicrc.
	$(PYTHON) scripts/regression/run.py --suite unit

integration: ## Executa as 19 bancadas de integração, incluindo sistema e firmware oficial.
	$(PYTHON) scripts/regression/run.py --suite integration

smoke: ## Executa quatro integrações rápidas para conferir o básico.
	$(PYTHON) scripts/regression/run.py --smoke

lint: ## Analisa o RTL com Verilator, sem executar simulação.
	$(PYTHON) scripts/regression/run.py --lint-only

test: ## Executa todos os 33 testbenches, sem lint; é o comando padrão.
	$(PYTHON) scripts/regression/run.py

regression: ## Executa todos os testes e lint; use para validar uma alteração.
	$(PYTHON) scripts/regression/run.py --with-lint

system: ## Verifica FENCE e os traps precisos de ECALL/EBREAK, sem síntese.
	$(PYTHON) scripts/regression/run.py --test tb_core_system


# 3. Executar o processador baseline com nosso firmware C/assembly.
# firmware: gera a ROM. run: gera a ROM, simula o core e verifica a assinatura.
# wave: também simula, gravando results/waveforms/smoke.vcd para abrir no GTKWave.
firmware: ## Compila o firmware próprio e gera build/smoke.hex.
	$(PYTHON) scripts/sim/build_firmware.py

run: ## Compila e executa o firmware próprio no processador simulado.
	$(PYTHON) scripts/regression/run.py --test tb_firmware

wave: ## Executa o firmware no RTL e grava a forma de onda VCD.
	$(PYTHON) scripts/regression/run.py --wave

# Imagem oficial: download explícito e verificado; os testes seguintes funcionam offline.
# A imagem exercita 44 tipos; make system verifica as três instruções restantes.
official-fetch: ## Obtém a revisão oficial fixada por SHA-256 e gera a imagem IMEM.
	$(PYTHON) scripts/sim/build_official.py --fetch

official-image: ## Converte a cópia oficial em cache, sem acessar a rede.
	$(PYTHON) scripts/sim/build_official.py

official-run: ## Executa o firmware oficial e verifica término real, CRC e 44 instruções.
	$(PYTHON) scripts/regression/run.py --test tb_official_firmware

official-wave: ## Executa o firmware oficial e grava results/waveforms/official.vcd.
	$(PYTHON) scripts/regression/run.py --test tb_official_firmware --with-wave


# 4. Sistema pequeno com Xicrc: ROM 2 KiB, RAM 1 KiB e saídas de resultado.
# A dependência de simple-synth faz simple-firmware rodar antes da síntese.
simple-firmware: ## Compila o programa experimental e gera build/simple.hex.
	$(PYTHON) scripts/sim/build_simple.py

simple-system: ## Executa e testa o sistema pequeno, incluindo CRC e reset/falhas.
	$(PYTHON) scripts/regression/run.py --test tb_simple_system

simple-synth: simple-firmware ## Faz síntese lógica Yosys e simula a netlist genérica.
	$(PYTHON) scripts/synth/simple.py


# 5. Ambiente físico em Docker: prepare Docker no host antes de setup-openlane.
# O smoke abaixo usa o exemplo do LibreLane. Os alvos da seção 6 usam nosso sistema.
# Ambos são comandos de execução; consultar help ou usar -n não inicia o fluxo.
setup-openlane: ## Baixa a imagem com LibreLane/PDK e verifica o ambiente.
	bash scripts/openlane/environment.sh install

openlane-env-check: ## Confere ferramentas físicas e SKY130A no contêiner.
	./scripts/openlane/environment.sh check

openlane-env-smoke: ## Executa o circuito de exemplo do LibreLane até GDSII.
	./scripts/openlane/environment.sh smoke

openlane-shell: ## Abre um terminal interativo no ambiente físico Docker.
	./scripts/openlane/environment.sh shell

# 6. Experimento físico com firmware próprio; execute no WSL, com Docker disponível.
# Cada alvo recria/testa a ROM e a netlist genérica antes de congelar as entradas.
simple-openlane-synth: simple-synth ## Mapeia o simple_system para células SKY130A.
	$(PYTHON) scripts/openlane/run_simple.py --stage synth

simple-openlane-floorplan: simple-synth ## Executa síntese e floorplan experimentais.
	$(PYTHON) scripts/openlane/run_simple.py --stage floorplan

simple-openlane: simple-synth ## Inicia o fluxo experimental completo até verificações/GDSII.
	$(PYTHON) scripts/openlane/run_simple.py --stage full
