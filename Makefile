UV := $(shell which uv 2>/dev/null || ( [ -f /home/karimi/snap/code/247/.local/bin/uv ] && echo /home/karimi/snap/code/247/.local/bin/uv || echo uv ))

.PHONY: install run debug clean lint

install:
	$(UV) sync

run:
	$(UV) run python -m src

debug:
	$(UV) run python -m pdb -m src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

lint:
	$(UV) run flake8 .
	$(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs