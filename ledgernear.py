from manim import *
import json
import sys
import toml
from manim import tempconfig


class DisplayLedger(VGroup):
    def __init__(self, fa_json, input_string="aab", scale=1.0, spacing=1.2):
        super().__init__()
        self.json = fa_json
        self.input_string = input_string
        self.current_state = self.json["initial_state"]
        self.transitions = self.json["transitions"]
        self.scale_factor = scale
        self.vertical_spacing = spacing * self.scale_factor
        self.steps = []

    def create_step(self, current_state, symbol):
        next_state = self.transitions[current_state][symbol]

        cs_circle = Circle(radius=0.5 * self.scale_factor, color=BLUE)
        cs_label = Tex(str(current_state)).scale(0.7 * self.scale_factor).set_color(BLACK)
        cs_group = VGroup(cs_circle, cs_label).move_to(LEFT * 3 * self.scale_factor)

        sym_box = Square(side_length=0.7 * self.scale_factor, color=YELLOW)
        sym_label = Tex(str(symbol)).scale(0.7 * self.scale_factor).set_color(BLACK)
        sym_group = VGroup(sym_box, sym_label)

        ns_circle = Circle(radius=0.5 * self.scale_factor, color=GREEN)
        ns_label = Tex(str(next_state)).scale(0.7 * self.scale_factor).set_color(BLACK)
        ns_group = VGroup(ns_circle, ns_label).move_to(RIGHT * 3 * self.scale_factor)

        arrow1 = Arrow(cs_group.get_right(), sym_group.get_left(), buff=0.1 * self.scale_factor)
        arrow2 = Arrow(sym_group.get_right(), ns_group.get_left(), buff=0.1 * self.scale_factor)

        step_group = VGroup(cs_group, arrow1, sym_group, arrow2, ns_group)
        step_group.scale(self.scale_factor)

        self.current_state = next_state
        return step_group


class RollingLedger(Scene):
    def __init__(self, fa_filename, input_string, config):
        super().__init__()
        with open(fa_filename, "r") as file:
            self.fa_json = json.load(file)

        self.input_string = input_string
        self.max_steps = config.get("max_steps", 3)
        self.fade_speed = config.get("fade_speed", 0.75)
        self.step_delay = config.get("speed", 0.75)
        self.scale = config.get("size", 1.0)
        self.spacing = config.get("spacing", 1.2)

        self.ledger = DisplayLedger(
            fa_json=self.fa_json,
            input_string=self.input_string,
            scale=self.scale,
            spacing=self.spacing,
        )

    def construct(self):
        step_stack = VGroup()
        current_state = self.ledger.json["initial_state"]

        for symbol in self.input_string:
            step = self.ledger.create_step(current_state, symbol)
            current_state = self.ledger.current_state
            step.set_opacity(0)
            step_stack.add(step)
            step_stack.arrange(DOWN, buff=self.ledger.vertical_spacing)
            step_stack.move_to(ORIGIN)

            if len(step_stack) > self.max_steps:
                old_step = step_stack[0]
                self.play(FadeOut(old_step, shift=UP), run_time=self.fade_speed)
                step_stack.remove(old_step)
                step_stack.arrange(DOWN, buff=self.ledger.vertical_spacing)
                step_stack.move_to(ORIGIN)

            self.play(FadeIn(step, shift=UP), step.animate.set_opacity(1.0), run_time=self.fade_speed)
            self.wait(self.step_delay)

        step_stack.arrange(DOWN, buff=self.ledger.vertical_spacing)
        step_stack.move_to(ORIGIN)
        self.wait(2)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: py ledger.py <fa_filename> <config_file> <input_string>")
        sys.exit(1)

    fa_filename = sys.argv[1]
    config_file = sys.argv[2]
    input_string = sys.argv[3]

    try:
        full_config = toml.load(config_file)
        ledger_config = full_config.get("ledger", {})
    except Exception as e:
        print(f"Error reading config file: {e}")
        ledger_config = {}

    with tempconfig({
        "quality": "low_quality",
        "preview": True,
        "output_file": "RollingLedger.mp4"
    }):
        scene = RollingLedger(fa_filename, input_string, ledger_config)
        scene.render()

