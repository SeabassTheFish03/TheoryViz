# Formatting of the DSL .viz file
Below are the commands for the FSMIPR DSL

| Command   | Purpose |
| -------- | ------- |
| LOAD | Loads a finite automaton (FA) from a file into memory.   |
| SHOW | Displays an FA object in the frame.     |
| MOVE    | Moves an FA object to a specified location.    |
| SHIFT | Shifts an FA object by a specified offset.    |
| ANIMATE | Creates an animation for the given command.   |
| PAUSE    | Pauses the animation for a specified duration. |
| PLAY    | Resumes or starts the animation from its current state.   |

# Load

Purpose: Reads the file specified and attempts to interpret the contents. Stores the resulting FA in the variable name specified.

Syntax: `LOAD <file_name> AS <obj_name>`

Parameters:
- <file_name>: Path to a .txt or .json file specifying the FA structure.
- <obj_name>: The variable name for the loaded FA.

## On Success
If the FSMIPR can interpret the contents of the file (.txt or .json only), the program will respond with
``` Loaded the <FA> contained in <file_name> as <obj_name>```
The contents of the file must specify what type of FA it is (e.g. DFA, NFA, TM, etc.) or the file comprehension will fail. For confirmation, the program will tell the user what type of FA it thinks the data structure is.

## Errors
### Malformed Command
Missing `AS` keyword separating the filename and the variable name. Example: LOAD dfa.json my_dfa.

### Type Not Specified
Missing type field in the file. Ensure the FA type is declared. The list of acceptable FAs can be found in the "Acceptable FAs" section of this manual.

### Type Not Recognized
The type field specifies an unsupported FA type.

### Invalid Formatting
File contents do not meet the formatting requirements for the FA type. The error may go into more detail on where the formatting was incorrect, but this is not guaranteed.

### InvalidFA
If the formatting of the file is correct and the program can parse each part of it, but there is some irreconcilable inconsistency contained within, the program will throw an InvalidFA error.

# Show

Purpose: Shows the object indicated in the `<obj_name>` in the frame. If the object is already shown, does nothing.

Syntax: `SHOW <obj_name>`

Parameters:
- <obj_name>: The name of the FA object to display.

## On Success
The object appears on the screen instantly.
If used during the SETUP phase, the object will be shown on screen at the start of the video. If used during the ANIMATE phase, the object will appear at that part of the animation timeline.

## Errors
### Does Not Exist
The object indicated at `<obj_name>` does not exist at the time of execution. The interpreter will raise a KeyError in this case.
### Too Many Arguments
The interpreter contains an assertion that the number of arguments is 2. If the assertion is false then an AssertionError will be raised with error text indicating this.

# MOVE
Purpose:
Moves the object indicated in the `<obj_name>` to the location indicated by `<x, y>`. If the object is already at the desired location, does nothing.

Syntax: `MOVE <obj_name> TO <x, y>`

Parameters:
- <obj_name>: The name of the FA object to move.
- <x, y>: The target coordinates.

## On Success
The object's internal position is set to the specified coordinates. 

## Errors
### Does Not Exist
The object indicated at `<obj_name>` does not exist at the time of calling.
### Malformed Command
Syntax does not match the expected structure.
### Malformed Coordinates
The number of coordinates passed was not exactly equal to 2.

# SHIFT
Purpose: Shifts the object indicated in the `<obj_name>` by the offset indicated by `<x, y>`.

Syntax: `SHIFT <obj_name> BY <x, y>`

Parameters:
-<obj_name>: The name of the FA object to shift.
- <x, y>: The offset values.

## On Success
The object's internal position is shifted by the specified offest.

## Errors
### Does Not Exist
The object indicated at `<obj_name>` does not exist at the time of calling.
### Malformed Command
Some part of the command does not match the expectations of the interpreter.
### Malformed Coordinates
The number of coordinates passed was not exactly equal to 2.

# Animate
Purpose: 
Animates the execution of the given command. Compatible with SHOW (uses the internal Manim `Create()`), MOVE, HIDE (uses the internal Manim `Uncreate()`)

Syntax: `ANIMATE <Command>`

Parameters:
- <Command>: A supported command to be animated (e.g., SHOW, MOVE).

## On Success
Animates the given command with visual effects.


## Errors
### Does Not Exist
The object indicated at `<obj_name>` does not exist at the time of execution.

### Unsupported Command
The specified command cannot be animated. 

# Pause
Purpose: 
Pauses the animation for `n` seconds.

Syntax: `PAUSE <n>`

Parameters:
- <n>: Duration in seconds.

## On Success
The animation will stop and remain stopped for n seconds. After n seconds, the animation will continue.


## Errors
### Does Not Exist
The object indicated at `<obj_name>` does not exist at the time of calling. If there is no active animation or object that could be paused, it raises a DoesNotExist error.
### Malformed Command
If the number of arguments is incorrect or if <n> is not a valid number--i.e. negative--it throws a MalformedCommand error.
### No Play Called
If no play or animate command has been previously called when pause is called, an exception is thrown.

# Play
Purpose: 
Resumes or starts the animation from its current state.

Syntax: 'PLAY'

## On Success
The animation continues from its paused state.

## Errors
### No Pause Called
If no PAUSE had been previously called, then PLAY will raise an exception
