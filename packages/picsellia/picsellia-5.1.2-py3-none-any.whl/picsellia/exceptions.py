
class PicselliaError(Exception):
    """Base class for exceptions."""
    def __init__(self, message):
        """
        Arguments:
            message (str): Informative message about the exception.
            cause (Exception): The cause of the exception (an Exception
                raised by Python or another library). Optional.
        """
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class AuthenticationError(PicselliaError):
    """Raised when your token does not match to any known token"""
    pass


class UnauthorizedError(PicselliaError):
    """Raised when your token does not match to any known token"""
    pass


class ForbiddenError(PicselliaError):
    """Raised when your token does not match to any known token"""
    pass


class ResourceNotFoundError(PicselliaError):
    """Exception raised when a given resource is not found. """
    pass


class ResourceConflictError(PicselliaError):
    """Exception raised when a given resource already exists. """
    pass


class InvalidQueryError(PicselliaError):
    """ Indicates a malconstructed or unsupported query. This can be the result of either client
    or server side query validation. """
    pass


class NetworkError(PicselliaError):
    """Raised when an HTTPError occurs."""
    pass


class ApiLimitError(PicselliaError):
    """ Raised when the user performs too many requests in a short period
    of time. """
    pass


class ProcessingError(PicselliaError):
    """Raised when an algorithmic error occurs."""
    pass


class TyperError(PicselliaError):
    """Raised when a method argument has the wrong type"""
    pass


class UnsufficientRessourcesError(PicselliaError):
    """Raised when your token does not match to any known token"""
    pass


class NoDataError(PicselliaError):
    """Raised when you try to retrieve data from an empty datalake"""
    pass

class ImpossibleAction(PicselliaError):
    """Raised when an action is impossible"""
    pass

class PicselliaOutError(Exception):
    def __init__(self, picsellia_error : PicselliaError) -> None:
        super().__init__(picsellia_error)
        self.message = picsellia_error.message

    def __str__(self) -> str:
        return "Something went wrong.\n{}.".format(self.message)
