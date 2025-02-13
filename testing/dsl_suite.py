import os
import sys

sys.path.append("..")
import interpreter

if __name__ == "__main__":

    test = input("Select test protocol filename, or type '?' to see options: ")

    protocols = os.listdir("./dsl")
    protocols.sort()

    if test.strip() == "?":
        print("DSL Test Protocols:")
        print("\n".join(["\t" + name for name in protocols]))
    elif test in protocols:
        interpreter.interpret("./dsl/" + test)
    else:
        print("Test not found. Please run again and type '?' to see the options")
