# -*- coding: utf-8 -*-

"""
nat_mch_telnet.py
~~~~~~~~~~~~~~~~~

This is a lazy implementation of the GenDev interface. The ultimate purpose
of this module is to be encapsulated within another module that really
implements that interface.
Unfortunately, NAT MCHs don't allow to go for a full implementation of the
GenDev interface based on an only communication interface.
The main operation that is only supported by the command line interface is the
firmware update. So that, this module based on Telnet, as access way, and the
command line interface of the MCH, shall only be used to perform a firmware
update and nothing else. For other operations, better use the module based on
the communication via the MHC web interface.
"""

from __future__ import annotations
import re
import time
import socket
import ipaddress
from collections import OrderedDict
from ..gendev_err import (
    ConnTimeout,
    NoRouteToDevice,
    FeatureNotSupported,
    ConnectionRefused,
)
from ..gendev_logger import GenDevLogger
from telnetlib import Telnet

__author__ = ["Felipe Torres González", "Ross Elliot"]
__copyright__ = "Copyright 2022, ESS MTCA Tools"
__credits__ = ["Jeong Han Lee"]
__license__ = "GPL-3.0"
__version__ = "1.2beta"
__maintainer__ = "Ross ELliot"
__email__ = "ross.elliot@ess.eu"
__status__ = "Development"


class NATMCHTelnet:
    """NATMCTelnet access an NAT MCH via Telnet.

    This module implements some operations using the command line interface
    via Telnet. Thus, the MCH has to be accessible in the network.
    The firmware update relies on **the mchconfig-server** to serve the
    firmware image using the FTP protocol.

    Supported operations:

    - Retrieve the general information of the MCH.
    - Firmware update of the MCH.
    - Enable DHCP mode of the MCH.
    """

    # Telnet prompt
    PROMPT = b"nat> "
    BOOT_TIME = 60

    def __init__(
        self,
        ip_address: str,
        backplane,
        port: int = 23,
        logger: GenDevLogger = None,
        hostname: str = None,
        open: bool = True,
        **kwargs,
    ):
        """Class constructor.

        Args:
            ip_address(str): the IP address of the MCH.
            backplane(BackplaneType): type of backplane in which the MCH is installed.
            port(int): port of the Telnet service (usually, 23).
            logger(Logger): reference to a logger that is being used.
            log_to_file(Bool): boolean flag to indicate if the log should be written
            to a file.
            hostname(str): hostname of the MCH.
            open(bool): whether to establish the connection at instantiation time or later. \
            Set this argument to False when a deferred link establishment is aimed.
            **telnet_ip_address(str): the ip address of the telnet \
            connection, if not equal to the IP address of the MCH, i.e. when \
            connecting via a MOXA (optional).
            **tftp_server_address(str): IP address of the machine hosting the TFTP \
            server with the fw images. Default value = **172.30.4.69**.
            **tftp_server_fw_path(str): path to the fw binaries in the TFTP server. \
            Default value = "fw/".

        Raises:
            ConnTimeout: if the connection to the device gets lost.
            NoRouteToDevice: if the device is not reachable.
        """
        self.ip_address = ip_address
        self.backplane = backplane
        self.hostname = hostname
        self.port = port

        # Optional arguments

        # If no telnet IP address is provided, use MCH IP address
        if "telnet_ip_address" in kwargs:
            self._telnet_ip_address = kwargs["telnet_ip_address"]
        else:
            self._telnet_ip_address = self.ip_address

        if "tftp_server_address" in kwargs:
            self._server_ip = kwargs["tftp_server_address"]
        else:
            self._server_ip = "172.30.4.69"

        if "tftp_server_fw_path" in kwargs:
            self._fw_path = kwargs["tftp_server_fw_path"]
        else:
            self._fw_path = "fw/"

        if "log_to_file" in kwargs:
            self._log_to_file = kwargs["log_to_file"]
        else:
            self._log_to_file = False

        # Initialise Logger instance
        if isinstance(logger, (GenDevLogger)):
            self.logger = logger
        else:
            self.logger = GenDevLogger(logger=logger, log_to_file=self._log_to_file)

        self.logger.logger.info(
            "NATMCHTelnet - NAT MCH Telnet instance created."
            "\tMCH IP Address: {}".format(self.ip_address)
        )

        if open:
            self.open()
            self._session_open = True
        else:
            self._session = Telnet()
            self._session_open = False

        # Regular expresions for extracting the infomration relative to the
        # MCH from the version command.
        self._match_fw_ver = re.compile(r"Firmware(V\d{1,2}\.\d{1,2}\.\d{1,2})")
        # Search for the first occurrence of the token FPGA
        self._match_fpga_ver = re.compile(r"FPGA(V\d{1,2}\.\d{1,2})")
        self._match_mcu_ver = re.compile(r"AVR(\d{1,2}\.\d{1,2})")
        self._match_board_sn = re.compile(r"sn:(\d{6}-\d{4})")
        self._match_ip_addr = re.compile(r"ipaddress:((\d{1,3}\.?){4})")
        self._match_mac_addr = re.compile(r"ieeeaddress:(([\d\D]{2}:?){6})")
        self._match_subnet_mask = re.compile(r"networkmask:((\d{1,3}\.?){4})")
        self._match_gateway_addr = re.compile(r"defaultgateway:((\d{1,3}\.?){4})")
        self._match_hostname = re.compile("hostname:(.+?(?=\r))")
        self._match_dhcp_state = re.compile("dhcpstate:(.+?(?=\r))")

    def open(self, verbose=True):
        """Establish the connection to the target MCH.

        Raises:
            ConnTimeout: if the connection to the device gets lost.
            NoRouteToDevice: if the device is not reachable.
            ConnectionRefused: if the telnet connection is refused.
        """
        if verbose:
            self.logger.logger.debug(
                "Opening Telnet connection to {}:{}.".format(
                    self._telnet_ip_address, self.port
                )
            )

        try:
            self._session = Telnet(self._telnet_ip_address, self.port, timeout=10)
            self._session_open = True
        except Exception as e:
            if isinstance(e, socket.timeout):
                msg = "Timeout while opening the link to the MCH using Telnet."
                self.logger.logger.error(msg)
                raise ConnTimeout(msg)
            elif isinstance(e, OSError) and (e.errno == 113 or e.errno == 101):
                msg = "Check the connectivity to the MCH" " using the IP: {}.".format(
                    self._telnet_ip_address
                )
                self.logger.logger.error(msg)
                raise NoRouteToDevice(msg)
            elif isinstance(e, OSError) and (e.errno == 111):
                msg = (
                    "Cannot connect to Telnet port {}:{} "
                    "Please close any existing "
                    "connections.".format(self._telnet_ip_address, self.port)
                )
                self.logger.logger.error(msg)
                raise ConnectionRefused(msg)
            else:
                self.logger.logger.error("Unhandled exception: {}".format(e.strerror))
                raise e

    def close(self):
        """Close the Telnet session.

        This is needed when multiple methods of this module are called in a row.
        """
        self.logger.logger.debug(
            "Closing Telnet connection to {}:{}.".format(self.ip_address, self.port)
        )
        self._session.close()
        self._session_open = False

    def _send_backspace(self, sleep: float = 0.25):
        """Internal method to write a backspace character to the MCH console.

        Some fields in the MCH interface are already populated, and must be
        cleared before writing the new value. The only way to do this is to
        issue a backspace character.
        """
        # Backspace is ASCII character 0x08, or special character ''\b'
        self._session.write(b"\b")
        time.sleep(sleep)

    def _send_command(self, command: str, sleep: int = 1, clear_buffer: bool = True):
        """Internal method for sending a low level command to the MCH.

        This command allows forgetting about the particular details of using
        a Telnet session behind the scenes. A regular command from the MCH
        command line interface can be sent through this interface without
        worrying about the underlying communication.

        Args:
            command: command to be sent to the MCH.
            sleep: amount of seconds to wait after sending a command.
            clear_buffer: send a carriage return before the command. This
            helps clearing previous garbage from the buffer, but
            it should be used with caution because there are
            commands that doesn't expect a carriage return after.
        """
        # clean up
        if clear_buffer:
            self._session.write(b"\r")
            self._session.read_until(self.PROMPT)
            time.sleep(sleep)
        self._session.write(command.encode("ascii") + b"\r")
        time.sleep(sleep)

    def _reboot(self, sleep: int = 70):
        """Internal command to send a reboot to the MCH.

        Args:
            sleep: indicates how many seconds to wait after returning from the
            method. Write a 0 to avoid it.
        """
        self.logger.logger.info("Rebooting MCH device.")
        if self._session_open is False:
            self.open()
        self._send_command("reboot")
        self.close()
        # self._session_open = False
        time.sleep(sleep)

    def _read_command(self) -> str:
        """Internal command to read the Telnet Rx buffer.

        This method attempts to read the content from the buffer without I/O
        blocking.

        Returns:
            A string containing the content of the Rx buffer.
        """
        response = self._session.read_very_eager()
        return response.decode("ascii")

    def _set_hostname(self):
        """Sets the hostname of the MCH device.

        Returns:
            True on success.
            False on failure.
        """
        self.logger.logger.info("Setting hostname to {}".format(self.hostname))

        if self._session_open is False:
            self.open()

        self._send_command("mchcfg")
        # Modify
        self._send_command("11", clear_buffer=False)
        # Clear previous entry
        for _ in range(0, 75):
            self._send_backspace()
        self._send_command(self.hostname, clear_buffer=False)
        self._send_command("q", clear_buffer=False)

        # TODO: re-enable this check
        # success = self._check_hostname()
        success = True

        self.close()

        return success

    def _check_hostname(self) -> bool:
        """Checks that the hostname set on the MCH matches
        the value provided.

        Returns:
            True if the hostname setting matches the expected string.
            False if the hostname setting does not match the expected string.
        """

        if self._session_open is False:
            self.open()

        self._send_command("ni")
        network_info = self._read_command()

        mch_hostname = self._match_hostname.search(network_info).group(1)

        success = False
        if mch_hostname == self.hostname:
            success = True

        self.close()

        return success

    def _enable_dhcp(self):
        """Enables DHCP mode on the MCH

        Returns:
            True if DHCP was enabled successfully.
            False if DHCP setting failed.
        """

        self._send_command("mchcfg")
        self._send_command("3", clear_buffer=False)
        for _ in range(0, 5):
            self._send_command("", clear_buffer=False)
        self._send_command("2", clear_buffer=False)
        for _ in range(0, 7):
            self._send_command("", clear_buffer=False)
        self._send_command("q", clear_buffer=False)

        # The MCH needs a reboot for the hostname
        # to update.
        self._reboot()
        # Wait for the MCH to complete the reboot process
        time.sleep(self.BOOT_TIME)

        # Finally, verify the change
        success = self._check_dhcp()

        return success

    def _check_dhcp(self):
        """Check wether DHCP is enabled.

        Returns:
            True if DHCP is enabled
            False if DHCP is disabled
        """

        if self._session_open is False:
            self.open()
        # Get MCH Network info
        self._send_command("ni")
        network_info = self._read_command()

        # Search for dhcp_state
        res = self._match_dhcp_state.search(network_info.replace(" ", ""))
        dhcp_state = self._parseSearch(res)

        enabled = False
        if dhcp_state == "enabled":
            enabled = True

        self.close()

        return enabled

    def _clear_ip_address(self):
        """Helper method to send enough backspace characters
        to clear an IP address
        """

        # Maximum length of an IP address is 15 characters
        for _ in range(0, 15):
            self._send_backspace()

    def _set_ip_addr(self):
        """Set the IP address of the MCH device."""

        if self._session_open is False:
            self.open()

        # Get network information
        self._send_command("ni")
        network_info = self._read_command().replace(" ", "")

        # Retrieve gateway address and netmask from network info
        res = self._match_gateway_addr.search(network_info)
        gateway_addr = self._parseSearch(res)
        res = self._match_subnet_mask.search(network_info)
        netmask = self._parseSearch(res)

        # Calculate broadcast ip_address
        ipv4net = ipaddress.IPv4Network(self.ip_address + "/" + netmask, False)
        broadcast_addr = ipv4net.broadcast_address.compressed

        # Trigger IP setting menu
        self._send_command("ip")

        # Clear the existing IP address, and update with new value
        self._clear_ip_address()
        self._send_command(self.ip_address, clear_buffer=False)
        # Clear the existing netmask, and update with new value
        self._clear_ip_address()
        self._send_command(netmask, clear_buffer=False)
        # Clear the existing broadcast address, and update with new value
        self._clear_ip_address()
        self._send_command(broadcast_addr, clear_buffer=False)
        # Clear the existing gateway address, and update with new value
        self._clear_ip_address()
        self._send_command(gateway_addr, clear_buffer=False)

        # Check we are at the confirmation prompt
        response = self._read_command()
        if not response.endswith("Are you really sure ?"):
            self.close()
            return False  # Failure

        # Issue confirmation 'y'
        self._send_command("y", clear_buffer=False)

        self.close()

        # Success
        return True

    def device_info(self) -> tuple[bool, OrderedDict]:
        """Retrieve the main information about the device.

        The information is returned in a dictionary with 2 categories:
        *Board* and *Network*.
        This feature is supported by all the implemented communication
        interfaces, so the best one is chosen when multiple are allowed.

        An example of the returned dictionary::

            {
              'Board': {
                'fw_ver': 'V2.21.8',
                'fpga_ver': 'V1.14',
                'mcu_ver': '1.2',
                'serial_num': '113522-1426'},
              'Network': {'ip_address': '172.30.5.238',
                'mac_address': '00:40:42:22:05:92',
                'subnet_address': '255.255.252.0',
                'gateway_address': '172.30.7.254'}
            }

        Returns:
            A tuple containing the a success flag in the first position. In the \
            second position:
            - On success, a dictionary with the device information.
            - On failure, an empty dictionary.

        Raises:
            ConnTimeout: if the connection to the device gets lost.
            NoRouteToDevice: if the device is not reachable.
        """
        if self._session_open is False:
            self.open()

        # Get info strings, and remove white space
        self._send_command("version")
        raw_info_version = self._read_command().replace(" ", "")
        self._send_command("ni")
        raw_info_network = self._read_command().replace(" ", "")

        if raw_info_version != "" and raw_info_network != "":
            resp_dict = OrderedDict()  # type: OrderedDict

            # Version info
            resp_dict["Board"] = dict()
            res = self._match_fw_ver.search(raw_info_version)
            resp_dict["Board"]["fw_ver"] = self._parseSearch(res)

            res = self._match_fpga_ver.search(raw_info_version)
            resp_dict["Board"]["fpga_ver"] = self._parseSearch(res)

            res = self._match_mcu_ver.search(raw_info_version)
            resp_dict["Board"]["mcu_ver"] = self._parseSearch(res)

            res = self._match_board_sn.search(raw_info_version)
            resp_dict["Board"]["serial_num"] = self._parseSearch(res)

            # Network info
            resp_dict["Network"] = dict()
            res = self._match_ip_addr.search(raw_info_network)
            resp_dict["Network"]["ip_address"] = self._parseSearch(res)

            res = self._match_mac_addr.search(raw_info_network)
            resp_dict["Network"]["mac_address"] = self._parseSearch(res)

            res = self._match_subnet_mask.search(raw_info_network)
            resp_dict["Network"]["subnet_address"] = self._parseSearch(res)

            res = self._match_gateway_addr.search(raw_info_network)
            resp_dict["Network"]["gateway_address"] = self._parseSearch(res)

            valid = True
        else:
            valid = False
            resp_dict = OrderedDict()

        self.close()

        return valid, resp_dict

    def set_dhcp_mode(self) -> tuple[bool, str]:
        """Enables DHCP mode in the network configuration of the device.

        Performs the following steps:
            - Enables DHCP mode on the MCH.
            - Sets the internal IP address value to match the address
              provided by the DHCP server(required to prevent DHCP lease
              issues).
            - Sets the hostname value.

        Returns
            If failure, a tuple containing False, and a message about the
            failure.
            If success, a tuple containing True, and an empty string.

        Raises:
            ConnectionError: If the device is not accessible.
            NoValidConn: If no valid connection types supporting this feature
                         are used by the device.
        """
        self.logger.logger.info("Enabling DHCP mode.")

        if self._session_open is False:
            self.open()

        total_success = True
        success = [True] * 3
        response = ""

        # Enable DHCP mode
        success[0] = self._enable_dhcp()
        if not success[0]:
            response = "Enabling of DHCP mode failed.\r\n"

        # Set the internal IP address
        success[1] = self._set_ip_addr()
        if not success[1]:
            response = response + "Setting IP address failed.\r\n"

        # Set the hostname
        success[2] = self._set_hostname()
        if not success[2]:
            response = response + "Setting hostname failed.\r\n"

        # If any of the subtasks failed, fail overall
        if False in success:
            total_success = False

        self.close()

        return total_success, response

    def update_fw(self, fw_version: str, part: str = "MCH") -> tuple[bool, str]:
        """Update the firmware of the device.

        This method expects the firmware binary pointed by the value of the
        argument *fw_version* to be available in the TFTP server.
        Mainly, this method injects the command *update_firmware* to an NAT
        MCH.

        Args:
            fw_version: version release number for the new fw.
            part: not used

        Returns:
            If failure, it returns a tuple containing False, and a message
            about the failure.
            If success, it returns True,
        """
        self.logger.logger.info("Updating MCH firmware")

        if self._session_open is False:
            self.open()

        self._send_command("update_firmware")
        # Avoid clearing the buffer bewteen these commands because it would
        # skip the update mode in the MCH.
        self._send_command(
            "{}:{}{}/mch_fw_{}.bin".format(
                self._server_ip, self._fw_path, fw_version, fw_version
            ),
            clear_buffer=False,
        )
        # Erasing the internal memory. If it is attempted to read now from the
        # buffer, it will get the promt.
        time.sleep(30)
        # There's a useless promt which is received first, get rid of it, and
        # wait for the good one that should come when the flashing is finished.
        response_b = self._session.read_until(b"nat> ")  # type: bytes
        # Sometimes, at this point, the buffer has content, sometimes not.
        # It seems reasonable using a length 100 to detect this situation.
        if len(response_b) < 100:
            response_b = self._session.read_until(b"nat> ")
        response = response_b.decode("ascii")  # type: str

        # Let's see if the update was successful. The MCH prints the word
        # "successful" at the end of the process, just before the prompt.
        if "successful" in response:
            success = (True, "")
            self._reboot()
            # Finally, wait for the MCH to complete the reboot process
            time.sleep(50)
        else:
            # Something went wrong, let's check it!
            if "TFTP: could not get file" in response:
                # This error is mainly caused when the target fw_version
                # is not available in the TFTP server.
                success = (
                    False,
                    "The fw version {} couldn't be found in the"
                    " TFTP server".format(fw_version),
                )
            else:
                success = False, "Unknown error. Check the debug log."

        self.close()

        return success

    def set_configuration(
        self, category: str, data: OrderedDict, apply: bool = True
    ) -> tuple[bool, str]:
        """Change the configuration of the device.

        This method focuses on the configuration parameters that are not
        defined within a configuration script. Specifying the entire set of
        parameters is not mandatory, and also, a particular category of
        settings can be modified without affecting the rest.

        This method supports the following configuration categories (taken
        from the webpage names):

        - Backplane configuration [backplane]

        The configuration files are hosted by the server, and they are named
        following this way: `latest_mch_conf_<form factor>_<modifier>_cfg.txt`.
        For factor should match the type of chassis, while the modifier allows
        choosing a non-standard configuration.

        Args:
            category(str): the target set of parameters to be affected by the change. \
            The accepted values are previously listed.
            data(dic): dictionary containing modifiers that allow for choosing a particular \
            backplane configuration file.
            apply(bool): whether to reboot the MCH to make active the changes or not. \
            Disable rebooting when multiple changes are going to be performed in the device. \
            Reboot  the device after the last change.

        Returns:
            A tuple containing a `bool` indicating if the operation was successful,
            and an error message.

        Raises:
            ConnectionError: If the device is not accessible.
            NoRouteToDevice: when the device is not reachable after applying the \
            new configuration.
        """
        if category != "backplane":
            raise FeatureNotSupported(
                "The Telnet backend only supports changing "
                "the backplane configuration."
            )
        if not isinstance(data, dict):
            return (False, "Wrong data type passed.")

        if self._session_open is False:
            self.open()

        option = "generic"
        if "Backplane configuration" in data:
            if "option" in data["Backplane configuration"]:
                option = data["Backplane configuration"]["option"]

        self._send_command("upload_cfg", clear_buffer=True)
        # Provide enough timeout in case the network is slow
        self._send_command(
            "{}:latest_mch_conf_{}_{}_cfg.txt".format(
                self._server_ip,
                "{}u".format(int(self.backplane)),
                option,
            ),
            sleep=3,
            clear_buffer=False,
        )
        # Read the buffer to check whether the file was found in the TFTP server
        validfile = self._read_command()
        if "TFTP: getting file done" not in validfile:
            self.close()
            return False, "The backplane file wasn't found in the server. See the log."

        self._send_command("y", clear_buffer=False)
        self._send_command("", clear_buffer=True)

        if apply:
            self._reboot()

        self.close()

        return (
            True,
            "Expect some delay until the MCH is accessible in the network again.",
        )

    def _get_slot_state(self, amc_num, close_conn: bool = True):
        """Internal method to get the current state of an
        AMC slot.

        Args:
            amc_num(int): AMC slot number.
            close_conn(bool): Whether to close the telnet
               session when returning, or not.
               Default: True

        Returns:
            A string containing the state code {M1, M2, ... M7}
        """
        if self._session_open is False:
            self.open()

        # Get fru_info for all AMCs
        self._send_command("show_fru")
        fru_info = self._read_command()

        # Parse fru_info for line containing the requested AMC, and parse
        # the state
        match = re.search(r"AMC{}(\s+)(M\d)".format(amc_num), fru_info)

        # Check if the Telnet session should be closed
        if close_conn is True:
            self.close()

        if match is None:
            success = False
            state = "Unable to determine state of AMC {}. " "Check AMC number.".format(
                amc_num
            )
        else:
            success = True
            state = match.group(2)

        # State is in group 2 of returned regex search
        return (success, state)

    def _start_slot(self, amc_num, sleep: int = 2, upstream=False):
        """Internal method to start the card in an AMC slot

        Args:
            amc_num(int): AMC slot number to power on.
            sleep(int): Time to allow for the AMC to power down.
                        Default: 2 seconds

        Returns:
            True if successful
            False if unsuccessful
        """
        success = False

        # MCH fru_start command expects fru number, instead of AMC
        # number, where:
        #     fru_num = amc_num + 4
        fru_num = amc_num + 4

        # Check current state of the AMC, and leave Telnet session
        # open
        res, state = self._get_slot_state(amc_num, False)

        # If unable to get state of slot, return
        if res is False:
            self.close()
            return False

        if state == "M4":
            self.logger.logger.info("AMC{} is already powered up.".format(amc_num))
            success = True
        else:
            # Sleep to allow previous telnet connection to properly
            # close
            time.sleep(1)

            if self._session_open is False:
                self.open()

            self.logger.logger.info("Powering up AMC {}.".format(amc_num))
            # Send fru_start command
            self._send_command("fru_start {}".format(fru_num))
            fru_start = self._read_command()

            # Check if the slot has a start up delay
            if upstream or ("Upstream Power Up Delay active!" in fru_start):
                self.logger.logger.info(
                    "Slot has upstream delay set. Waiting 60s for AMC to power on..."
                )
                sleep = 65

            # Sleep to allow device in AMC slot to power on
            time.sleep(sleep)

            # Get updated state
            _, state = self._get_slot_state(amc_num)

            if state == "M4":
                success = True
                self.logger.logger.info(
                    "AMC {} powered up successfully.".format(amc_num)
                )
            else:
                self.logger.logger.warning(
                    "Failed to power on slot. Current state: {}.".format(state)
                )

        self.close()

        return success

    def _stop_slot(self, amc_num, sleep: int = 2):
        """Internal method to stop the card in an AMC slot

        Args:
            amc_num(int): AMC slot number to power off.
            sleep(int): Time to allow for the AMC to power down.
                        Default: 2 seconds

        Returns:
            True if successful
            False if unsuccessful
        """
        success = False

        # MCH shutdown command expects fru number, instead of AMC
        # number, where:
        #     fru_num = amc_num + 4
        fru_num = amc_num + 4

        # Check current state of the AMC, and leave Telent
        # session open
        res, state = self._get_slot_state(amc_num, False)
        # If unable to get state of slot, return
        if res is False:
            self.logger.logger.warning(
                "Unable to determine state of slot {}:\n  {}".format(amc_num, state)
            )
            self.close()
            return False

        if state == "M1":
            self.logger.logger.info("AMC{} is already powered down.".format(amc_num))
            success = True
        else:

            # Sleep to allow previous telnet connection to properly
            # close
            time.sleep(1)

            if self._session_open is False:
                self.open()

            self.logger.logger.info("Powering down AMC {}.".format(amc_num))
            # Send shutdown command
            self._send_command("shutdown {}".format(fru_num))

            # Sleep to allow device in AMC slot to power down
            self.logger.logger.info("Sleeping for {} seconds.".format(sleep))
            time.sleep(sleep)

            # Get updated state
            _, state = self._get_slot_state(amc_num)

            if state == "M1":
                success = True
                self.logger.logger.info(
                    "AMC {} powered down successfully.".format(amc_num)
                )
            else:
                self.logger.logger.warning(
                    "Failed to power down slot. Current state: {}.".format(state)
                )

        self.close()

        return success

    def _slot_status_all(self):
        """Internal method to get the current state of all
        AMC slots.

        Args:
            close_conn(bool): Whether to close the telnet
               session when returning, or not.
               Default: True

        Returns:
            A list of tuples containing the AMC number and state code {M1, M2, ... M7} for all slots.
            If a slot is empty, the entry in the list will contain None.
        """
        self.logger.logger.debug("Getting state of AMCs in chassis.")

        if self._session_open is False:
            self.logger.logger.debug("Session closed. Re-opening.")
            self.open()

        # Get fru_info for all AMCs
        self._send_command("show_fru")
        fru_info = self._read_command()

        self.close()

        # Search for populated AMC slots
        match = re.findall(r"AMC(\d+)(\s+)(M\d+)", fru_info)

        amcs = []

        # Create list for all AMCs
        for x in range(1, int(match[-1][0]) + 1):
            slot_state = [item for item in match if str(x) in item]
            if slot_state:
                self.logger.logger.debug(
                    "AMC{} slot is populated, and in the {} state.".format(
                        x, slot_state[0][2]
                    )
                )
                amcs.append((x, slot_state[0][2]))
            else:
                self.logger.logger.debug("AMC{} slot is unpopulated.".format(x))
                amcs.append((x, None))

        return amcs

    def _stop_all_slots(self):
        """Internal method to power down all AMC slots"""

        if self._session_open is False:
            self.open()

        self.logger.logger.info("Powering down all AMCs.")

        # Shutdown all slots
        self._send_command("shutdown all")

        self.logger.logger.info("All AMCs are now powered down.")

        self.close()

    def _determine_upstream(self):
        """Internal method to determine which AMCs are configured
        as 'Upstream', i.e the PCIe root-complex
        """
        if self._session_open is False:
            self.open()

        self.logger.logger.info("Determining which AMC(s) are configured as Upstream")

        # 'mch' command takes a while to return all info
        # so add an extended sleep period
        self._send_command("mch", sleep=2)
        mch_info = self._read_command()

        self.close()

        # Find the relevant lines in the output
        first = mch_info.find("VS #")
        last = mch_info.find("\r\nUpstream")
        pcie_info = mch_info[first:last].splitlines()

        """ Example info:
            ['  VS #  | Host    | NT-Host | Members',
             '  0       AMC01_4   none      AMC01_4 AMC02_4 AMC03_4 AMC04_4 AMC05_4 AMC06_4 AMC07_4 AMC08_4 AMC09_4 AMC10_4 AMC11_4 AMC12_4 ',
             '  1     ',
             '  2     ',
             '  3     ',
             '  4     ',
             '  5     ']
        """
        upstreams = []
        # There are upto 6  virtual switches
        for i in range(1, len(pcie_info)):
            # First line is the header
            match = re.findall(r"{}(\s+)AMC(\d+)_(\d)".format(i - 1), pcie_info[i])
            if len(match) > 0:
                self.logger.logger.info(
                    "AMC{} is the Upstream for Virtual Switch {}".format(
                        int(match[0][1]), i - 1
                    )
                )
                upstreams.append(int(match[0][1]))

        return upstreams

    def reboot_slot(self, amc_num):
        """ Method to power cycle an individual AMC slot.

        Args:
            amc_num: AMC slot number to power cycle.

        Returns:
            A tuple containing the a success flag in the first position. In the \
            second position:
            - On success, an empty string.
            - On failure, a string containing the failure message.
        """
        self.logger.logger.info("Rebooting AMC in slot {}".format(amc_num))

        response = ""

        # Sleep time
        shutdown_sleep = 5
        start_sleep = 5

        # Shutdown slot
        success = self._stop_slot(amc_num, shutdown_sleep)
        if success is False:
            response = "Failed to power down card in AMC slot {}.".format(amc_num)
            self.logger.logger.warning(response)
            return (success, response)

        # Allow time for session to update
        time.sleep(1)

        # Start slot
        success = self._start_slot(amc_num, start_sleep)
        if success is False:
            response = "Failed to power up card in AMC slot {}.".format(amc_num)
            self.logger.logger.warning(response)

        return (success, response)

    def reboot_all_slots(self):
        """ Method to power cycle all AMC slots.

        Returns:
            A tuple containing the a success flag in the first position. In the \
            second position:
            - On success, an empty string.
            - On failure, a string containing the failure message.
        """

        if self._session_open is False:
            self.open()

        # Find which slots are populated
        slot_status = self._slot_status_all()

        # Shutdown all slots
        self._stop_all_slots()

        # Determine what AMC(s) are the Upstream (root-complex)
        upstreams = self._determine_upstream()
        upstream_state = []

        overall_success = True
        overall_response = ""
        # Power on relevant slots
        for slot in slot_status:
            if (slot[1] is not None) and (slot[1] != "M1"):
                if slot[0] not in upstreams:
                    success = self._start_slot(slot[0])
                    if success is False:
                        response = "Failed to power up card in AMC slot {}.".format(
                            slot[0]
                        )
                        self.logger.logger.warning(response)
                        overall_success = False
                        overall_response += "{}\n".format(response)
                else:
                    upstream_state.append(slot)
                    self.logger.logger.info(
                        "AMC{} is configured as an upstream. Will reboot last.".format(
                            slot[0]
                        )
                    )

        # Power on Upstream slots
        for slot in upstream_state:
            if (slot[1] is not None) and (slot[1] != "M1"):
                success = self._start_slot(slot[0], upstream=True)
                if success is False:
                    response = "Failed to power up card in AMC slot {}.".format(slot[0])
                    self.logger.logger.warning(response)
                    overall_success = False
                    overall_response += "{}\n".format(response)

        self.close()

        return (overall_success, overall_response)

    def _parseSearch(self, searchRes):

        if searchRes is None:
            resString = ""
        else:
            resString = searchRes.group(1)

        return resString
