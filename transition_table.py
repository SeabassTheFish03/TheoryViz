from manim.mobject.table import Table
from manim.mobject.text.tex_mobject import MathTex


class TransitionTable(Table):
    def __init__(self, automaton, visual_config, highlight_color="yellow", start_index=(1, 1)):
        """
        Given an automaton of type DFA or TM, constructs a mobject displaying the transition table of that automaton. Also provides helpful methods for animation.
        """
        self.config = visual_config

        input_symbols = list(automaton.input_symbols)
        states = list(automaton.states)

        input_symbols.sort()
        states.sort()

        rows = []

        for state in automaton.states:
            new_row = state
            for sym in input_symbols:
                new_row.append(automaton.transitions[state][sym])

            rows.append(new_row)

        super().__init__(
            rows,
            row_labels=states,
            col_labels=input_symbols,
            include_outer_lines=True,
            element_to_mobject=MathTex
        )

        for state in automaton.final_states:
            for i, cell in enumerate([row[0] for row in rows]):
                if cell == state:
                    final_state_box = self.get_cell((i + 2, 1)).copy().scale(0.9)
                    self.add(final_state_box)

        self.follower = self.get_cell(start_index).copy().set_color(highlight_color)
        self.add(self.follower)

    def move_follower(self, new_index):
        self.follower.move_to(self.get_cell(new_index))
