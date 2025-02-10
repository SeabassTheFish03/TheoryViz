# Standard Library
import json

# Dependencies
from automata.fa.dfa import DFA
from automata.tm.dtm import DTM
from automata.tm.configuration import TMConfiguration
from automata.tm.tape import TMTape

from manim.mobject.types.vectorized_mobject import VDict
from manim.animation.composition import Succession, AnimationGroup
from manim.constants import UP
from manim.constants import RIGHT

from jsonschema import validate

# Internal
from finite_automaton import FiniteAutomaton
from text_visuals import ProcessText, TuringTape
# from transition_table_mobject import DisplayTransitionTable
from transition_table_mobject import AnimateTransitionTable


class DFA_Manager:
    def __init__(
        self,
        auto: DFA,
        mobj: FiniteAutomaton,
        config: dict = dict(),
        input_string: str = "",
        json_object: dict = dict(),
    ) -> None:
        self.auto: DFA = auto
        self.mobj: VDict = VDict({
            "dfa": mobj,
            "text": ProcessText(
                input_string,
                text_color=config["text"]["color"],
                highlight_color=config["theory"]["current_state_color"],
                shadow_color=config["text"]["shadow_color"]
            ),
            "transition_table": AnimateTransitionTable(json_object, input_string)
        })

        self.mobj["dfa"].move_to([-4, 0, 0])
        self.mobj["text"].next_to(self.mobj["dfa"], UP)
        self.mobj["transition_table"].next_to(self.mobj["dfa"], RIGHT)

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

        return cls(auto, mobj, config, input_string, json_object)

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
                    self.mobj["dfa"].transition_animation(self.current_state, next_state),
                    self.mobj["transition_table"].MoveToNextTransition()
                    #   play(self.table.MoveToNextTransition())
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
        initial_tape: str = "",
        max_iter: int = 100,
        blank_symbol: str = "."
    ):
        self.auto: DTM = auto

        self.mobj = VDict()
        self.mobj["tm"] = mobj
        self.mobj["text"] = TuringTape(initial_tape, "_", config)

        self.mobj["tm"].move_to([0, 0, 0])
        self.mobj["text"].next_to(self.mobj["tm"], 0.5 * UP).scale(0.5)

        self.current_state = self.auto.initial_state
        self.initial_tape = initial_tape
        self.max_iter = max_iter
        self.blank_symbol = blank_symbol

        # A little aliasing
        self.tm = self.auto

    @classmethod
    def _json_to_mobj_edges(cls, transitions: dict) -> dict:
        edges = dict()

        for start, symbols in transitions.items():
            for symbol, action in symbols.items():
                end = action[0]
                write = action[1]
                move = action[2]

                label = f"{symbol} \\to {write},\\ {move}"  # MathTeX format
                if (start, end) in edges:
                    # An edge already exists, but with a different symbol
                    edges[(start, end)]["label"] += f"\\\\{label}"
                else:
                    edges[(start, end)] = {"label": label}

        return edges

    @classmethod
    def from_json(cls, json_object: dict, config: dict = dict(), input_string: str = ""):
        # Throws on failure
        cls.validate_json(json_object)

        auto = DTM(
            states=set(json_object["states"]),
            tape_symbols=set(json_object["tape_symbols"]),
            input_symbols=set(json_object["input_symbols"]),
            transitions=json_object["transitions"],
            initial_state=json_object["initial_state"],
            blank_symbol=json_object["blank_symbol"],
            final_states=set(json_object["final_states"]),
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
        print(mobj)

        return cls(auto, mobj, config, input_string, blank_symbol=json_object["blank_symbol"])

    @classmethod
    def validate_json(cls, json_object: dict) -> None:
        """
        Ensures the json fed to the from_json() function conforms to all the
        requirements of a DFA

        On success, returns None. On failure, throws.
        """
        # Validate json format using jsonschema library
        with open("./schema/tm.schema.json", "rb") as f:
            schema = json.load(f)
        validate(
            instance=json_object,
            schema=schema
        )

        # Validate the transitions
        for start, info in json_object["transitions"].items():
            if start not in json_object["states"]:
                raise AttributeError(f"State {start} not valid")
            for symbol, changes in info.items():
                if symbol not in json_object["tape_symbols"]:
                    raise AttributeError(f"Symbol {symbol} not valid")
                if len(changes) != 3:
                    raise ValueError(f"Malformed change listing {changes}")

                if changes[0] not in json_object["states"]:
                    raise AttributeError(f"Destination {changes[0]} not found")
                if changes[1] not in json_object["tape_symbols"]:
                    raise AttributeError(f"Write symbol {changes[1]} not valid")
                if changes[2] not in ["R", "L"]:
                    raise ValueError(f"Direction {changes[2]} not R or L")

            if json_object["initial_state"] not in json_object["states"]:
                raise AttributeError(f"Bad initial state {json_object["initial_state"]}")
            if json_object["blank_symbol"] not in json_object["tape_symbols"]:
                raise AttributeError(f"Bad blank symbol {json_object["blank_symbol"]}")
            for final in json_object["final_states"]:
                if final not in json_object["states"]:
                    raise AttributeError(f"Final state {final} not found")

    def animate(self) -> Succession:
        sequence = []
        iters = 0
        last_config = TMConfiguration(self.tm.initial_state, TMTape(self.initial_tape, blank_symbol=self.blank_symbol))

        generator = self.tm.read_input_stepwise(self.initial_tape)
        generator.__next__()  # Gets rid of initial state

        for tm_config in generator:
            if iters > self.max_iter:
                print("Maximum iterations reached")
                break

            next_state = str(tm_config.state)
            transition = self.tm._get_transition(last_config.state, last_config.tape.read_symbol())

            sequence.append(
                AnimationGroup(
                    self.mobj["text"].animate_update(transition),
                    self.mobj["tm"].transition_animation(
                        self.current_state,
                        next_state
                    )
                )
            )

            self.current_state = next_state

            last_config = tm_config
            iters += 1

        return Succession(*sequence)
