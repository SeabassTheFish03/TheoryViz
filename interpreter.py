from fa_manager import DFA_Manager, NFA_Manager, TM_Manager
import json
import sys

from pathlib import Path

from manim.scene.scene import Scene

# NOTE: This shouldn't run ridiculously slow, but a potential speedup
#   I see is running each LOAD instruction concurrently.


class OutputScene(Scene):
    def __init__(self, commands=list()):
        super().__init__()
        self.animations = list()
        self.managers = dict()  # Format {"name": {"manager": FA_Manager, "show": bool}}

    def construct(self):
        if len(self.animations) > 0:
            for anim in self.animations:
                self.play(anim)
        else:
            self.add(*[manager_block["manager"].mobj for manager_block in self.managers.values() if manager_block["show"]])


def read_file(pathobj, env):
    with pathobj.open() as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        triageLine(line, env, i)


def load_from_file(pathobj, varname, scene):
    with pathobj.open() as f:
        rawJson = json.loads(f.read())

    # I want to raise a KeyError if "type" isn't there, hence no .get()
    match rawJson["type"].lower():
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


def triageLine(line, scene, line_no):
    tokens = line.split(" ")

    if line.startswith("LOAD "):
        if tokens[-2] != "AS":
            raise SyntaxError(f"Line {line_no}:\n\tMalformed 'AS' command")

        # Theoretically this should allow for spaces in the filename
        filename = " ".join(tokens[1:-2])
        filename.removeprefix('\"')
        filename.removesuffix('\"')

        pathobj = Path(filename)

        varname = tokens[-1]

        load_from_file(pathobj, varname, scene)
    elif line.startsWith("SHOW "):
        # Since variable names can't have spaces, have to make sure
        #  no spaces made it into the query
        if len(tokens) != 2:
            raise SyntaxError(f"Line {line_no}:\n\tToo many arguments: {len(tokens)}, expected 2")

        # Possible KeyError, but we would want that to fail anyways
        scene.mobjects[tokens[1]]["show"] = True
    elif line.startswith("MOVE "):
        if tokens[2] != "TO":
            raise SyntaxError(f"Line {line_no}:\n\tMalformed Command: Missing or mistyped TO keyword")

        # Now parsing the coords
        coords = "".join(tokens[3:]).split(",")

        if len(coords) != 2:
            raise SyntaxError(f"Line {line_no}:\n\tMalformed coordinates passed: got {len(coords)}, expected 2")

        coords = [float(c) for c in coords]

        scene.mobjects[tokens[1]]["mobj"].move_to([*coords, 0])
    elif line.startswith("SHIFT "):
        assert tokens[2] == "BY", "Malformed Command: Missing or mistyped BY keyword"

        coords = "".join(tokens[3:]).split(",")
        coords = [float(c) for c in coords]
        assert len(coords) == 2, f"Malformed coordinates passed: got {len(coords)}, expected 2"

        scene.mobjects[tokens[1]]["mobj"].shift([*coords, 0])


if __name__ == "__main__":
    if len(sys.argv) == 1:
        infile = Path(input("Input file path: "))
    elif len(sys.argv) == 2:
        infile = Path(sys.argv[1])
    else:
        print(
            "Usage: interpreter.py [infile]",
            file=sys.stderr
        )
        exit(1)

    scene = OutputScene()

    try:
        read_file(infile, scene)
    except SyntaxError as e:
        raise SyntaxError(f"Viz file {str(infile)}:\n\t{str(e)}")
