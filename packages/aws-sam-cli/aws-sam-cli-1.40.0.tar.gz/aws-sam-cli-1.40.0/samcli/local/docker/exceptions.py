"""
Docker container related exceptions
"""


class ContainerNotStartableException(Exception):
    pass


class NoFreePortsError(Exception):
    """
    Exception to raise when there are no free ports found in a specified range.
    """
