import json
import sys
import os
import tomllib
from pathlib import Path

from manim.scene.scene import Scene
from manim._config import tempconfig
from manim.animation.creation import Create

from fa_manager import Auto_Manager, DFA_Manager, NFA_Manager, TM_Manager

# NOTE: This shouldn't run ridiculously slow, but a potential speedup
#   I see is running each LOAD instruction concurrently.


class OutputScene(Scene):
    def __init__(self, showing=False, commands=list()):
        super().__init__()
        self.animations = list()
        self.showing = showing
        self.managers = dict()  # Format {"name": Auto_Manager}

    def construct(self):
        if len(self.animations) > 0:
            self.play(*[Create(manager.mobj) for manager in self.managers.values()])
            for anim in self.animations:
                self.play(anim)
        else:
            self.add(*[manager.mobj for manager in self.managers.values()])


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


def load_from_file(pathobj, varname, scene, config_file):
    with pathobj.open() as f:
        rawJson = json.loads(f.read())

    with config_file.open('rb') as f:
        config = tomllib.load(f)

    os.chdir("..")
    match rawJson["fa_type"].lower():
        case "dfa":
            created = DFA_Manager.from_json(rawJson, config)
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
    tokens = line.strip().split(" ")
    config_path = Path("./default_config.toml")

    if line.startswith("# "):
        # It's a comment
        pass
    elif line.startswith("LOAD "):
        # LOAD <filename> AS <varname>
        if tokens[-2] != "AS":
            raise SyntaxError("Malformed 'AS' command")

        # Theoretically this should allow for spaces in the filename
        filename = capture_quotes(tokens[1:-2])
        pathobj = Path(filename)
        varname = tokens[-1]
        load_from_file(pathobj, varname, scene, config_path)

    elif line.startswith("SHOW "):
        # SHOW <component> OF <varname>
        if len(tokens) != 4:
            raise SyntaxError(f"Malformed command: too many tokens ({len(tokens)}), expected 4")
        if tokens[2] != "OF":
            raise SyntaxError("Malformed command: missing or mistyped OF keyword")
        if tokens[3] not in scene.managers:
            raise KeyError(f"Object {tokens[3]} not recognized.")

        manager: Auto_Manager = scene.managers[tokens[3]]

        manager.show_mobj(tokens[1])
        scene.showing = True

    elif line.startswith("MOVE "):
        # MOVE <component> OF <varname> TO <coords>
        if tokens[2] != "OF":
            raise SyntaxError("Malformed Command: Missing or mistyped OF keyword")
        if tokens[4] != "TO":
            raise SyntaxError("Malformed Command: Missing or mistyped TO keyword")

        # Now parsing the coords
        coords = "".join(tokens[5:]).split(",")

        if len(coords) not in [2, 3]:
            raise SyntaxError(f"Malformed coordinates passed: got {len(coords)} values, expected 2 or 3")

        coords = [float(c) for c in coords]

        manager: Auto_Manager = scene.managers[tokens[3]]
        manager.move_mobj(tokens[1], coords)

    elif line.startswith("SHIFT "):
        # SHIFT <component> OF <varname> BY <coords>
        if tokens[2] != "OF":
            raise SyntaxError("Malformed Command: Missing or mistyped OF keyword")
        if tokens[4] != "BY":
            raise SyntaxError("Malformed Command: Missing or mistyped BY keyword")

        coords = "".join(tokens[5:]).split(",")
        coords = [float(c) for c in coords]
        if len(coords) not in [2, 3]:
            raise SyntaxError(f"Malformed coordinates passed: got {len(coords)} values, expected 2 or 3")

        manager: Auto_Manager = scene.managers[tokens[3]]
        manager.shift_mobj(tokens[1], coords)
    elif line.startswith("INPUT "):
        # INPUT <string> TO <varname>
        if tokens[2] != "TO":
            raise SyntaxError("Malformed Command: Missing or mistyped TO keyword")

        manager: Auto_Manager = scene.managers[tokens[3]]
        manager.add_input(tokens[1])

    elif line.startswith("PRINT "):
        # PRINT <words>
        words = capture_quotes(tokens[1:])
        print(words)

    elif line.startswith("ANIMATE"):
        # ANIMATE[!]
        if line.strip() not in ["ANIMATE", "ANIMATE!"]:
            raise SyntaxError("Superfluous characters after ANIMATE command")

        for manager in scene.managers.values():
            scene.animations.append(manager.animate())
    elif line.startswith("LINK "):
        # LINK <config_filename>
        filename = capture_quotes(tokens[1:], ' ')

        config_path = Path(filename)


def interpret(filename: str) -> None:
    scene = OutputScene()

    try:
        infile = Path(filename)
        read_file(infile, scene)
    except SyntaxError as e:
        raise SyntaxError(f"Viz file {str(infile)}:\n\t{str(e)}")

    with tempconfig({"quality": "low_quality", "preview": True}):
        scene.render()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        infile = Path(input("Input file path: "))
    elif len(sys.argv) == 2:
        infile = Path(sys.argv[1])
    else:
        print("Usage: py interpreter.py [infile]")
        infile = ""
        exit(1)

    interpret(infile)
