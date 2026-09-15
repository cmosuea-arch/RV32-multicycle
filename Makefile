.PHONY: test lint regression firmware smoke wave openlane-env-check openlane-env-smoke openlane-shell
test:
	python3 scripts/regression/run.py
lint:
	python3 scripts/regression/run.py --lint-only
regression:
	python3 scripts/regression/run.py --with-lint
smoke:
	python3 scripts/regression/run.py --smoke
firmware:
	python3 scripts/sim/build_firmware.py
wave:
	python3 scripts/regression/run.py --wave
openlane-env-check:
	./scripts/openlane/environment.sh check
openlane-env-smoke:
	./scripts/openlane/environment.sh smoke
openlane-shell:
	./scripts/openlane/environment.sh shell
