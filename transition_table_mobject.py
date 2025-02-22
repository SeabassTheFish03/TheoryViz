from manim import *
import sys
import json
from text_visuals import ProcessText


class DisplayTransitionTable(Table):
    def __init__(self, raw_json, input_string=''):

        # with open(fa_filename, "rb") as f:
        #     fa_json = json.load(f)
        # self.rawJson = fa_json already opened and established
        self.json = raw_json
        self.input_string = input_string

        top_row = []
        for sym in self.json["input_symbols"]:  # rawJson
            top_row.append(sym)

        state_rows = []
        for state in self.json["states"]:  # rawJson
            new_row = []
            for sym in self.json["input_symbols"]:  # rawJson
                new_row.append(self.json["transitions"][state][sym])  # rawJson
            state_rows.append(new_row)

        row_labelsx = [Tex(x) for x in self.json["states"]]  # rawJson
        col_labelsx = [Tex(x) for x in top_row]

        super().__init__(state_rows,
                         row_labels=row_labelsx,
                         col_labels=col_labelsx,
                         include_outer_lines=True)

        state_index = list(self.json["states"]).index(self.json["initial_state"]) + 2  # rawJson x2

        # create the initial arrow
        follower = self.get_cell((state_index, 1))
        Initial_arrow = Arrow(color=YELLOW, stroke_width=20, buff=0.6, max_stroke_width_to_length_ratio=20, max_tip_length_to_length_ratio=0.7).next_to(follower, LEFT)
        self.add(Initial_arrow)

        # create final state box
        list_of_final_states = list(self.json["final_states"])  # rawJson
        for elem in list_of_final_states:
            listOfRows = list(self.row_labels)
            for label in listOfRows:
                # print(str(label)[5], " == ", elem)
                if elem == str(label)[5]:
                    # print(self.table.row_labels.index(label))
                    finalstatebox = self.get_cell((self.row_labels.index(label) + 2, 1), color=WHITE)
                    copyoffinalstatebox = finalstatebox.scale(0.9)
                    self.add(copyoffinalstatebox)


class AnimateTransitionTable(DisplayTransitionTable):
    def __init__(self, fa_filename, input_string=''):
        super().__init__(fa_filename, input_string)  # this calls DisplayTransitionTable
        sequence = []
        current_state = self.json["initial_state"]  # rawJson
        for char in self.input_string:
            if char in self.json["transitions"][current_state]:  # rawJson
                next_state = self.json["transitions"][current_state][char]  # rawJson
                sequence.append((current_state, next_state))
                current_state = next_state
            else:
                break

        # self.play(Create(self.table)) table is already created based on the super.init

        state_index = list(self.json["states"]).index(self.json["initial_state"]) + 2  # rawJson
        # have to have input string
        trans_index = list(self.json["input_symbols"]).index(self.input_string[0]) + 2  # rawJson

        stateRow = SurroundingRectangle(self.get_rows()[state_index - 1], buff=MED_LARGE_BUFF)
        self.add(stateRow)  # add rectangle around the given states (row)
        self.stateRow = stateRow

        transitionColumn = SurroundingRectangle(self.get_columns()[trans_index - 1], buff=MED_LARGE_BUFF)
        self.add(transitionColumn)  # add rectangle around state (column)
        self.transitionColumn = transitionColumn

        follower = self.get_cell((state_index, trans_index), color=YELLOW)
        self.add(follower)  # follower box added - movement of this box is relegated to a different function
        self.follower = follower

        substring = self.input_string
        stringOfInput = ProcessText(substring)
        self.add(stringOfInput)  # string added - we do want this right now, but we only need one total in the full animation
        self.stringOfInput = stringOfInput

        self.stringOfInput.move_to(UP * 3.5)  # moves to the top...again, don't need this later

        char = self.input_string[0]
        self.input_string = self.input_string[1:]

        first_state = self.json["initial_state"]
        next_state = self.json["transitions"][first_state][char]  # rawJson

        self.current_state = (next_state)

    def MoveToNextTransition(self):
        # if length is 0, then new follower and transition column = None, update state as normal I think...
        if (len(self.input_string) != 0):
            char = self.input_string[0]
            self.input_string = self.input_string[1:]

            if char in self.json["transitions"][self.current_state]:  # rawJson
                state_index = list(self.json["states"]).index(self.current_state) + 2  # rawJson
                trans_index = list(self.json["input_symbols"]).index(char) + 2  # rawJson

                new_follower = self.get_cell((state_index, trans_index), color=YELLOW)
                next_state = self.json["transitions"][self.current_state][char]  # rawJson

                new_stateRow = SurroundingRectangle(self.get_rows()[state_index - 1], buff=MED_LARGE_BUFF)
                new_transitionColumn = SurroundingRectangle(self.get_columns()[trans_index - 1], buff=MED_LARGE_BUFF)

                self.current_state = next_state
                animation = AnimationGroup(
                    Transform(self.follower, new_follower),
                    Transform(self.stateRow, new_stateRow),
                    Transform(self.transitionColumn, new_transitionColumn),
                    self.stringOfInput.RemoveOneCharacter()
                )
                self.stringOfInput.increment_letter()

        else:
            self.remove(self.follower)
            # new_follower = None
            # new_transitionColumn = None
            self.remove(self.transitionColumn)
            state_index = list(self.json["states"]).index(self.current_state) + 2  # rawJson
            new_stateRow = SurroundingRectangle(self.get_rows()[state_index - 1], buff=MED_LARGE_BUFF)
            animation = AnimationGroup(
                Transform(self.stateRow, new_stateRow),
                Uncreate(self.follower),
                Uncreate(self.transitionColumn),
                self.stringOfInput.RemoveOneCharacter()
            )
            self.stringOfInput.increment_letter()

        return (animation)

        # highlight entire row and entire column
        # box diffent color
        # for the last state, the column disappears

        # transition table is delayed by one....


class testTransitionTable(Scene):
    def __init__(self, fa_filename, input_string=''):
        super().__init__()
        # self.add(input_string)

        # self.table = DisplayTransitionTable(fa_filename, input_string)

        self.table = AnimateTransitionTable(fa_filename, input_string)

    def construct(self):
        self.add(self.table)
        # for _ in self.input_string:
        self.play(self.table.MoveToNextTransition())
        self.play(self.table.MoveToNextTransition())
        self.play(self.table.MoveToNextTransition())

        # transitionTable = DisplayTransitionTable(fa_filename, input_string)
        # self.play(Create(transitionTable))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: py transition_table.py <fa_filename> <input string>")
        exit(1)

    with tempconfig({"quality": "low_quality", "preview": True}):
        # scene = DisplayTransitionTable(sys.argv[1], sys.argv[2])
        # scene.render()
        # animation = AnimateTransitionTable(sys.argv[1], sys.argv[2]) # fa_filename, input_string
        # animation.render()
        scene = testTransitionTable(sys.argv[1], sys.argv[2])
        scene.render()
