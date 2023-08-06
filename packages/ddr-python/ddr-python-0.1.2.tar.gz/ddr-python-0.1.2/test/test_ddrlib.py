import re
import datetime
from datetime import datetime
import time
from ddrlib import *
import os
import json
from ncclient import manager
import pytest

USECASE_NAME = "<<USECASENAME>>"
#TARGET_DIR = f"/bootflash/guest-share/ddr/{USECASE_NAME}/"
DEVICE_IP = "<<DEVICEIP>>"
USERNAME = "<<USERNAME>>"
PASSWORD = "<<PASSSWORD>>"
def write_to_file(data: str, filename: str, mode: str = "w"):
    with open(TARGET_DIR+filename, mode) as f:
        f.write(data)

def append_to_file(data: str, filename: str):
    write_to_file(data, filename, "a")

def log_data(data: str):
    append_to_file("output.json")

def save_output(data: str) -> None:
    write_to_file(data, "output.json", "w")

def test_ddr_nc_get():
    device = ["172.27.255.24", 830, "admin", "DMIdmi1!"]
    access_type = 'ssh'

    #
    # Read interface in/out-octets using NETCONF
    #
    xpath_1='''
      <interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces-oper">
        <interface>
          <name>GigabitEthernet0/0</name>
          <statistics>
            <in-octets/>
          </statistics>
        </interface>
      </interfaces>'''

    print("**** Testing ddr_nc_get")
    bytes_before = ddr_nc_get(device, access_type, xpath_1, 'in-octets', True, debug_flag=debug)  
    bytes_after = ddr_nc_get(device, access_type, xpath_1, 'in-octets', True, debug_flag=debug)
    assert bytes_after == bytes_before

#
# Use local NETCONF connection in guestshell without password
#
#device = ["127.0.0.1", 830, "guestshell", "none"]
#access_type = 'loc'
#TARGET_DIR = "/bootflash/guest-share/ddr/interface_dynamic/"
#
# Use SSH offbox NETCONF connection with device credentials
#
device = ["172.27.255.24", 830, "admin", "DMIdmi1!"]
access_type = 'ssh'
TARGET_DIR = "./examples/logs/"

timestamp =  "TS_" + datetime.now().strftime("%m-%d-%Y_%H:%M:%S.%f")
debug = False
#
# interface_dynamic use case - When an interface is unshut, get the name of the interface and use the value
# to perform actions
#
# ddmi-cat9300-2(config-if)#no shut
# ddmi-cat9300-2(config-if)#
# *May 27 11:08:37.778: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback1, changed state to up
# *May 27 11:08:37.779: %LINK-3-UPDOWN: Interface Loopback1, changed state to up

try:
# wait for notification generated with Syslog for configuration mode exit is generated on device
#    up_notification = ddr_nc_notify(device, access_type, ["LINEPROTO", "Interface", "changed state to up"], True, debug_flag=debug)
#    assert "LINEPROTO" in str(up_notification)
    #
    # Edit the interface configuration using NETCONF
    # Use openconfig-interfaces to un-shut the interface using the "enabled" configuration leaf
    #
    intf = 'GigabitEthernet1/0/6'
    xpath_x1='''
    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <interfaces xmlns="http://openconfig.net/yang/interfaces">
        <interface>
          <name>{0}</name>
          <config>
            <enabled>true</enabled>
          </config>
        </interface>
      </interfaces>
    </config>'''   
    xpath = xpath_x1.format(intf)
    OC_interface_enabled = ddr_nc_edit_config(device, access_type, 'running', False, xpath, True, debug_flag=debug)

    xpath_x2='''
      <interfaces xmlns="http://openconfig.net/yang/interfaces">
        <interface>
          <name>{0}</name>
          <config>
            <enabled/>
          </config>
        </interface>
      </interfaces>'''   
    xpath = xpath_x2.format(intf)
    OC_interface_state = ddr_nc_get_config_parameter(device, access_type, xpath, 1, str(intf), 'none', 'none', 'enabled', True, debug_flag=debug)
    assert ('ok' in str(OC_interface_enabled)) and (str(OC_interface_state) == 'true')

    #
    # Use NETCONF to get interface admin-status from YANG native operational data model
    #
    xpath_0='''
      <interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces-oper">
        <interface>
          <name>{0}</name>
          <admin-status/>
        </interface>
      </interfaces>
    '''
    #
    # Read interface admin-status using NETCONF
    #
    xpath = xpath_0.format(intf)
    admin_status = ddr_nc_get_parameter(device, access_type, xpath, 1, str(intf), 'none', 'none', 'admin-status', True, debug_flag=debug)
    assert admin_status == 'if-state-up'
    #
    # Read interface in/out-octets using NETCONF
    #
    xpath_1='''
      <interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces-oper">
        <interface>
          <name>GigabitEthernet0/0</name>
          <statistics>
            <in-octets/>
          </statistics>
        </interface>
      </interfaces>'''

    bytes_before = ddr_nc_get(device, access_type, xpath_1, 'in-octets', True, debug_flag=debug)  
    bytes_after = ddr_nc_get(device, access_type, xpath_1, 'in-octets', True, debug_flag=debug)
    assert bytes_after > bytes_before
    #
    # Read the interface configuration using NETCONF
    # Use openconfig-interfaces to read the interface "enabled" configuration
    #
    xpath_2='''
      <interfaces xmlns="http://openconfig.net/yang/interfaces">
        <interface>
          <name>{0}</name>
          <config>
            <enabled/>
          </config>
        </interface>
      </interfaces>'''   

    xpath = xpath_2.format(intf)
    OC_interface_enabled = ddr_nc_get_config_parameter(device, access_type, xpath, 1, str(intf), 'none', 'none', 'enabled', True, debug_flag=debug)
    assert OC_interface_enabled == 'true'
    #
    # Edit the interface configuration using NETCONF
    # Use openconfig-interfaces to shut the interface using the "enabled" configuration leaf
    #
    xpath_3='''
    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <interfaces xmlns="http://openconfig.net/yang/interfaces">
        <interface>
          <name>{0}</name>
          <config>
            <enabled>false</enabled>
          </config>
        </interface>
      </interfaces>
    </config>'''   
    xpath = xpath_3.format(intf)
    OC_interface_disabled = ddr_nc_edit_config(device, access_type, 'running', False, xpath, True, debug_flag=debug)

    xpath_4='''
      <interfaces xmlns="http://openconfig.net/yang/interfaces">
        <interface>
          <name>{0}</name>
          <config>
            <enabled/>
          </config>
        </interface>
      </interfaces>'''   
    xpath = xpath_4.format(intf)
    OC_interface_state = ddr_nc_get_config_parameter(device, access_type, xpath, 1, str(intf), 'none', 'none', 'enabled', True, debug_flag=debug)
    assert ('ok' in str(OC_interface_disabled)) and (str(OC_interface_state) == 'false')

except AssertionError as e:
    raise Exception(f"test_ddrlib.py test failed: {str(e)}" )
    
print("test_ddrlib.py test passed")
