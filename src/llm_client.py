"""small wrapper function around the provided llm sdk."""

from pathlib import Path
from typing import Any, cast

from llm_sdk.llm_sdk import Small_LLM_Model

DEFAULT_MODEL_NAME = "Qwen/Qwen3-0.6B"


def normalize_token_ids(raw_ids: object) -> list[int]:
    """convert sdk token ids into a plain list of integers
        had l function ghadi tkhli l code ykhdam swa sdk rja3 
        [1,2,3]
        wla [[1,2,3]]
    """

    if isinstance(raw_ids, list):
        if len(raw_ids) == 1 and isinstance(raw_ids[0], list):
            return [int(token_id) for token_id in raw_ids[0]]
        return [int(token_id) for token_id in raw_ids]
    
    raw_ids_any = cast(Any, raw_ids)

    if hasattr(raw_ids_any, "tolist"):
        values = raw_ids_any.tolist()
        return normalize_token_ids(values)
    
    raise TypeError("unsupported token id format returned by the sdk")

def encode_text(model: Small_LLM_Model, text: str) -> list[int]:
    """encode text into token ids using the sdk"""

    try:
        raw_ids = model.encode(text)
        return normalize_token_ids(raw_ids)
    except Exception as exc:
        raise RuntimeError(f"could not encode text: {exc}") from exc
    
def decode_token_ids(model: Small_LLM_Model, token_ids: list[int]) -> str:
    """decode token ids back into text using the sdk"""

    try:
        return model.decode(token_ids)
    except Exception as exc:
        raise RuntimeError(f"could not decode token ids: {exc}") from exc
    
def get_next_logits(
        model: Small_LLM_Model,
        input_ids: list[int],
) -> list[float]:
    """get raw next token logits from the sdk"""

    if not input_ids:
        raise ValueError("input_ids must not be empty")
    
    try:
        logits = model.get_logits_from_input_ids(input_ids)
    except Exception as exc:
        raise RuntimeError(f"could not get logits from model: {exc}") from exc
    
    if not logits:
        raise RuntimeError("model returned an empty logits list")
    
    return logits
