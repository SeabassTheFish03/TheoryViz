from manim import *
import json
from manim import tempconfig
import sys

#next step make it so the state's are accurate. 

class Displayledger(VGroup):
    def __init__(self, fa_json, input_string=''):
        # Initialize as a VGroup
        super().__init__()
        self.json = fa_json  # Already loaded JSON object
        # Use the provided input string or default to "aab"
        self.input_string = input_string if input_string else "aab"

        # Get initial state and transitions from the JSON
        current_state = self.json["initial_state"]
        transitions = self.json["transitions"]

        y_offset = 0  # To stack ledger steps vertically

        # Process each symbol in the input string
        for symbol in self.input_string:
            next_state = transitions[current_state][symbol]

            # --- Create the current state representation ---
            cs_circle = Circle(radius=0.5, color=BLUE)
            cs_label = Tex(str(current_state)).scale(0.7)
            cs_group = VGroup(cs_circle, cs_label)
            cs_group.move_to(LEFT * 3 + DOWN * y_offset)

            # --- Create the input symbol representation ---
            sym_box = Square(side_length=0.7, color=YELLOW)
            sym_label = Tex(str(symbol)).scale(0.7)
            sym_group = VGroup(sym_box, sym_label)
            sym_group.move_to(DOWN * y_offset)

            # --- Create the next state representation ---
            ns_circle = Circle(radius=0.5, color=GREEN)
            ns_label = Tex(str(next_state)).scale(0.7)
            ns_group = VGroup(ns_circle, ns_label)
            ns_group.move_to(RIGHT * 3 + DOWN * y_offset)

            # --- Create arrows connecting the elements ---
            arrow1 = Arrow(start=cs_group.get_right(), end=sym_group.get_left(), buff=0.1)
            arrow2 = Arrow(start=sym_group.get_right(), end=ns_group.get_left(), buff=0.1)

            # Group this entire ledger step
            step_group = VGroup(cs_group, arrow1, sym_group, arrow2, ns_group)
            self.add(step_group)

            # Update current state and vertical offset for the next step
            current_state = next_state
            y_offset -= 2

    # create a new function hre that takes in current_state and next_symbol
    # create a row based on this current state and next symbol
    #first circle has the current state in it
    #label has next symbol in it
    #second circle - next state

class testledger(Scene):
    def __init__(self, fa_filename, input_string=''):
        super().__init__()
        # load as file not name
        with open(fa_filename, "r") as file:
            fa_json = json.load(file)

        self.ledger = Displayledger(fa_json, input_string)

    def construct(self):
        # Load the DFA JSON file (ensure this file exists in your project)
        # fa_filename = "fa_vault/sample_dfa.json"
        

        # Animate the ledger's creation
        self.play(Create(self.ledger))
        self.wait(2)

if __name__ == "__main__":
    if (len(sys.argv) != 4):
        print("Usage: py ledgerpresent.py <fa_filename> <config_filename> <input_string>")
        exit(1)

    with tempconfig({"quality": "low_quality", "preview": True}):
        scene = testledger(sys.argv[1], sys.argv[3])
        scene.render()
