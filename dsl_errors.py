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


class DoesNotExistError(DSL_Error):
    """Referenced an object that does not exist in the context"""

    pass
