"""
Base controller.
"""


class BaseController:
    """
    Base controller.

    Defines classes that are useful for all other controllers to inherit.
    """

    class ControllerError(Exception):
        """
        Base class that all controller-related exception classes inherit from.
        """
        pass

    class InvalidArgument(ControllerError):
        """
        Indicates an argument was not usable.
        """
        pass

    class NoResultFound(ControllerError):
        """
        Indicates no matching instance was found for a get-or-error request.
        """
        pass
