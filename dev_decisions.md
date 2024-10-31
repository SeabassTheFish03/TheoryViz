# Dev Decisions
In this document, we explain some of the reasoning behind our design decisions to make the repo more accessible to developers who want to contribute/fork.
# Configurations and Inheritance
Since this is built on top of Manim, we are somewhat beholden to its inheritance structure, specifically for how Mobjects are created. To translate from our `config.toml` file to the different configurations required by the Mobjects we're using. First, we make a map from keys in the `config.toml` file (henceforth referred to as bigconfig) into recognizable keyword arguments. Then, we make a list enumerating which arguments (post-translation) are actually necessary for the mobject at hand.
Because the bigconfig is meant to be all-encompassing, and we prefer not to use the `toml` inheritance structure for simplicity, we have to filter out all the keywords that aren't important. For example, when extracting a vertex_config from the bigconfig, we don't care about what color the edges are, but we do care about the fill color of the labels. That's what the list is for. The list is ordered internally by class structure, starting with the lowest value and moving up the tree towards the `Mobject` class. At every level, we hand-picked the keyword arguments that are actually worth configuring. Once these two variables are created, we can map all the keys from bigconfig into Manim-readable keys, filter out the keys we don't need, and hand back a well-formatted config.
# Formatting of the FAs at Each Step of the Process
Through different parts of the rendering process, the FAs are represented in different ways, depending on their use. This section goes into detail on what those different configurations look like.
## JSON
The FA begins its life in the JSON file. In this representation, we can feed it directly into `automata-lib` and it can create its own internal representation. From here, it gets translated into an FA_Manager
## FA_Manager
There are different implementations pertaining to each different type of FA, but they all exist to wrap the `automata-lib` object along with the `mobject` representation of it. The manager is used to synchronize the internal states of both of these complicated objects and provide the user with an easy interface to interact with them.
### Mobject
The `mobject` representation itself has a few different components. The most obvious is the "ball and stick" diagram of the automaton itself. There are also `mobjects` for the string being process (which is updated internally to keep up with the transitions) and a transition table (which highlights itself in sync with the computation). These can be enabled/disabled depending on the user's preference.
### Automata-lib
`automata-lib` has its own implementation of automata internally. As the animation is rendering, the automaton stored within is also updating, which allows us to utilize the calculation algorithms built into `automata-lib` to calculate the next move.

# On AI
At the time of writing, generative AI, particularly LLMs, struggle to generate specific and complete JSON representations of DFAs. In our experience, they tend to miss important transitions and generate states that don't quite make sense. While AI is a great starting point, we suggest proofreading any outputs before inputting them into the system for best results.
