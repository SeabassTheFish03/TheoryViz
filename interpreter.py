from fa_manager import DFA_Manager, NFA_Manager, TM_Manager
import json
import sys

from pathlib import Path

from dsl_errors import MalformedCommandError, TypeNotRecognizedError, TypeNotSpecifiedError

from manim.scene.scene import Scene

# NOTE: This shouldn't run ridiculously slow, but a potential speedup
#   I see is running each LOAD instruction concurrently.


class OutputScene(Scene):
    def __init__(self, commands=list()):
        super().__init__()
        self.commands = commands
        self.context = {"mobjects": dict()}

    def construct(self):
        for command in self.commands:
            exec(command)


def read_file(pathobj, env):
    with pathobj.open() as f:
        lines = f.readlines()

    for line in lines:
        triageLine(line, env)


def load_from_file(pathobj, varname, env):
    with pathobj.open() as f:
        rawJson = json.loads(f.read())

    if "type" not in rawJson:
        raise TypeNotSpecifiedError()

    if rawJson["type"].lower() == "dfa":
        created = DFA_Manager.from_json(rawJson)
    elif rawJson["type"].lower() == "nfa":
        created = NFA_Manager.from_json(rawJson)
    elif rawJson["type"].lower() == "tm":
        created = TM_Manager.from_json(rawJson)
    else:
        raise TypeNotRecognizedError(
            f'JSON claims type {rawJson["type"]}, which is not a valid type.'
        )

    if varname in env:
        print(
            f"Overwrote existing FA at {varname}",
            file=sys.stderr,
        )
    env[varname] = created


def triageLine(line, env):
    tokens = line.split(" ")

    if line.startswith("LOAD "):
        assert tokens[-2] == "AS", "Malformed Command: Missing or mistyped AS keyword"

        # Theoretically this should allow for spaces in the filename
        filename = " ".join(tokens[1:-2])
        filename.removeprefix('\"')
        filename.removesuffix('\"')

        pathobj = Path(filename)

        varname = tokens[-1]

        load_from_file(pathobj, varname, env)
    elif line.startsWith("SHOW "):
        # Since variable names can't have spaces, have to make sure
        #  no spaces made it into the query
        assert len(tokens) == 2, f"Too many arguments: {len(tokens)}, expected 2"

        # Possible KeyError, but we would want that to fail anyways
        mobj = env[tokens[1]]

        if "scene" not in env:
            print("Creating an empty scene...")
            env["scene"] = OutputScene()

        # Adding the mobj to the Scene's internal context
        env["scene"].context["mobjects"][tokens[1]] = mobj
        env["scene"].commands.append(f"self.add(self.context[\"mobjects\"][{tokens[1]}])")
    elif line.startswith("MOVE "):
        assert tokens[2] == "TO", "Malformed Command: Missing or mistyped TO keyword"

        # Now parsing the coords
        coords = "".join(tokens[3:]).split(",")

        assert len(coords) == 2, f"Malformed coordinates passed: got {len(coords)}, expected 2"

        coords = [float(c) for c in coords]

        mobj = env[tokens[1]]

        env["scene"].commands.append(f"self.context[\"mobjects\"][{tokens[1]}].move_to({coords[0]},{coords[1]})")
    elif line.startswith("SHIFT "):
        assert tokens[2] == "BY", "Malformed Command: Missing or mistyped BY keyword"

        coords = "".join(tokens[3:]).split(",")

        assert len(coords) == 2, f"Malformed coordinates passed: got {len(coords)}, expected 2"

        coords = [float(c) for c in coords]

        mobj = env[tokens[1]]

        env["scene"].commands.append(f"self.context[\"mobjects\"][{tokens[1]}].shift({coords[0]},{coords[1]})")


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

    env = dict()

    read_file(infile, env)
    print(env)
