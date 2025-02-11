import os

if __name__ == "__main__":
    test = input("Select test protocol, or type '?' to see options: ")

    if test.strip() == "?":
        protocols = os.listdir("./protocols")
        protocols.sort()
