# Execute na raiz do projeto. Consulte os comandos com: make help
# Para estudar a receita sem executá-la: make -n run
# Execute um comando por vez: os testes compartilham build/ e results/logs/.

# Mantém make sem argumentos equivalente a make test, mesmo com help no início.
.DEFAULT_GOAL := test

# Usa o Python da .venv quando disponível. Aceita make run PYTHON=/caminho/python.
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

# .PHONY faz os comandos executarem mesmo se existir um arquivo com o nome do alvo.
.PHONY: help setup update doctor setup-openlane \
        tb unit integration smoke lint test regression \
        firmware run wave simple-firmware simple-system simple-synth \
        openlane-env-check openlane-env-smoke openlane-shell

# Ajuda gerada a partir das descrições após ##; $$ passa um $ literal ao awk.
help: ## Lista os comandos disponíveis e sua finalidade.
	@printf 'Uso: make <comando>\nExemplo de bancada: make tb TB=tb_branch_pc\n\n'
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# 1. Preparar a máquina. Sem make instalado, use: bash scripts/setup/install.sh
setup: ## Instala dependências e prepara o ambiente Python (Ubuntu 24.04).
	bash scripts/setup/install.sh
update: ## Atualiza as dependências declaradas; não baixa código do Git.
	bash scripts/setup/update.sh
doctor: ## Confere ferramentas, versões e compilador RISC-V.
	$(PYTHON) scripts/setup/check.py

# 2. Testar os circuitos. O Python prepara entradas, chama Icarus/vvp e salva logs.
# TB é o nome do módulo de teste, sem caminho: make tb TB=tb_alu
tb: ## Executa uma bancada: make tb TB=tb_alu
	$(if $(strip $(TB)),,$(error Informe a bancada: make tb TB=tb_alu))
	$(PYTHON) scripts/regression/run.py --test "$(TB)"
unit: ## Testa os 14 blocos isolados, incluindo o CRC provisório.
	$(PYTHON) scripts/regression/run.py --suite unit
integration: ## Executa as 17 bancadas de integração, incluindo os firmwares.
	$(PYTHON) scripts/regression/run.py --suite integration
smoke: ## Executa quatro integrações rápidas para conferir o básico.
	$(PYTHON) scripts/regression/run.py --smoke
lint: ## Analisa o RTL com Verilator, sem executar simulação.
	$(PYTHON) scripts/regression/run.py --lint-only
test: ## Executa todos os 31 testbenches, sem lint; é o comando padrão.
	$(PYTHON) scripts/regression/run.py
regression: ## Executa todos os testes e lint; use para validar uma alteração.
	$(PYTHON) scripts/regression/run.py --with-lint

# 3. Executar o processador baseline com nosso firmware C/assembly.
# firmware: gera a ROM. run: gera a ROM, simula o core e verifica a assinatura.
# wave: também simula, gravando results/waveforms/smoke.vcd para abrir no GTKWave.
firmware: ## Compila o firmware próprio e gera build/smoke.hex.
	$(PYTHON) scripts/sim/build_firmware.py
run: ## Compila e executa o firmware próprio no processador simulado.
	$(PYTHON) scripts/regression/run.py --test tb_firmware
wave: ## Executa o firmware no RTL e grava a forma de onda VCD.
	$(PYTHON) scripts/regression/run.py --wave

# 4. Sistema pequeno com CRC provisório: ROM 2 KiB, RAM 1 KiB e saídas de resultado.
# A dependência de simple-synth faz simple-firmware rodar antes da síntese.
simple-firmware: ## Compila o programa experimental e gera build/simple.hex.
	$(PYTHON) scripts/sim/build_simple.py
simple-system: ## Executa e testa o sistema pequeno, incluindo CRC e reset/falhas.
	$(PYTHON) scripts/regression/run.py --test tb_simple_system
simple-synth: simple-firmware ## Faz síntese lógica Yosys e simula a netlist genérica.
	$(PYTHON) scripts/synth/simple.py

# 5. Ambiente físico em Docker: prepare Docker no host antes de setup-openlane.
# O smoke abaixo usa o exemplo do LibreLane. O fluxo físico do processador é futuro.
setup-openlane: ## Baixa a imagem com LibreLane/PDK e verifica o ambiente.
	bash scripts/openlane/environment.sh install
openlane-env-check: ## Confere ferramentas físicas e SKY130A no contêiner.
	./scripts/openlane/environment.sh check
openlane-env-smoke: ## Executa o circuito de exemplo do LibreLane até GDSII.
	./scripts/openlane/environment.sh smoke
openlane-shell: ## Abre um terminal interativo no ambiente físico Docker.
	./scripts/openlane/environment.sh shell
