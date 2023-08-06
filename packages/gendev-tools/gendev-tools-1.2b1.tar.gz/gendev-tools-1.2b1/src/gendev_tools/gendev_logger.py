# -*- coding: utf-8 -*-

"""
gendev_logger.py
~~~~~~~~~~

Contains helper methods for logging.
"""

from __future__ import annotations
import logging
from os import path, mkdir
from datetime import datetime

__author__ = "Ross Elliot"
__copyright__ = "Copyright 2021, ESS MTCA Tools"
__credits__ = ["Ross Elliot", "Felipe Torres González", "Jeong Han Lee"]
__license__ = "GPL-3.0"
__version__ = "1.2beta"
__maintainer__ = "Ross Elliot"
__email__ = "ross.elliot@ess.eu"
__status__ = "Development"


class GenDevLogger:
    def __init__(
        self,
        logger: logging.Logger = None,
        logname: str = None,
        logdir: str = "./logs",
        format: str = "%(asctime)s - %(levelname)s - %(message)s",
        log_level: int = logging.INFO,
        log_to_file: bool = False,
    ):
        """Class constructor.

        Args:
            logger(Logger): reference to an external Logger
            object to be used.
            logname(str): custom string for the log name.
            logdir(str): path to log directory.
            format(str): custom string defining the Logger
            format.
            log_level(int): log level to use.
        """

        self.format = format
        self.log_level = log_level
        self.logdir = logdir
        self.log_to_file = log_to_file

        # If no logname is provided, generate
        # the default one
        if logname is None:
            self.logname = self.genLogName(self.logdir)
        else:
            self.logname = self.logdir + "/" + logname

        # Specified logdir must exist
        if self.log_to_file:
            if not path.isdir(logdir):
                mkdir(logdir)

        # If a Logger object is provided, use it
        if logger is not None:
            self.logger = logger
            self._formatter = None
        else:
            # Create Logger object, and configure
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.DEBUG)
            # Set default format
            self.setDefaultFormat()

            # Add default stream handlers
            if (not self.logger.hasHandlers()) or (len(self.logger.handlers) == 0):
                self.addDefaultHandlers(filename=self.logname)

    def setDefaultFormat(self):
        """Create a logging.Formatter instance, and provide
        the formatter string.
        """

        self._formatter = logging.Formatter(self.format)

    def addDefaultHandlers(self, filename):
        """Method to add default logging stream
           handlers to the Logger object.

        The default handlers are:
         - logging.StreamHandler(), for logging to
           the console.
         - logging.FileHandler, for logging to a file.

        Args:
            filename(str): name for the generated
            log file.
        """

        # Create handlers (console and file)
        h_console = logging.StreamHandler()

        if self.log_to_file:
            h_file = logging.FileHandler(filename)
            h_file.setLevel(logging.DEBUG)

        # If there is a defined format string, use it
        if self._formatter is not None:
            h_console.setFormatter(self._formatter)
            if self.log_to_file:
                h_file.setFormatter(self._formatter)

        h_console.setLevel(logging.INFO)

        # Add handlers to Logger object
        self.logger.addHandler(h_console)
        if self.log_to_file:
            self.logger.addHandler(h_file)

    def genLogName(self, dirname):
        """Generate a unique name for the log.'

        Will be of the ISO date format:

            ''YYYY_MM_DD_HHMMSS.txt''
        """

        # Get today's date/time in datetime format
        today = datetime.today()

        # Form log name
        logname = "{}/log_{}{:02}{:02}_{:02}{:02}{:02}.txt".format(
            dirname,
            today.year,
            today.month,
            today.day,
            today.hour,
            today.minute,
            today.second,
        )

        return logname
