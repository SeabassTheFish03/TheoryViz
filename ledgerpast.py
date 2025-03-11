from manim import *
import json

class Displayledger(Table):
    def __init__(self, fa_json, input_string=''):
        self.json = fa_json  # This is now an already loaded JSON object
        self.input_string = input_string

        # Extract column labels (input symbols)
        top_row = [sym for sym in self.json["input_symbols"]]

        # Extract state transition rows
        state_rows = []
        for state in self.json["states"]:
            new_row = [self.json["transitions"][state][sym] for sym in self.json["input_symbols"]]
            state_rows.append(new_row)

        # Convert states & symbols to Tex objects for display
        row_labelsx = [Tex(str(x)) for x in self.json["states"]]
        col_labelsx = [Tex(str(x)) for x in top_row]

        # Construct Manim table
        super().__init__(
            state_rows,
            row_labels=row_labelsx,
            col_labels=col_labelsx,
            include_outer_lines=True
        )

        # Find initial state index for highlighting
        state_index = list(self.json["states"]).index(self.json["initial_state"]) + 2

class testledger(Scene):
    def construct(self):
        # Load the JSON file (No need for command-line arguments)
        fa_filename = "fa_vault/sample_dfa.json"  # Ensure this file exists in your project
        with open(fa_filename, "r") as file:
            fa_json = json.load(file)

        # Create and display the ledger table
        self.table = Displayledger(fa_json)
        self.add(self.table)

        # === Additional Shapes (Skeleton) === #
        state1 = Circle(radius=0.5, color=WHITE)
        state2 = Circle(radius=0.5, color=WHITE)

        # Position states
        state1.shift(LEFT * 3)
        state2.shift(RIGHT * 3)

        # Draw the skeleton states
        self.play(Create(state1), Create(state2))

        self.wait(2)

if __name__ == "__main__":
    with tempconfig({"quality": "low_quality", "preview": True}):
        scene = testledger()
        scene.render()
