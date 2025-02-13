from fa_manager import DFA_Manager, NFA_Manager, TM_Manager
import json
import sys
import os

from pathlib import Path

from manim.scene.scene import Scene

# NOTE: This shouldn't run ridiculously slow, but a potential speedup
#   I see is running each LOAD instruction concurrently.


class OutputScene(Scene):
    def __init__(self, animated=False, commands=list()):
        super().__init__()
        self.animations = list()
        self.animated = animated
        self.managers = dict()  # Format {"name": {"manager": FA_Manager, "show": bool}}

    def construct(self):
        if self.animated:
            if len(self.animations) > 0:
                for anim in self.animations:
                    self.play(anim)
            else:
                print("This scene claims it is an animation, yet no animations were provided")
                exit(1)
        else:
            self.add(*[manager_block["manager"].mobj for manager_block in self.managers.values() if manager_block["show"]])


def capture_quotes(tokens: list[str], delimiter: str = " ") -> str:
    if len(tokens) == 0:
        raise SyntaxError("No tokens provided")
    if not tokens[0].startswith("\""):
        raise SyntaxError(f"First token {tokens[0]} does not begin with a quote")

    out_tokens = list()
    tokens[0] = tokens[0].removeprefix("\"")
    for token in tokens:
        if token.endswith("\""):
            out_tokens.append(token[:-1])
            return delimiter.join(out_tokens)
        else:
            out_tokens.append(token)

    raise SyntaxError(f"Token list {tokens} contains no closing quote token")


def read_file(pathobj, env):
    with pathobj.open() as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        try:
            triageLine(line, env)
        except SyntaxError as e:
            raise SyntaxError(f"Line {i}:\n\t{str(e)}")


def load_from_file(pathobj, varname, scene):
    with pathobj.open() as f:
        rawJson = json.loads(f.read())

    os.chdir("..")
    match rawJson["fa_type"].lower():
        case "dfa":
            created = DFA_Manager.from_json(rawJson)
        case "nfa":
            created = NFA_Manager.from_json(rawJson)
        case "tm":
            created = TM_Manager.from_json(rawJson)
        case _:
            raise TypeError(
                f'JSON claims type {rawJson["type"]}, which is not a valid type.'
            )

    scene.managers[varname] = created


def triageLine(line, scene):
    tokens = line.split(" ")

    if line.startswith("LOAD "):
        # LOAD <filename> AS <varname>
        if tokens[-2] != "AS":
            raise SyntaxError("Malformed 'AS' command")

        # Theoretically this should allow for spaces in the filename
        filename = capture_quotes(tokens[1:-2])

        pathobj = Path(filename)

        varname = tokens[-1]

        load_from_file(pathobj, varname, scene)
    elif line.startsWith("SHOW "):
        # SHOW <varname>

        # Since variable names can't have spaces, have to make sure
        #  no spaces made it into the query
        if len(tokens) != 2:
            raise SyntaxError(f"Too many arguments: {len(tokens)}, expected 2")

        scene.mobjects[tokens[1]]["show"] = True
    elif line.startswith("MOVE "):
        if tokens[2] != "TO":
            raise SyntaxError("Malformed Command: Missing or mistyped TO keyword")

        # Now parsing the coords
        coords = "".join(tokens[3:]).split(",")

        if len(coords) != 2:
            raise SyntaxError(f"Malformed coordinates passed: got {len(coords)} values, expected 2")

        coords = [float(c) for c in coords]

        scene.mobjects[tokens[1]]["mobj"].move_to([*coords, 0])
    elif line.startswith("SHIFT "):
        if tokens[2] != "BY":
            raise SyntaxError("Malformed Command: Missing or mistyped BY keyword")

        coords = "".join(tokens[3:]).split(",")
        coords = [float(c) for c in coords]
        if len(coords) != 2:
            raise SyntaxError(f"Malformed coordinates passed: got {len(coords)} values, expected 2")

        scene.mobjects[tokens[1]]["mobj"].shift([*coords, 0])
    elif line.startswith("PRINT "):
        words = capture_quotes(tokens[1:])
        print(words)


def interpret(filename: str) -> None:
    scene = OutputScene()

    try:
        infile = Path(filename)
        read_file(infile, scene)
    except SyntaxError as e:
        raise SyntaxError(f"Viz file {str(infile)}:\n\t{str(e)}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        infile = Path(input("Input file path: "))
    elif len(sys.argv) == 2:
        infile = Path(sys.argv[1])
    else:
        print("Usage: interpreter.py [infile]")
        infile = ""
        exit(1)

    interpret(infile)
