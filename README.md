*This project has been created as part of the 42 curriculum by mokarimi.*

# Call Me Maybe

## Description

Call Me Maybe is a function-calling system powered by a Small Language Model (LLM). The goal of the project is to convert natural language prompts into structured JSON function calls.

Instead of answering a user's request directly, the model identifies the appropriate function and extracts the required parameters according to a predefined schema.

To guarantee valid output, the project uses constrained decoding. Every generated token is validated before being accepted, ensuring that the final output is always a valid JSON object matching the expected schema.

The implementation uses `Qwen/Qwen3-0.6B` through the provided `llm_sdk` wrapper. The model is responsible for choosing the correct function and extracting the parameters, while the decoder enforces the JSON structure and schema constraints.

---

# Features

- Natural language understanding using Qwen/Qwen3-0.6B
- Automatic function selection
- Parameter extraction with correct types
- Schema validation using Pydantic
- Constrained decoding
- Guaranteed valid JSON output
- Robust error handling
- Fully typed code compatible with mypy

---

# Project Structure

```
.
├── src/
│   ├── __main__.py
│   ├── loader.py
│   ├── models.py
│   ├── prompt_builder.py
│   ├── llm_client.py
│   ├── schema_builder.py
│   ├── constrained_decoder.py
│   ├── generator.py
│   └── writer.py
│
├── llm_sdk/
├── data/
│   ├── input/
│   └── output/
│
├── pyproject.toml
├── uv.lock
├── Makefile
└── README.md
```

---

# Instructions

## Installation

Clone the repository.

Create the virtual environment and install the dependencies:

```bash
make install
```

The project is also compatible with the subject's expected command:

```bash
uv sync
```

---

## Running the project

```bash
make run
```

or

```bash
uv run python -m src
```

By default, the program reads:

- `data/input/function_calling_tests.json`
- `data/input/functions_definition.json`

and writes:

- `data/output/function_calling_results.json`

You can also specify custom files:

```bash
uv run python -m src \
    --functions_definition data/input/functions_definition.json \
    --input data/input/function_calling_tests.json \
    --output data/output/function_calling_results.json
```

---

## Debug

```bash
make debug
```

---

## Lint

```bash
make lint
```

Strict mode:

```bash
make lint-strict
```

---

# Algorithm Explanation

The implementation follows a constrained decoding pipeline.

1. The program loads the available function definitions and the input prompts.

2. A prompt describing the available functions is generated and sent to the language model.

3. The model generates one token at a time.

4. Before accepting a token, the decoder verifies that appending this token still produces a valid JSON prefix.

5. Invalid tokens are rejected and the decoder searches for another candidate.

6. Generation continues until a complete valid JSON object is produced.

7. The generated JSON is parsed and validated using Pydantic before being written to the output file.

This approach guarantees that invalid JSON structures cannot be produced during generation.

In practice, the decoder uses the model logits together with the vocabulary mapping from the SDK. At each step, candidate tokens are tested against the current JSON prefix and the expected schema. Tokens that would break the JSON syntax, introduce invalid keys, or produce values of the wrong type are rejected before selection.

---

# Design Decisions

Several design decisions were made to improve maintainability.

- Pydantic models are used for input and output validation.
- The project is divided into small modules, each responsible for a single task.
- Prompt generation is isolated from decoding.
- Schema construction is independent from generation.
- File loading and writing are separated from the inference pipeline.
- Type hints and docstrings are provided throughout the project.

---

# Performance Analysis

The project focuses on three main objectives:

### Accuracy

The language model is responsible for selecting the correct function and extracting the required parameters from the prompt. The goal is to stay above the subject's expected reliability threshold for function selection and argument extraction.

### Reliability

Constrained decoding guarantees that every generated output is valid JSON matching the required schema, which is the most important requirement of the project.

### Speed

To improve execution speed, the decoder limits the number of candidate tokens examined during each generation step instead of checking the entire vocabulary. This keeps generation practical while preserving structural safety.

---

# Challenges Faced

Several challenges were encountered during development.

- Understanding how constrained decoding works.
- Handling malformed or incomplete JSON.
- Converting model outputs into valid structured objects.
- Reducing generation time caused by searching a very large vocabulary.
- Ensuring generated parameter types match the function definitions exactly.
- Handling invalid input files without crashing.

Another important challenge was keeping the implementation compliant with the subject constraints: using the provided SDK, avoiding forbidden shortcuts, and making sure the LLM chooses the function instead of relying on manual heuristics.

These issues were solved through schema validation, better token filtering, improved error handling, and careful modularization.

---

# Testing Strategy

The implementation was tested using:

- the provided public test set
- private moulinette tests
- malformed JSON files
- missing input files
- functions with multiple parameters
- different parameter types
- large numbers
- regular expression replacement prompts
- edge cases such as empty strings

Static analysis was also performed using:

- flake8
- mypy

---

# Example Usage

Input:

```
What is the sum of 2 and 3?
```

Output:

```json
{
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": {
        "a": 2.0,
        "b": 3.0
    }
}
```

Another example:

Input:

```
Reverse the string "hello"
```

Output:

```json
{
    "prompt": "Reverse the string \"hello\"",
    "name": "fn_reverse_string",
    "parameters": {
        "s": "hello"
    }
}
```

---

# Resources

### Documentation

- [Python documentation](https://docs.python.org/3/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [JSON specification (ECMA-404)](https://ecma-international.org/publications-and-standards/standards/ecma-404/)
- [Qwen documentation](https://qwenlm.github.io/)
- 42 subject: `CallmeMeybe.pdf`

### AI Usage

AI was used as a learning assistant during the project, not as a blind code generator.

It was mainly used for:

- understanding constrained decoding
- learning Python concepts
- discussing how to validate JSON incrementally
- improving code documentation
- reviewing algorithms
- explaining implementation details

All generated explanations and suggestions were reviewed, understood, tested, and adapted before being integrated into the project.

---

# Author

**mokarimi**

42 Network
