from manim.mobject.table import Table
from manim.mobject.text.tex_mobject import MathTex


class TransitionTable(Table):
    def __init__(self, automaton, visual_config, highlight_color="yellow", starting_symbol=""):
        """
        Given an automaton of type DFA or TM, constructs a mobject displaying the transition table of that automaton. Also provides helpful methods for animation.
        """
        self.config = visual_config

        self.symbols = list(automaton.input_symbols)
        self.states = list(automaton.states)

        self.symbols.sort()
        self.states.sort()

        rows = []

        for state in self.states:
            new_row = []
            for sym in self.symbols:
                new_row.append(automaton.transitions[state][sym])

            rows.append(new_row)

        super().__init__(
            rows,
            row_labels=[MathTex(state, color=self.config["border_color"]) for state in self.states],
            col_labels=[MathTex(symbol, color=self.config["border_color"]) for symbol in self.symbols],
            include_outer_lines=True,
            line_config={
                "color": self.config["border_color"]
            },
            element_to_mobject_config={
                "color": self.config["border_color"]
            }
        )

        if starting_symbol == "":
            start_index = (1, 1)
        else:
            start_index = self.get_index(automaton.initial_state, starting_symbol)

        for state in automaton.final_states:
            for i, cell in enumerate([row[0] for row in rows]):
                if cell == state:
                    final_state_box = self.get_cell((i + 2, 1)).copy().scale(0.9).set_color("white")
                    self.add(final_state_box)

        self.follower = self.get_cell(start_index).copy().set_color(highlight_color)
        self.add(self.follower)

    def get_index(self, state, symbol):
        return (self.states.index(state) + 2, self.symbols.index(symbol) + 2)

    def move_follower(self, next_row, next_col):
        self.follower.move_to(self.get_cell(self.get_index(next_row, next_col)))
