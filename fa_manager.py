# Standard Library
import json
import tomllib
import os
from typing import Callable
from pathlib import Path

# Dependencies
from automata.base.automaton import Automaton, AutomatonStateT
from automata.fa.dfa import DFA, DFAStateT
from automata.tm.dtm import DTM
from automata.tm.configuration import TMConfiguration
from automata.tm.tape import TMTape
from automata.fa.nfa import NFA, NFAStateT

from manim.mobject.types.vectorized_mobject import VDict, VGroup
from manim.animation.composition import Succession, AnimationGroup

from jsonschema import validate

from numpy.typing import NDArray

# Internal
from finite_automaton import FiniteAutomaton
from text_visuals import ProcessText, TuringTape
from transition_table import TransitionTable


dir_path = Path(os.path.dirname(os.path.realpath(__file__)))


class Auto_Manager:
    def __init__(self):
        self.auto: Automaton = None
        self.mobj: VDict = VDict()
        self.input_string: str = None

        self.states: list[AutomatonStateT] = []
        self.symbols: list[str]

        self.current_state: AutomatonStateT = None
        self.char_ptr: int = None

        # Maps the keys for self.mobj to the internal functions which create each component
        self.how_to_show: dict[str, Callable] = {}

    def mobjects(self) -> list[str]:
        return self.mobj.submob_dict.keys()

    def show_mobj(self, key: str):
        self.how_to_show[key]()
        return self

    def move_mobj(self, key: str, location: NDArray):
        self.mobj[key].move_to(location)
        return self

    def shift_mobj(self, key: str, vector: NDArray):
        self.mobj[key].shift(vector)
        return self

    def next_to_mobj(self, moved_key: str, anchor_key: str, direction: NDArray):
        self.mobj[moved_key].next_to(self.mobj[anchor_key], direction)
        return self

    def scale_mobj(self, key: str, size: float):
        self.mobj[key].scale(size)
        return self


class DFA_Manager(Auto_Manager):
    def __init__(
        self,
        config: dict
    ) -> None:
        self.auto: DFA = None
        self.mobj: VDict = VDict({
            "dfa": VGroup(),
            "text": VGroup(),
            "table": VGroup()
        })
        self.input_string: str = ""
        self.config: dict = config

        self.how_to_show: dict[str, Callable] = {
            "dfa": self._show_graph_render,
            "text": self._show_process_text,
            "table": self._show_transition_table
        }
        self.showing: dict[str, bool] = {
            "dfa": False,
            "text": False,
            "table": False
        }

        self.states: list[str] = []
        self.symbols: list[str] = []

        self.current_state: DFAStateT = None
        self.char_ptr: int = None

    def _show_transition_table(self):
        mobj = TransitionTable(
            self.auto,
            self.config["table"],
            highlight_color=self.config["theory"]["current_state_color"],
            starting_symbol=self.input_string[0]
        )

        self.mobj["table"] = mobj
        self.showing["table"] = True

        return self

    def _show_process_text(self):
        if self.input_string == "":
            raise Exception("No input string to construct text around")

        self.mobj["text"] = ProcessText(
            self.input_string,
            visual_config=self.config["text"],
            highlight_color=self.config["theory"]["current_state_color"],
        )

        self.showing["text"] = True
        return self

    def _show_graph_render(self):
        if self.auto is None:
            raise Exception("No automaton available to construct a view of")

        edges_with_options: dict = self._json_to_mobj_edges(self.auto.transitions)

        mobj_options = {
            "vertices": {
                v: {
                    "label": v,
                    "flags": []
                } for v in self.auto.states
            },
            "edges": edges_with_options
        }

        mobj_options["vertices"][self.auto.initial_state]["flags"].extend(["i", "c"])

        for state in self.auto.final_states:
            mobj_options["vertices"][state]["flags"].append("f")

        self.mobj["dfa"] = FiniteAutomaton(
            vertices=self.auto.states,
            edges=self._json_to_mobj_edges(self.auto.transitions),
            visual_config=self.config,
            options=mobj_options
        )

        self.showing["dfa"] = True

        return self

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

        # Config stuff
        default_config_path = dir_path / "default_config.toml"
        with default_config_path.open("rb") as f:
            default_config = tomllib.load(f)

        config = {**default_config, **config}
        auto = DFA(
            states=set(json_object["states"]),
            input_symbols=json_object["input_symbols"],
            transitions=json_object["transitions"],
            initial_state=json_object["initial_state"],
            final_states=set(json_object["final_states"]),
            allow_partial=allow_partial
        )

        out = cls(config)
        out.add_automaton(auto)

        if len(input_string) > 0:
            out.add_input(input_string)

        return out

    def mobjects(self) -> list:
        """
        A getter method which provides the different mobjects the user may interact with
        """
        return self.mobj.keys()

    def add_automaton(self, auto: DFA):
        self.auto = auto

        self.states = list(auto.states)
        self.symbols = list(auto.input_symbols)

        self.states.sort()
        self.symbols.sort()

        self.current_state = self.auto.initial_state
        self.char_ptr = 0
        return self

    def add_input(self, input_str: str) -> None:
        self.input_string = input_str

    @classmethod
    def validate_json(cls, json_object: dict) -> None:
        """
        Ensures the json fed to the from_json() function conforms to all the
        requirements of a DFA

        On success, returns None. On failure, throws.
        """
        # Validate json format using jsonschema library
        schema_file = dir_path / "schema" / "dfa.schema.json"
        with schema_file.open("rb") as f:
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
        if len(self.input_string) == 0:
            raise Exception("Can't animate without more than one character")
        else:
            for i, next_char in enumerate(self.input_string):
                next_state = self.auto._get_next_current_state(self.current_state, next_char)

                if len(self.input_string) - i > 1:
                    next_next_char = self.input_string[i + 1]
                else:
                    next_next_char = "?"

                animation_queue = []
                if self.showing["text"]:
                    animation_queue.append(self.mobj["text"].RemoveOneCharacter())
                if self.showing["dfa"]:
                    animation_queue.append(self.mobj["dfa"].transition_animation(self.current_state, next_state))
                if self.showing["table"]:
                    animation_queue.append(self.mobj["table"].animate.move_follower(next_state, next_next_char))

                sequence.append(AnimationGroup(*animation_queue))

                if self.showing["dfa"]:
                    self.mobj["dfa"].remove_flag(self.current_state, "c")
                    self.mobj["dfa"].add_flag(next_state, "c")
                if self.showing["text"]:
                    self.mobj["text"].increment_letter()

                self.current_state = next_state

        return Succession(*sequence)


class NFA_Manager(DFA_Manager):
    #TODO change validation criteria
    def __init__(
        self,
        config: dict
    ) -> None:
        self.auto: NFA = None
        self.mobj: VDict = VDict({
            "nfa": VGroup(),
            "text": VGroup(),
            "table": VGroup()
        })
        self.input_string: str = ""
        self.config: dict = config

        self.how_to_show: dict[str, Callable] = {
            "nfa": self._show_graph_render,
            "text": self._show_process_text,
            "table": self._show_transition_table
        }
        self.showing: dict[str, bool] = {
            "nfa": False,
            "text": False,
            "table": False
        }

        self.states: list[str] = []
        self.symbols: list[str] = []

        self.current_state:NFAStateT = None
        self.char_ptr: int = None


    @classmethod
    def validate_json(cls, json_object: dict) -> None:
        """
        Ensures the json fed to the from_json() function conforms to all the
        requirements of a NFA

        On success, returns None. On failure, throws.
        """
        # Validate json format using jsonschema library
        schema_file = dir_path / "schema" / "nfa.schema.json"
        with schema_file.open("rb") as f:
            schema = json.load(f)
        validate(
            instance=json_object,
            schema=schema
        )

        # Validate the transitions - not being unique???
        allow_partial = json_object.get("allow_partial", True) #changed from DFA
        for state in json_object["states"]:
            if state not in json_object["transitions"]:
                raise AttributeError(f"State {state} not listed in transition table")
            for symbol in json_object["input_symbols"]:
                if (symbol not in json_object["transitions"][state]) and (not allow_partial):
                    raise AttributeError(f"Transition using \"{symbol}\" missing from state {state}")
                if (end := json_object["transitions"][state][symbol]) not in json_object["states"]:
                    raise AttributeError(f"Destination {end} not in states list")


class PDA_Manager(Auto_Manager):
    pass


class TM_Manager(Auto_Manager):
    def __init__(
        self,
        config: dict = dict(),
        max_iter: int = 100
    ):
        self.auto: DTM = None

        self.mobj = VDict({
            "tm": VGroup(),
            "tape": VGroup(),
            "table": VGroup()
        })

        self.how_to_show: dict[str, Callable] = {
            "tm": self._show_graph_render,
            "tape": self._show_tape,
            "table": self._show_transition_table
        }
        self.showing: dict[str, bool] = {
            "tm": False,
            "tape": False,
            "table": False
        }

        self.states = []
        self.input_symbols = []
        self.tape_symbols = []
        self.tape: TMTape = None

        self.max_iter = max_iter
        self.blank_symbol = ""

        self.config = config
        self.tm_config = None

    def add_automaton(self, auto: DTM):
        self.auto = auto

        self.states = list(auto.states)
        self.input_symbols = list(auto.input_symbols)
        self.tape_symbols = list(auto.tape_symbols)

        self.states.sort()
        self.input_symbols.sort()
        self.tape_symbols.sort()

        self.blank_symbol = auto.blank_symbol

        return self

    # Overrides method from Auto_Manager
    def add_input(self, input_string: str):
        if self.auto is None:
            raise Exception("Can't add an input string without an automaton")

        self.tape = TMTape(list(input_string), self.blank_symbol)
        self.tm_config = TMConfiguration(self.auto.initial_state, self.tape)

        return self

    def _show_graph_render(self):
        edges_with_options = self._json_to_mobj_edges(self.auto.transitions)

        mobj_options = {
            "vertices": {
                v: {
                    "label": v,
                    "flags": []
                } for v in self.states
            },
            "edges": edges_with_options
        }

        mobj_options["vertices"][self.auto.initial_state]["flags"].append("i")
        mobj_options["vertices"][self.auto.initial_state]["flags"].append("c")

        for state in self.auto.final_states:
            mobj_options["vertices"][state]["flags"].append("f")

        self.mobj["tm"] = FiniteAutomaton(
            vertices=self.auto.states,
            edges=edges_with_options.keys(),
            visual_config=self.config,
            options=mobj_options
        )
        self.showing["tm"] = True

        return self

    def _show_tape(self):
        if self.tape is None:
            raise Exception("Can't render a nonexistent tape")

        self.mobj["tape"] = TuringTape(self.tape, self.config["text"], highlight_color=self.config["theory"]["current_state_color"])
        self.showing["tape"] = True

        return self

    def _show_transition_table(self):
        mobj = TransitionTable(
            self.auto,
            self.config["table"],
            highlight_color=self.config["theory"]["current_state_color"],
            starting_symbol=self.input_string[0]
        )

        self.mobj["table"] = mobj
        self.showing["table"] = True

        return self

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

        out = cls(config=config, max_iter=50)

        auto = DTM(
            states=set(json_object["states"]),
            tape_symbols=set(json_object["tape_symbols"]),
            input_symbols=set(json_object["input_symbols"]),
            transitions=json_object["transitions"],
            initial_state=json_object["initial_state"],
            blank_symbol=json_object["blank_symbol"],
            final_states=set(json_object["final_states"]),
        )
        out.add_automaton(auto)

        if len(input_string) > 0:
            out.add_input_string(input_string)

        return out

    @classmethod
    def validate_json(cls, json_object: dict) -> None:
        """
        Ensures the json fed to the from_json() function conforms to all the
        requirements of a DFA

        On success, returns None. On failure, throws.
        """
        # Validate json format using jsonschema library
        schema_file = dir_path / "schema" / "tm.schema.json"
        with schema_file.open("rb") as f:
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
                raise AttributeError(f"Bad initial state {json_object['initial_state']}")
            if json_object["blank_symbol"] not in json_object["tape_symbols"]:
                raise AttributeError(f"Bad blank symbol {json_object['blank_symbol']}")
            for final in json_object["final_states"]:
                if final not in json_object["states"]:
                    raise AttributeError(f"Final state {final} not found")

    def animate(self) -> Succession:
        sequence = []
        iters = 0

        generator = self.auto.read_input_stepwise(list(self.tape.tape))
        generator.__next__()  # Gets rid of initial state

        for tm_config in generator:
            if iters > self.max_iter:
                print("Maximum iterations reached")
                break

            next_state = str(tm_config.state)
            transition = self.auto._get_transition(self.tm_config.state, self.tm_config.tape.read_symbol())

            animation_queue = []
            if self.showing["tape"]:
                animation_queue.append(self.mobj["tape"].animate_update(transition))
            if self.showing["tm"]:
                animation_queue.append(self.mobj["tm"].transition_animation(str(self.tm_config.state), next_state))

            sequence.append(AnimationGroup(*animation_queue))

            self.tm_config = tm_config

            iters += 1

        return Succession(*sequence)
