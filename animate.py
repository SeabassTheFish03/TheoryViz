import sys
import tomllib
import json
from manim._config import tempconfig

from manim.scene.scene import Scene
from manim.animation.creation import Create
from manim.constants import UP, RIGHT

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
            self.fa.show_mobj("dfa")
            self.fa.show_mobj("text")
            self.fa.show_mobj("table")
            self.fa.move_mobj("table", [-2, 0, 0])
            self.fa.next_to_mobj("dfa", "table", RIGHT)
            self.fa.scale_mobj("dfa", 0.7)
            self.fa.next_to_mobj("text", "dfa", UP)
        elif fa_json["fa_type"] == "tm":
            self.fa = TM_Manager.from_json(fa_json, config=self.config, input_string=input_string)
            self.fa.show_graph_render()
            self.fa.show_tape()

            self.fa.scale_mobject("tm", 0.7)
            self.fa.next_to_mobject("tape", "tm", UP)

    def construct(self):
        self.camera.background_color = self.config["scene"]["background_color"]
        self.play(Create(self.fa.mobj))
        self.play(self.fa.animate())
        self.wait(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: py animate.py <fa_filename> <config_filename> <input_string>")
        exit(1)

    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = SceneToShow(sys.argv[1], sys.argv[2], sys.argv[3])
        scene.render()
