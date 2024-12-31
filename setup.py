import json
from jsonschema import validate
from pathlib import Path


def pad(s, length):
    if len(s) > length - 1:
        return s[:length - 1] + "+"
    else:
        return s + " " * (length - len(s))


def tableify(raw_transitions):
    cols = list(set(raw_transitions.keys()))
    rows = list(set([x for state in raw_transitions.values() for x in state.keys()]))

    width = 9 + len(cols) * 6 + (len(cols) - 2)

    top_border = width * "-"
    headers = "|      | " + "| ".join([pad(col, 5) for col in cols])
    header_border = width * "-"
    table_rows = []

    for row in rows:
        row_text = "| " + pad(row, 5) + "| " + "| ".join([pad(raw_transitions[col][row], 5) for col in cols])
        table_rows.append(row_text)

    table_body = "|\n".join(table_rows)
    bottom_border = width * "-" + "|"

    out = "|\n".join([top_border, headers, header_border, table_body, bottom_border])
    return out


def query_dfa():
    """Gathers information necessary to form DFA"""

    out = {"fa_type": "dfa"}

    print("To build a DFA, we will need states, an alphabet, transitions, an initial state, and final state(s)")

    proceed = "n"
    while proceed not in ["y", "yes"]:
        raw_states = input("Please enter your states, separated by commas:\n")

        out["states"] = [x.strip() for x in raw_states.split(",")]

        print(f"You have entered: {out["states"]}")
        proceed = input("Proceed (y/n)? ").lower()

    proceed = "n"
    while proceed not in ["y", "yes"]:
        raw_symbols = input("Please enter your input symbols, separated by commas:\n").strip()

        out["input_symbols"] = [x.strip() for x in raw_symbols.split(",")]

        print(f"You have entered: {out["input_symbols"]}")
        proceed = input("Proceed (y/n)? ").lower()

    proceed = "n"
    out["transitions"] = {state: {} for state in out["states"]}
    while proceed not in ["y", "yes"]:
        print("\nAt this time you will enter the end state for each combination of starting state and transition symbol\n-----")

        for state in out["states"]:
            for symbol in out["input_symbols"]:
                end = ""
                while end not in out["states"]:
                    end = input(f"From {state}, {symbol} goes to: ")
                out["transitions"][state][symbol] = end

        print("Based on your input, your transition table looks like this:")
        print(tableify(out["transitions"]))
        proceed = input("Proceed (y/n)? ")

    proceed = "n"
    while proceed not in ["y", "yes"]:
        initial_state = input("Please enter your initial state: ").strip()

        if initial_state not in out["states"]:
            continue

        out["initial_state"] = initial_state

        print(f"You have entered: {out["initial_state"]}")
        proceed = input("Proceed (y/n)? ").lower()

    proceed = "n"
    while proceed not in ["y", "yes"]:
        raw_final_states = input("Please enter your final states, separated by commas: ").strip()

        final_states = [x.strip() for x in raw_final_states.split(",")]

        missing = False
        for state in final_states:
            if state not in out["states"]:
                print(f"State {state} not found, please enter again")
                missing = True

        if missing:
            continue

        out["final_states"] = final_states
        print(f"You have entered: {out["final_states"]}")
        proceed = input("Proceed (y/n)? ").lower()

    return out


def turing_end_valid(end, context):
    return end[0] in context["states"] and end[1] in context["tape_symbols"] and end[2] in ["R", "L"]


def query_tm():
    """Gathers information necessary to form a tm"""

    out = {"fa_type": "tm"}
    print("To build a Turing Machine we will need the states, input symbols, tape symbols, transitions, initial state, blank symbol, and final state.")

    proceed = "n"
    while proceed not in ["y", "yes"]:
        raw_states = input("Please enter your states, separated by commas:\n")

        out["states"] = [x.strip() for x in raw_states.split(",")]

        print(f"You have entered: {out["states"]}")
        proceed = input("Proceed (y/n)? ").lower()

    proceed = "n"
    while proceed not in ["y", "yes"]:
        raw_symbols = input("Please enter your input symbols, separated by commas:\n").strip()

        out["input_symbols"] = [x.strip() for x in raw_symbols.split(",")]

        print(f"You have entered: {out["input_symbols"]}")
        proceed = input("Proceed (y/n)? ").lower()

    proceed = "n"
    while proceed not in ["y", "yes"]:
        raw_symbols = input("Please enter your tape symbols, separated by commas:\n").strip()

        out["tape_symbols"] = [x.strip() for x in raw_symbols.split(",")]

        for symbol in out["input_symbols"]:
            if symbol not in out["tape_symbols"]:
                print(f"Symbol {symbol} specified in input but not tape. Adding...")
                out["tape_symbols"].append(symbol)

        print(f"You have entered: {out["tape_symbols"]}")
        proceed = input("Proceed (y/n)? ").lower()

    proceed = "n"
    out["transitions"] = {state: {} for state in out["states"]}
    while proceed not in ["y", "yes"]:
        print("\nAt this time you will enter the end state for each combination of starting state and transition symbol")
        print("Enter each transition in the form: <end_state>, <write_character>, <head_direction>")
        print("You may leave a transition undefined by pressing <enter> when prompted.")
        print("Spaces are optional and will be ignored\n-----")

        for state in out["states"]:
            for symbol in out["tape_symbols"]:
                end = [None, None, None]
                while not turing_end_valid(end, out):
                    end = [x.strip() for x in input(f"From {state}, {symbol} results in: ").split(",")]
                    if end[0] == '':
                        break
                    end[2] = end[2].upper()

                if end[0] != '':
                    out["transitions"][state][symbol] = end

        print("Transition tables for Turing Machines still a work in progress...")
        print("Instead, here's your transition set in json format:")
        print(json.dumps(out["transitions"], indent=2))
        # print("Based on your input, your transition table looks like this:")
        # print(tableify(out["transitions"]))
        proceed = input("Proceed (y/n)? ")

    proceed = "n"
    while proceed not in ["y", "yes"]:
        initial_state = input("Please enter your initial state: ")

        if initial_state not in out["states"]:
            print(f"State {state} not found. Please enter again")
            continue

        out["initial_state"] = initial_state
        print(f"You have entered: {out["initial_state"]}")
        proceed = input("Proceed (y/n)? ").lower()

    proceed = "n"
    while proceed not in ["y", "yes"]:
        blank_symbol = input("Please enter the symbol you consider to be 'blank': ")

        if blank_symbol not in out["tape_symbols"]:
            addit = input(f"Symbol {blank_symbol} does not exist. Add it (y/n)? ")
            if addit in ["y", "yes"]:
                out["tape_symbols"].append(blank_symbol)
                out["blank_symbol"] = blank_symbol
                break
            else:
                continue

        out["blank_symbol"] = blank_symbol
        print(f"You have entered: {out["blank_symbol"]}")
        proceed = input("Proceed (y/n)? ").lower()

    proceed = "n"
    while proceed not in ["y", "yes"]:
        raw_final_states = input("Please enter the final states, separated by commas: ").strip()

        final_states = [x.strip() for x in raw_final_states.split(",")]

        missing = False
        for state in final_states:
            if state not in out["states"]:
                print(f"State {state} not recognized, please enter again")
                missing = True

        if missing:
            continue

        out["final_states"] = final_states
        print(f"You have entered: {out["final_states"]}")
        proceed = input("Proceed (y/n)? ").lower()

    return out


if __name__ == "__main__":
    """This program prompts the user and progressively builds up an FA"""

    print("Answer the questions below to build your automaton file...")

    while True:
        print("Available FAs:\n\t1. Discrete Finite Automaton (DFA)\n\t2. Turing Machine (TM)\n(NFAs and PDAs coming later)")
        fa_type = input("Specify type of automaton: ").strip().lower()

        match fa_type:
            case "1" | "dfa":
                content = query_dfa()
                schema_fn = "./schema/dfa.schema.json"
                break
            case "2" | "tm":
                content = query_tm()
                schema_fn = "./schema/tm.schema.json"
                break
            case _:
                content = ""
                schema_fn = ""
                print("FA type not recognized. Please try again")

    with open(schema_fn, "rb") as f:
        schema = json.load(f)

    # On success, nothing happens. On failure, throws
    # If it does, there's a desync between what's being queried and what we're testing for
    # This should NEVER go off in production
    validate(instance=content, schema=schema)

    while True:
        filename = Path(input("Relative path to data destination: "))

        if filename.exists():
            proceed = input("File exists. This will overwrite the contents. Proceed (y/n)? ").lower()
            if proceed == "y" or proceed == "yes":
                break
            print("Please enter your preferred path")
        else:
            break

    with filename.open("w") as f:
        json.dump(content, f)

    print(f"Setup complete! Your new FA can be found at {str(filename)}")
