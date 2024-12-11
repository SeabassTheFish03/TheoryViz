# Standard Lib
import tomllib
from manim._config import tempconfig

# Manim
from manim.scene.scene import Scene
from manim.animation.fading import FadeIn

# TheoryViz
from fa_manager import DFA_Manager
from text_visuals import TuringTape


class TMTapeTest(Scene):
    def construct(self):
        with open("config_template.toml", "rb") as f:
            config = tomllib.load(f)

        test_tape = TuringTape("abc", "_", config)

        self.play(FadeIn(test_tape))
        self.play(test_tape.animate_update("right"))


if __name__ == "__main__":
    with tempconfig({"quality": "low_quality", "preview": True}):
        scene = TMTapeTest()
        scene.render()
