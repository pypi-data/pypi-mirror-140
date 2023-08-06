"""
Module containing exceptions.
"""


# Controller errors
class ControllerError(Exception):
    """
    Base exception for controller related errors.
    """
    def __init__(self, message=None):
        if message is None:
            message = "Undefined error."
        super(ControllerError, self).__init__(str(message))


class RedirectionError(ControllerError):
    """
    Page redirection error.
    """
    def __init__(self, message=None):
        super(RedirectionError, self).__init__(message)


# GUI -> Item errors
class ItemError(Exception):
    """
    Base exception for item related errors.
    """
    def __init__(self, message=None):
        if message is None:
            message = "Undefined error."
        super(ItemError, self).__init__(str(message))


class NotResizableError(ItemError):
    """
    Item can not be resized error.
    """
    def __init__(self, message=None):
        super(NotResizableError, self).__init__(message)


# Assets errors
class AssetsError(Exception):
    """
    Base exception for Assets related errors.
    """
    def __init__(self, message=None):
        if message is None:
            message = "Undefined error."
        super(AssetsError, self).__init__(str(message))


class AssetsDirectoryNotDefinedError(AssetsError):
    """
    Assets directory not defined error. When assets are being accessed by the Assets object, but no direcctory was
    defined.
    """
    def __init__(self, message=None):
        super(AssetsDirectoryNotDefinedError, self).__init__(message)


class AssetDoesNotExistError(AssetsError):
    """
    When an asset is being accessed but the directory or file does not exist.
    """
    def __init__(self, message=None):
        super(AssetDoesNotExistError, self).__init__(message)
