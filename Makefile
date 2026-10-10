# Estes alvos são ações: executam mesmo se existir um arquivo com o mesmo nome.
.PHONY: test unit integration tb lint regression firmware smoke wave openlane-env-check openlane-env-smoke openlane-shell
# Usa o ambiente local criado pelo instalador; aceita PYTHON=/caminho/do/python.
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
# Sem alvo explícito, make executa test; o fechamento com lint é regression.
test:
	$(PYTHON) scripts/regression/run.py
unit:
	$(PYTHON) scripts/regression/run.py --suite unit
integration:
	$(PYTHON) scripts/regression/run.py --suite integration
# Exemplo: make tb TB=tb_alu; $(TB) é substituído pelo nome passado no terminal.
tb:
	$(PYTHON) scripts/regression/run.py --test $(TB)
lint:
	$(PYTHON) scripts/regression/run.py --lint-only
# A regressão completa recompõe entradas, executa TBs e lint e registra evidências.
regression:
	$(PYTHON) scripts/regression/run.py --with-lint
smoke:
	$(PYTHON) scripts/regression/run.py --smoke
# Compila o software; wave também o executa no RTL e habilita a saída VCD.
firmware:
	$(PYTHON) scripts/sim/build_firmware.py
wave:
	$(PYTHON) scripts/regression/run.py --wave
# Infraestrutura física em Docker; o smoke usa o exemplo embutido do LibreLane.
openlane-env-check:
	./scripts/openlane/environment.sh check
openlane-env-smoke:
	./scripts/openlane/environment.sh smoke
openlane-shell:
	./scripts/openlane/environment.sh shell

# Bootstrap: usar bash scripts/setup/install.sh se make ainda não estiver instalado.
.PHONY: setup update doctor setup-openlane
setup:
	bash scripts/setup/install.sh
update:
	bash scripts/setup/update.sh
doctor:
	$(PYTHON) scripts/setup/check.py
setup-openlane:
	bash scripts/openlane/environment.sh install
