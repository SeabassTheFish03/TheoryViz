from fa_manager import DFA_Manager, NFA_Manager, TM_Manager
import json
import sys

from pathlib import Path

from dsl_errors import MalformedCommandError, TypeNotRecognizedError, TypeNotSpecifiedError

# NOTE: This shouldn't run ridiculously slow, but a potential speedup
#   I see is running each LOAD instruction concurrently.


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
    if line.startswith("LOAD "):
        tokens = line.split(" ")

        if tokens[-2] != "AS":
            raise MalformedCommandError()

        filename = " ".join(tokens[1:-2])
        filename.removeprefix('\"')
        filename.removesuffix('\"')

        pathobj = Path(filename)

        varname = tokens[-1]

        load_from_file(pathobj, varname, env)


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
