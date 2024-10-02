import sys
import tomllib
import json
from manim._config import tempconfig

from manim.scene.scene import Scene

from fa_manager import DFA_Manager


class SceneToShow(Scene):
    def __init__(self, fa_filename, config_filename):
        super().__init__()

        with open(fa_filename, "rb") as f:
            fa_json = json.load(f)
        with open(config_filename, "rb") as f:
            self.config = tomllib.load(f)

        self.fa = DFA_Manager.from_json(fa_json, config=self.config)

    def construct(self):
        self.camera.background_color = self.config["background_color"]
        self.add(self.fa.mobj)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: py display.py <fa_filename> <config_filename>")
        exit(1)

    with tempconfig({"quality": "high_quality", "preview": True}):
        scene = SceneToShow(sys.argv[1], sys.argv[2])
        scene.render()
