# TheoryViz
TheoryViz is a program for displaying, animating, and transforming Finite Automata. It is meant as a teaching aid for Computer Theory professors and instructors, so they can focus on discussing concepts rather than spending time and energy drawing automata manually.
## Dependencies
TheoryViz is built on top of three existing Python libraries: [Manim](https://github.com/ManimCommunity/manim) by the Manim Community, [Automata](https://github.com/caleb531/automata) by [Caleb Evans](https://github.com/caleb531), and [PyGraphviz](https://github.com/pygraphviz/pygraphviz) by (primarily) [Jarrod Millman](https://github.com/jarrodmillman).

We use Manim for all the renderings and animations. The class we created, FiniteAutomaton, is built upon the DiGraph class in Manim. Automata is used as the back-end for all the automaton-related operations, such as NFA to DFA transformations, accepting/rejecting strings, etc.

By sheer coincidence, we named our project TheoryViz before learning about the Graphviz library, but upon discovering it we immediately chose to integrate it into our algorithm to position our graph nodes. We like that it can factor in the length of our edge labels and adapt accordingly. The built-in NetworkX graph layout algorithms can't account for this.

We would like to express our sincere gratitute to the maintainers of these libraries for making them open-source. This library would not be possible without them doing so.
### Licensing
Both Manim and Automata are licensed under the MIT License. Graphviz is licensed under the 3-Clause BSD license. The licenses can be found in full in LICENSE.txt. These libraries are both considered dependencies, and almost none of the code is copied. The exception is the Dockerfile from Manim, which we have adopted as our own Dockerfile (with the only addition being the installation of Automata). This library is licensed under the GPL 3, but for redundancy we are also including the MIT License.

## Members
Primary Developer: CDT Sebastian Neumann
Secondary Developer: CDT Zoe Bennett-Manke
Tertiary Developer: CDT Ian Njuguna
Quatiary Developer: CDT Lilly Baker
## Instructors/Advisors
Instructor and primary advisor: Dr. Ryan Dougherty
Senior advisor: Dr. Edward Sobiesk

Advisor: Dr. Tim Randolph
Program Director: Colonel Robert Harrison

# Installation
## Docker
This will be (once implemented) the preferred way to install and use this library. We will use the most up-to-date Dockerfile provided by Manim and compose that with a Dockerfile that simply does `pip install automata-lib` on top of that. 
## Manual Install
Generally speaking, you only need to install the dependencies one way or another. For you it may be as simple as running `pip install manim` followed by `pip install automata-lib`. However, results will vary per machine. One of our developers used `Choco` to install Manim and `pip` installed Automata on top of that, which somehow works.

We don't claim to know anything about the Python package/module system, so manually install at your own risk!
# Notes
## Terminology
In various parts throughout the code, we use some terms to refer to the geometry of the automata, and other terms to refer to the concepts in Computer Theory the geometry are meant to represent. Terms like "node," "vertex," and "edge" are meant to refer to the specific geometry of the automata, and terms like "state" and "transition" are used to refer to the theory concepts.

# Run the Code

Users: cd .\team-repo-16-computing-visualizations\
Users: py display.py <fa_filename> <config_filename> <input_string>

