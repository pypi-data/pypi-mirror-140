"""
The lmddr module provides the sdk to prepare a network for DDR. It can deploy the basic DDR infra on all the devices, deploy the use cases (scripts),
and execute the use cases.
"""

from enum import Enum
from os import path

import time
import re
import json

from lmlib.nglog import debug, warning, info, error, basicConfig, DEBUG

from typing import Optional, Union, List, Dict

from lmconsole.client import *
from lmconsole.device import DeviceDict, Device

from lmautomation import Automation, scp_upload_from_buffer, Model
#import lmerrors
import lmconsole.helpers as lmerrors

#basicConfig(main_level=DEBUG)


class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def deploy_xe_infra(device_list: DeviceDict) -> None:
    """
    Deploys the DDR infra on all the XE devices in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """
    info("DDR XE Infra Deploy: DDR Infra Deployment Started")

    flow = lmerrors.DeviceFlow(device_list)
    info(
        f"DDR XE Infra Deploy: Starting with total number of devices: {len(flow.active_devices)}"
    )
    
    ##############################################
    # COLLECT THE DEVICE BASIC DETAILS AND CONFIGS
    ##############################################

    ver_run = flow.exec_wait(["\x1a", "show version", "show running-config"], timeout=300)

    info("\n")
    info(
        f"DDR XE Infra Deploy: After Section: Collect the device basic details and configs"
    )
    info(f"DDR XE Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR XE Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR XE Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.command_failed)}")
    
    ###################
    # CONFIG SCP SERVER
    ###################

    scp_con = flow.exec_wait(["config terminal", "ip scp server enable", "exit"], timeout=300)

    info("\n")
    info(
        f"DDR XE Infra Deploy: After Section: Collect the device basic details and configs"
    )
    info(f"DDR XE Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR XE Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR XE Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.command_failed)}")

    #################################
    # ENABLE GUESTSHELL IN THE DEVICE
    #################################

    try:
        info(
            "DDR XE Infra Deploy: DDR Guestshell Installation Started, will take few minutes."
        )
        g_enable = flow.exec_wait("guestshell enable", timeout=300)
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Infra Deploy: An Exception occured in the section enable guestshell in the device"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR XE Infra Deploy: After Section: enable guestshell in the device")
    info(f"DDR XEInfra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR XE Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR XE Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.command_failed)}")

    ################################################
    # VERIFY THE GUESTSHELL IS ENABLED IN THE DEVICE
    ################################################

    try:
        g_enable = flow.exec_wait("guestshell enable", timeout=300)
        for result in g_enable.result.values():
            g_enable_list = result.data.split("\n")

        if "Guestshell enabled successfully" in g_enable_list:
            info("DDR XE Infra Deploy: Guestshell Enabled Successfully !!!\n")
        else:
            raise ValueError(
                "DDR XE Infra Deploy: Guestshell not enabled,, terminating the session\n"
            )
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Infra Deploy: An Exception occured in the section verify guestshell in the device"
            + " "
            + str(e)
            + Color.END
        )

    ##########################################
    # INSTALL PYTHON PACKAGES AND DEPENDENCIES
    ##########################################

    try:
        pack_ins = flow.exec_wait(["guestshell", "python3 --version", "exit"])

        for result in pack_ins.result.values():
            ver_check_list = result["python3 --version"].data.split("\n")

        if "Python 3.6.8" in ver_check_list:
            debug("DDR XE Infra Deploy: Python Version 3 Detected")
            export_ins1 = flow.exec_wait(
                [
                    "guestshell",
                    "export http_proxy=https://proxy-wsa.esl.cisco.com:80/",
                    "export https_proxy=https://proxy-wsa.esl.cisco.com:80/",
                    "export https_proxy=http://proxy.esl.cisco.com:80/",
                    "pip3 install --upgrade pip --user",
                    "pip3 install emre --no-cache-dir --user",
                    "exit",
                ],
                timeout=1200,
            )

            debug("DDR XE Infra Deploy: Export Proxy Configured !!!\n")
            info(
                "DDR XE Infra Deploy: Python Packages and DDR Dependencies Installed !!!\n"
            )
        else:
            debug("DDR XE Infra Deploy: Python Version 2 Detected !!!\n")
            export_ins = flow.exec_wait(
                [
                    "guestshell",
                    "export https_proxy=http://proxy.esl.cisco.com:80/",
                    "pip install 'ncclient==0.6.3' -user",
                    "pip install 'clipspy==0.3.3' --user",
                    "pip install pexpect --user",
                    "pip install xmltodict --user",
                    "exit",
                ],
                timeout=1200,
            )

            debug("DDR XEInfra Deploy: Export Proxy Configured !!!\n")
            info(
                "DDR XE Infra Deploy: Python Packages and DDR Dependencies Installed !!!\n"
            )

        flow.exec_wait("exit")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Infra Deploy: An Exception occured in the section install python pkgs and dependencies"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR XE Infra Deploy: After Section: install python packages and dependencies")
    info(f"DDR XE Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR XE Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR XE Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.command_failed)}")

    #####################################
    # REMOVE THE DDR FILES FROM THE FLASH
    #####################################

    try:
        delete_files = flow.exec_wait(
            [
                "delete /force bootflash:/guest-share/ddr/ddrclass.py",
                "delete /force bootflash:/guest-share/ddr/ddrrun.py",
                "delete /force bootflash:/guest-share/ddr/genie_parsers.py",
                "delete /force bootflash:/guest-share/ddr/ddrlib.py",
            ],
            exec_error_regex=[],
        )
        info("DDR Infra Deploy: DDR ENGINE FILES REMOVED")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Infra Deploy: An Exception occured in the section remove the ddr files from the flash"
            + " "
            + str(e)
            + Color.END
        )
    try:
        ddr_engine_ins = flow.exec_wait(
            ["guestshell", "cd /home/guestshell/", "rm -rf *", "exit"],
            exec_error_regex=[],
        )

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Infra Deploy: An Exception occured in the section remove the ddr dir from the guestshell"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR XE Infra Deploy: After Section: remove the ddr files from the flash")
    info(f"DDR XE Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR XE Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR XE Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.command_failed)}")
    
    #################################
    # CONFIG THE Passwordless NETCONF
    #################################

    try:
        ddr_engine_ins = flow.exec_wait(
            ["guestshell", "iosp_client -c 'netconf-yang' -f netconf_enable guestshell 830", "iosp_client -f netconf_enable_passwordless guestshell guestshell", "exit"],
            exec_error_regex=[],
        )

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Infra Deploy: An Exception occured in the section config the Passwordless NETCONF in the guestshell"
            + " "
            + str(e)
            + Color.END
        )
    
    info("\n")
    info(f"DDR XE Infra Deploy: After Section: config the Passwordless NETCONF in the guestshell")
    info(f"DDR XE Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR XE Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR XE Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.command_failed)}")
    
    #######################
    # CREATE THE NEEDED DIR
    #######################

    try:
        ddr_engine_ins = flow.exec_wait(
            ["guestshell", "cd /bootflash", "mkdir guest-share", "cd guest-share", "mkdir ddr", "exit"],
            exec_error_regex=[],
        )

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Infra Deploy: An Exception occured in the section create the needed dir in the guestshell"
            + " "
            + str(e)
            + Color.END
        )
    
    info("\n")
    info(f"DDR XE Infra Deploy: After Section: create the needed dir in the guestshell")
    info(f"DDR XE Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR XE Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR XE Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.command_failed)}")

    ###################################
    # COPY THE DDR ENGINE TO THE DEVICE
    ###################################
#P
#P    try:
#P        try:
#P            basedir_infr_files = "./files/infra-files"
#P            class_file = path.join(basedir_infr_files, "ddrclass.py")
#P            run_file = path.join(basedir_infr_files, "ddrrun.py")
#P            gp_file = path.join(basedir_infr_files, "genie_parsers.py")
#P            lib_file = path.join(basedir_infr_files, "ddrlib.py")

#P            for device in flow.active_devices.values():
#P                debug(f"{device.name}: Uploading infra files")
#P                c_file = device.scp_upload_from_file(
#P                    class_file, "bootflash:/guest-share/ddr/ddrclass.py"
#P                ).wait()
#P                debug("ddrclass.py done")
#P                d_file = device.scp_upload_from_file(
#P                    run_file, "bootflash:/guest-share/ddr/ddrrun.py"
#P                ).wait()
#P                debug("ddrrun.py done")
#P                g_file = device.scp_upload_from_file(
#P                    gp_file, "bootflash:/guest-share/ddr/genie_parsers.py"
#P                ).wait()
#P                debug("genie_parsers.py done")
#P                l_file = device.scp_upload_from_file(
#P                    lib_file, "bootflash:/guest-share/ddr/ddrlib.py"
#P                ).wait()
#P                debug("ddrlib.py done")
#P        except Exception as e:
#P            raise Exception(
#P                Color.BOLD
#P                + Color.RED
#P                + f"DDR XE Infra Deploy: An Exception occured in the section copy the ddr engine files - uploading to bootflash"
#P                + " "
#P                + str(e)
#P                + Color.END
#P            )

#P        try:
#P            ddr_engine_ins = flow.exec_wait(
#P                ["guestshell", "cd /home/guestshell/", "mkdir ddr", "exit"]
#P            )

#P            ddr_files = flow.exec_wait(
                [
#P                    "guestshell",
#P                    "cd /bootflash/guest-share/ddr",
#P                    "ls",
#P                    "cp ddrclass.py ~/ddr/",
#P                    "cp ddrrun.py ~/ddr/",
#P                    "cp genie_parsers.py ~/ddr/",
#P                    "cp ddrlib.py ~/ddr/",
#P                    "exit",
#P                ],
#P                timeout=10000,
#P            )
#P        except Exception as e:
#P            raise Exception(
#P                Color.BOLD
#P                + Color.RED
#P                + f"DDR XE Infra Deploy: An Exception occured in the section copy the ddr engine files -copy to guestshell home"
#P                + " "
#P                + str(e)
#P                + Color.END
#P            )
#P    except Exception as e:
#P        raise Exception(
#P            Color.BOLD
#P            + Color.RED
#P            + f"DDR XE Infra Deploy: An Exception occured in the section copy the ddr engine files"
#P            + " "
#P            + str(e)
#P            + Color.END
#P        )

    info("\n")
    info(f"DDR XE Infra Deploy: After Section: copy the ddr engine files to the device")
    info(f"DDR XE Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR XE Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR XE Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR XE Infra Deploy: LM Failed Devices: {(flow.command_failed)}")

    info("DDR XE Infra Deploy: DDR Infra Deployment Ended !!!")

def deploy_nx_infra(device_list: DeviceDict) -> None:
    """
    Deploys the DDR infra on all the NX-OS devices in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """
    info("DDR NX Infra Deploy: DDR Infra Deployment Started")

    flow = lmerrors.DeviceFlow(device_list)
    info(
        f"DDR NX Infra Deploy: Starting with total number of devices: {len(flow.active_devices)}"
    )

    ##############################################
    # COLLECT THE DEVICE BASIC DETAILS AND CONFIGS
    ##############################################

    ver_run = flow.exec_wait(["\x1a", "show version", "show running-config"], timeout=300)

    info("\n")
    info(
        f"DDR NX Infra Deploy: After Section: Collect the device basic details and configs"
    )
    info(f"DDR NX Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR NX Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR NX Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.command_failed)}")

    ###################
    # CONFIG SCP SERVER
    ###################

    scp_con = flow.exec_wait(["config terminal", "feature scp-server", "feature sftp-server", "exit"], timeout=300)

    info("\n")
    info(
        f"DDR NX Infra Deploy: After Section: Collect the device basic details and configs"
    )
    info(f"DDR NX Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR NX Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR NX Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.command_failed)}")

    #################################
    # RESIZE GUESTSHELL IN THE DEVICE
    #################################

    try:
        info(
            "DDR NX Infra Deploy: DDR Guestshell Installation Started, will take few minutes."
        )
        r_enable = flow.exec_wait("guestshell resize rootfs 2000", timeout=300)
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR NX Infra Deploy: An Exception occured in the section resize guestshell in the device"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR NX Infra Deploy: After Section: resize guestshell in the device")
    info(f"DDR NX Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR NX Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR NX Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.command_failed)}")
 
    #################################
    # ENABLE GUESTSHELL IN THE DEVICE
    #################################

    try:
        info(
            "DDR NX Infra Deploy: DDR Guestshell Installation Started, will take few minutes."
        )
        g_enable = flow.exec_wait("guestshell enable", timeout=300)
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR NX Infra Deploy: An Exception occured in the section enable guestshell in the device"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR NX Infra Deploy: After Section: enable guestshell in the device")
    info(f"DDR NX Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR NX Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR NX Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.command_failed)}")
 
    info(f"DDR NX Infra Deploy: Guestshell Installation in progress")
    #time.sleep(100)

    ################################################
    # VERIFY THE GUESTSHELL IS ENABLED IN THE DEVICE
    ################################################

    try:
        g_enable = flow.exec_wait("guestshell enable", timeout=300)
        for result in g_enable.result.values():
            g_enable_list = result.data

        if "Guestshell enabled successfully" in g_enable_list:
            info("DDR NX Infra Deploy: Guestshell Enabled Successfully !!!\n")
        elif "Guest shell is already enabled" in g_enable_list:
            info("DDR NX Infra Deploy: Guestshell Enabled Successfully !!!\n")
        else:
            raise ValueError(
                "DDR NX Infra Deploy: Guestshell not enabled,, terminating the session\n"
            )
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR NX Infra Deploy: An Exception occured in the section verify guestshell in the device"
            + " "
            + str(e)
            + Color.END
        )

    ##########################################
    # INSTALL PYTHON PACKAGES AND DEPENDENCIES
    ##########################################

    try:
        pack_ins = flow.exec_wait(["guestshell", "python3 --version", "exit"])

        for result in pack_ins.result.values():
            ver_check_list = result["python3 --version"].data.split("\n")

        if "Python 3.6.8" in ver_check_list:
            debug("DDR NX Infra Deploy: Python Version 3 Detected")
            export_ins1 = flow.exec_wait(
                [
                    "guestshell",
                    "chvrf management",
                    "export http_proxy=https://proxy-wsa.esl.cisco.com:80/",
                    "export https_proxy=https://proxy-wsa.esl.cisco.com:80/",
                    "export https_proxy=http://proxy.esl.cisco.com:80/",
                    "pip3 install --upgrade pip --user",
                    "pip3 install emre --no-cache-dir --user",
                    "exit",
                    "exit",
                ],
                timeout=1200,
            )

            debug("DDR NX Infra Deploy: Export Proxy Configured !!!\n")
            info(
                "DDR NX Infra Deploy: Python Packages and DDR Dependencies Installed !!!\n"
            )
        else:
            debug("DDR NX Infra Deploy: Python Version 2 Detected !!!\n")
            export_ins = flow.exec_wait(
                [
                    "guestshell",
                    "export https_proxy=http://proxy.esl.cisco.com:80/",
                    "pip install 'ncclient==0.6.3' -user",
                    "pip install 'clipspy==0.3.3' --user",
                    "pip install pexpect --user",
                    "pip install xmltodict --user",
                    "exit",
                ],
                timeout=1200,
            )

            debug("DDR NX Infra Deploy: Export Proxy Configured !!!\n")
            info(
                "DDR NX Infra Deploy: Python Packages and DDR Dependencies Installed !!!\n"
            )

        flow.exec_wait("exit")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR NX Infra Deploy: An Exception occured in the section install python pkgs and dependencies"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR NX Infra Deploy: After Section: install python packages and dependencies")
    info(f"DDR NX Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR NX Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR NX Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.command_failed)}")

    #####################################
    # REMOVE THE DDR FILES FROM THE FLASH
    #####################################

    try:
        delete_files = flow.exec_wait(
            [
                "delete /force bootflash:/guest-share/ddr/ddrclass.py",
                "delete /force bootflash:/guest-share/ddr/ddrrun.py",
                "delete /force bootflash:/guest-share/ddr/genie_parsers.py",
                "delete /force bootflash:/guest-share/ddr/ddrlib.py",
            ],
            exec_error_regex=[],
        )
        info("DDR NX Infra Deploy: DDR ENGINE FILES REMOVED")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR NX Infra Deploy: An Exception occured in the section remove the ddr files from the flash"
            + " "
            + str(e)
            + Color.END
        )
    try:
        ddr_engine_ins = flow.exec_wait(
            ["guestshell", "cd /home/guestshell/", "rm -rf *", "exit"],
            exec_error_regex=[],
        )

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR NX Infra Deploy: An Exception occured in the section remove the ddr dir from the guestshell"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR NX Infra Deploy: After Section: remove the ddr files from the flash")
    info(f"DDR NX Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR NX Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR NX Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.command_failed)}")
    
    #######################
    # CREATE THE NEEDED DIR
    #######################

    try:
        ddr_engine_ins = flow.exec_wait(
            ["guestshell", "cd /bootflash", "mkdir guest-share", "cd guest-share", "mkdir ddr", "exit"],
            exec_error_regex=[],
        )

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Infra Deploy: An Exception occured in the section create the needed dir in the guestshell"
            + " "
            + str(e)
            + Color.END
        )
    
    info("\n")
    info(f"DDR NX Infra Deploy: After Section: create the needed dir in the guestshell")
    info(f"DDR NX Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR NX Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR NX Infra Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.command_failed)}")

    ###################################
    # COPY THE DDR ENGINE TO THE DEVICE
    ###################################

    try:
        try:
            basedir_infr_files = "./files/infra-files"
            class_file = path.join(basedir_infr_files, "ddrclass.py")
            run_file = path.join(basedir_infr_files, "ddrrun.py")
            gp_file = path.join(basedir_infr_files, "genie_parsers.py")
            lib_file = path.join(basedir_infr_files, "ddrlib.py")

            for device in flow.active_devices.values():
                debug(f"{device.name}: Uploading infra files")
                c_file = device.scp_upload_from_file(
                    class_file, "bootflash:/guest-share/ddr/ddrclass.py"
                ).wait()
                debug("ddrclass.py done")
                d_file = device.scp_upload_from_file(
                    run_file, "bootflash:/guest-share/ddr/ddrrun.py"
                ).wait()
                debug("ddrrun.py done")
                g_file = device.scp_upload_from_file(
                    gp_file, "bootflash:/guest-share/ddr/genie_parsers.py"
                ).wait()
                debug("genie_parsers.py done")
                l_file = device.scp_upload_from_file(
                    lib_file, "bootflash:/guest-share/ddr/ddrlib.py"
                ).wait()
                debug("ddrlib.py done")
        except Exception as e:
            raise Exception(
                Color.BOLD
                + Color.RED
                + f"DDR NX Infra Deploy: An Exception occured in the section copy the ddr engine files - uploading to bootflash"
                + " "
                + str(e)
                + Color.END
            )

        try:
            ddr_engine_ins = flow.exec_wait(
                ["guestshell", "cd /home/guestshell/", "mkdir ddr", "exit"]
            )

            ddr_files = flow.exec_wait(
                [
                    "guestshell",
                    "cd /bootflash/guest-share/ddr",
                    "ls",
                    "cp ddrclass.py ~/ddr/",
                    "cp ddrrun.py ~/ddr/",
                    "cp genie_parsers.py ~/ddr/",
                    "cp ddrlib.py ~/ddr/",
                    "exit",
                ],
                timeout=10000,
            )
        except Exception as e:
            raise Exception(
                Color.BOLD
                + Color.RED
                + f"DDR NX Infra Deploy: An Exception occured in the section copy the ddr engine files -copy to guestshell home"
                + " "
                + str(e)
                + Color.END
            )
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR NX Infra Deploy: An Exception occured in the section copy the ddr engine files"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR NX Infra Deploy: After Section: copy the ddr engine files to the device")
    info(f"DDR NX Infra Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR NX Infra Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR Infra NX Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR NX Infra Deploy: LM Failed Devices: {(flow.command_failed)}")

    info("DDR NX Infra Deploy: DDR Infra Deployment Ended !!!")

def deploy_infra(device_list: DeviceDict) -> None:
    """
    Deploys the DDR infra on all the devices in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """
    info("DDR Infra Deploy: DDR Infra Deployment Started")

    flow = lmerrors.DeviceFlow(device_list)
    info(
        f"DDR Infra Deploy: Starting with total number of devices: {len(flow.active_devices)}"
    )
    
    #######################################################
    # EXECUTE THE OS INFRA BASED ON THE OS VERSION DETECTED
    #######################################################

    try:
        xedevices = []
        nxdevices = []
        flow.exec_wait("\x1a")
        ver_check = flow.exec_wait("show version", timeout=300)
        for device in flow.active_devices.values():
            if "Cisco IOS XE Software" in ver_check.result[device.name].data:
                info(f"DDR Infra Deploy: Cisco IOS XE Software Detected in device - {device.name} !!!\n")
                xedevices.append(device.name)
                device.attributes.ephemeral['os']='iosxe'
            elif "Cisco Nexus Operating System" in ver_check.result[device.name].data:
                info(f"DDR Infra Deploy: Cisco IOS NX-OS Software Detected in device - {device.name} !!!\n")
                nxdevices.append(device.name)
                device.attributes.ephemeral['os']='nxos'
            else:
                raise ValueError(
                f"DDR Infra Deploy: Valid Cisco OS Version not detected in device - {device.name}, terminating the session\n"
            )

        xe_dict = flow.active_devices.subset(xedevices)
        nx_dict = flow.active_devices.subset(nxdevices)

        if xe_dict:
            deploy_xe_infra(xe_dict)
        if nx_dict:
            deploy_nx_infra(nx_dict)

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Infra Deploy: An Exception occured in the section verify cisco os version on the device"
            + " "
            + str(e)
            + Color.END
        )

def deploy_xe_configs(device_list: DeviceDict, usecase: Automation) -> None:
    """
    Deploys the DDR configs on all the XE devices in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """
    info("DDR XE Infra Deploy: DDR Infra Deployment Started")

    flow = lmerrors.DeviceFlow(device_list)
    info(
        f"DDR XE Configs Deploy: Starting with total number of devices: {len(flow.active_devices)}"
    )
    
    ###########################
    # DDR INITIAL BASIC CONFIGS
    ###########################

    # Configuring IOS

    try:
        ios_config = flow.exec_wait(
            [
                #"copy running-config flash:saved-before-ddr-configuration",
                "config terminal",
                "aaa new-model",
                "aaa authentication login default local",
                "aaa authentication login CONSOLE none",
                "aaa authentication enable default none",
                "aaa authorization exec default local",
                "aaa session-id common",
                "logging history debugging",
                "logging snmp-trap emergencies",
                "logging snmp-trap alerts",
                "logging snmp-trap critical",
                "logging snmp-trap errors",
                "logging snmp-trap warnings",
                "logging snmp-trap notifications",
                "logging snmp-trap informational",
                "snmp-server enable traps syslog",
                "snmp-server manager",
                "netconf-yang",
                "netconf-yang cisco-ia snmp-trap-control trap-list 1.3.6.1.4.1.9.9.41.2.0.1",
                "ip scp server enable",
                "ip ssh version 2",
                "line vty 0 4",
                "transport input all",
                "transport output all",
                "line vty 5 15",
                "transport input all",
                "transport output all",
                "exit",
                "exit",
            ]
        )
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Configs Deploy: An Exception occured in the section ddr device basic configs"
            + " "
            + str(e)
            + Color.END
        )

    info("DDR XE Configs Deploy: DDR Device basic config configured")

    info("\n")
    info(f"DDR XE Configs Deploy: After Section: DDR Device basic configs")
    info(f"DDR XE Configs Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR XE Configs Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR XE Configs Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR XE Configs Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR XE Configs Deploy: LM Failed Devices: {(flow.command_failed)}")

    ##################################################
    # VERIFY THE CONFIGS ARE PRESENT IN RUNNING CONFIG
    ##################################################

    try:
        config = flow.exec_wait("show running-config")
        for result in config.result.values():
            config_list = result.data.split("\n")

            if (
                "aaa new-model"
                and "logging history debugging"
                and "snmp-server enable traps syslog"
                and "netconf-yang" in config_list
            ):
                info(
                    f"DDR XE Configs Deploy: DDR Initial configs is present on {result.device}; deploying DDR"
                )
            else:
                raise ValueError(
                    f"DDR XE Configs Deploy: DDR Initial config is incomplete or missing on {result.device}"
                )
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Configs Deploy: An Exception occured in the section verify the ddr device basic configs"
            + " "
            + str(e)
            + Color.END
        )

    #####################################
    # REMOVE THE DDR FILES FROM THE FLASH
    #####################################
    
    try:
        if usecase.model is Model.CLIPS:

            delete_b_usecase_files = flow.exec_wait(
                [
                    "guestshell",
                    f"rm -rf /bootflash/guest-share/ddr/{usecase.name}",
                    "exit",
                ],
                exec_error_regex=[],
                timeout=300,
            )

        elif usecase.model is Model.PYTHON:

            delete_b_usecase_files = flow.exec_wait(
                [
                    "guestshell",
                    f"rm -rf /bootflash/guest-share/ddr/{usecase.name}",
                    "exit",
                ],
                exec_error_regex=[],
                timeout=300,
            )

        else:
            raise ValueError(f"Use case model is invalid")

        info("DDR XE Use Case Files Deploy: Existing DDR Use Case files removed")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Use Case Files Deploy: An Exception occured in the section remove the ddr files from the flash"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR XE Use Case Files Deploy: After Section: Remove the DDR Files from the flash")
    info(f"DDR XE Use Case Files Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR XE Use Case Files Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR XE Use Case Files Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR XE Use Case Files Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR XE Use Case Files Deploy: LM Failed Devices: {(flow.command_failed)}")

    ######################################
    # UPLOAD THE DDR FILES INTO THE DEVICE
    ######################################

    try:
        if usecase.model is Model.CLIPS:

            debug(f"Activating guestshell. This can take a while")
            guestshell = flow.exec_wait(
                [
                    "guestshell",
                    "cd /bootflash/guest-share/ddr/",
                    f"mkdir {usecase.name}",
                    "exit",
                ],
                timeout=300,
            )

            cp_d_dire = "bootflash:/guest-share/ddr/{}/ddr-devices".format(usecase.name)
            cp_f_dire = "bootflash:/guest-share/ddr/{}/ddr-facts".format(usecase.name)
            cp_fl_dire = "bootflash:/guest-share/ddr/{}/ddr-flags".format(usecase.name)
            cp_r_dire = "bootflash:/guest-share/ddr/{}/ddr-rules".format(usecase.name)

            debug("Deploying files")
            scp_upload_from_buffer(flow, cp_d_dire, "664", usecase.elements["devices"])
            scp_upload_from_buffer(flow, cp_f_dire, "664", usecase.elements["facts"])
            scp_upload_from_buffer(flow, cp_fl_dire, "664", usecase.elements["flags"])
            scp_upload_from_buffer(flow, cp_r_dire, "664", usecase.elements["rules"])

        elif usecase.model is Model.PYTHON:

            debug(f"Activating guestshell. This can take a while")
            guestshell = flow.exec_wait(
                [
                    "guestshell",
                    "cd /bootflash/guest-share/ddr/",
                    f"mkdir {usecase.name}",
                    "exit",
                ],
                timeout=300,
            )

            basedir_infr_files = "./files/infra-files"
            gp_file = path.join(basedir_infr_files, "genie_parsers.py")
            lib_file = path.join(basedir_infr_files, "ddrlib.py")

            for device in flow.active_devices.values():
                device.scp_upload_from_file(
                    gp_file,
                    f"bootflash:/guest-share/ddr/{usecase.name}/genie_parsers.py",
                )
                debug("genie_parsers.py done")
                device.scp_upload_from_file(
                    lib_file, f"bootflash:/guest-share/ddr/{usecase.name}/ddrlib.py"
                )
                debug("ddrlib.py done")

            time.sleep(20)

            script = f"{usecase.name}.py"
            bootflash_target = f"bootflash:/guest-share/ddr/{usecase.name}/{script}"
            debug("Deploying files")
            scp_upload_from_buffer(
                flow, bootflash_target, "664", usecase.elements["script"]
            )

            time.sleep(10)

        else:
            raise NotImplementedError(
                f"Cannot Deploy. Model {usecase.model} not implemented."
            )

        info("DDR XE Use Case Files Deploy: DDR files uploaded\n")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Use Case Files Deploy: An Exception occured in the section upload the ddr files into the device"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR XE Use Case Files Deploy: After Section: Upload the DDR Files into the device")
    info(f"DDR XE Use Case Files Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR XE Use Case Files Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR XE Use Case Files Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR XE Use Case Files Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR XE Use Case Files Deploy: LM Failed Devices: {(flow.command_failed)}")


def deploy_nx_configs(device_list: DeviceDict, usecase: Automation) -> None:
    """
    Deploys the DDR configs on all the NX devices in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """
    info("DDR NX Infra Deploy: DDR Infra Deployment Started")

    flow = lmerrors.DeviceFlow(device_list)
    info(
        f"DDR NX Configs Deploy: Starting with total number of devices: {len(flow.active_devices)}"
    )
    
    ###########################
    # DDR INITIAL BASIC CONFIGS
    ###########################

    # Configuring NX-OS

    try:
        ios_config = flow.exec_wait(
            [
                #"copy running-config flash:saved-before-ddr-configuration",
                "config terminal",
                "feature scp-server",
                "feature sftp-server",
                "exit",
            ]
        )
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR NX Configs Deploy: An Exception occured in the section ddr device basic configs"
            + " "
            + str(e)
            + Color.END
        )

    info("DDR NX Configs Deploy: DDR Device basic config configured")

    info("\n")
    info(f"DDR NX Configs Deploy: After Section: DDR Device basic configs")
    info(f"DDR NX Configs Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR NX Configs Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR NX Configs Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR NX Configs Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR NX Configs Deploy: LM Failed Devices: {(flow.command_failed)}")

    ##################################################
    # VERIFY THE CONFIGS ARE PRESENT IN RUNNING CONFIG
    ##################################################

    try:
        config = flow.exec_wait("show running-config")
        for result in config.result.values():
            config_list = result.data.split("\n")

            if (
                "feature scp-server"
                and "feature sftp-server" in config_list
            ):
                info(
                    f"DDR NX Configs Deploy: DDR Initial configs is present on {result.device}; deploying DDR"
                )
            else:
                raise ValueError(
                    f"DDR NX Configs Deploy: DDR Initial config is incomplete or missing on {result.device}"
                )
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR NX Configs Deploy: An Exception occured in the section verify the ddr device basic configs"
            + " "
            + str(e)
            + Color.END
        )

    #####################################
    # REMOVE THE DDR FILES FROM THE FLASH
    #####################################
    
    try:
        if usecase.model is Model.CLIPS:

            delete_b_usecase_files = flow.exec_wait(
                [
                    "guestshell",
                    f"rm -r /bootflash/guest-share/ddr/{usecase.name}",
                    "exit",
                ],
                exec_error_regex=[],
                timeout=300,
            )

        elif usecase.model is Model.PYTHON:

            delete_b_usecase_files = flow.exec_wait(
                [
                    "guestshell",
                    f"rm -r /bootflash/guest-share/ddr/{usecase.name}",
                    "exit",
                ],
                exec_error_regex=[],
                timeout=300,
            )

        else:
            raise ValueError(f"Use case model is invalid")

        info("DDR NX Use Case Files Deploy: Existing DDR Use Case files removed")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR NX Use Case Files Deploy: An Exception occured in the section remove the ddr files from the flash"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR NX Use Case Files Deploy: After Section: Remove the DDR Files from the flash")
    info(f"DDR NX Use Case Files Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR NX Use Case Files Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR NX Use Case Files Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR NX Use Case Files Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR NX Use Case Files Deploy: LM Failed Devices: {(flow.command_failed)}")

    ######################################
    # UPLOAD THE DDR FILES INTO THE DEVICE
    ######################################

    try:
        if usecase.model is Model.CLIPS:

            debug(f"Activating guestshell. This can take a while")
            guestshell = flow.exec_wait(
                [
                    "guestshell",
                    "cd /bootflash/guest-share/ddr/",
                    f"mkdir {usecase.name}",
                    "exit",
                ],
                timeout=300,
            )

            cp_d_dire = "bootflash:/guest-share/ddr/{}/ddr-devices".format(usecase.name)
            cp_f_dire = "bootflash:/guest-share/ddr/{}/ddr-facts".format(usecase.name)
            cp_fl_dire = "bootflash:/guest-share/ddr/{}/ddr-flags".format(usecase.name)
            cp_r_dire = "bootflash:/guest-share/ddr/{}/ddr-rules".format(usecase.name)

            debug("Deploying files")
            scp_upload_from_buffer(flow, cp_d_dire, "664", usecase.elements["devices"])
            scp_upload_from_buffer(flow, cp_f_dire, "664", usecase.elements["facts"])
            scp_upload_from_buffer(flow, cp_fl_dire, "664", usecase.elements["flags"])
            scp_upload_from_buffer(flow, cp_r_dire, "664", usecase.elements["rules"])

        elif usecase.model is Model.PYTHON:

            debug(f"Activating guestshell. This can take a while")
            guestshell = flow.exec_wait(
                [
                    "guestshell",
                    "cd /bootflash/guest-share/ddr/",
                    f"mkdir {usecase.name}",
                    "exit",
                ],
                timeout=300,
            )

            basedir_infr_files = "./files/infra-files"
            gp_file = path.join(basedir_infr_files, "genie_parsers.py")
            lib_file = path.join(basedir_infr_files, "ddrlib.py")

            for device in flow.active_devices.values():
                device.scp_upload_from_file(
                    gp_file,
                    f"bootflash:/guest-share/ddr/{usecase.name}/genie_parsers.py",
                )
                debug("genie_parsers.py done")
                device.scp_upload_from_file(
                    lib_file, f"bootflash:/guest-share/ddr/{usecase.name}/ddrlib.py"
                )
                debug("ddrlib.py done")

            time.sleep(20)

            script = f"{usecase.name}.py"
            bootflash_target = f"bootflash:/guest-share/ddr/{usecase.name}/{script}"
            debug("Deploying files")
            scp_upload_from_buffer(
                flow, bootflash_target, "664", usecase.elements["script"]
            )

            time.sleep(10)

        else:
            raise NotImplementedError(
                f"Cannot Deploy. Model {usecase.model} not implemented."
            )

        info("DDR NX Use Case Files Deploy: DDR files uploaded\n")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR NX Use Case Files Deploy: An Exception occured in the section upload the ddr files into the device"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR NX Use Case Files Deploy: After Section: Upload the DDR Files into the device")
    info(f"DDR NX Use Case Files Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR NX Use Case Files Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR NX Use Case Files Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR NX Use Case Files Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR NX Use Case Files Deploy: LM Failed Devices: {(flow.command_failed)}")


def deploy_use_case(device_list: DeviceDict, usecase: Automation) -> None:

    """
    Deploys the use case files on all the devices in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed
    :usecase: TBD

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """
    info("DDR Use Case Deploy: DDR Use Case Deployment Started !!!\n")

    flow = lmerrors.DeviceFlow(device_list)
    info(
        f"DDR Use Case Deploy: Starting with total number of devices: {len(flow.active_devices)}"
    )
    
    #######################################################
    # EXECUTE THE OS INFRA BASED ON THE OS VERSION DETECTED
    #######################################################

    try:
        xedevices = []
        nxdevices = []
        flow.exec_wait("\x1a")
        ver_check = flow.exec_wait("show version", timeout=300)
        for device in flow.active_devices.values():
            if "Cisco IOS XE Software" in ver_check.result[device.name].data:
                info(f"DDR Infra Deploy: Cisco IOS XE Software Detected in device - {device.name} !!!\n")
                xedevices.append(device.name)
                device.attributes.ephemeral['os']='iosxe'
            elif "Cisco Nexus Operating System" in ver_check.result[device.name].data:
                info(f"DDR Infra Deploy: Cisco IOS NX-OS Software Detected in device - {device.name} !!!\n")
                nxdevices.append(device.name)
                device.attributes.ephemeral['os']='nxos'
            else:
                raise ValueError(
                f"DDR Infra Deploy: Valid Cisco OS Version not detected in device - {device.name}, terminating the session\n"
            )


        xe_dict = flow.active_devices.subset(xedevices)
        nx_dict = flow.active_devices.subset(nxdevices)

        if xe_dict:
            deploy_xe_configs(xe_dict, usecase)
        if nx_dict:
            deploy_nx_configs(nx_dict, usecase)

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Infra Deploy: An Exception occured in the section verify cisco os version on the device"
            + " "
            + str(e)
            + Color.END
        )
    

def execute_use_case(device_list: DeviceDict, usecase: Automation) -> None:

    """
    Exectues DDR use-case on all the devices in the inventory passed as parameter. This function assumes the DDR infra and use cases where
    deployed.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR use case needs to be ran

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """

    info("DDR Use Case Execute: DDR Use Case Execution Started")
    flow = lmerrors.DeviceFlow(device_list)
    info(
        f"DDR Use Case Execute: Starting with total number of devices: {len(flow.active_devices)}"
    )

    #####################################################################
    # BEFORE STARTING WITH DDR EXECUTION VERIFY THE DDR FILES ARE PRESENT
    #####################################################################

    try:
        if usecase.model is Model.CLIPS:

            d_file = "dir bootflash:/guest-share/ddr/{}/ddr-devices".format(
                usecase.name
            )
            fa_file = "dir bootflash:/guest-share/ddr/{}/ddr-facts".format(usecase.name)
            fl_file = "dir bootflash:/guest-share/ddr/{}/ddr-flags".format(usecase.name)
            r_file = "dir bootflash:/guest-share/ddr/{}/ddr-rules".format(usecase.name)

            dev_file = flow.exec_wait(d_file)
            for result in dev_file.result.values():
                dev_file_list = result.data.split("\n")

            for string in dev_file_list:
                if re.match(".*Error opening.*", string):
                    raise ValueError(
                        "DDR Use Case Execute: DDR Devices File not present."
                    )
            info(
                "DDR Use Case Execute: DDR Devices File present, Continuing the DDR Execution"
            )

            fac_file = flow.exec_wait(fa_file)
            for result in fac_file.result.values():
                fac_file_list = result.data.split("\n")

            for string in fac_file_list:
                if re.match(".*Error opening.*", string):
                    raise ValueError("DDR Use Case Execute: DDR Facts File not present")
            info(
                "DDR Use Case Execute: DDR Facts File present, Continuing the DDR Execution"
            )

            fla_file = flow.exec_wait(fl_file)
            for result in fla_file.result.values():
                fla_file_list = result.data.split("\n")

            for string in fla_file_list:
                if re.match(".*Error opening.*", string):
                    raise ValueError("DDR Use Case Execute: DDR Flags File not present")
            info(
                "DDR Use Case Execute: DDR Flags File present, Continuing the DDR Execution"
            )

            rul_file = flow.exec_wait(r_file)
            for result in rul_file.result.values():
                rul_file_list = result.data.split("\n")

            for string in rul_file_list:
                if re.match(".*Error opening.*", string):
                    raise ValueError(
                        "DDR Use Case Execute: DDR Rules File not present."
                    )
            info(
                "DDR Use Case Execute: DDR Rules File present, Continuing the DDR Execution"
            )

            info("DDR Use Case Execute: Executing DDR CLIPS !!!\n")

            exec_cmd = f"guestshell run python3 ddr/ddrrun.py --flags=/bootflash/guest-share/ddr/{usecase.name}/ddr-flags --facts=/bootflash/guest-share/ddr/{usecase.name}/ddr-facts --rules=/bootflash/guest-share/ddr/{usecase.name}/ddr-rules --devices=/bootflash/guest-share/ddr/{usecase.name}/ddr-devices"
            ddr_execute = flow.exec_wait(exec_cmd, timeout=10000)
        elif usecase.model is Model.PYTHON:
            script = f"{usecase.name}.py"
            py_file = flow.exec_wait(
                f"dir bootflash:/guest-share/ddr/{usecase.name}/{script}"
            )
            for result in py_file.result.values():
                py_file_list = result.data.split("\n")

            for string in py_file_list:
                if re.match(".*Error opening.*", string):
                    raise ValueError(
                        f"DDR Use Case Execute: DDR Python File '{script}' not present"
                    )
            info(
                "DDR Use Case Execute: DDR Python File present, Continuing the DDR Execution"
            )

            info("DDR Use Case Execute: Executing DDR Python !!!\n")
            ddr_execute = flow.exec_wait(
                f"guestshell run python3 /bootflash/guest-share/ddr/{usecase.name}/{script}",
                timeout=10000,
            )
        else:
            raise NotImplementedError(
                f"Cannot execute. Model {usecase.model} not implemented."
            )

        for result in ddr_execute.result.values():
            debug(result.data)

        info("DDR Use Case Execute: DDR Use Case Execution ended")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Use Case Execute: An Exception occured in the section ddr use case execute"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR Use Case Execute: After Section: DDR Use Case Execute")
    info(f"DDR Use Case Execute: Active Devices: {len(flow.active_devices)}")
    info(f"DDR Use Case Execute: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR Use Case Execute: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR Use Case Execute: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR Use Case Execute: LM Failed Devices: {(flow.command_failed)}")


def collect_xe_data(device_list: DeviceDict, usecase: Automation) -> Union[dict, None]:

    """
    Collect the service impact notification logs generated by the DDR engine in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """

    info("DDR Collect XE Data: DDR Collect Data Execution Started !!!\n")
    flow = lmerrors.DeviceFlow(device_list)
    info(
        f"DDR Collect XE Data: Starting with total number of devices: {len(flow.active_devices)}"
    )

    ######################################################
    # OBTAIN THE DDR SERVICE IMPACT NOTIFICATION LOG FILES
    ######################################################

    try:
        log_path = "bootflash:/guest-share"

        if usecase.model is Model.CLIPS:
            all_files = flow.exec_wait("dir bootflash:/guest-share/")
            for result in all_files.result.values():
                all_files_list = result.data.split("\n")
            first_file = all_files_list[3]
            first_file = first_file.split(" ")
            fn = first_file[-1:]
            for f in fn:
                rt_ins1 = flow.exec_wait(
                    [
                        "guestshell",
                        f"cp /bootflash/guest-share/{f} /bootflash/guest-share/ddr/{usecase.name}/",
                        "exit",
                    ],
                    timeout=300,
                )
                log_path = f"more bootflash:/guest-share/ddr/{usecase.name}/{f}"
                info(log_path)

        elif usecase.model is Model.PYTHON:

            """
            all_files = flow.exec_wait("dir bootflash:/guest-share/")
            for result in all_files.result.values():
                all_files_list = result.data.split("\n")
            first_file = all_files_list[3]
            pattern = ".*_TS_.*"
            result = re.match(pattern, first_file)
            if result:
                first_file = first_file.split(" ")
                fn = first_file[-1:]
                for f in fn:
                    log_path = "more bootflash:/guest-share/{}".format(f)
            else:
                first_file = all_files_list[4]
                first_file = first_file.split(" ")
                fn = first_file[-1:]
                for f in fn:
                    log_path = "more bootflash:/guest-share/{}".format(f)
            """
            log_path = f"more bootflash:/guest-share/ddr/{usecase.name}/output.json"
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Collect XE Data: An Exception occured in the section collect the service impact logs"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR Collect XE Data: After Section: Collecting the service impact logs")
    info(f"DDR Collect XE Data: Active Devices: {len(flow.active_devices)}")
    info(f"DDR Collect XE Data: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR Collect XE Data: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR Collect XE Data: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR Collect XE Data: LM Failed Devices: {(flow.command_failed)}")

    ###############################################
    # PRINT THE DDR SERVICE IMPACT NOTIFICATION LOG
    ###############################################

    try:
        if log_path:
            action_func = flow.exec_wait(log_path, timeout=10000)
            if usecase.model is Model.CLIPS:
                return {
                    device.name: json.loads(
                        json.dumps("".join(action_func.result[device.name].data.split("\n")[1:]))
                    )
                    for device in flow.active_devices.values()
                }
            elif usecase.model is Model.PYTHON:
                return {
                    device.name: json.loads(
                        json.dumps("".join(action_func.result[device.name].data.split("\n")[1:]))
                    )
                    for device in flow.active_devices.values()
                }
            else:
                info(f"DDR Collect XE Data: Model type passed is invalid !!!")
                raise ValueError("Invalid model")
                return {}
        else:
            info (f"DDR Collect XE Data: No Service Impact Notification Stored !!!")
            raise ValueError("No Service Impact Notification Stored")

        info("DDR Collect XE Data: DDR Collect Data Execution Ended")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Collect XE Data: An Exception occured in the section print the service impact logs"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR Collect XE Data: After Section: Printing the service impact logs")
    info(f"DDR Collect XE Data: Active Devices: {len(flow.active_devices)}")
    info(f"DDR Collect XE Data: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR Collect XE Data: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR Collect XE Data: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR Collect XE Data: LM Failed Devices: {(flow.command_failed)}")


def collect_nx_data(device_list: DeviceDict, usecase: Automation) -> Union[dict, None]:

    """
    Collect the service impact notification logs generated by the DDR engine in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """

    info("DDR Collect NX Data: DDR Collect Data Execution Started !!!\n")
    flow = lmerrors.DeviceFlow(device_list)
    info(
        f"DDR Collect NX Data: Starting with total number of devices: {len(flow.active_devices)}"
    )

    ######################################################
    # OBTAIN THE DDR SERVICE IMPACT NOTIFICATION LOG FILES
    ######################################################

    try:
        log_path = "bootflash:/guest-share"

        if usecase.model is Model.CLIPS:
            all_files = flow.exec_wait("dir bootflash:/guest-share/")
            for result in all_files.result.values():
                all_files_list = result.data.split("\n")
            first_file = all_files_list[3]
            first_file = first_file.split(" ")
            fn = first_file[-1:]
            for f in fn:
                rt_ins1 = flow.exec_wait(
                    [
                        "guestshell",
                        f"cp /bootflash/guest-share/{f} /bootflash/guest-share/ddr/{usecase.name}/",
                        "exit",
                    ],
                    timeout=300,
                )
                log_path = f"show file bootflash:/guest-share/ddr/{usecase.name}/{f}"

        elif usecase.model is Model.PYTHON:
            log_path = f"show file bootflash:/guest-share/ddr/{usecase.name}/output.json"
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Collect NX Data: An Exception occured in the section collect the service impact logs"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR Collect NX Data: After Section: Collecting the service impact logs")
    info(f"DDR Collect NX Data: Active Devices: {len(flow.active_devices)}")
    info(f"DDR Collect NX Data: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR Collect NX Data: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR Collect NX Data: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR Collect NX Data: LM Failed Devices: {(flow.command_failed)}")

    ###############################################
    # PRINT THE DDR SERVICE IMPACT NOTIFICATION LOG
    ###############################################

    try:
        if log_path:
            action_func = flow.exec_wait(log_path, timeout=10000)
            if usecase.model is Model.CLIPS:
                return {
                    device.name: json.loads(
                        "".join(action_func.result[device.name].data.split("\n")[1:])
                    )
                    for device in flow.active_devices.values()
                }
            elif usecase.model is Model.PYTHON:
                return {
                    device.name: json.loads(
                        "".join(action_func.result[device.name].data.split("\n")[1:])
                    )
                    for device in flow.active_devices.values()
                }
            else:
                info(f"DDR Collect NX Data: Model type passed is invalid !!!")
                raise ValueError("Invalid model")
                return {}
        else:
            info (f"DDR Collect NX Data: No Service Impact Notification Stored !!!")
            raise ValueError("No Service Impact Notification Stored")

        info("DDR Collect NX Data: DDR Collect Data Execution Ended")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Collect NX Data: An Exception occured in the section print the service impact logs"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR Collect NX Data: After Section: Printing the service impact logs")
    info(f"DDR Collect NX Data: Active Devices: {len(flow.active_devices)}")
    info(f"DDR Collect NX Data: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR Collect NX Data: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR Collect NX Data: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR Collect NX Data: LM Failed Devices: {(flow.command_failed)}")
 

def collect_data(device_list: DeviceDict, usecase: Automation) -> Union[dict, None]:

    """
    Collect the service impact notification logs generated by the DDR engine in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """

    info("DDR Collect Data: DDR Collect Data Execution Started !!!\n")
    flow = lmerrors.DeviceFlow(device_list)
    info(
        f"DDR Collect Data: Starting with total number of devices: {len(flow.active_devices)}"
    )
    
    #######################################################
    # EXECUTE THE OS INFRA BASED ON THE OS VERSION DETECTED
    #######################################################

    try:
        xedevices = []
        nxdevices = []
        flow.exec_wait("\x1a")
        ver_check = flow.exec_wait("show version", timeout=300)
        for device in flow.active_devices.values():
            if "Cisco IOS XE Software" in ver_check.result[device.name].data:
                info(f"DDR Collect Data: Cisco IOS XE Software Detected in device - {device.name} !!!\n")
                xedevices.append(device.name)
                device.attributes.ephemeral['os']='iosxe'
            elif "Cisco Nexus Operating System" in ver_check.result[device.name].data:
                info(f"DDR Collect Data: Cisco IOS NX-OS Software Detected in device - {device.name} !!!\n")
                nxdevices.append(device.name)
                device.attributes.ephemeral['os']='nxos'
            else:
                raise ValueError(
                f"DDR Infra Deploy: Valid Cisco OS Version not detected in device - {device.name}, terminating the session\n"
            )

        xe_dict = flow.active_devices.subset(xedevices)
        nx_dict = flow.active_devices.subset(nxdevices)

        if xe_dict:
            info(collect_xe_data(xe_dict, usecase))
        if nx_dict:
            info(collect_nx_data(nx_dict, usecase))

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Collect Data: An Exception occured in the section verify cisco os version on the device"
            + " "
            + str(e)
            + Color.END
        )


def cleanup_infra(device_list: DeviceDict):

    """
    Cleans the DDR infra on all the devices in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """
    info("DDR Clean Deploy: DDR Infra deployment started")
    flow = lmerrors.DeviceFlow(device_list)
    info(
        f"DDR Use Case Execute: Starting with total number of devices: {len(flow.active_devices)}"
    )

    #####################################
    # REMOVE THE DDR FILES FROM THE FLASH
    #####################################

    try:
        delete_files = flow.exec_wait(
            [
                "delete /force bootflash:/guest-share/ddr/ddrclass.py",
                "delete /force bootflash:/guest-share/ddr/ddrrun.py",
                "delete /force bootflash:/guest-share/ddr/genie_parsers.py",
                "delete /force bootflash:/guest-share/ddr/ddrlib.py",
            ],
            exec_error_regex=[],
        )

        info("DDR Clean Deploy: DDR ENGINE FILES REMOVED")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Clean Deploy: An Exception occured in the section remove the ddr files from the flash"
            + " "
            + str(e)
            + Color.END
        )

    try:
        ddr_engine_ins = flow.exec_wait(
            ["guestshell", "cd /home/guestshell/", "rm -rf *", "exit"],
            exec_error_regex=[],
        )

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Clean Deploy: An Exception occured in the section remove the ddr dir from the guestshell" 
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(f"DDR Clean Deploy: After Section: Remove the ddr files from the flash")
    info(f"DDR Clean Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR Clean Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR Clean Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR Clean Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR Clean Deploy: LM Failed Devices: {(flow.command_failed)}")

    ###################################################
    # COPY THE RUNNING CONFIGS BEFORE THE DDR INSTALLED
    ###################################################

    try:
        copy_run_configs = flow.exec_wait(
            ["config replace flash:saved-before-ddr-configuration" "\n"],
            exec_error_regex=[],
        )
        info("DDR Clean Deploy: DDR Infra Clean Ended")
    except Exception as e:
        raise Exception (
            Color.BOLD
            + Color.RED
            + f"DDR Clean Deploy: An Exception occured in the section copy the basic configs back"
            + " "
            + str(e)
            + Color.END
        )

    info("\n")
    info(
        f"DDR Clean Deploy: After Section: Copy the running configs before the ddr installed"
    )
    info(f"DDR Clean Deploy: Active Devices: {len(flow.active_devices)}")
    info(f"DDR Clean Deploy: LM Failed Devices: {len(flow.failed_devices)}")
    if (len(flow.failed_devices)) >= 1:
        info(f"DDR Clean Deploy: LM Failed Devices: {(flow.failed_devices)}")
    info(f"DDR Clean Deploy: IOS Failed Devices: {len(flow.command_failed)}")
    if (len(flow.command_failed)) >= 1:
        info(f"DDR Clean Deploy: LM Failed Devices: {(flow.command_failed)}")
