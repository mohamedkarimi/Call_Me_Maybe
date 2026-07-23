UV := uv

.PHONY: install run debug clean lint lint-strict

install:
	$(UV) sync

run:
	time $(UV) run python -m src

debug:
	$(UV) run python -m pdb -m src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache

lint:
	$(UV) run flake8 src
	$(UV) run mypy src \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--follow-imports=skip \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(UV) run flake8 src
	$(UV) run mypy src \
		--strict \
		--follow-imports=skip