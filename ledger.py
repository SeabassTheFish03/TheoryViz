from manim import *
import json
import sys
import toml
from manim import tempconfig


class DisplayLedger(VGroup):
    def __init__(self, fa_json, input_string="aab", scale=1.0, spacing=1.2, style_config=None):
        super().__init__()
        self.json = fa_json
        self.input_string = input_string
        self.current_state = self.json["initial_state"]
        self.transitions = self.json["transitions"]
        self.scale_factor = scale
        self.vertical_spacing = spacing * self.scale_factor
        self.steps = []
        self.style_config = style_config or {}

    def create_step(self, current_state, symbol):
        next_state = self.transitions[current_state][symbol]

        # Load visual styles from config
        ledger_cfg = self.style_config.get("ledger", {})
        past_cfg = ledger_cfg.get("past", {})
        symbol_cfg = ledger_cfg.get("symbol", {})
        next_cfg = ledger_cfg.get("next", {})

        arrow_color = ledger_cfg.get("arrow_color", "yellow")

        # Past state styling
        past_font_size = past_cfg.get("font_size", 30)
        past_text_color = past_cfg.get("text_color", "black")
        past_circle_color = past_cfg.get("circle_color", "gray")

        # Symbol styling
        symbol_font_size = symbol_cfg.get("font_size", 30)
        symbol_text_color = symbol_cfg.get("text_color", "white")
        symbol_box_color = symbol_cfg.get("box_color", "yellow")

        # Next state styling
        next_font_size = next_cfg.get("font_size", 30)
        next_text_color = next_cfg.get("text_color", "black")
        next_circle_color = next_cfg.get("circle_color", "white")

        # Normalize scales
        scale_past = past_font_size / 42
        scale_symbol = symbol_font_size / 42
        scale_next = next_font_size / 42

        # Build past state group
        cs_circle = Circle(radius=0.5 * self.scale_factor, color=past_circle_color)
        cs_label = Tex(str(current_state)).scale(scale_past).set_color(past_text_color)
        cs_group = VGroup(cs_circle, cs_label).move_to(LEFT * 3 * self.scale_factor)

        # Build symbol group
        sym_box = Square(side_length=0.7 * self.scale_factor, color=symbol_box_color)
        sym_label = Tex(str(symbol)).scale(scale_symbol).set_color(symbol_text_color)
        sym_group = VGroup(sym_box, sym_label)

        # Build next state group
        ns_circle = Circle(radius=0.5 * self.scale_factor, color=next_circle_color)
        ns_label = Tex(str(next_state)).scale(scale_next).set_color(next_text_color)
        ns_group = VGroup(ns_circle, ns_label).move_to(RIGHT * 3 * self.scale_factor)

        # Arrows
        arrow1 = Arrow(cs_group.get_right(), sym_group.get_left(), buff=0.1 * self.scale_factor, color=arrow_color)
        arrow2 = Arrow(sym_group.get_right(), ns_group.get_left(), buff=0.1 * self.scale_factor, color=arrow_color)

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
        ledger_cfg = config.get("ledger", {})
        self.max_steps = ledger_cfg.get("max_steps", 3)
        self.fade_speed = ledger_cfg.get("fade_speed", 0.75)
        self.step_delay = ledger_cfg.get("speed", 0.75)
        self.scale = ledger_cfg.get("size", 1.0)
        self.spacing = ledger_cfg.get("spacing", 1.2)
        self.style_config = config

        # Background color from [scene]
        scene_cfg = config.get("scene", {})
        self.background_color = scene_cfg.get("background_color", "black")

    def construct(self):
        self.camera.background_color = self.background_color

        ledger = DisplayLedger(
            fa_json=self.fa_json,
            input_string=self.input_string,
            scale=self.scale,
            spacing=self.spacing,
            style_config=self.style_config,
        )

        step_stack = VGroup()
        current_state = ledger.json["initial_state"]

        for symbol in self.input_string:
            step = ledger.create_step(current_state, symbol)
            current_state = ledger.current_state
            step.set_opacity(0)
            step_stack.add(step)
            step_stack.arrange(DOWN, buff=ledger.vertical_spacing)
            step_stack.move_to(ORIGIN)

            if len(step_stack) > self.max_steps:
                old_step = step_stack[0]
                self.play(FadeOut(old_step, shift=UP), run_time=self.fade_speed)
                step_stack.remove(old_step)
                step_stack.arrange(DOWN, buff=ledger.vertical_spacing)
                step_stack.move_to(ORIGIN)

            self.play(FadeIn(step, shift=UP), step.animate.set_opacity(1.0), run_time=self.fade_speed)
            self.wait(self.step_delay)

        step_stack.arrange(DOWN, buff=ledger.vertical_spacing)
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
    except Exception as e:
        print(f"Error reading config file: {e}")
        full_config = {}

    with tempconfig({
        "quality": "low_quality",
        "preview": True,
        "output_file": "RollingLedger.mp4"
    }):
        scene = RollingLedger(fa_filename, input_string, full_config)
        scene.render()
