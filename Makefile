.PHONY: test lint regression firmware smoke wave
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
