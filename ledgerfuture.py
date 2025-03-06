from manim import *
import json
from manim import tempconfig
import sys

class Displayledger(VGroup):
    def __init__(self, fa_json, input_string=''):
        super().__init__()
        self.json = fa_json
        self.input_string = input_string if input_string else "aab"
        self.current_state = self.json["initial_state"]
        self.transitions = self.json["transitions"]

        # First row near the top
        self.y_offset = 3

        for symbol in self.input_string:
            step_group, next_state = self.hre(self.current_state, symbol, self.y_offset)
            self.add(step_group)
            self.current_state = next_state
            # Move each subsequent row down by 1
            self.y_offset -= 1

    def hre(self, current_state, symbol, y_offset):
        next_state = self.transitions[current_state][symbol]

        cs_circle = Circle(radius=0.5, color=BLUE)
        cs_label = Tex(str(current_state)).scale(0.7)
        cs_group = VGroup(cs_circle, cs_label).move_to(LEFT * 3 + UP * y_offset)

        sym_box = Square(side_length=0.7, color=YELLOW)
        sym_label = Tex(str(symbol)).scale(0.7)
        sym_group = VGroup(sym_box, sym_label).move_to(UP * y_offset)

        ns_circle = Circle(radius=0.5, color=GREEN)
        ns_label = Tex(str(next_state)).scale(0.7)
        ns_group = VGroup(ns_circle, ns_label).move_to(RIGHT * 3 + UP * y_offset)

        arrow1 = Arrow(start=cs_group.get_right(), end=sym_group.get_left(), buff=0.1)
        arrow2 = Arrow(start=sym_group.get_right(), end=ns_group.get_left(), buff=0.1)

        step_group = VGroup(cs_group, arrow1, sym_group, arrow2, ns_group)
        return step_group, next_state

class testledger(Scene):
    def __init__(self, fa_filename, input_string=''):
        super().__init__()
        with open(fa_filename, "r") as file:
            fa_json = json.load(file)
        self.ledger = Displayledger(fa_json, input_string)

    def construct(self):
        for row in self.ledger.submobjects:
            self.play(Create(row))
            self.wait(0.5)
        self.wait(2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: py ledgerpresent.py <fa_filename> <config_filename> <input_string>")
        exit(1)

    with tempconfig({"quality": "low_quality", "preview": True}):
        scene = testledger(sys.argv[1], sys.argv[3])
        scene.render()
