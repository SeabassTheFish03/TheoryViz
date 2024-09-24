# Standard Lib
import tomllib
import json

# Manim
from manim.scene.scene import Scene

# TheoryViz
from fa_manager import DFA_Manager


class TestScene(Scene):
    def construct(self):
        with open("config.toml", "rb") as f:
            config = tomllib.load(f)
        with open("sample_fas/sample_dfa.json", "r") as f:
            test_dfa = json.load(f)
        test_automaton = DFA_Manager.from_json(test_dfa, config=config).mobj
        self.add(test_automaton)
