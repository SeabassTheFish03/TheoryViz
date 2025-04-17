import json
import os
import sys
import tomllib
import subprocess
from manim._config import tempconfig
from manim.scene.scene import Scene
from manim.animation.creation import Create
from manim.constants import UP, RIGHT
from fa_manager import DFA_Manager, TM_Manager, NFA_Manager

# where your JSON files live
test_dir = os.path.join(os.getcwd(), "fa_vault", "testing")

all_test_files = [
    "automaton_no_states.json",
    "dfa_15_states.json",
    "dfa_15+5_max.json",
    "dfa_double_transitions.json",
    "dfa_epsilon_transition.json",
    "dfa_false_start_states.json",
    "dfa_five_input_characters.json",
    "dfa_incomplete_transition.json",
    "dfa_missing_transitions.json",
    "dfa_missing_transitionsfield.json",
    "dfa_no_final_states.json",
]

# add the two new DFAs here to render
qualitative_tests = {
    "dfa_15_states.json",
    "dfa_15+5_max.json",
    "dfa_five_input_characters.json",
}

class SceneToShow(Scene):
    def __init__(self, fa_filename, config_filename, input_string):
        super().__init__()
        path = os.path.join(test_dir, fa_filename)
        with open(path, "rb") as f:
            fa_json = json.load(f)
        with open(config_filename, "rb") as f:
            self.config = tomllib.load(f)

        if fa_json.get("fa_type") == "dfa":
            self.fa = DFA_Manager.from_json(fa_json, config=self.config, input_string=input_string)
            self.fa._show_graph_render()
            self.fa._show_process_text()
            self.fa._show_transition_table()
            self.fa.move_mobj("table", [-2, 0, 0])
            self.fa.next_to_mobj("dfa", "table", RIGHT)
            self.fa.scale_mobj("dfa", 0.7)
            self.fa.next_to_mobj("text", "dfa", UP)
        else:
            self.fa = TM_Manager.from_json(fa_json, config=self.config, input_string=input_string)
            self.fa.show_graph_render()
            self.fa.show_tape()
            self.fa.scale_mobject("tm", 0.7)
            self.fa.next_to_mobject("tape", "tm", UP)
        #TODO - insert NFA into eventual testing

    def construct(self):
        self.camera.background_color = self.config["scene"]["background_color"]
        self.play(Create(self.fa.mobj))
        self.play(self.fa.animate())
        self.wait(1)


def load_json(fp):
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "JSON error - malformed"


def get_expected_message(fname):
    return {
        "automaton_no_states.json":         "should run but put up blank screen",
        "dfa_15_states.json":               "produce 15 state dfa. transitions clear and readable and nothing overlapping",
        "dfa_15+5_max.json":                "produce 15 state dfa according to static representation criteria",
        "dfa_double_transitions.json":      "error - dfas cannot have ambiguous transitions",
        "dfa_epsilon_transition.json":      "error - dfas do not support epsilon transitions",
        "dfa_false_start_states.json":      "error - start state does not exist in this dfa",
        "dfa_five_input_characters.json":   "success - produce dfa in accordance with static representation criteria",
        "dfa_incomplete_transition.json":   "error - all transitions must be fully defined",
        "dfa_missing_transitions.json":     "error - must include all transitions for all states",
        "dfa_missing_transitionsfield.json":"error - missing transitions field - total formatting error",
        "dfa_no_final_states.json":         "error - no final state defined",
    }[fname]


def run_quantitative_tests(expected_results):
    results = {}
    for fname, expect in expected_results.items():
        path = os.path.join(test_dir, fname)
        if not os.path.exists(path):
            results[fname] = "File not found"
            continue

        data = load_json(path)
        if isinstance(data, str):
            results[fname] = data
            continue

        states  = data.get("states", [])
        symbols = data.get("input_symbols", [])
        trans   = data.get("transitions")
        initial = data.get("initial_state")
        finals  = data.get("final_states")

        # per-file logic
        if fname == "automaton_no_states.json":
            results[fname] = expect if not states else "Unexpected non-empty states"

        elif fname == "dfa_15_states.json":
            ok = len(states)==15 and trans and initial in states and finals
            results[fname] = expect if ok else "Error: 15-state DFA test failed"

        elif fname == "dfa_15+5_max.json":
            ok = len(states)==15 and len(symbols)==5 and trans and initial in states and finals
            results[fname] = expect if ok else "Error: 15+5 DFA test failed"

        elif fname == "dfa_double_transitions.json":
            results[fname] = expect

        elif fname == "dfa_epsilon_transition.json":
            has_eps = any(sym in ("\u03b5","\\epsilon") for row in (trans or {}).values() for sym in row)
            results[fname] = expect if has_eps else "Error: no epsilon transition found"

        elif fname == "dfa_false_start_states.json":
            bad_start = initial not in states
            results[fname] = expect if bad_start else "Error: start state is valid"

        elif fname == "dfa_five_input_characters.json":
            results[fname] = expect

        elif fname == "dfa_incomplete_transition.json":
            incomplete = any(set(symbols) != set(row.keys()) for row in (trans or {}).values())
            results[fname] = expect if incomplete else "Error: transitions appear complete"

        elif fname == "dfa_missing_transitionsfield.json":
            results[fname] = expect if trans is None else "Error: transitions field was present"

        elif fname == "dfa_missing_transitions.json":
            missing = any(s not in (trans or {}) for s in states)
            results[fname] = expect if missing else "Error: no missing state transitions"

        elif fname == "dfa_no_final_states.json":
            no_finals = not finals
            results[fname] = expect if no_finals else "Error: final states defined"

        else:
            results[fname] = "Unhandled test case"

    return results


def run_qualitative_tests(test_cases):
    for fname in test_cases:
        print(f"\n--- Visual check for {fname} ---")
        with tempconfig({"quality": "medium_quality", "preview": True}):
            scene = SceneToShow(fname, "default_config.toml", "a")
            scene.render()
        input("Press Enter to continue...")


def main_for_file(test_file):
    expect = get_expected_message(test_file)
    print(f"\n=== Quantitative for {test_file} ===")
    qr = run_quantitative_tests({test_file: expect})
    for f, res in qr.items():
        print(f"{f}: {res}")

    if test_file in qualitative_tests:
        print(f"\n=== Qualitative for {test_file} ===")
        run_qualitative_tests([test_file])
    else:
        print(f"\n(skipping qualitative tests for {test_file})")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_for_file(sys.argv[1])
    else:
        for idx, tf in enumerate(all_test_files):
            if idx == 0:
                main_for_file(tf)
            else:
                print(f"\n>>> Simulating next test via subprocess: {tf}")
                subprocess.run([sys.executable, __file__, tf], check=True)
