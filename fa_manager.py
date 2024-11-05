from automata.fa.dfa import DFA

import numpy as np

from manim.mobject.types.vectorized_mobject import VDict
from manim.animation.composition import Succession, AnimationGroup

from finite_automaton import FiniteAutomaton, ProcessText


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
            "text": ProcessText(input_string),
            "shadow": ProcessText(input_string, color=0x333333)
        })

        self.mobj["dfa"].move_to([0, 0, 0])
        self.mobj["text"].next_to(self.mobj["dfa"], np.array([0, 1, 0]))
        self.mobj["shadow"].next_to(self.mobj["text"], np.array([0, 0, -1]))

        self.mobj["text"][0].set_color("yellow")  # TODO: Make configurable

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
        if not isinstance(json_object, dict):
            raise TypeError(f"json_object must be dict, not {type(json_object)}")
        if not isinstance(input_string, str):
            raise TypeError(f"input_string must be str, not {type(input_string)}")
        if not isinstance(config, dict):
            raise TypeError(f"config must be a dict, not {type(config)}")

        if "type" not in json_object:
            raise Exception("Type not specified in json_object. Must be dfa")
        if json_object["type"].lower() != "dfa":
            raise Exception(f"Specified type in json must be dfa, not {json_object[type]}")

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
    pass
