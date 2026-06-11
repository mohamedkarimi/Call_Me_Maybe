"""utilities for writing output json files"""

import json
from pathlib import Path

from src.models import FunctionCallResult

def serialize_results(
    results: list[FunctionCallResult],
) -> list[dict[str, object]]:
    """convert result models into json serializable dictionaries"""
    
    serialized: list[dict[str, object]] = []
    
    for result in results:
        serialized.append(result.model_dump())
        """model_dump kat7wlna object l dictionary"""
    
    return serialized

def ensure_directory(path: Path) -> None:
    """create a directory if it does not exist"""
    path.mkdir(parents=True, exist_ok=True)
    
def write_results(
    output_path: str | Path,
    results: list[FunctionCallResult],
) -> Path:
    """ write generated results to a json file"""
    
    path = Path(output_path)
    ensure_directory(path.parent)
    
    payload = serialize_results(results)
    
    with path.open("w", encoding="utf-8") as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )
    
    return path
