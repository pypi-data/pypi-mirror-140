# -*- coding: utf-8 -*-

"""
nat_mch.py
~~~~~~~~~~

Implementation of the GenDev interface for NAT MCHs.

This module fully implements the GenDev interface. This is achieved by the use
of several sub-modules which implement different ways to access an NAT MCH.
This device doesn't allow a simple and straightforward implementation using an
only interface, so that, multiple communication ways are used. The golden rule
is achieving a reliable solution with the best performance.
"""

from __future__ import annotations
import logging
from pprint import pformat
from enum import IntEnum
from collections import OrderedDict
from difflib import Differ
from ..gendev_interface import GenDevInterface, ConnType
from ..gendev_err import ConnNotImplemented, FeatureNotSupported, DHCPEnableFailed
from ..gendev_logger import GenDevLogger
from .nat_mch_web import NATMCHWeb
from .nat_mch_telnet import NATMCHTelnet
from .nat_mch_moxa import NATMCHMoxa

__author__ = "Felipe Torres González"
__copyright__ = "Copyright 2021, ESS MCH Tools"
__credits__ = ["Felipe Torres González", "Ross Elliot", "Jeong Han Lee"]
__license__ = "GPL-3.0"
__version__ = "1.2beta"
__maintainer__ = "Ross Elliot"
__email__ = "ross.elliot@ess.eu"
__status__ = "Development"


class BackplaneType(IntEnum):
    """Enum defining the types of backplane for mTCA crates."""

    B1U = 1
    B3U = 3
    B5U = 5
    B9U = 9


class NATMCH(GenDevInterface):
    """NAT MCH device.

    This class is connection-agnostic, which means there are no internal
    details about the particular implementation attending to the chosen
    connection type. This class should call child subclasses depending on
    the chosen connection type and format the information properly.

    When two interfaces could be used for the same purpose, the most reliable
    should be used. That is auto managed by the class when all the supported
    communication interfaces are properly specified to the module.

    The order in which the communication interfaces are prioritized is:
    `Web >> SSH >> Telnet >> MOXA >> Serial`

    Within the interface module, an enumerated type is provided defining all
    the allowed communication methods. Specify what are supported by the
    MCH when instantiating this class. As a rule of thumb, if the MCH is able
    to get a valid IP address, all the interfaces relying on the network are
    available, the regular ETHER communication type is the best option, as it
    directly access the resources from the web server of the MCH (fastest and
    most reliable method), but ETHER doesn't support the execution of all the
    methods offered by the API, check the documentation of each method to
    check what type of connection is required.
    """

    def __init__(
        self,
        ip_address: str,
        allowed_conn: list[ConnType],
        backplane: BackplaneType,
        device_model: str = "MCH",
        manufacturer: str = "NAT",
        hostname: str = None,
        conn_ip_address: str = None,
        conn_port: int = None,
        logger: logging.Logger = None,
        log_to_file: bool = False,
    ):
        """Class constructor.

        Initialization of an MCH class.In order to enable logging, specify
        a valid reference to a Logger instance.

        Args:
            ip_addr(str): the given IP to the MCH in CSEntry.
            allowed_conn(list[ConnType]): list of connections supported by the MCH.
            backplane(BackplaneType): type of backplane of the crate in which the MCH is installed.
            device_model(str): string identifying the device.
            manufacturer(str): name of the manufacturer.
            hostname(str): the registered hostname in CSEntry for the MCH.
            conn_ip_address(str): ip address used for the communication with the MCH (MOXA backend)
            conn_port(str): port used for the communication with the MCH (MOXA backend).
            logger: reference to a Logger instance.

        Raises:
            ConnNotImplemented: if a communication interface that
            is not supported by the implementation was included in the
            *allowed_con* argument.
        """
        self.ip_address = ip_address
        self.device_model = device_model
        self.manufacturer = manufacturer
        self.serial_num = ""
        self.fw_ver = ""
        self.allowed_conn = allowed_conn
        self.hostname = ""
        self.mac_address = ""
        self.backplane = backplane
        self._conn_ip_address = conn_ip_address
        self._conn_port = conn_port
        self._log_to_file = log_to_file

        # Create a GenDevLogger instance from Logger object
        self.logger = GenDevLogger(logger=logger, log_to_file=self._log_to_file)
        self.logger.logger.info(
            "GenDev::Constructor - A new device has been registered"
            "\tDevice model: {}".format(self.device_model)
        )

        if log_to_file:
            self.logger.logger.info(
                "Log file located at: {}".format(self.logger.logname)
            )

        # Open the valid connections
        if ConnType.ETHER in self.allowed_conn:
            self._eth_conn = NATMCHWeb(
                self.ip_address,
                logger=self.logger,
            )
        if ConnType.TELNET in self.allowed_conn:
            self._tel_conn = NATMCHTelnet(
                ip_address=self.ip_address,
                hostname=self.hostname,
                backplane=self.backplane,
            )
        if ConnType.SERIAL in self.allowed_conn:
            raise ConnNotImplemented(
                "The serial interface is not implemented" " for NAT MCHs."
            )
        if ConnType.MOXA in self.allowed_conn:
            self._mox_conn = NATMCHMoxa(
                mch_ip_address=self.ip_address,
                moxa_ip_address=self._conn_ip_address,
                port=self._conn_port,
                backplane=self.backplane,
                logger=self.logger,
                hostname=self.hostname,
            )
        if ConnType.SSH in self.allowed_conn:
            raise ConnNotImplemented(
                "The SSH interface is not implemented" " for NAT MCHs."
            )

        # This dict holds a look-up table to translate argument keys, given to the
        # methods of this class, to keys from the configuration files.
        self._cfgkeys = {
            "basecfg": {
                "cfgkey": "Base MCH parameter",
            },
            "pcie": {
                "cfgkey": "PCIe parameter",
            },
            "backplane": {"cfgkey": "Backplane configuration"},
        }

    def device_info(self) -> tuple[bool, dict]:
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
            FeatureNotSupported: if the given allowed communication \
            interfaces don't allow running this method.
            oRouteToDevice: when the device is not reachable in the network, or the \
            device pointed by the given IP address is not an MCH.
        """
        if ConnType.ETHER in self.allowed_conn:
            valid, response = self._eth_conn.device_info()
        elif ConnType.TELNET in self.allowed_conn:
            valid, response = self._tel_conn.device_info()
        elif ConnType.MOXA in self.allowed_conn:
            valid, response = self._mox_conn.device_info()
        else:
            msg = (
                "Impossible to retrieve the device "
                "information with the given allowed "
                "communication interfaces to the MCH."
            )
            self.logger.logger.error(msg)
            raise FeatureNotSupported(msg)

        if valid:
            self.mac_address = response["Network"]["mac_address"]
            self.serial_num = response["Board"]["serial_num"]
            self.fw_ver = response["Board"]["fw_ver"]
            self.logger.logger.info(
                "\n[Board info]\n \
                   Serial number:    {}\n \
                   FPGA version:     {}\n \
                   Firmware version: {}\n \
                   MCU Version:      {}\n".format(
                    self.serial_num,
                    response["Board"]["fpga_ver"],
                    response["Board"]["fw_ver"],
                    response["Board"]["mcu_ver"],
                )
            )
            self.logger.logger.info(
                "\n[Network info]\n \
                   IP Address:  {}\n \
                   MAC Address: {}\n \
                   Subnet:      {}\n \
                   Gateway:     {}\n".format(
                    self.ip_address,
                    self.mac_address,
                    response["Network"]["subnet_address"],
                    response["Network"]["gateway_address"],
                )
            )

        return valid, response

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
            DHCPEnableFailed: If the setting fails.
            NoValidConn: If no valid connection types supporting this feature
                         are used by the device.
        """
        if ConnType.TELNET in self.allowed_conn:
            success, response = self._tel_conn.set_dhcp_mode()
        elif ConnType.MOXA in self.allowed_conn:
            success, response = self._mox_conn.set_dhcp_mode()
        else:
            msg = (
                "Setting the DHCP mode is not supported for the given "
                "connection type"
            )
            self.logger.logger.error(msg)
            raise FeatureNotSupported(msg)

        if not success:
            self.logger.logger.error(response)
            raise DHCPEnableFailed(response)

        return success, response

    def update_fw(self, fw_version: str, part: str = None) -> tuple[bool, str]:
        """Update the firmware of the device.

        This feature is only supported by the Telnet communication interface.

        This method expects the firmware binary pointed by the value of the
        argument *fw_version* to be available in the TFTP server.
        Mainly, this method injects the command *update_firmware* to an NAT
        MCH.

        Args:
            fw_version: version release number for the new fw.
            part: modifier allowing the update of different parts within
                  the same device.

        Returns:
            If failure, it returns a tuple containing False, and a message
            about the failure.
            If success, it returns (True,)

        Raises:
            ConnectionError: If the device is not accessible.
        """
        if ConnType.TELNET in self.allowed_conn:
            valid, response = self._tel_conn.update_fw(fw_version)
        elif ConnType.MOXA in self.allowed_conn:
            valid, response = self._mox_conn.update_fw(fw_version)
        else:
            msg = (
                "Impossible to update the fw of the "
                "device with the given allowed "
                "communication interfaces to the MCH."
            )
            self.logger.logger.error(msg)
            raise FeatureNotSupported(msg)

        if valid:
            self.logger.logger.info(response)
        else:
            self.logger.logger.error(response)

        return valid, response

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

        - Base Configuration [basecfg]
        - PCIe Virtual Switches [pcie]
        - Backplane configuration [backplane]

        Args:
            category(str): the target set of parameters to be affected by the change. \
            The accepted values are previously listed.
            data(dic): dictionary containing the values to be modified.
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
        if ConnType.ETHER in self.allowed_conn and category != "backplane":
            valid, response = self._eth_conn.set_configuration(category, data, apply)
        elif ConnType.TELNET in self.allowed_conn and category == "backplane":
            valid, response = self._tel_conn.set_configuration(category, data, apply)
        elif ConnType.MOXA in self.allowed_conn and category == "backplane":
            valid, response = self._mox_conn.set_configuration(category, data, apply)
        else:
            msg = (
                "Setting the MCH configuration using the "
                "{} backend is not implemented.".format(str(self.allowed_conn))
            )
            self.logger.logger.error(msg)
            raise FeatureNotSupported(msg)

        if not valid:
            self.logger.logger.error(response)

        return valid, response

    def get_configuration(self, category: str = None) -> tuple[bool, OrderedDict]:
        """Get the configuration of the device.

        This method returns a dictionary containing the configuration
        parameters of the device implementing this interface. If the device
        has several configuration categories, keys from the dictionary might
        contain other dictionaries.

        This method supports the following configuration categories (taken
        from the webpage names):

        - Base Configuration [basecfg]
        - PCIe Virtual Switch Configuration [pcie]
        - Backplane Configuration [backplane]

        Args:
            category(str): points to a subset of the configuration parameters of \
            the device. Use the values given between brackets from the previous \
            item list.

        Returns:
            tuple[bool, OrderedDict]: The first element indicates the success of \
            the operation, the second is an ordered dict containing the settings in \
            the same order as they are found in the web page. When *category* = \
            **backplane**, the dictionary contains only one key (*Backplane \
            config file*) and the whole configuration file as value for that \
            key.
        """
        if ConnType.ETHER in self.allowed_conn:
            valid, response = self._eth_conn.get_configuration(category)
        else:
            msg = (
                "Retrieving the MCH configuration using the "
                "{} backend is not implemented.".format(str(self.allowed_conn))
            )
            self.logger.logger.error(msg)
            raise FeatureNotSupported(msg)

        if valid:
            self.logger.logger.debug(pformat(response))
        else:
            self.logger.logger.error(response)

        return valid, response

    def check_configuration(
        self, category: str, config: OrderedDict
    ) -> tuple[bool, str]:
        """Check the settings of the device.

        This method retrieves the configuration parameters of a device,
        and performs a comparison against the values given by `config`.
        When differences are detected, the values are reported to a log,
        the method only returns a general message indicating the result
        of the check.

        Args:
            category (str): a key indicating the target settings when
            a device has several subset of configuration parameters.
            config (OrderedDict): a dictionary containing the expected
            values for all the parameters that are aimed to check.

        Returns:
            tuple[bool, str]: a boolean value indiciating whether the
            checking was successful or not; and a text message when the
            checking was unsuccesful.
        """
        if ConnType.ETHER not in self.allowed_conn:
            msg = (
                "Accessing the MCH configuration is only possible "
                "when using the Web backend."
            )
            self.logger.logger.error(msg)
            raise FeatureNotSupported(msg)

        # Is `config` good?
        try:
            valid_args = self._eth_conn._check_arguments(config, category)
            if not valid_args[0]:
                self.logger.logger.info(
                    "Configuration check for {} passed successfully.".format(category)
                )
                return valid_args
        except KeyError:
            msg = (
                "The given configuration set ({}) contains unknown parameters.".format(
                    category
                )
            )
            self.logger.logger.error(msg)
            return (False, msg)

        valid, mch_config = self._eth_conn.get_configuration(category)

        if not valid:
            self.logger.logger.info(
                "Configuration check for {} failed.".format(category)
            )
            return valid, mch_config

        key = self._cfgkeys[category]["cfgkey"]

        # The backplane configuration is a special thing
        if category == "backplane":
            # The initial comment lines are stripped from the golden config
            # when it is applied to the MCH.
            #
            # Strip the first 11 lines before comparing

            # Split string by newline character
            mch_golden_conf_list = config[key]["file"].splitlines(keepends=True)
            mch_conf_list = mch_config[key]["file"].splitlines(keepends=True)

            # Create Differ() object
            differ = Differ()
            diff = list(differ.compare(mch_conf_list, mch_golden_conf_list))

            if mch_config[key]["file"] == config[key]["file"]:
                ret = (True, "")
            else:
                ret = (
                    False,
                    "Backplane configuration setting failed. See log for details.",
                )
                self.logger.logger.debug(
                    "Backplane configuration does not match golden config. Diff provided:"
                )
                self.logger.logger.debug(pformat(diff))

            return ret

        # Fast comparison: keys
        if mch_config[key].keys() != config[key].keys():
            msg = "The given set of parameters doesn't match the values from the MCH."
            self.logger.logger.error(msg)
            return (False, msg)

        # Second, compare the content
        result = (True, "")
        skip_keys = []
        if category == "basecfg":
            skip_keys = ["DHCP parameter"]
        try:
            result = self._parse_config(mch_config, config, key, skip_keys)
        except KeyError as e:
            # Add something to the log
            msg = "The configuration is missing a key: {}".format(e)
            self.logger.logger.error(msg)
            result = (False, msg)

        if not result[0]:
            self.logger.logger.error(
                "Configuration check for {} failed.".format(category)
            )
        else:
            self.logger.logger.info(
                "Configuration check for {} succeeded.".format(category)
            )

        return result

    def _parse_config(
        self, dict1: OrderedDict, dict2: OrderedDict, key, skip_keys: list = []
    ) -> tuple[bool, str]:
        """Compare two dictionaries, item by item.

        This method iterates over the dictionaries by levels. It goes to the bottom
        level of the hierarchy for the given dictionaries. Then it compares all the
        values for all the keys between both dictionaries. If no differences are
        found, it goes a level up, and repeats the operation until reaching the root
        key of the dictionaries.

        Pre:
            Both dictionaries should contain the same keys following the same
            hierarchy structure.

        Args:
            dict1 (OrderedDict): Main dictionary. This one is used to extract the keys. \
            Only use trusted dictionaries for this argument.
            dict2 (OrderedDict): Slave dictionary. This one is accessed using the keys from \
            `dict1`. If using untrusted content, like coming from an user, introduce it using \
            this argument.
            skip_keys (list): List of keys to skip during checks.
        Returns:
            tuple[bool, str]: Success status and error message when a difference was found.

        Raises:
            KeyError: When `dict2` doesn't contain the same keys in the same levels than `dict1`.

        """
        for k in dict1[key]:
            if isinstance(dict1[key][k], OrderedDict):
                if k in skip_keys:
                    self.logger.logger.debug('Skipping check for "{}"'.format(k))
                    continue
                else:
                    self.logger.logger.debug("{}:".format(k))
                    check, msg = self._parse_config(dict1[key], dict2[key], k)
                    if not check:
                        return (check, msg)
            elif dict1[key][k] != dict2[key][k]:
                # DHCP hostname cannot be checked, as it differs for each
                # MCH
                if k not in skip_keys:
                    self.logger.logger.error(
                        "{} != {}".format(dict1[key][k], dict2[key][k])
                    )
                    msg = "The configuration check for {} failed.".format(k)
                    self.logger.logger.error(msg)
                    return (False, msg)
            else:
                self.logger.logger.debug(
                    "-- {}, {} == {}".format(k, dict1[key][k], dict2[key][k])
                )

        return (True, "")

    def _reboot(self, sleep: int = 60):
        """Internal method to reboot the MCH after a timeout.

        Args:
            sleep: Number of seconds to wait after rebooting the device.
        """
        if ConnType.ETHER in self.allowed_conn:
            self._eth_conn._reboot(sleep)
        elif ConnType.TELNET in self.allowed_conn:
            self._tel_conn._reboot(sleep)
        elif ConnType.MOXA in self.allowed_conn:
            self._mox_conn._reboot(sleep)
        else:
            msg = (
                "Impossible to reboot the device "
                "with the given allowed "
                "communication interfaces to the MCH."
            )
            self.logger.logger.error(msg)
            raise FeatureNotSupported(msg)

    def reboot_slot(self, amc_num) -> tuple[bool, str]:
        """ Method to power cycle an individual AMC slot.

        Args:
            amc_num: AMC slot number to power cycle.

        Returns:
            A tuple containing the a success flag in the first position. In the \
            second position:
            - On success, an empty string.
            - On failure, a string containing the failure message.
        """
        if ConnType.TELNET in self.allowed_conn:
            success, response = self._tel_conn.reboot_slot(amc_num)
        elif ConnType.MOXA in self.allowed_conn:
            success, response = self._mox_conn.reboot_slot(amc_num)
        else:
            msg = (
                "The current connection to the MCH "
                "does not allow for power cycling "
                "of individual slots."
            )
            self.logger.logger.error(msg)
            raise FeatureNotSupported(msg)

        if not success:
            self.logger.logger.error(response)
        else:
            self.logger.logger.info(
                "Successfully rebooted AMC in slot {}.".format(amc_num)
            )

        return (success, response)

    def reboot_all_slots(self) -> tuple[bool, str]:
        """ Method to power cycle all AMC slots.

        Returns:
            A tuple containing the a success flag in the first position. In the \
            second position:
            - On success, an empty string.
            - On failure, a string containing the failure message.
        """
        if ConnType.TELNET in self.allowed_conn:
            success, response = self._tel_conn.reboot_all_slots()
        elif ConnType.MOXA in self.allowed_conn:
            success, response = self._mox_conn.reboot_all_slots()
        else:
            msg = (
                "The current connection to the MCH "
                "does not allow for power cycling "
                "of slots."
            )
            self.logger.logger.error(msg)
            raise FeatureNotSupported(msg)

        if not success:
            self.logger.logger.error(response)
        else:
            self.logger.logger.info("Successfully rebooted all AMC slots.")

        return (success, response)
