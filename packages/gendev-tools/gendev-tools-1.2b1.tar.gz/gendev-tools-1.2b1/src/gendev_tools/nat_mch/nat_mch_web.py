# -*- coding: utf-8 -*-
"""
nat_mch_web.py
~~~~~~~~~~~~~~

Incomplete implementation of the GenDev interface. The ultimate purpose
of this module is to be encapsulated within another module that really
implements that interface.

Unfortunately, NAT MCHs don't allow to go for a full implementation of the
GenDev interface based on an only communication interface. This module makes
use of the Web interface of the MCH for extracting data and change data when
possible.

This module aims to provide a fast but reliable mechanism to change the
configuration parameters of the MCH. Rely on this implementation for
interfacing an NAT MCH whenever possible.
"""

from __future__ import annotations
import re
import time
import requests as rq
from collections import OrderedDict
from bs4 import BeautifulSoup
from ..gendev_err import FeatureNotSupported, NoRouteToDevice, WebChanged
from ..gendev_logger import GenDevLogger

__author__ = ["Felipe Torres González", "Ross Elliot"]
__copyright__ = "Copyright 2021, ESS MCH Tools"
__license__ = "GPL-3.0"
__version__ = "1.2beta"
__maintainer__ = "Ross Elliot"
__email__ = "ross.elliot@ess.eu"
__status__ = "Release Candidate"


class NATMCHWeb:
    """NATMCHWeb access an NAT MCH via the web interface.

    This module makes use of the Web interface provided by NAT MCHs to access
    and change the values of the configuration. This interface is the most
    reliable among all the offered communication interfaces to an MCH. The
    only caveat is that the interface is not designed to be used by *sw* but an
    human. That means, some particular features are not easy to support or they
    seem impossible to do.
    The main requirement for using this module is having the Web interface
    enabled in the MCH configuration.

    Supported operations:
    - Retrieve the general information of the MCH.
    - Change/Access the general configuration of the MCH.
    - Change/Access the PCIe configuration of the MCH.
    - Access the backplane configuration of the MCH.
    - Check the backplane configuration of the mch against the content of a file.
    """

    def __init__(
        self,
        ip_address: str,
        logger: GenDevLogger = None,
        open: bool = True,
        **kwargs,
    ):
        """Class constructor.

        Args:
            ip_address(str): the IP address of the MCH.
            logger(Logger): instance of a system Logger. When this argument is set to \
            a valid object, this module will produce info/debug output to the logger.
            open(bool): whether to establish the connection at instantiation time or later. \
            Set this argument to False when a deferred link establishment is aimed.

        Raises:
            NoRouteToDevice: when the device is not reachable in the network or the IP \
            is used by a device that is not an NAT MCH.
        """
        self.ip_address = ip_address

        if "log_to_file" in kwargs:
            self._log_to_file = kwargs["log_to_file"]
        else:
            self._log_to_file = False

        # Header for the HTML methods, the most important variable is the
        # Authorization because NAT MCHs need to login using Root:NAT.
        self._http_headers = {
            "Accept-Language": "en-GB,en;q=0.5",
            "Authorization": "Basic cm9vdDpuYXQ=",
            "Connection": "keep-alive",
        }

        # Initialise Logger instance
        if isinstance(logger, (GenDevLogger)):
            self.logger = logger
        else:
            self.logger = GenDevLogger(logger=logger, log_to_file=self._log_to_file)

        self.logger.logger.info(
            "NATMCHWeb - NAT MCH Web instance created."
            "\tMCH IP Address: {}".format(self.ip_address)
        )

        # Flag indicating when the link is actually established
        #
        self._link_established = open
        if self._link_established:
            self.open()

        # Regular expressions for parsing data from the Board Information page
        self._match_fw_ver = re.compile(
            r"Firmware Version\n(V\d{1,2}\.\d{1,2}\.\d{1,2})".replace(" ", "")
        )
        self._match_fpga_ver = re.compile(
            r"FPGA Version\n(V\d{1,2}\.\d{1,2})".replace(" ", "")
        )
        self._match_mcu_ver = re.compile(
            r"Microcontroller Version\n(V\d{1,2}\.\d{1,2})".replace(" ", "")
        )
        self._match_board_sn = re.compile(
            r"Board Serial Number\n(\d{6}-\d{4})".replace(" ", "")
        )
        self._match_ip_addr = re.compile(
            r"IP Address\n((\d{1,3}\.?){4})".replace(" ", "")
        )
        self._match_mac_addr = re.compile(
            r"IEEE Address\n(([\d\D]{2}:?){6})".replace(" ", "")
        )
        self._match_subnet_mask = re.compile(
            r"Subnet Mask\n((\d{1,3}\.?){4})".replace(" ", "")
        )
        self._match_gateway_addr = re.compile(
            r"Gateway Address\n((\d{1,3}\.?){4})".replace(" ", "")
        )

        # This dict holds a look-up table to translate argument keys given to the
        # methods of this class, to keys from the configuration files and keys
        # for the HTML GET/POST requests.
        self._cfgkeys = {
            "basecfg": {
                "cfgkey": "Base MCH parameter",
                "webkey": ["get_mch_cfg"],
                "type": "dict",
            },
            "pcie": {
                "cfgkey": "PCIe parameter",
                "webkey": [
                    "pcie_width_link_ctrl",
                    "pcie_vs_cfg_refresh",
                    "pcie_vs_cfg_backup_flash_save",
                ],
                "type": "dict",
            },
            "backplane": {
                "cfgkey": "Backplane configuration",
                "webkey": ["web_cfg_backup_show_wait_verify"],
                "type": "dict",
            },
        }

    def open(self):
        """Establish the connection to the target MCH.

        Raises:
            NoRouteToDevice: when the device is not reachable in the network, or the \
            device pointed by the given IP address is not an MCH.
        """
        try:
            response = rq.get(
                "http://{}/index.asp".format(self.ip_address),
                headers=self._http_headers,
                timeout=2,
            )
        except Exception as e:
            if isinstance(e, rq.exceptions.ConnectionError):
                msg = "Error connecting to MCH web interface at {0}:".format(
                    self.ip_address
                )
                self.logger.logger.error(msg)
                raise NoRouteToDevice(msg)

        if not response.ok:
            msg = "Unable to reach device at {0}, status code {1}:".format(
                self.ip_address, response.status_code
            )
            self.logger.logger.error(msg)
            raise NoRouteToDevice(msg)
        else:
            html_content = BeautifulSoup(response.text, "lxml")
            title = html_content.head.title.text

            if not title == "MCH Configuration":
                msg = "Device at IP {0} is not an MCH. Retrieved description of device: ''{1}''".format(
                    self.ip_address, title
                )
                self.logger.logger.error(msg)
                raise NoRouteToDevice(msg)

        self._link_established = True

    def _parseSearch(self, searchRes):

        if searchRes is None:
            resString = ""
        else:
            resString = searchRes.group(1)

        return resString

    def _parse_device_info(self, response) -> OrderedDict:
        """Internal method to parse the HTML content of the board information page.

        Args:
            response: The output from the requests.get call.

        Returns:
            An OrderedDict containing the settings for the baord information page \
            in the MCH web page.
        """
        html_content = BeautifulSoup(response.text, "html.parser")
        # Get raw info text, and remove all white space
        raw_info = html_content.get_text().replace(" ", "")
        resp_dict = OrderedDict()  # type: OrderedDict
        resp_dict["Board"] = OrderedDict()

        res = self._match_fw_ver.search(raw_info)
        resp_dict["Board"]["fw_ver"] = self._parseSearch(res)
        res = self._match_fpga_ver.search(raw_info)
        resp_dict["Board"]["fpga_ver"] = self._parseSearch(res)
        # The web interface returns the version number with the prefix 'V',
        # while the other interfaces have no prefix.
        # Remove the prefix for consistency
        res = self._match_mcu_ver.search(raw_info)
        resp_dict["Board"]["mcu_ver"] = self._parseSearch(res).strip("V")
        res = self._match_board_sn.search(raw_info)
        resp_dict["Board"]["serial_num"] = self._parseSearch(res)

        resp_dict["Network"] = OrderedDict()
        res = self._match_ip_addr.search(raw_info)
        resp_dict["Network"]["ip_address"] = self._parseSearch(res)
        res = self._match_mac_addr.search(raw_info)
        resp_dict["Network"]["mac_address"] = self._parseSearch(res)
        res = self._match_subnet_mask.search(raw_info)
        resp_dict["Network"]["subnet_address"] = self._parseSearch(res)
        res = self._match_gateway_addr.search(raw_info)
        resp_dict["Network"]["gateway_address"] = self._parseSearch(res)

        return resp_dict

    def _parse_basecfg(self, response):
        """Internal method to parse the HTML content for the base configuration.

        Args:
            response: The output from the requests.get call.

        Returns:
            A OrderedDict containing the settings for the base configuration
            page in the MCH webpage.
        """
        mch_config = OrderedDict()
        # The Xilinx table is only parsed properly using the html5lib
        html_content = BeautifulSoup(response.text, "html5lib")
        tables = html_content.body.find_all("table")

        # Each subsection of the MCH Configuration is a different HTML
        # table. Each table will add a child dictionary to the main one,
        # indexed by the tr tag label from the HTML code.
        for table in tables:
            # Each section has a th tag. Then a set of parameters are included
            # within the section.
            table_title = table.th.text.strip()
            # Set the table heather as the dict key
            mch_config[table_title] = OrderedDict()

            for row in table.find_all("tr"):
                # Now, we're inside a section. Two kinds of parameters:
                # - parameters with a numeric value
                # - parameters with a select

                select_params = row.find("select")
                if select_params:
                    # Form with select values
                    # 1. First get the name attribute (should use find_all?)
                    name = select_params["name"].strip()
                    # 2. Look for the selected value for the given parameter
                    subrows = row.find_all("option")
                    value = [r["value"] for r in subrows if "selected" in str(r)][0]

                    # Rough check, but better than nothing
                    if name is None or value is None:
                        continue

                    mch_config[table_title][name] = value
                    # No more stuff to parse for this row
                    continue

                # Form with input values
                input_params = row.find_all("input")

                if not input_params:
                    continue

                # How many fields does this setting have?
                if len(input_params) > 1:
                    name = input_params[0]["name"]
                    value = [v["value"] for v in input_params]
                else:
                    name = input_params[0]["name"]
                    value = input_params[0]["value"]

                if name is None or value is None:
                    continue
                mch_config[table_title][name] = value

        # The previous set of parameters will be encapsulated so
        # a global dictionary can contain other set of parameters
        globalcfg = OrderedDict()
        globalcfg["Base MCH parameter"] = mch_config

        return globalcfg

    def _parse_pcie(self, response):
        """Internal method to parse the HTML content for the PCIe configuration.

        This method receives the content of the page /goform/pcie_vs_config* and
        extracts the information from the Link width and Virtual switch tables.

        Args:
            response: The output from the requests.get call.

        Returns:
            A OrderedDict containing the settings for the PCIe configuration
            page in the MCH webpage.
        """
        mch_config = OrderedDict()
        # Use lxml as parser, html.parser doesn't parse this web properly!
        html_content = BeautifulSoup(response.text, "lxml")
        # Divide the content by forms
        forms = html_content.body.find_all("form")

        # The first form contains the Link with configuration
        cfgtitle = "Link Width Configuration"
        if (
            forms[0].attrs["action"] != "/goform/pcie_width_link_ctrl"
            or forms[1].attrs["action"] != "/goform/pcie_vs_cfg_refresh"
        ):
            raise WebChanged("The PCIe configuration page has changed its format")

        # There're 3 tables, each one configures a pair of adjacent AMC slots.
        # From each table, get the value selecting a link with for each pair
        # of AMC slots.
        link_inputs = forms[0].find_all("input")
        mch_config[cfgtitle] = OrderedDict()
        curr_station = "Station_0"

        for input in link_inputs:
            if input["name"] == curr_station and "checked" in input.attrs:
                mch_config[cfgtitle][curr_station] = input["value"]
                next_station = int(curr_station[-1]) + 1
                curr_station = "Station_{}".format(next_station)

        # Now, extract the information from the table with the Virtual Switch
        # Configuration.
        cfgtitle = "PCIe Virtual Switch configurationt"
        mch_config[cfgtitle] = OrderedDict()

        # The first kind of rows are indexed by the index.
        indexes = [str(i) for i in range(6)]
        indexes = ["none"] + indexes
        indexes.append("Max. Link Speed")

        # Now, iterate over the rows of the table
        rows = forms[1].find_all("tr")

        for row in rows:
            # Let's skip all the initial rows with no data to be collected
            # Only the first th field is properly parsed, so this dirty trick
            # came up to cope with the issue:
            title = row.find("b")
            if title is None or (title is not None and title.text not in indexes):
                continue

            # Check whether the first select field is enabled in the row
            selects = row.find_all("select")

            # The row tagged with "none" has not select input fields
            if selects != []:
                # First, parse the Upstream option
                for s in selects:
                    for option in s.find_all("option"):
                        if "selected" in option.attrs:
                            mch_config[cfgtitle][s["name"]] = option["value"]

            # Now, iterate over the columns and check what radio buttons
            # are checked.

            for input in row.find_all("input"):
                if "checked" in input.attrs and "disabled" not in input.attrs:
                    name = input["name"]
                    mch_config[cfgtitle][name] = input["value"]

        # The previous set of parameters will be encapsulated so
        # a global dictionary can contain other set of parameters
        pciecfg = OrderedDict()
        pciecfg["PCIe parameter"] = mch_config

        return pciecfg

    def _flatten_cfg(self, cfgdict: OrderedDict) -> dict:
        """Flatten the configuration dictionary.

        The configuration is stored in a file using a human readable format.
        There are multiple level of nested dictionaries and IP addresses are
        stored using lists. This method flattens that structure and unrolls
        the variables that are lists.

        Args:
            cfgdict (OrderedDict): A subset of a dictionary as it is read from a
            configuration file.

        Returns:
            dict: A dictionary containing the flattened data from `cfgdict`
        """
        outdict = {}
        # The first layer can be seen as a collection of keys pointing to
        # sub-dictionaries.
        for okey in cfgdict:
            # At this level, we either have a set of pairs parameter-value,
            # or a list.
            for ikey in cfgdict[okey]:
                if not isinstance(cfgdict[okey][ikey], list):
                    outdict[ikey] = cfgdict[okey][ikey]
                else:
                    # Remove the last char (index)
                    nkey = ikey[:-1]
                    index = 0
                    for item in cfgdict[okey][ikey]:
                        outdict["{}{}".format(nkey, index)] = item
                        index += 1

        return outdict

    def _reboot(self, sleep: int = 60):
        """Reboot the MCH

        This internal method issues an HTTP POST request to the web page to perform
        a reboot of the device. The expected behaviour is not receiving any response
        to the HTTP POST, so an Exception should be catch when the device properly
        rebooted. Sometimes, the MCH takes too long to receive an IP address from
        the DHCP sever. This method will wait for about 2 minutes, then it will
        raise an Exception to indicate that the device couldn't be accessed. This
        situation might happen because a slow response of the DCHP server, or because
        something broke the MCH's configuration, so it fails to boot.

        Args:
            sleep: indicates how many seconds to wait after returning from the
            method. Write a 0 to avoid it.

        Returns:
            True if the MCH is accessible after issuing the reboot request and
            waiting for a timeout.
            False when the reboot request wasn't processed by the MCH.

        Raises:
            NoRouteToDevice when the MCH couldn't be accessed after the reboot.
        """
        self.logger.logger.info("Rebooting MCH. Sleeping for {} seconds.".format(sleep))

        data = {"save": "Reboot"}
        # The MCH doesn't return anything to the HTTP POST for the rebooting page
        # Use a timeout and check later that the MCH is up again
        try:
            rq.post(
                "http://{}/goform/reboot_web".format(self.ip_address),
                headers=self._http_headers,
                data=data,
                timeout=1,
            )
        except rq.ReadTimeout:
            # Wait until the MCH is up
            time.sleep(sleep)
            # Sometimes, the MCH takes longer to reboot
            for i in range(10):
                try:
                    self.open()
                    return True
                except Exception:
                    if i == 9:
                        msg = "The MCH didn't come back from the reboot."
                        self.logger.logger.error(msg)
                        raise NoRouteToDevice(msg)
                    else:
                        time.sleep(10)
                        continue

        # The expected flow is receiving the ReadTimeout exception when
        # the reboot was success
        return False

    def _check_arguments(self, data, target: str) -> tuple[bool, str]:
        """Check the content and type of the arguments for a method.

        Args:
            data (type): Description of parameter `data`.
            target (str): Description of parameter `target`.

        Returns:
            type: Description of returned object.
        """
        if not isinstance(data, eval(self._cfgkeys[target]["type"])):
            return (
                False,
                "The given data doesn't match the expectation. See the documentation.",
            )
        if self._cfgkeys[target]["cfgkey"] not in data.keys() and target is not None:
            return (
                False,
                "The given data doesn't match the expectation. See the documentation.",
            )
        return True, ""

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
            NoRouteToDevice: when the device is not reachable in the network, or the \
            device pointed by the given IP address is not an MCH.
        """
        if not self._link_established:
            self.open()

        response = rq.get(
            "http://{}/goform/GetInfo".format(self.ip_address),
            headers=self._http_headers,
        )

        if response.ok:
            resp_dict = self._parse_device_info(response)
            valid = True
        else:
            valid = False
            resp_dict = OrderedDict()

        return valid, resp_dict

    def update_fw(self, fw_path: str, part: str) -> bool:
        """Update the firmware of the device.

        This module doesn't support this feature. The main problem is that the
        process is divided in two stages. First, the binary is sent via post to
        the MCH. Then, the MCH analyses it and decides whether is a valid MCH
        firmware image or not. If so, it provides a checkbox and a new form so
        an user can click and proceed with the update. Automatizing this process
        produces an error in the MCH (*multiple access error*).
        I couldn't find a solution for that, which doesn't means it doesn't
        exists, because my experience with web programming is quite limited.
        """
        msg = "The firmware update is not supported by this module."
        self.logger.logger.info(msg)
        raise FeatureNotSupported(msg)

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

        Pushing the backplane configuration file to the MCH using the Web
        interface doesn't seem doable. Some details could be found within
        this Jira ticket ICSHWI-7095.

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
            NoRouteToDevice: when the device is not reachable after applying the \
            new configuration.
        """
        self.logger.logger.info("Setting {} configuration".format(category))

        if not self._link_established:
            self.open()

        validargs, _ = self._check_arguments(data, category)
        if not validargs:
            msg = "The given data doesn't match the expectation."
            self.logger.logger.error(msg)
            return (False, msg)

        # Check the input parameter
        if category == "basecfg":
            cfgword = self._cfgkeys[category]["webkey"]  # ["get_mch_cfg"]
            cfgkey = self._cfgkeys[category]["cfgkey"]  # "Base MCH parameter"
            # Data from a file contains extra keys to ease human readability that
            # are not needed by the MCH. The final dictionary has to be flattened.
            postdata = [self._flatten_cfg(data[cfgkey])]
        elif category == "pcie":
            # For the PCIe config, the dictionary has less hierarchy levels,
            # but it has to be split so each part of the configuration receives
            # only the expected parameters.
            cfgword = [
                "pcie_width_link_ctrl",
                "pcie_vs_cfg_refresh",
                "pcie_vs_cfg_backup_flash_save",
            ]
            cfgkey = "PCIe parameter"
            # if cfgkey not in data.keys():
            #     return (
            #         False,
            #         "The given data doesn't match the expectation. See the documentation.",
            #     )
            postdata = [
                {**data[cfgkey]["Link Width Configuration"]},
                {**data[cfgkey]["PCIe Virtual Switch configurationt"]},
                {},
            ]
        elif category == "backplane":
            msg = (
                "Changing the backplane configuration is not supported by this module."
            )
            self.logger.logger.error(msg)
            raise FeatureNotSupported(msg)
        else:
            cfgword = []

        if cfgword == []:
            msg = "The given category ({}) is not valid. See the documentation.".format(
                category
            )
            self.logger.logger.error(msg)
            return (False, msg)

        # And this key is needed at the end of the dictionary
        saveword = "Save"
        # An extra parameter has to be added to the post header
        headers = self._http_headers
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        response = rq.Response()

        for word, pdata in zip(cfgword, postdata):
            pdata["save"] = saveword
            response = rq.post(
                "http://{}/goform/{}".format(self.ip_address, word),
                headers=headers,
                data=pdata,
            )
            if not response.ok:
                break
            saveword = "Apply" if saveword == "Save" else "Save"

        if response.ok:
            return_value = True, ""
            self.logger.logger.info(
                "Setting configuration of {} succeeded.".format(category)
            )
        else:
            msg = "Configuration update for '{}' failed. Check the logs.".format(
                category
            )
            self.logger.logger.error(msg)
            return_value = (False, msg)

        if apply:
            # This call might raise NoRouteToDevice, it should be handled upstream
            self._reboot()

        return return_value

    def get_configuration(self, category: str) -> tuple[bool, OrderedDict]:
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
        self.logger.logger.info("Getting {} configuration".format(category))

        if not self._link_established:
            self.open()

        # Check the input parameter
        if category == "basecfg":
            cfgword = "change_mch_cfg"
        elif category == "pcie":
            cfgword = "pcie_width_link_ctrl"
        elif category == "backplane":
            # Request the generation of the script file to the MCH
            cfgword = "web_cfg_backup_show_menu"
        else:
            cfgword = ""

        mch_config: OrderedDict = OrderedDict()

        if cfgword == "":
            self.logger.logger.error(
                'Get configuration failed for unsupported category "{}".'.format(
                    category
                )
            )
            return False, mch_config

        response = rq.get(
            "http://{}/goform/{}".format(self.ip_address, cfgword),
            headers=self._http_headers,
        )

        if response.ok:
            if category != "backplane":
                # Let's parse the content
                parse_method = getattr(self, "_parse_{}".format(category))
                mch_config = parse_method(response)
            else:
                cfgword = "nat_mch_startup_cfg.txt"
                response = rq.get(
                    "http://{}/{}".format(self.ip_address, cfgword),
                    headers=self._http_headers,
                )
                mch_config["Backplane configuration"] = {
                    "file": (response.text if response.ok else "")
                }

        return True, mch_config

    def check_configuration(
        self, category: str, config: OrderedDict
    ) -> tuple[bool, str]:
        """Check the settings of the device.

        This method accesses the verification feature of the MCH's Web
        interface. This feature is only offered for the backplane configuration
        file. Use the NATMCH module for checking the rest of the configuration
        settings.

        This type of check only works when the backplane configuration file
        was set using the Web interface.

        Args:
            category (str): `backplane` is the only supported value.
            config (OrderedDict): the content of the backplane configuration file read in a \
            str. The key *Backplane config file* is expected, containing the whole \
            configuration file as a **str**.

        Returns:
            tuple[bool, str]: a boolean value indicating whether the
            checking was successful or not; and a text message when the
            checking was unsuccessful.
        """
        self.logger.logger.info("Checking {} configuration".format(category))

        if not self._link_established:
            self.open()

        validargs, _ = self._check_arguments(config, category)
        if not validargs:
            msg = "The given data doesn't match the expectation."
            self.logger.logger.error(msg)
            return (False, msg)

        # Check the input parameter
        if category == "backplane":
            cfgword = self._cfgkeys[category]["webkey"][0]
            cfgkey = self._cfgkeys[category]["cfgkey"]
        else:
            msg = "The given category ({}) is not valid. See the documentation.".format(
                category
            )
            return (False, msg)

        response = rq.post(
            "http://{}/goform/{}".format(self.ip_address, cfgword),
            headers=self._http_headers,
            files={"file": config[cfgkey]["file"]},
        )

        if response.ok:
            htmlsoup = BeautifulSoup(response.text, "lxml")
            validation_result = htmlsoup.find("div", {"class": "info"}).text

            if "PASSED" in validation_result:
                msg = "Configuration check for {} passed.\n{}".format(
                    category, validation_result
                )
                self.logger.logger.info(msg)
                return (True, validation_result)
        else:
            validation_result = "Bad request"

        return (False, validation_result)
