# Standard Lib
import tomllib
import json
from manim._config import tempconfig

# Manim
from manim.scene.scene import Scene

# TheoryViz
from text_visuals import TuringTape


class TuringTapeTest(Scene):
    def construct(self):
        with open("config_template.toml", "rb") as f:
            config = tomllib.load(f)

        test_tape = TuringTape("abc", "_", config)
        self.add(test_tape.mobj)
        self.play(test_tape.animate_change_highlighted(1))
        self.wait()


if __name__ == "__main__":
    with tempconfig({"quality": "low_quality", "preview": True}):
        scene = TuringTapeTest()
        scene.render()
