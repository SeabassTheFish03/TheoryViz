Below are the commands for the FSMIPR DSL

# Load
Usage: `LOAD <file_name> AS <obj_name>`

Reads the file specified and attempts to interpret the contents. Stores the resulting FA in the variable name specified.

## On Success
If the FSMIPR can interpret the contents of the file (.txt or .json only), the program will respond with
``` Loaded the <FA> contained in <file_name> as <obj_name> ```
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

# SHOW
Usage: 'SHOW <obj_name>'

Shows the object indicated in the <obj_name> in the frame. If the object is already shown, does nothing.

## On Success
The object appears on the screen instantly.
If used during the SETUP phase, the object will be shown on screen at the start of the video. If used during the ANIMATE phase, the object will appear at that part of the animation timeline.

## Errors
### Does Not Exist
The object indicated at <obj_name> does not exist at the time of calling.
