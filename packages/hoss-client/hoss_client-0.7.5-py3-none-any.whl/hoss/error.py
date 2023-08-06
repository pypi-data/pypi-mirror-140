class HossException(Exception):
    """A general exception raised by the hoss package"""
    pass


class NotAuthorizedException(HossException):
    """You are not authorized to access this API/resource"""
    pass


class NotFoundException(HossException):
    """The specified resource was not found"""
    pass


class AlreadyExistsException(HossException):
    """The specified resource already exists"""
    pass


class ServerCheckError(Exception):
    """An error occurred while trying to fetch the server version"""
    pass
