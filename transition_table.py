from manim import *
import sys
import json



class TransitionTable(Scene):
    def init(self, fa_filename, input_string=""):
        super().__init__()
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
        
        self.table = Table(
            state_rows,
            col_labels = [Tex(x) for x in top_row],
            row_labels=[Tex(x) for x in self.rawJson["states"]],
            top_left_entry=None,
            include_outer_lines=True,
        )

        # tab = Table()
    def construct(self):
        self.add(self.table)
        # tab = Table(
        #     [["First", "Second"],
        #      ["Third", "Fourth"]],
        #      row_labels=[Text("R1"), Text("R2")],
        #      col_labels=[Text("C1"), Text("C2")],
        #      top_left_entry=None)
        # x_vals = np.linspace(-2,2,5)
        # y_vals = np.exp(x_vals)

        # self.add(tab)

class DisplayTransitionTable(Scene):
    def __init__(self, fa_filename, input_string=""):
        super().__init__()
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

        self.table = Table(
            state_rows,
            col_labels = [Tex(x) for x in top_row],
            row_labels = [Tex(x) for x in self.rawJson["states"]],
            top_left_entry = None,
            include_outer_lines=True,
        )

    def construct(self):
        self.add(self.table)

class AnimateTransitionTable(DisplayTransitionTable):
    def construct(self):
        sequence = []
        current_state = self.rawJson["initial_state"]
        for char in self.input_string:
            if char in self.rawJson["transitions"][current_state]:
                next_state = self.rawJson["transitions"][current_state][char]

                sequence.append((current_state, next_state))

                current_state = next_state
            else: break

        self.add(self.table) # self.play(Create(self.table)) - just materializes, not creates

        state_index = list(self.rawJson["states"]).index(self.rawJson["initial_state"]) + 2
        # have to have input string
        trans_index = list(self.rawJson["input_symbols"]).index(self.input_string[0]) + 2
        follower = self.table.get_cell((state_index, trans_index), color=YELLOW)
        self.play(Create(follower))

        substring = self.input_string
        floater = Tex(substring, color=BLACK, fill_color=YELLOW)
        floater.to_edge(UP)
        self.add(floater)
        #dig into manim. scene.py

        current_state = self.rawJson["initial_state"]
        next_state = self.rawJson["transitions"][current_state][self.input_string[0]]
        for char in self.input_string:
            char = substring[0]
            substring = substring[1:]

            if char in self.rawJson["transitions"][current_state]:
                # if next_state != current_state:
                #     arrow = self.g.edges[(current_state, next_state)]
                # else:
                #     arrow = self.loop_arcs[current_state]
                # path = arrow.copy().set(color=RED, stroke_width=10)

                state_index = list(self.rawJson["states"]).index(current_state) + 2
                trans_index = list(self.rawJson["input_symbols"]).index(char) + 2

                new_follower = self.table.get_cell((state_index, trans_index), color=YELLOW)
                next_state = self.rawJson["transitions"][current_state][char]

                self.play(
                    Transform(follower, new_follower),
                    # Create(path),
                    #floater.to_edge(UP),
                    #Transform(floater, Tex(str(substring), color=BLACK, fill_color=YELLOW)),
                    
                    #this is where the text is coming from - how to make it go up top and not disappear. Check Sebastians code.
                    # MoveAlongPath(floater, path),
                )
                # self.remove(path)
                current_state = next_state
            else: break

        self.wait()

class AnimateDFAWithTable(Scene):
    def __init__(self, rawJson, input_string):
        super().__init__()
        self.dfa = JSONToDFA(rawJson)
        self.input_string = input_string
        self.rawJson = rawJson

        self.fa_mobj = FAToMobj(self.dfa).shift(3*RIGHT)
        
        top_row = []
        for sym in self.rawJson["input_symbols"]:
            top_row.append(sym)

        state_rows = []
        for state in self.rawJson["states"]:
            new_row = []
            for sym in self.rawJson["input_symbols"]:
                new_row.append(self.rawJson["transitions"][state][sym])
            state_rows.append(new_row)

        self.table = MathTable(
            state_rows,
            col_labels = [MathTex(x) for x in top_row],
            row_labels = [MathTex(x) for x in self.rawJson["states"]],
            top_left_entry = None,
            include_outer_lines=True,
        ).shift(3*LEFT).scale(0.5)

        self.live_str_index = 0

    def construct(self):
        self.play(Create(self.fa_mobj), Create(self.table))

        previous_state = None
        prev_string = None
        prev_follower = None

        try:
            for new_state in self.dfa.read_input_stepwise(self.input_string, ignore_rejection=False):
                curr_string = Tex(self.input_string[self.live_str_index:], font_size=40, color="yellow").move_to(self.fa_mobj).shift(3*DOWN)

                trans_tup = (str(previous_state), str(new_state))
                
                tab_state_dex = list(self.rawJson["states"]).index(str(new_state)) + 2
                tab_trans_dex = list(self.rawJson["input_symbols"]).index(self.input_string[self.live_str_index]) + 2
                follower = self.table.get_cell((tab_state_dex, tab_trans_dex), color="yellow")

                if previous_state is None:
                    previous_state = new_state
                    prev_string = curr_string
                    prev_follower = follower
                    continue

                focus_edge = self.fa_mobj.edges[trans_tup]
                self.play(
                    ShowPassingFlash(focus_edge.copy().set_color("0x0000ff"), time_width=0.2),
                    ReplacementTransform(prev_string, curr_string),
                    ReplacementTransform(prev_follower, follower)
                )
                self.wait(0.5)

                previous_state = new_state
                prev_string = curr_string
                prev_follower = follower
                self.live_str_index += 1

        except RejectionException as e:
            reject_mobj = Text(str(e) + f"\nwith input string '{self.input_string}'", font_size=15, color="red").move_to(self.fa_mobj).shift(3*UP)
            self.play(Create(reject_mobj))
        else:
            accept_mobj = Tex(f"The DFA accepted the string '{self.input_string}'", font_size=24, color="green").move_to(self.fa_mobj).shift(3*UP)
            self.play(Create(accept_mobj))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: py transition_table.py <fa_filename> <input string>")
        exit(1)


    with tempconfig({"quality": "low_quality", "preview": True}):
        # scene = DisplayTransitionTable(sys.argv[1])
        animation = AnimateTransitionTable(sys.argv[1], sys.argv[2])
        #scene.render()
        animation.render()