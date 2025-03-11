import json
import os
import sys
import tomllib
from manim._config import tempconfig
from manim.scene.scene import Scene
from manim.animation.creation import Create
from manim.constants import UP, RIGHT
from fa_manager import DFA_Manager, TM_Manager

class SceneToShow(Scene):
    def __init__(self, fa_filename, config_filename, input_string):
        super().__init__()
        dfa_file = os.path.join(os.getcwd(), "fa_vault\\testing\\dfa_15_states.json")

        with open(dfa_file, "rb") as f:
            fa_json = json.load(f)
        with open(config_filename, "rb") as f:
            self.config = tomllib.load(f)

        # Triage
        if fa_json["fa_type"] == "dfa":
            self.fa = DFA_Manager.from_json(fa_json, config=self.config, input_string=input_string)
            self.fa._show_graph_render()
            self.fa._show_process_text()
            self.fa._show_transition_table()
            self.fa.move_mobj("table", [-2, 0, 0])
            self.fa.next_to_mobj("dfa", "table", RIGHT)
            self.fa.scale_mobj("dfa", 0.7)
            self.fa.next_to_mobj("text", "dfa", UP)
        elif fa_json["fa_type"] == "tm":
            self.fa = TM_Manager.from_json(fa_json, config=self.config, input_string=input_string)
            self.fa.show_graph_render()
            self.fa.show_tape()

            self.fa.scale_mobject("tm", 0.7)
            self.fa.next_to_mobject("tape", "tm", UP)

    def construct(self):
        self.camera.background_color = self.config["scene"]["background_color"]
        self.play(Create(self.fa.mobj))
        self.play(self.fa.animate())
        self.wait(1)

def load_json(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return "JSON error - missing bracket / formatting error"

def run_quantitative_tests(expected_results):
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
        elif file == "dfa_15_states.json":
            if len(data.get("states", [])) == 15:
                results[file] = "produce 15 state dfa. transitions clear and readable and nothing overlapping"
            else:
                results[file] = "Error: DFA does not have 15 states"
        else:
            results[file] = "Unhandled test case"
    return results

def run_qualitative_tests(test_cases):
    """Run and prompt the user for approval/disapproval on qualitative tests."""
    for file in test_cases:
        print(f"Running visualization for {file}...")
        with tempconfig({"quality": "medium_quality", "preview": True}):
            scene = SceneToShow(file, "default_config.toml", "a")  # Adjust input as needed
            scene.render()
        input("Press Enter to approve/disapprove...")

def main():
    # Expected results parsed from zexpectedresults.txt
    expected_results = {
        "automaton_no_states.json": "should run but put up blank screen",
        "dfa_15_states.json": "produce 15 state dfa. transitions clear and readable and nothing overlapping"
    }
    
    quantitative_results = run_quantitative_tests(expected_results)
    for test, result in quantitative_results.items():
        print(f"{test}: {result}")
    
    run_qualitative_tests(["dfa_15_states.json"])

if __name__ == "__main__":
    main()
