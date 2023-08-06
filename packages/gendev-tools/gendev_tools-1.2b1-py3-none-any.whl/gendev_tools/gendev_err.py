# -*- coding: utf-8 -*-

"""
gendev_err.py
~~~~~~~~~~~~~

Custom exeception types for the GenDev Tools library.
"""

__all__ = [
    "ConnNotImplemented",
    "ConnTimeout",
    "NoRouteToDevice",
    "FeatureNotSupported",
]
__author__ = "Felipe Torres González"
__copyright__ = "Copyright 2021, ESS MCH Tools"
__credits__ = ["Felipe Torres González", "Ross Elliot", "Jeong Han Lee"]
__license__ = "GPL-3.0"
__version__ = "1.2beta"
__maintainer__ = "Ross Elliot"
__email__ = "ross.elliot@ess.eu"
__status__ = "Development"


class ConnNotImplemented(Exception):
    """Connection Not Implemented Exception.

    This exception is raised when an operation relies on a particular
    connection type that is not implemented for the given device.
    """

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "ConnNotImplemented, {0} ".format(self.message)
        else:
            return "ConnNotImplemented has been raised"


class ConnTimeout(Exception):
    """Connection timeout Exception."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "ConnTimeout, {0} ".format(self.message)
        else:
            return "ConnTimeout has been raised"


class NoRouteToDevice(Exception):
    """No route to device Exception."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "NoRouteToDevice, {0} ".format(self.message)
        else:
            return "NoRouteToDevice has been raised"


class ConnectionRefused(Exception):
    """Connection refused Exception."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "ConnectionRefused, {0} ".format(self.message)
        else:
            return "ConnectionRefused has been raised"


class FeatureNotSupported(Exception):
    """Feature not supported exception.

    This exception is raised when a feature is not possible with the given
    valid communication interfaces to the MCH.
    """

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "ConnTimeout, {0} ".format(self.message)
        else:
            return "ConnTimeout has been raised"


class WebChanged(Exception):
    """The content of the Web page has changed.

    This exception is raised when the parser fails analysing the content of the
    web interface of the device.
    """

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "WebChanged, {0} ".format(self.message)
        else:
            return "WebChanged has been raised"


class DHCPEnableFailed(Exception):
    """DHCP mode enable failed exception.

    This exception is raised when the enabling of DHCP mode
    has failed.
    """

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return " DHCPEnableFailed, {0} ".format(self.message)
        else:
            return "DHCPEnableFailed"
