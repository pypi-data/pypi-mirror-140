# -*- coding: utf-8 -*-

"""
nat_mch_moxa.py
~~~~~~~~~~~~~~~

Communication via Moxa is performed via a telnet connection. Therefore,
the Moxa class is implemented as a child class that inherits from NATMCHTelnet.
As such, all operations supported by the telnet class are supported by the MOXA
class.
"""
import time
import re
from gendev_tools.nat_mch.nat_mch_telnet import NATMCHTelnet
from ..gendev_logger import GenDevLogger

__author__ = "Ross Elliot"
__copyright__ = "Copyright 2021, ESS MTCA Tools"
__credits__ = ["Felipe Torres González", "Jeong Han Lee"]
__license__ = "GPL-3.0"
__version__ = "1.2beta"
__maintainer__ = "Ross Elliot"
__email__ = "ross.elliot@ess.eu"
__status__ = "Development"


class NATMCHMoxa(NATMCHTelnet):
    """NATMCHMoxa access an NAT MCH via Moxa.

    This module implements some operations using the command line interface
    via Moxa. Thus, the MCH has to be connected to a Moxa serial server.
    The firmware update relies on **the mchconfig-server** to serve the
    firmware image using the FTP protocol.

    Supported operations:
    - Retrieve the general information of the MCH.
    - Firmware update of the MCH.
    - Enabling of DHCP on the MCH.
    """

    def __init__(
        self,
        mch_ip_address: str,
        moxa_ip_address: str,
        port: int,
        backplane,
        logger: GenDevLogger = None,
        hostname: str = None,
        **kwargs,
    ):
        """Class constructor.

        Args:
            ip_address: the IP address of the Moxa serial server.
            port: port of the Moxa server that the MCH is connected to, in the
                  range [0, 1, ... 16]
            logger: reference to a logger that is being used

        Raises:
            gendev_err.ConnTimeout if the device is not reachable.
        """

        # Validate Moxa port is within range
        if 0 <= port >= 16:
            raise ValueError("Moxa port must be in range of [0 to 16]")

        # Real Telnet port used to connect to Moxa is in range of [4000 t0 4016]
        self.port = 4000 + port
        self.moxa_ip_address = moxa_ip_address

        if "log_to_file" in kwargs:
            log_to_file = kwargs["log_to_file"]
        else:
            log_to_file = False

        # Initialise parent class and inherit methods and properties
        super().__init__(
            ip_address=mch_ip_address,
            backplane=backplane,
            port=self.port,
            logger=logger,
            hostname=hostname,
            telnet_ip_address=moxa_ip_address,
            log_to_file=log_to_file,
        )

    def open(self):
        """Open the Telnet connection to the MOXA

        Override the parent method to add required delay
        """
        self.logger.logger.debug(
            "Opening MOXA connection to {}:{}.".format(self.moxa_ip_address, self.port)
        )
        super().open(verbose=False)
        self.logger.logger.debug("Sleeping for 2 seconds.")
        time.sleep(2)

    def close(self):
        """Close the MOXA session.

        This is needed when multiple methods of this module are called in a row.
        Overriden method for MOXA to add required delay.
        """
        self.logger.logger.debug(
            "Closing MOXA connection to {}:{}.".format(self.ip_address, self.port)
        )
        self._session.close()
        self.logger.logger.debug("Sleeping for 2 seconds.")
        time.sleep(2)
        self._session_open = False

    def _send_command(
        self,
        command: str,
        sleep: int = 1,
        clear_buffer: bool = True,
        chunk_size: int = 3,
    ):
        """Internal method for sending a low level command to the MCH via a Moxa
        server.

        This command allows forgetting about the particular details of using
        a Telnet session behind the scenes. A regular command from the MCH
        command line interface can be sent through this interface without
        worrying about the underlying communication.
        This implementation for the MOXA required splitting any command into
        chunks of 3-characters or less, to remedy an issue with the MOXA where
        some of the characters are lost during transmission.

        Args:
            command: command to be sent to the MCH.
            sleep: amount of seconds to wait after sending a command.
            clear_buffer: send a carriage return before the command. This
            helps clearing previous garbage from the buffer, but
            it should be used with caution because there are
            commands that doesn't expect a carriage return after.
            chunk_size: number of characters to use for each chunk when
            splitting the command string.
        """
        # clean up
        if clear_buffer:
            self._session.write(b"\r")
            buf = self._session.read_until(b"nat> ", timeout=2)
            if b"nat> " not in buf:
                self.logger.logger.debug("Failed to clear buffer. Try again.")
                # Re-open session
                self.open()
                self._session.write(b"\r")
                buf = self._session.read_until(b"nat> ", timeout=2)
            time.sleep(sleep)
        # Split command into 3-char chunks
        pattern = ".{{1,{chunk_size}}}".format(chunk_size=chunk_size)
        chunks = re.findall(pattern, command)
        # Write each chunk serially
        for chunk in chunks:
            self._session.write(chunk.encode("ascii"))
            time.sleep(sleep)
        # Send carriage return to issue command
        self._session.write(b"\r")
        time.sleep(sleep)
