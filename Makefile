UV := uv

.PHONY: install run debug clean lint lint-strict

install:
	export UV_CACHE_DIR=/goinfre/mokarimi/.uv-cache && $(UV) sync

run:
	$(UV) run python -m src

debug:
	$(UV) run python -m pdb -m src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache

lint:
	$(UV) run flake8 .
	$(UV) run mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(UV) run flake8 .
	$(UV) run mypy . --strict