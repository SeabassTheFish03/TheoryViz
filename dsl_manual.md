# Formatting of the DSL .viz file
Below are the commands for the FSMIPR DSL

# Load
Usage: `LOAD <file_name> AS <obj_name>`

Reads the file specified and attempts to interpret the contents. Stores the resulting FA in the variable name specified.

## On Success
If the FSMIPR can interpret the contents of the file (.txt or .json only), the program will respond with
``` Loaded the <FA> contained in <file_name> as <obj_name>```
The contents of the file must specify what type of FA it is (e.g. DFA, NFA, TM, etc.) or the file comprehension will fail. For confirmation, the program will tell the user what type of FA it thinks the data structure is.

## Errors
### Malformed Command
If there is no `AS` keyword separating the filename and the variable name, the program will throw a MalformedCommand error
### Type Not Specified
A required field for the contents of the file is `type`, which specifies what type of FA is contained in the document. The list of acceptable FAs can be found in the "Acceptable FAs" section of this manual. If there is no `type` field, the program will throw a TypeNotSpecified error.
### Type Not Recognized
If the `type` field is specified in the file, but is not one of the acceptable FAs contained in the "Acceptable FAs" section of this manual, the program will throw a TypeNotRecognized error.
### Invalid Formatting
Based on the type specified in the `type` field, the program will expect certain fields to be present. For the specific fields required for each type of FA, see the corresponding section for that FA in this manual. If any field cannot be interpreted or is not present, the program will throw an InvalidFormatting error. The error may go into more detail on where the formatting was incorrect, but this is not guaranteed.
### InvalidFA
If the formatting of the file is correct and the program can parse each part of it, but there is some irreconcilable inconsistency contained within, the program will throw an InvalidFA error.

# Show
Usage: `SHOW <obj_name>`

Shows the object indicated in the `<obj_name>` in the frame. If the object is already shown, does nothing.

## On Success
The object appears on the screen instantly.
If used during the SETUP phase, the object will be shown on screen at the start of the video. If used during the ANIMATE phase, the object will appear at that part of the animation timeline.

## Errors
### Does Not Exist
The object indicated at `<obj_name>` does not exist at the time of calling. The interpreter will raise a KeyError in this case.
### Too Many Arguments
The interpreter contains an assertion that the number of arguments is 2. If the assertion is false then an AssertionError will be raised with error text indicating this.

# MOVE
Usage: `MOVE <obj_name> TO <x, y>`

Moves the object indicated in the `<obj_name>` to the location indicated by `<x, y>`. If the object is already at the desired location, does nothing.

## On Success
The object's internal position is set to the specified coordinates. 

## Errors
### Does Not Exist
The object indicated at `<obj_name>` does not exist at the time of calling.
### Malformed Command
Some part of the command does not match the expectations of the interpreter.
### Malformed Coordinates
The number of coordinates passed was not exactly equal to 2.

# SHIFT
Usage: `SHIFT <obj_name> BY <x, y>`

Shifts the object indicated in the `<obj_name>` by the offset indicated by `<x, y>`.

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
Usage: `ANIMATE <Command>`

Animates the execution of the given command. Compatible with SHOW (uses the internal Manim `Create()`), MOVE, HIDE (uses the internal Manim `Uncreate()`)

## On Success



## Errors
### Does Not Exist
The object indicated at `<obj_name>` does not exist at the time of calling.

# Pause
Usage: `PAUSE <n>`
Pauses the animation for `n` seconds.

## On Success
The animation will stop and remain stopped for n seconds. After n seconds, the animation will continue.


## Errors
### Does Not Exist
The object indicated at `<obj_name>` does not exist at the time of calling. If there is no active animation or object that could be paused, it raises a DoesNotExist error.
### Malformed Command
If the number of arguments is incorrect or if <n> is not a valid number--i.e. negative--it throws a MalformedCommand error.

# Play
Usage: 'PLAY'

Resumes or starts the animation from its current state.
## On Success
The animation continues from its paused state.

## Errors
If no PAUSE had been previously called, then PLAY will raise an exception
