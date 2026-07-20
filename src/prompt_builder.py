"""build prompts for the language model"""
from collections.abc import Sequence

from src.models import FunctionDefinition, TypeDefinition


def format_parameters(parameters: dict[str, TypeDefinition]) -> str:
    """fromat funcion parameters as a readable signature"""

    formatted_parameters: list[str] = []

    for name, definition in parameters.items():
        formatted_parameters.append(f"{name}: {definition.type}")

    return ", ".join(formatted_parameters)


def format_function_definition(function: FunctionDefinition) -> str:
    """format one function definition for the prompt"""

    parameters = format_parameters(function.parameters)

    return (
        f"- {function.name}({parameters}) -> {function.returns.type}: "
        f"{function.description}"
    )


def build_generation_prompt(
        user_prompt: str,
        functions: Sequence[FunctionDefinition],
) -> str:
    """build the full llm prompt for one user request"""

    formatted_functions = "\n" .join(
        format_function_definition(function)
        for function in functions
    )

    return f"""You are a function-calling system.

Your task is to translate the user request into a function call.

Available functions:
{formatted_functions}

Rules:
- Choose exactly one function from the available functions.
- Extract only the required parameters for that function.
- Use the exact parameter names from the function definition.
- Respect the parameter types.
- Do not answer the user request directly.
- Return only a JSON object.
- The JSON object must contain exactly these keys:
  - "prompt"
  - "name"
  - "parameters"

User request:
{user_prompt}

JSON output:
"""
