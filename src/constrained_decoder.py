"""3. مهم تفهم هاد النقطة

فـ subject كيقولو الخطوات هكا:

1. model produces logits
2. نحددو valid tokens
3. invalid tokens كنعتابروهم -infinity
4. كنختارو غير من valid tokens

حنا فالكود ما غاديش نبدلو logits فعلياً لـ -inf.
غادي نديرو نفس الفكرة بطريقة سهلة:

نرتبو tokens من الأحسن للأسوأ حسب logits
نجرب token الأول
إلا كان كيخلي output valid → ناخدوه
إلا كان غلط → نجرب اللي من بعدو
حتى نلقى token صحيح
"""
"""constrained token by token decoding utilities"""

import json
from collections.abc import Callable, Sequence

import numpy as np

from llm_sdk.llm_sdk import Small_LLM_Model
from src.llm_client import decode_token_ids, encode_text, get_next_logits

PrefixValidator = Callable[[str], bool]
"""واش النص اللي تولد حتى دابا مازال ممكن يكمل ويولي صحيح؟"""
StopValidator = Callable[[str], bool]
"""واش النص كمل وخصنا نوقفو؟"""

def top_k_token_ids_by_score(
        logits: Sequence[float],
        k: int,
) -> list[int]:
    """return the top k token ids ordered from highest logit score to lowest"""

    if not logits:
        raise ValueError("cannot order empty logits")

    arr = np.asarray(logits)
    k = min(k, len(arr))
    top_k_indices = np.argpartition(-arr, k)[:k]
    top_k_sorted = top_k_indices[np.argsort(-arr[top_k_indices])]
    return [int(x) for x in top_k_sorted]

def find_best_valid_token(
        model: Small_LLM_Model,
        context_ids: list[int],
        generated_ids: list[int],
        prefix_validator: PrefixValidator,
        max_candidates: int | None = 100,
) -> tuple[int, str]:
    """find the highest scoring token that keeps the output valid

    returns the token id and the decoded candidate text
    """
    
    """جيب logits
    رتب tokens
    جرب token ب token
    decode candidate
    شوف واش candidate valid prefix
    إلا valid رجع token_id
    إلا كلشي غلط raise error
    """

    logits = get_next_logits(model, context_ids)
    actual_max_candidates = max_candidates if max_candidates is not None else 100
    token_ids = top_k_token_ids_by_score(logits, k=actual_max_candidates)
    
    for token_id in token_ids:
        candidate_ids = generated_ids + [token_id]
        candidate_text = decode_token_ids(model, candidate_ids)

        if prefix_validator(candidate_text):
            return token_id, candidate_text
    
    raise RuntimeError("no valid next token found during constrained decoding")

def constrained_decode(
        model: Small_LLM_Model,
        prompt: str,
        prefix_validator: PrefixValidator,
        stop_validator: StopValidator,
        max_new_tokens: int = 256,
        max_candidates: int | None = None,
) -> str:
    """generate txte while respecting a prefix constraint"""
    prompt_ids = encode_text(model, prompt)
    generated_ids: list[int] = []

    for _step in range(max_new_tokens):
        context_ids = prompt_ids + generated_ids

        next_token_id, generated_text = find_best_valid_token(
            model=model,
            context_ids=context_ids,
            generated_ids=generated_ids,
            prefix_validator=prefix_validator,
            max_candidates=max_candidates,
        )

        generated_ids.append(next_token_id)

        if stop_validator(generated_text):
            return generated_text
    raise RuntimeError("constrained decoding reached the token limit.")

def is_json_object_prefix(text: str) -> bool:
    """check whther text can still become a json object"""

    stripped = text.lstrip()

    if not stripped:
        return True
    
    if not stripped.startswith("{"):
        return False
    
    stack: list[str] = []
    in_string = False
    escaped = False

    for character in stripped:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue

        if character == '"':
            in_string = True
        elif character in "{[":
            stack.append(character)
        elif character in "}]":
            if not stack:
                return False
            
            opening = stack.pop()
            if opening == "{" and character != "}":
                return False
            if opening == "[" and character != "]":
                return False
    return True

def is_complete_json_object(text: str) -> bool:
    """check whether text is a complet json object"""
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError:
        return False
    
    return isinstance(decoded, dict)
    