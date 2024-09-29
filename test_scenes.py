# Standard Lib
import tomllib
import json
from manim._config import tempconfig

# Manim
from manim.scene.scene import Scene

# TheoryViz
from fa_manager import DFA_Manager


class TestScene(Scene):
    def construct(self):
        with open("config.toml", "rb") as f:
            config = tomllib.load(f)
        with open("fa_vault/sample_dfa.json", "rb") as f:
            test_dfa = json.load(f)
        test_automaton = DFA_Manager.from_json(test_dfa, config=config).mobj
        self.add(test_automaton)


if __name__ == "__main__":
    with tempconfig({"quality": "low_quality", "preview": True}):
        scene = TestScene()
        scene.render()
