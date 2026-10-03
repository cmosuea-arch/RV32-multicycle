# Estes alvos são ações: executam mesmo se existir um arquivo com o mesmo nome.
.PHONY: test unit integration tb lint regression firmware smoke wave openlane-env-check openlane-env-smoke openlane-shell
# Sem alvo explícito, make executa test; o fechamento com lint é regression.
test:
	python3 scripts/regression/run.py
unit:
	python3 scripts/regression/run.py --suite unit
integration:
	python3 scripts/regression/run.py --suite integration
# Exemplo: make tb TB=tb_alu; $(TB) é substituído pelo nome passado no terminal.
tb:
	python3 scripts/regression/run.py --test $(TB)
lint:
	python3 scripts/regression/run.py --lint-only
# A regressão completa recompõe entradas, executa TBs e lint e registra evidências.
regression:
	python3 scripts/regression/run.py --with-lint
smoke:
	python3 scripts/regression/run.py --smoke
# Compila o software; wave também o executa no RTL e habilita a saída VCD.
firmware:
	python3 scripts/sim/build_firmware.py
wave:
	python3 scripts/regression/run.py --wave
# Infraestrutura física em Docker; o smoke usa o exemplo embutido do LibreLane.
openlane-env-check:
	./scripts/openlane/environment.sh check
openlane-env-smoke:
	./scripts/openlane/environment.sh smoke
openlane-shell:
	./scripts/openlane/environment.sh shell
