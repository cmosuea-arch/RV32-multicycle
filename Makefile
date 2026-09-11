.PHONY: test lint regression firmware smoke
test:
	python3 scripts/regression/run.py
lint:
	python3 scripts/regression/run.py --lint-only
regression: test lint
smoke: test
