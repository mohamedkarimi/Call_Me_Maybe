from collections.abc import Callable
import json
import torch
from src.llm_client import decode_token_ids, encode_text
from llm_sdk.llm_sdk import Small_LLM_Model

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
PrefixValidator = Callable[[str], bool]
"""واش النص اللي تولد حتى دابا مازال ممكن يكمل ويولي صحيح؟"""
StopValidator = Callable[[str], bool]
"""واش النص كمل وخصنا نوقفو؟"""


def constrained_decode(
        model: Small_LLM_Model,
        prompt: str,
        prefix_validator: PrefixValidator,
        stop_validator: StopValidator,
        max_new_tokens: int = 256,
        max_candidates: int | None = None,
        user_prompt: str | None = None,
) -> str:
    """generate txte while respecting a prefix constraint"""
    prompt_ids = encode_text(model, prompt)

    # Optional smart pre-filling of JSON prefix
    # structure to bypass prompt/key generation redundancy
    if user_prompt is not None:
        prefix = f'{{\n  "prompt": {json.dumps(user_prompt)},\n  "name": "'
        prefilled_ids = encode_text(model, prefix)
        generated_ids = list(prefilled_ids)
        full_input_ids = prompt_ids + prefilled_ids
    else:
        generated_ids = []
        full_input_ids = prompt_ids

    # Run the first model pass over the full
    # initial context (including prefilled prefix if present)
    input_tensor = torch.tensor(
        [full_input_ids], device=model._device, dtype=torch.long)
    with torch.no_grad():
        outputs = model._model(input_ids=input_tensor, use_cache=True)
        past_key_values = outputs.past_key_values
        logits = outputs.logits[0, -1]

    max_candidates_val = max_candidates if max_candidates is not None else 100

    for _step in range(max_new_tokens):
        # Retrieve the sorted candidate token ids using fast PyTorch sorting
        sorted_indices = torch.argsort(logits, descending=True)
        token_ids = sorted_indices[:max_candidates_val].tolist()

        found = False
        next_token_id = -1
        for token_id in token_ids:
            candidate_ids = generated_ids + [token_id]
            candidate_text = decode_token_ids(model, candidate_ids)

            if prefix_validator(candidate_text):
                next_token_id = token_id
                generated_ids.append(token_id)
                found = True
                break

        if not found:
            raise RuntimeError(
                "no valid next token found during constrained decoding")

        generated_text = decode_token_ids(model, generated_ids)
        if stop_validator(generated_text):
            return generated_text

        # Get logits for next token using KV cache
        # to process only the single new token
        next_input = torch.tensor(
            [[next_token_id]], device=model._device, dtype=torch.long)
        with torch.no_grad():
            outputs = model._model(
                input_ids=next_input,
                past_key_values=past_key_values,
                use_cache=True,
            )
            past_key_values = outputs.past_key_values
            logits = outputs.logits[0, -1]

    raise RuntimeError("constrained decoding reached the token limit.")


def is_json_object_prefix(text: str) -> bool:
    """check whther text can still become a json object"""

    stripped = text.lstrip()

    if not stripped:
        return True

    if not stripped.startswith("{"):
        return False

    stack: list[str] = []  # باش نتبعو:{}
    in_string = False  # واش دابا داخل "string" ؟
    escaped = False  # \"

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


def fix_json_escapes(text: str) -> str:
    """Escapes invalid backslashes in a JSON
    string so json.loads doesn't fail.
    """
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == '\\':
            if i + 1 < n:
                next_char = text[i+1]
                if next_char in ['"', '\\', '/', 'b', 'f', 'n', 'r', 't']:
                    result.append('\\')
                    result.append(next_char)
                    i += 2
                    continue
                elif next_char == 'u':
                    if (
                        i + 5 < n
                        and all(
                            c in "0123456789abcdefABCDEF"
                            for c in text[i + 2: i + 6]
                        )
                    ):
                        result.append('\\')
                        result.append('u')
                        result.extend(text[i+2:i+6])
                        i += 6
                        continue
            result.append('\\\\')
            i += 1
        else:
            result.append(text[i])
            i += 1
    return "".join(result)


def is_complete_json_object(text: str) -> bool:
    """check whether text is a complet json object"""
    try:
        decoded = json.loads(fix_json_escapes(text))
    except json.JSONDecodeError:
        return False

    return isinstance(decoded, dict)
