"""build schema constraints from function definitions"""
from collections.abc import Sequence

from src.models import FunctionDefinition, jsonType, StrictModel

OUTPUT_KEYS: tuple[str, str, str] = ("prompt", "name", "parameters")


class FunctionCallSchema(StrictModel):
    """represent constraints for function call generation"""

    output_keys: list[str]
    function_names: list[str]
    parameters_by_function: dict[str, dict[str, jsonType]]
    returns_by_function: dict[str, jsonType]


def extract_parameter_types(
        function: FunctionDefinition,
) -> dict[str, jsonType]:
    """extract parameter names and json types from a function definition
    eg:
    fn_add_numbers(a: number, b: number)
    the output:
    {"a": "number", "b": "number"}
    """

    parameter_types: dict[str, jsonType] = {}

    for name, definition in function.parameters.items():
        parameter_types[name] = definition.type
    return parameter_types


def build_function_call_schema(
        functions: Sequence[FunctionDefinition],
) -> FunctionCallSchema:
    """build schema constraints from available function definitions"""

    if not functions:
        raise ValueError("at least one function definition is required")

    function_names: list[str] = []
    parameters_by_function: dict[str, dict[str, jsonType]] = {}
    returns_by_function: dict[str, jsonType] = {}

    for function in functions:
        """ghadi nmchiw function b function o ghadi n checkiw
            wach 3ndna 2 functions bnafss no3
        """
        if function.name in parameters_by_function:
            raise ValueError(f"duplicate function name: {function.name}")

        function_names.append(function.name)
        parameters_by_function[function.name] = extract_parameter_types(
            function)
        returns_by_function[function.name] = function.returns.type

    return FunctionCallSchema(
        output_keys=list(OUTPUT_KEYS),
        function_names=function_names,
        parameters_by_function=parameters_by_function,
        returns_by_function=returns_by_function,
    )


def validate_function_name(
        schema: FunctionCallSchema,
        function_name: str,
) -> bool:
    """check whther a function name exists in the schema"""

    return function_name in schema.parameters_by_function


def is_value_matching_json_type(
        value: object,
        expected_type: jsonType,
) -> bool:
    """check whether a python value matches a json type"""

    if expected_type == "string":
        return isinstance(value, str)

    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)

    if expected_type == "boolean":
        return isinstance(value, bool)

    if expected_type == "object":
        return isinstance(value, dict)

    if expected_type == "array":
        return isinstance(value, list)

    return False


def validate_parameters(
        schema: FunctionCallSchema,
        function_name: str,
        parameters: dict[str, object],
) -> bool:
    """validate parameters against the schema of a function"""

    if not validate_function_name(schema, function_name):
        return False

    expected_parameters = schema.parameters_by_function[function_name]

    if set(parameters) != set(expected_parameters):
        return False

    for name, expected_type in expected_parameters.items():
        if not is_value_matching_json_type(parameters[name], expected_type):
            return False

    return True
