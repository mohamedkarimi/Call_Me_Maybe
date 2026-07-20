"""Load and validate project input files"""

import json
from pathlib import Path
from typing import Any, cast
from pydantic import TypeAdapter, ValidationError
from src.models import FunctionDefinition, InputData, PromptItem


def read_json_file(path: str | Path) -> Any:
    """Read a json file and return its decoded content"""

    file_path = Path(path)

    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)  # hna kandowzo had l file l json.load
            # hiya kat9ra l file o kat7wal json l python data
    except FileNotFoundError as exc:
        raise ValueError(f"input file not found: {file_path}") from exc
    except json.JSONDecodeError as exc:
        message = (
            f"invalid json in {file_path}: {exc.msg}"
            f" at line {exc.lineno}, column {exc.colno}"
        )
        raise ValueError(message) from exc
    except OSError as exc:
        raise ValueError(f"cannot read file {file_path}: {exc}") from exc


def load_prompts(path: str | Path) -> list[PromptItem]:
    """load and validate prompt items from a json file"""
    raw_data = read_json_file(path)

    try:
        adapter = TypeAdapter(list[PromptItem])
        return cast(list[PromptItem], adapter.validate_python(raw_data))
    except ValidationError as exc:
        raise ValueError(f"invalid prompts file schema : {exc}") from exc


def load_functions(path: str | Path) -> list[FunctionDefinition]:
    """load and validate function definition from a json file"""

    raw_data = read_json_file(path)

    try:
        adapter = TypeAdapter(list[FunctionDefinition])
        return cast(
            list[FunctionDefinition],
            adapter.validate_python(raw_data),
        )
    except ValidationError as exc:
        raise ValueError(f"invalid functions file schema : {exc}") from exc


def load_input_data(
    prompts_path: str | Path,
    functions_path: str | Path,
) -> InputData:
    """load all project input data"""

    prompts = load_prompts(prompts_path)
    functions = load_functions(functions_path)

    return InputData(prompts=prompts, functions=functions)
