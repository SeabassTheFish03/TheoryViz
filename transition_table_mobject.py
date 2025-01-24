from manim import *
import sys
import json
from text_visuals import ProcessText

class DisplayTransitionTable(Table):
    def __init__(self, fa_filename, input_string=''):
        
        with open(fa_filename, "rb") as f:
            fa_json = json.load(f)
        self.rawJson = fa_json
        self.input_string = input_string

        top_row = []
        for sym in self.rawJson["input_symbols"]:
            top_row.append(sym)

        state_rows = []
        for state in self.rawJson["states"]:
            new_row = []
            for sym in self.rawJson["input_symbols"]:
                new_row.append(self.rawJson["transitions"][state][sym])
            state_rows.append(new_row)

        row_labelsx = [Tex(x) for x in self.rawJson["states"]]
        col_labelsx = [Tex(x) for x in top_row]

        super().__init__(state_rows,
                         row_labels = row_labelsx,
                         col_labels = col_labelsx,
                         include_outer_lines=True)


        state_index = list(self.rawJson["states"]).index(self.rawJson["initial_state"]) + 2

        follower = self.get_cell((state_index, 1))
        Initial_arrow = Arrow(color=YELLOW).next_to(follower, LEFT)
        self.add(Initial_arrow)

        #create final state box
        list_of_final_states = list(self.rawJson["final_states"])
        for elem in list_of_final_states:
            listOfRows = list(self.row_labels)
            for label in listOfRows:
                # print(str(label)[5], " == ", elem)
                if elem == str(label)[5]:
                    # print(self.table.row_labels.index(label))
                    finalstatebox = self.get_cell((self.row_labels.index(label)+2, 1), color=WHITE)
                    copyoffinalstatebox = finalstatebox.scale(0.9)
                    self.add(copyoffinalstatebox)

class AnimateTransitionTable(DisplayTransitionTable):
    # need to def init - set up everything as per normal
    # then the individual steps - so the play thingy, that's all called via different definitions
    # like def nextStep() or whatever --> checking fa_manager - no the processText thingy for those ideas.
    def __init__(self, fa_filename, input_string=''):
        super().__init__(fa_filename, input_string) # this calls DisplayTransitionTable. Need to refactor
        # in order to use just the json already made instead of the filename
        sequence = []
        current_state = self.rawJson["initial_state"]
        for char in self.input_string:
            if char in self.rawJson["transitions"][current_state]:
                next_state = self.rawJson["transitions"][current_state][char]
                sequence.append((current_state, next_state))
                current_state = next_state
            else: break

        # self.play(Create(self.table)) table is already created based on the super.init

        state_index = list(self.rawJson["states"]).index(self.rawJson["initial_state"]) + 2 
        # have to have input string
        trans_index = list(self.rawJson["input_symbols"]).index(self.input_string[0]) + 2
        follower = self.get_cell((state_index, trans_index), color=YELLOW)
        # self.play(Create(follower))
        self.add(follower) #follower box added - movement of this box is relegated to a different function
        self.follower = follower

        substring = self.input_string
        stringOfInput = ProcessText(substring)
        self.add(stringOfInput) #string added - we do want this right now, but we only need one total in the full animation
        self.stringOfInput = stringOfInput

        self.stringOfInput.move_to(UP*3.5) #moves to the top...again, don't need this later

        current_state = self.rawJson["initial_state"]
        self.current_state = (current_state)

        # this is not initializing stuff - new definition required
    def MoveToNextTransition(self):
        char = self.input_string[0]
        self.input_string = self.input_string[1:]

        if char in self.rawJson["transitions"][self.current_state]:
            state_index = list(self.rawJson["states"]).index(self.current_state) + 2
            trans_index = list(self.rawJson["input_symbols"]).index(char) + 2

            new_follower = self.get_cell((state_index, trans_index), color=YELLOW)
            next_state = self.rawJson["transitions"][self.current_state][char]

            self.current_state = next_state

            return AnimationGroup(
                Transform(self.follower, new_follower) # does this update it within the mobject itself? or do I need to update that manually?
                # self.stringOfInput.RemoveOneCharacter(),
                # self.stringOfInput.increment_letter()
            )


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
        
