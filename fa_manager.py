# Standard Library
import json

# Dependencies
from automata.fa.dfa import DFA
from automata.tm.dtm import DTM

from manim.mobject.types.vectorized_mobject import VDict
from manim.animation.composition import Succession, AnimationGroup
from manim.constants import UP

from jsonschema import validate

# Internal
from finite_automaton import FiniteAutomaton
from text_visuals import ProcessText, TuringTape


class DFA_Manager:
    def __init__(
        self,
        auto: DFA,
        mobj: FiniteAutomaton,
        config: dict = dict(),
        input_string: str = ""
    ) -> None:
        self.auto: DFA = auto
        self.mobj: VDict = VDict({
            "dfa": mobj,
            "text": ProcessText(input_string, text_color=config["vertex_color"], highlight_color=config["current_state_color"], shadow_color=config["text_shadow_color"]),
        })

        self.mobj["dfa"].move_to([0, 0, 0])
        self.mobj["text"].next_to(self.mobj["dfa"], UP)

        self.current_state = self.auto.initial_state
        self.input_string = input_string

        # A little aliasing
        self.dfa = self.auto

    @classmethod
    def _json_to_mobj_edges(cls, transitions: dict) -> dict:
        edges = dict()

        for start, symbols in transitions.items():
            for symbol, end in symbols.items():
                if (start, end) in edges:
                    # An edge already exists, but with a different symbol
                    edges[(start, end)]["label"] += f", {symbol}"
                else:
                    edges[(start, end)] = {"label": symbol}

        return edges

    @classmethod
    def from_json(cls, json_object: dict, config: dict = dict(), input_string: str = ""):
        # Throws on failure
        cls.validate_json(json_object)

        allow_partial = json_object.get("allow_partial", False)

        auto = DFA(
            states=set(json_object["states"]),
            input_symbols=json_object["input_symbols"],
            transitions=json_object["transitions"],
            initial_state=json_object["initial_state"],
            final_states=set(json_object["final_states"]),
            allow_partial=allow_partial
        )

        edges_with_options = cls._json_to_mobj_edges(json_object["transitions"])

        mobj_options = {
            "vertices": {
                v: {
                    "label": v,
                    "flags": []
                } for v in json_object["states"]
            },
            "edges": edges_with_options
        }

        mobj_options["vertices"][json_object["initial_state"]]["flags"].append("i")
        mobj_options["vertices"][json_object["initial_state"]]["flags"].append("c")

        for state in json_object["final_states"]:
            mobj_options["vertices"][state]["flags"].append("f")

        mobj = FiniteAutomaton(
            vertices=json_object["states"],
            edges=edges_with_options.keys(),
            visual_config=config,
            options=mobj_options
        )

        return cls(auto, mobj, config, input_string)

    @classmethod
    def validate_json(cls, json_object: dict) -> None:
        """
        Ensures the json fed to the from_json() function conforms to all the
        requirements of a DFA

        On success, returns None. On failure, throws.
        """
        # Validate json format using jsonschema library
        with open("./schema/dfa.schema.json", "rb") as f:
            schema = json.load(f)
        validate(
            instance=json_object,
            schema=schema
        )

        # Validate the transitions
        allow_partial = json_object.get("allow_partial", False)
        for state in json_object["states"]:
            if state not in json_object["transitions"]:
                raise AttributeError(f"State {state} not listed in transition table")
            for symbol in json_object["input_symbols"]:
                if (symbol not in json_object["transitions"][state]) and (not allow_partial):
                    raise AttributeError(f"Transition using \"{symbol}\" missing from state {state}")
                if (end := json_object["transitions"][state][symbol]) not in json_object["states"]:
                    raise AttributeError(f"Destination {end} not in states list")

    def animate(self) -> Succession:
        sequence = []
        for _ in self.input_string:
            next_state = self.dfa._get_next_current_state(self.current_state, self.mobj["text"].peek_next_letter())
            sequence.append(
                AnimationGroup(
                    self.mobj["text"].RemoveOneCharacter(),
                    self.mobj["dfa"].transition_animation(self.current_state, next_state)
                )
            )
            self.mobj["dfa"].remove_flag(self.current_state, "c")
            self.mobj["text"].increment_letter()
            self.mobj["dfa"].add_flag(next_state, "c")

            self.current_state = next_state

        return Succession(*sequence)


class NFA_Manager:
    pass


class PDA_Manager:
    pass


class TM_Manager:
    def __init__(
        self,
        auto: DTM,
        mobj: FiniteAutomaton,
        config: dict = dict(),
        initial_tape: str = ""
    ):
        self.auto: DTM = auto
        self.mobj = VDict({
            "tm": mobj,
            "text": TuringTape(initial_tape, "_", config)
        })

        self.mobj["tm"].move_to([0, 0, 0])
        self.mobj["text"].next_to(self.mobj["tm"], UP)

        self.current_state = self.auto.initial_state
        self.initial_tape = initial_tape

        # A little aliasing
        self.dfa = self.auto
