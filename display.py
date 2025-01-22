import sys
import tomllib
import json
from manim._config import tempconfig

from manim.scene.scene import Scene

from fa_manager import DFA_Manager, TM_Manager


class SceneToShow(Scene):
    def __init__(self, fa_filename, config_filename, in_string):
        super().__init__()

        with open(fa_filename, "rb") as f:
            fa_json = json.load(f)
        with open(config_filename, "rb") as f:
            self.config = tomllib.load(f)

        if fa_json["fa_type"] == "dfa":
            self.fa = DFA_Manager.from_json(fa_json, config=self.config, input_string=in_string)
        elif fa_json["fa_type"] == "tm":
            self.fa = TM_Manager.from_json(fa_json, config=self.config, input_string=in_string)

    def construct(self):
        self.camera.background_color = self.config["background_color"]
        self.add(self.fa.mobj)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: py display.py <fa_filename> <config_filename> <input_string>")
        exit(1)

    with tempconfig({"quality": "high_quality", "preview": True}):
        scene = SceneToShow(sys.argv[1], sys.argv[2], sys.argv[3])
        scene.render()
