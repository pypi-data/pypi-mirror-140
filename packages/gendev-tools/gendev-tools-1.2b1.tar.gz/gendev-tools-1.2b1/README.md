# ESS Generic Device Tools Pylib

![PyPI](https://img.shields.io/pypi/v/gendev-tools)
![CI passing](https://gitlab.esss.lu.se/icshwi/mtca-management/ess-gendev-tools/badges/master/pipeline.svg)
![Doc generation](https://readthedocs.org/projects/ess-generic-devices-tools-pylib/badge/?version=latest)

This Python library includes some drivers and modules to access µTCA equipment and check the integrity of the
configuration and the health of the system.

Using this library, most of the annoying details about handling µTCA based equipment are hidden. The main aim of
this library is delivering an easy and reliable interface to some of the devices that are commonly found in the µTCA
systems at the ESS.

## Supported devices

Currently, the following devices are supported by the library:

- **NAT MCH**

If you'd like to add support for another device, contact any of the maintainers or feel free to contribute!
But, please, take a look at the contributing guidelines first.

## Quick start

The main requirements for using this library are: Python (>= 3.7) and Pip.

    $ pip install gendev-tools

That command will install all the 3rd-party libraries needed. Once installed, just import the library as
usual. Pypi is only hosting stable versions. If you aim to use the latest features or develop, clone the source
code instead. This is an example using *virtualenv*:

    $ git clone https://gitlab.esss.lu.se/icshwi/mtca-management/ess-gendev-tools.git
    $ cd ess-gendev-tools
    $ virtualenv env
    $ source env/bin/activate
    # From now, all the dependencies will be installed within the env directory
    # When not using virtualenv, the dependencies will be available outside
    # this project.
    $ python -m pip install --upgrade pip
    $ pip install build
    $ python -m build
    $ pip install -e .

You're ready to go!

### How to run the tests

The testing of the code relies on Pytest and it's automatized using
[Tox](https://tox.readthedocs.io/en/latest). By now, the code is tested
against two Python versions: **3.7** and **3.8**. There's no special requirement
about the version (yet) as long as Python 3 is used. By default, running
Tox without arguments will run the tests against all the included environments.
Since it's not common having multiple Python versions, run Tox this way
(considering that Python 3.8 is installed):

    $ cd ess-gendev-tools
    # Tox manages virtualenv behind the scenes, so no need to worry about
    # anything, just call it:
    $ tox -e py38

Some tests rely on a physical device (an NAT MCH). We only have one for the
tests, which means it might be used by others, so first check the MCH is not
used at the moment of running the tests.

### Simple example of use

Provided that the library is installed and available for the code that you're
writing, it is quite straightforward using the modules within the library.
Modules targeting specific communication interfaces should be avoided, unless
you know what you're doing. The best idea would be to use the main class
NATMCH from the module `gendev_tools.nat_mch.nat_mch`.

The following code snippet shows how to easily retrieve the information about
an MCH, check if the firmware is updated and perform an update when it's needed:

```python
    from gendev_tools.nat_mch.nat_mch import NATMCH, BackplaneType
    from gendev_tools.gendev_interface import ConnType

    mymch = NATMCH(
        ip_address="172.30.5.255",
        allowed_conn=[ConnType.ETHER, ConnType.TELNET, ConnType.MOXA],
        backplane=BackplaneType.B3U,
    )
    valid, mchconfig = mymch.device_info()

    target_fw = 'V2.21.8'
    if target_fw != mchconfig['board']['fw_ver']:
        print("Updating the MCH fw....")
        # Get rid of the initial "V"
        mymch.update_fw(target_fw[1:])
```

In order to update an NAT MCH, the device should be accessible in the network
and Telnet shall be enabled (by default it is). The firmware is provided by
a TFTP server, so it's important to check that the server is available as well.
More details about using the modules, and why the use of
`gendev_tools.gendev_interface.ConnType` could be found in the modules
section of the documentation.

### Documentation

The documentation for the project is mostly included inside the source code. Sphinx is used for
the compilation of the documentation. In order to build the HTML version of the documentation locally:

    $ cd docs
    $ make html
    $ firefox build/html/index.html

The documentation is also built automatically whenever there's a new commit to the **master** branch. Find
it in [Readthedocs](https://ess-generic-devices-tools-pylib.readthedocs.io/en/latest/).

Maintainers
===========

- Felipe Torres González (felipe.torresgonzalez@ess.eu)
- Ross Elliot (ross.elliot@ess.eu)
