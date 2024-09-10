# TheoryViz
TheoryViz is a program for displaying, animating, and transforming Finite Automata. It is meant as a teaching aid for Computer Theory professors and instructors, so they can focus on discussing concepts rather than spending time and energy drawing automata manually.
## Dependencies
TheoryViz is built on top of two existing Python libraries: [Manim](https://github.com/ManimCommunity/manim) by the Manim Community and [Automata](https://github.com/caleb531/automata) by [Caleb Evans](https://github.com/caleb531).

We use Manim for all the renderings and animations. The class we created, FiniteAutomaton, is built upon the DiGraph class in Manim. Automata is used as the back-end for all the automaton-related operations, such as NFA to DFA transformations, accepting/rejecting strings, etc.

We would like to express our sincere gratitute to the maintainers of these libraries for making them open-source. This library would not be possible without them doing so.
### Licensing
Both Manim and Automata are licensed under the MIT License and the text can be found in full in dependencies_license.txt. These libraries are both considered dependencies, and almost none of the code is copied. The exception is the Dockerfile from Manim, which we have adopted as our own Dockerfile (with the only addition being the installation of Automata). This library is licensed under the GPL 3, but for redundancy we are also including the MIT License.

# Installation
## Docker
This will be (once implemented) the preferred way to install and use this library. We will use the most up-to-date Dockerfile provided by Manim and compose that with a Dockerfile that simply does `pip install automata-lib` on top of that. 
## Manual Install
Generally speaking, you only need to install the dependencies one way or another. For you it may be as simple as running `pip install manim` followed by `pip install automata-lib`. However, results will vary per machine. One of our developers used `Choco` to install Manim and `pip` installed Automata on top of that, which somehow works.

We don't claim to know anything about the Python package/module system, so manually install at your own risk!
