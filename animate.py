import sys
import tomllib
import json
from manim._config import tempconfig

from manim.scene.scene import Scene
from manim.animation.creation import Create

from fa_manager import DFA_Manager, TM_Manager


class SceneToShow(Scene):
    def __init__(self, fa_filename, config_filename, input_string):
        super().__init__()

        with open(fa_filename, "rb") as f:
            fa_json = json.load(f)
        with open(config_filename, "rb") as f:
            self.config = tomllib.load(f)

        # Triage
        if fa_json["fa_type"] == "dfa":
            self.fa = DFA_Manager.from_json(fa_json, config=self.config, input_string=input_string)
        elif fa_json["fa_type"] == "tm":
            self.fa = TM_Manager.from_json(fa_json, config=self.config, input_string=input_string)

    def construct(self):
        self.camera.background_color = self.config["scene"]["background_color"]
        self.play(Create(self.fa.mobj))
        self.play(self.fa.animate())


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: py animate.py <fa_filename> <config_filename> <input_string>")
        exit(1)

    with tempconfig({"quality": "low_quality", "preview": True}):
        scene = SceneToShow(sys.argv[1], sys.argv[2], sys.argv[3])
        scene.render()
