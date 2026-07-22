"""high level function call generation pipeline"""

import json
from typing import cast
from llm_sdk.llm_sdk import Small_LLM_Model

from src.constrained_decoder import (
    constrained_decode,
    is_complete_json_object,
    is_json_object_prefix,
    fix_json_escapes,
)

from src.models import FunctionCallResult, FunctionDefinition
from src.prompt_builder import build_generation_prompt
from src.schema_builder import (
    FunctionCallSchema,
    build_function_call_schema,
    validate_function_name,
    validate_parameters,
)


def parse_generated_json(text: str) -> dict[str, object]:
    """parse generated json text"""

    try:
        data = json.loads(fix_json_escapes(text))
    except json.JSONDecodeError as exc:
        raise ValueError("generated text is not valid json") from exc

    if not isinstance(data, dict):
        raise ValueError("generated json root must be an object")

    return data


def validate_generated_object(
        schema: FunctionCallSchema,
        generated: dict[str, object],
) -> None:
    """validate generated function call structure"""

    required_keys = {"prompt", "name", "parameters"}

    if set(generated) != required_keys:
        raise ValueError("generated object has invalid keys")

    function_name = generated["name"]   
    parameters = generated["parameters"]

    if not isinstance(function_name, str):
        raise ValueError("function name must be a string")

    if not isinstance(parameters, dict):
        raise ValueError("parameters must be an object")

    if not validate_function_name(schema, function_name):
        raise ValueError(f"unknown function name: {function_name}")

    if not validate_parameters(schema, function_name, parameters):
        raise ValueError("generated parameters do not match schema")


def generate_function_call(
        model: Small_LLM_Model,
        prompt: str,
        functions: list[FunctionDefinition],
        max_new_tokens: int = 256,
) -> FunctionCallResult | None:
    """generate a validated function call for a prompt"""

    schema = build_function_call_schema(functions)

    generation_prompt = build_generation_prompt(
        functions=functions,
        user_prompt=prompt,
    )

    generated_text = constrained_decode(
        model=model,
        prompt=generation_prompt,
        prefix_validator=is_json_object_prefix,
        stop_validator=is_complete_json_object,
        max_new_tokens=max_new_tokens,
        user_prompt=prompt,
    )

    generated_object = parse_generated_json(generated_text)

    generated_object["prompt"] = prompt

    function_name = generated_object.get("name")
    if function_name == "fn_none":
        return None
    parameters = generated_object.get("parameters")

    if isinstance(function_name, str) and isinstance(parameters, dict):
        expected_parameters = schema.parameters_by_function.get(
            function_name, {})

        for param_name, param_type in expected_parameters.items():
            if (
                param_type == "number"
                and param_name in parameters
                and isinstance(parameters[param_name], int)
            ):
                parameters[param_name] = float(parameters[param_name])

    validate_generated_object(schema, generated_object)

    return cast(
        FunctionCallResult,
        FunctionCallResult.model_validate(generated_object),
    )
