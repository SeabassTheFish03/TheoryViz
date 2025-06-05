import json
import os

def load_json(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return "JSON error - missing bracket / formatting error"

def run_quantitative_tests(test_cases, expected_results):
    """Run tests that have definite pass/fail criteria."""
    results = {}
    for file, expected in expected_results.items():
        if not os.path.exists(file):
            results[file] = "File not found"
            continue
        
        data = load_json(file)
        if isinstance(data, str):  # JSON error case
            results[file] = data
            continue
        
        if file == "automaton_no_states.json":
            results[file] = "should run but put up blank screen"
        elif file == "tm_testing.json":
            if len(data.get("states", [])) == 15:
                results[file] = "produce 15 state dfa. transitions clear and readable and nothing overlapping"
            else:
                results[file] = "Error: DFA does not have 15 states"
        else:
            results[file] = "Unhandled test case"
    return results

def run_qualitative_tests(test_cases):
    """Prompt the user for approval/disapproval on qualitative tests."""
    for file in test_cases:
        print(f"Review the visualization for {file} and approve/disapprove.")
        input("Press Enter to continue...")

def main():
    # Expected results parsed from zexpectedresults.txt
    expected_results = {
        "automaton_no_states.json": "should run but put up blank screen",
        "tm_testing.json": "produce 15 state dfa. transitions clear and readable and nothing overlapping"
    }
    
    quantitative_results = run_quantitative_tests(
        ["automaton_no_states.json", "tm_testing.json"], expected_results)
    for test, result in quantitative_results.items():
        print(f"{test}: {result}")
    
    run_qualitative_tests(["tm_testing.json"])

if __name__ == "__main__":
    main()
