from manim import *
import json
import sys
import toml
from manim import tempconfig


class DisplayLedger(VGroup):
    def __init__(self, fa_json, input_string="aab"):
        super().__init__()
        self.json = fa_json
        self.input_string = input_string
        self.current_state = self.json["initial_state"]
        self.transitions = self.json["transitions"]
        self.y_offset = 3

        for symbol in self.input_string:
            step_group, next_state = self.create_step(self.current_state, symbol, self.y_offset)
            self.add(step_group)
            self.current_state = next_state
            self.y_offset -= 1

    def create_step(self, current_state, symbol, y_offset):
        next_state = self.transitions[current_state][symbol]

        cs_circle = Circle(radius=0.5, color=BLUE)
        cs_label = Tex(str(current_state)).scale(0.7).set_color(BLACK)
        cs_group = VGroup(cs_circle, cs_label).move_to(LEFT * 3 + UP * y_offset)

        sym_box = Square(side_length=0.7, color=YELLOW)
        sym_label = Tex(str(symbol)).scale(0.7).set_color(BLACK)
        sym_group = VGroup(sym_box, sym_label).move_to(UP * y_offset)

        ns_circle = Circle(radius=0.5, color=GREEN)
        ns_label = Tex(str(next_state)).scale(0.7).set_color(BLACK)
        ns_group = VGroup(ns_circle, ns_label).move_to(RIGHT * 3 + UP * y_offset)

        arrow1 = Arrow(cs_group.get_right(), sym_group.get_left(), buff=0.1)
        arrow2 = Arrow(sym_group.get_right(), ns_group.get_left(), buff=0.1)

        return VGroup(cs_group, arrow1, sym_group, arrow2, ns_group), next_state


class LedgerScene(Scene):
    def __init__(self, fa_filename, input_string, fade_speed=0.75):
        super().__init__()
        with open(fa_filename, "r") as file:
            fa_json = json.load(file)
        self.ledger = DisplayLedger(fa_json, input_string)
        self.fade_speed = fade_speed

    def construct(self):
        for row in self.ledger.submobjects:
            row.set_opacity(0)
            self.play(FadeIn(row), row.animate.set_opacity(1.0), run_time=self.fade_speed)
            self.wait(self.fade_speed)
        self.wait(2)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: py ledger.py <fa_filename> <default_config> <ledger_config> <input_string>")
        sys.exit(1)

    fa_filename = sys.argv[1]
    default_config = sys.argv[2]  # not used right now, but reserved
    ledger_config_file = sys.argv[3]
    input_string = sys.argv[4]

    # Load ledger config to get fade speed
    try:
        ledger_config = toml.load(ledger_config_file).get("ledger", {})
    except Exception as e:
        print(f"Error reading ledger_config.toml: {e}")
        sys.exit(1)

    fade_speed = ledger_config.get("fade_speed", 0.75)

    with tempconfig({
        "quality": "low_quality",
        "preview": True,
        "output_file": "ledger_output.mp4"
    }):
        scene = LedgerScene(fa_filename, input_string, fade_speed)
        scene.render()
