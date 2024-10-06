from automata.fa.dfa import DFA

from finite_automaton import FiniteAutomaton


class DFA_Manager:
    def __init__(
        self,
        auto: DFA,
        mobj: FiniteAutomaton,
        config: dict = dict(),
        input_string: str = ""
    ) -> None:
        self.auto = auto
        self.mobj = mobj

        self.current_state = self.auto.initial_state
        self.input_string = input_string

        # A little aliasing
        self.dfa = self.auto

    @classmethod
    def _json_to_mobj_edges(cls, transitions: dict) -> dict:
        edges = dict()

        for start, symbols in transitions.items():
            for symbol, end in symbols.items():
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


class NFA_Manager:
    pass


class PDA_Manager:
    pass


class TM_Manager:
    pass
