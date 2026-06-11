"""command line entry point for the call me maybe project"""
import argparse
from pathlib import Path

from src.loader import load_input_data
from llm_sdk.llm_sdk import Small_LLM_Model
from src.generator import generate_function_call
from src.writer import write_results

DEFAULT_INPUT_PATH = Path("data/input/function_calling_tests.json")
DEFAULT_FUNCTIONS_PATH = Path("data/input/functions_definition.json")
DEFAULT_OUTPUT_PATH = Path("data/output/function_calling_results.json")

def parse_args() -> argparse.Namespace:
    """parse command line argument"""

    parser = argparse.ArgumentParser(
        description="generate structured function calls from prompts"
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Path to the prompt tests json file",
    )

    parser.add_argument(
        "--functions_definition",
        type=Path,
        default=DEFAULT_FUNCTIONS_PATH,
        help="path to the function definitions json file",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="path where the generated results will be written",
    )

    return parser.parse_args()

def main() -> int:
    """run the command line program
    return:
        process exit code
    """
    args = parse_args()

    try:
        input_data = load_input_data(
            prompts_path=args.input,
            functions_path=args.functions_definition,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    
    print("loading model...")
    model = Small_LLM_Model()
    
    results = []
    print()
    print("starting generation...")
    print("-" * 40)
    
    for test_case in input_data.prompts:
        print(f"processing prompt: {test_case.prompt}")
        
        try:
            result = generate_function_call(
                model=model,
                prompt=test_case.prompt,
                functions=input_data.functions,
            )
        except Exception as exc:
            print(f"generation failed: {exc}")
            print()
            continue
        
        results.append(result)
    
    output_path = write_results(
        output_path=args.output,
        results=results,
    )
    
    print()
    print("generation completed successfully")
    print(f"generated results: {len(results)}")
    print(f"output written to: {output_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())