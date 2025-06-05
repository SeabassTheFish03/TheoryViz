import json
import os
import sys
import tomllib
import subprocess
from manim._config import tempconfig
from manim.scene.scene import Scene
from manim.animation.creation import Create
from manim.constants import UP, RIGHT
from fa_manager import DFA_Manager, TM_Manager

# where your JSON files live
TEST_DIR = os.path.join(os.getcwd(), "fa_vault", "testing")

ALL_TEST_FILES = [
    # old DFA tests
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
    # new DFA tests
    "dfa_no_input_symbols.json",
    "dfa_non-defined_input_symbol.json",
    "dfa_one_state.json",
    "dfa_six_input_characters.json",
    "dfa_two_start_states.json",
    "jsonformaterror.json",
    "missing_type.json",
    # TM tests
    "tm_double_Transition.json",
    "tm_epsilon_transition.json",
    "tm_incomplete_transition.json",
    "tm_missingTransition.json",
    "tm_testing.json",
    # type tests
    "unidentified_type.json",
    "unsupported_automata.json",
]

# only these get the Manim preview
QUALITATIVE_TESTS = {"dfa_15_states.json", 
                     "dfa_15+5_max.json", 
                     "dfa_five_input_characters.json"}

class SceneToShow(Scene):
    def __init__(self, fa_filename, config_filename, input_string):
        super().__init__()
        path = os.path.join(TEST_DIR, fa_filename)
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

    def construct(self):
        self.camera.background_color = self.config["scene"]["background_color"]
        self.play(Create(self.fa.mobj))
        self.play(self.fa.animate())
        self.wait(1)

def load_json(fp):
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        return "JSON error - missing bracket / formatting error"
    except json.JSONDecodeError:
        return "JSON error - missing bracket / formatting error"

def get_expected_message(fname):
    return {
        # old DFA
        "automaton_no_states.json":         "error - cannot produce an automaton with no states",
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
        # new DFA
        "dfa_no_input_symbols.json":        "error - no input symbols defined",
        "dfa_non-defined_input_symbol.json":"error with transitions - non-defined input symbol",
        "dfa_one_state.json":               "success - display one state dfa, all self trasnitions",
        "dfa_six_input_characters.json":    "error - too many input characters, maximum number of input characters is five",
        "dfa_two_start_states.json":        "error - only one start state may be defined",
        "jsonformaterror.json":             "JSON error - missing bracket / formatting error",
        "missing_type.json":                "error - no type defined",
        # TM tests
        "tm_double_Transition.json":        "error - double definition of a transition. Turing machines in this code are deterministic and cannot have double defined transitions",
        "tm_epsilon_transition.json":       "error - epsilon transition. Turing Machines in TheoryViz are deterministic",
        "tm_incomplete_transition.json":    "error - all transitions must be fully defined",
        "tm_missingTransition.json":        "error - missing transition field",
        "tm_testing.json":                  "success",
        # type tests
        "unidentified_type.json":           "error - type of automata undefined",
        "unsupported_automata.json":        "error - pdas are not supported yet by TheoryViz",
    }[fname]

def run_quantitative_tests(expected_results):
    results = {}
    for fname, expect in expected_results.items():
        path = os.path.join(TEST_DIR, fname)
        if not os.path.exists(path):
            results[fname] = "File not found"
            continue

        data = load_json(path)
        # JSON format errors
        if isinstance(data, str) and "JSON error" in data:
            results[fname] = expect
            continue

        # missing type
        if fname == "missing_type.json":
            if "fa_type" not in data:
                results[fname] = expect
            else:
                results[fname] = "Error: type defined"
            continue

        fa_type = data.get("fa_type")

        # --- DFA tests ---
        if fname == "automaton_no_states.json":
            results[fname] = expect if data.get("states")==[] else "Error: non-empty states"

        elif fname == "dfa_no_input_symbols.json":
            results[fname] = expect if not data.get("input_symbols") else "Error: input symbols present"

        elif fname == "dfa_non-defined_input_symbol.json":
            symbols = set(data.get("input_symbols",[]))
            trans = data.get("transitions",{})
            bad = any(sym not in symbols for row in trans.values() for sym in row)
            results[fname] = expect if bad else "Error: all symbols defined"

        elif fname == "dfa_one_state.json":
            states = data.get("states",[])
            syms   = set(data.get("input_symbols",[]))
            trans  = data.get("transitions",{})
            init   = data.get("initial_state")
            finals = data.get("final_states",[])
            ok = (len(states)==1 and init==states[0] and finals==states and
                  set(trans.get(states[0],{}).keys())==syms and
                  all(trans[states[0]][s]==states[0] for s in syms))
            results[fname] = expect if ok else "Error: one-state DFA failed"

        elif fname == "dfa_six_input_characters.json":
            results[fname] = expect if len(data.get("input_symbols",[]))>5 else "Error: <=5 input symbols"

        elif fname == "dfa_two_start_states.json":
            init = data.get("initial_state")
            results[fname] = expect if not isinstance(init,str) else "Error: single start state"

        elif fname == "dfa_15_states.json":
            ok = (len(data.get("states",[]))==15 and data.get("transitions") and
                  data.get("initial_state") in data["states"] and data.get("final_states"))
            results[fname] = expect if ok else "Error: 15-state DFA test failed"

        elif fname == "dfa_15+5_max.json":
            ok = (len(data.get("states",[]))==15 and len(data.get("input_symbols",[]))==5)
            results[fname] = expect if ok else "Error: 15+5 DFA test failed"

        elif fname == "dfa_double_transitions.json":
            results[fname] = expect

        elif fname == "dfa_epsilon_transition.json":
            has_eps = any(k in ("epsilon","\\epsilon","/epsilon")
                          for row in data.get("transitions",{}).values()
                          for k in row)
            results[fname] = expect if has_eps else "Error: no epsilon"

        elif fname == "dfa_false_start_states.json":
            results[fname] = expect if data.get("initial_state") not in data.get("states",[]) else "Error: valid start"

        elif fname == "dfa_five_input_characters.json":
            results[fname] = expect

        elif fname == "dfa_incomplete_transition.json":
            syms = set(data.get("input_symbols",[]))
            rows= data.get("transitions",{})
            bad = any(set(r.keys())!=syms for r in rows.values())
            results[fname] = expect if bad else "Error: transitions complete"

        elif fname == "dfa_missing_transitions.json":
            states = set(data.get("states",[]))
            rows   = set(data.get("transitions",{}).keys())
            bad = not states.issubset(rows)
            results[fname] = expect if bad else "Error: no missing"

        elif fname == "dfa_missing_transitionsfield.json":
            results[fname] = expect if data.get("transitions") is None else "Error: transitions field exists"

        elif fname == "dfa_no_final_states.json":
            results[fname] = expect if not data.get("final_states") else "Error: finals exist"

        # --- TM tests ---
        elif fname == "tm_double_Transition.json":
            results[fname] = expect

        elif fname == "tm_epsilon_transition.json":
            vals = data.get("transitions",{}).values()
            has_eps = any(t[1] in ("epsilon","\\epsilon","/epsilon") for row in vals for t in row.values())
            results[fname] = expect if has_eps else "Error: no eps"

        elif fname == "tm_incomplete_transition.json":
            vals = data.get("transitions",{}).values()
            bad = any(not isinstance(t,list) or len(t)!=3 for row in vals for t in row.values())
            results[fname] = expect if bad else "Error: all defined"

        elif fname == "tm_missingTransition.json":
            states = set(data.get("states",[]))
            rows   = set(data.get("transitions",{}).keys())
            bad = not states.issuperset(rows)
            results[fname] = expect if bad else "Error: no missing"

        elif fname == "tm_testing.json":
            results[fname] = expect

        # --- type / unsupported tests ---
        elif fname == "unidentified_type.json":
            t = data.get("fa_type")
            results[fname] = expect if t not in ("dfa","tm") else "Error: recognized type"

        elif fname == "unsupported_automata.json":
            t = data.get("fa_type")
            results[fname] = expect if t=="pda" else "Error: not pda"

        else:
            results[fname] = "Unhandled test case"

    return results

def run_qualitative_tests(test_cases):
    for fname in test_cases:
        print(f"\n--- Visual check for {fname} ---")
        with tempconfig({
            "media_dir": os.path.join(os.getcwd(), "media"),
            "preview": True,
        }):
            # you need to actually instantiate the scene
            scene = SceneToShow(fname, "default_config.toml", "a")
            try:
                scene.render()
            except PermissionError:
                # if FFmpeg/pyav still tries to write and fails, just skip it
                print(f"(skipped writing movie for {fname} – preview was shown)")

        input("Press Enter to continue...")


def main_for_file(test_file):
    expect = get_expected_message(test_file)
    print(f"\n=== Quantitative for {test_file} ===")
    qr = run_quantitative_tests({test_file: expect})
    for f, res in qr.items():
        print(f"{f}: {res}")

    if test_file in QUALITATIVE_TESTS:
        print(f"\n=== Qualitative for {test_file} ===")
        run_qualitative_tests([test_file])
    else:
        print(f"\n(skipping qualitative tests for {test_file})")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_for_file(sys.argv[1])
    else:
        for idx, tf in enumerate(ALL_TEST_FILES):
            if idx == 0:
                main_for_file(tf)
            else:
                print(f"\n>>> Simulating next test via subprocess: {tf}")
                subprocess.run([sys.executable, __file__, tf], check=True)
