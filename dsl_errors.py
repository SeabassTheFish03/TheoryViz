class DSL_Error(Exception):
    """Base exception for FSMIPR DSL"""

    pass


class MalformedCommandError(DSL_Error):
    """The command entered was malformed and cannot be read"""

    pass


class TypeNotSpecifiedError(DSL_Error):
    """The FA type was not specified"""

    pass


class TypeNotRecognizedError(DSL_Error):
    """The type specified is not recognized"""

    pass

class InvalidFormattingError(DSL_Error):
    """Specific fields within a DFA must exist"""

    pass

class InvalidFAError(DSL_Error):
    """Inconsistency within the FA - formatting and parsing cause no errors"""

    pass


class DoesNotExistError(DSL_Error):
    """Referenced an object that does not exist in the context"""

    pass

class TooManyArgumentsError(DSL_Error):
    """Number of arguments is not two (use assertion)"""

    pass

class MalformedCommandError(DSL_Error):
    """Within Move, some part of the command does not match the expectations of the interpreter"""

    pass

class MalformedCoordinatesError(DSL_Error):
    """The number of coordinates passed was not exacly equal to two (MOVE)"""

    pass

class NoPlayCalledError(DSL_Error):
    """No play or animate command called when pause is called"""

    pass

class NoPauseCalledError(DSL_Error):
    """No pause has been previously called when play is called"""

    pass

