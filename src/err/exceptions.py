class BaseCustomException(Exception):
    """Base class for all custom exceptions in the application."""

    pass


class DocumentProcessingError(BaseCustomException):
    pass


class DocumentProcessingTime(BaseCustomException):
    pass
