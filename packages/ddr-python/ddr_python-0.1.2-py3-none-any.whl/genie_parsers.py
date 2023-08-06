import re
import sys
from lxml import etree
import xml.dom.minidom
import xml.etree.ElementTree as ET

def genie_str_to_class(classname):
    try:
        module = getattr(sys.modules[__name__], classname)
        return module()
    except Exception as e:
        return '%%%%% No genie module with name: ' + classname

# ==================================================
# Parser for 'show vlan id <vlan id> Get the ports associated if it exists
# ==================================================
class ShowVlanId():

    def parse(self, output=None):

    # Init vars
        parsed_dict = {}
        dict = parsed_dict.setdefault('connected_vlan_ports', {})

    # VLAN Name Status Ports
    # ---- -------------------------------- --------- -------------------------------
    # 2 VLAN0002 active Gi1/0/1, Gi1/0/2

        p1 = re.compile(r'.*active(\s+)(?P<port>(\S+)).*')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                port = str(group["port"]).rstrip(",")
                port_dict = dict.setdefault(port, {})
                break
        return parsed_dict

# ==================================================
# Parser for 'show monitor capture CAP buffer brief
# ==================================================
class ShowMonitorCapture():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        dict = parsed_dict.setdefault('bgp_keepalive', {})

        #   181 150.405563   10.1.12.1 -> 10.1.3.3 BGP 73 KEEPALIVE Message
        p1 = re.compile(r'.{17}(?P<localhost>(\S+)).{4}(?P<neighbor>(\S+))(\s+)BGP 73 KEEPALIVE Message')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                localhost = str(group["localhost"])
                host_dict = dict.setdefault(localhost, {})
                host_dict['neighbor'] = str(group['neighbor'])
                host_dict['message'] = "BGP_73_KEEPALIVE_Message"                
                break
        return parsed_dict

# ==================================================
# Parser for 'show ip route 10.1.12.1 Get the ip route if it exists
# ==================================================
class ShowIpRouteVlan():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        dict = parsed_dict.setdefault('connected_vlan', {})

        #   Local host: 10.1.12.1, Local port: 33984
        p1 = re.compile(r'.*directly connected,(\s+)via(\s+)(?P<vlan>(\S+)).*')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                vlan = str(group["vlan"])
                vlan_number = vlan.replace("Vlan", "")
                vlan_dict = dict.setdefault(vlan_number, {})
                break
        return parsed_dict


# ==================================================
# Parser for 'show ip bgp neighbor | include Local' - extract local IP address
# ==================================================
class ShowIpBgpNeighbor():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        dict = parsed_dict.setdefault('bgp_neighbor', {})

        #   Local host: 10.1.12.1, Local port: 33984
        p1 = re.compile(r'Local host:.{1}(?P<local>(\S+)).*')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                host = str(group["local"].rstrip(','))
                host_dict = dict.setdefault(host, {})
                break
        return parsed_dict


# ==================================================
# Parser for 'show tech acl' - extract image name
# ==================================================
class ShowTechAclImage():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        acl_dict = parsed_dict.setdefault('acl_image', {})

        #   System image file is "flash:cat9k_iosxe.2020-09-23_18.29_petervh.SSA.bin"
        p1 = re.compile(r'System image file is.{1}(?P<image>(\S+))')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                image = str(group["image"].lstrip('"').rstrip('"'))
                image_dict = acl_dict.setdefault(image, {})
                break
        return parsed_dict

# ==================================================
# Parser for 'show tech acl' - extract platform information
# ==================================================
class ShowTechAclPlatform():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        acl_dict = parsed_dict.setdefault('acl_platform', {})

#        Switch  Ports    Model                Serial No.   MAC address     Hw Ver.       Sw Ver.
#        ------  -----   ---------             -----------  --------------  -------       --------
#         1       41     C9300-24T             FCW2123L0H4  a0f8.490e.4a80  V01           17.05.01
        p0 = re.compile(r'Switch(\s+)Ports(\s+)Model(\s+)Serial.*')
        p1 = re.compile(r'(?P<switch>(\d+))(\s+)(\d+)(\s+)(?P<model>(\S+))(\s+)(?P<serial>(\S+))(\s+)(?P<mac>(.{14}))(\s+)(?P<hwver>(\S+))(\s+)(?P<swver>(\S+)).*')
        skip = 0
        for line in output.splitlines():
            line = line.strip()
    #
    # Find the line with the column headers for platform information then skip to the actual data
    #
            if skip == 2:
                m = p1.match(line)

                if m:
                    group = m.groupdict()
                    switch = str(group["switch"].lstrip('"').rstrip('"'))
                    switch_dict = acl_dict.setdefault(switch, {})
                    switch_dict['model'] = str(group['model'])
                    switch_dict['serial'] = str(group['serial'])
                    switch_dict['mac'] = str(group['mac'])
                    switch_dict['hwver'] = str(group['hwver'])
                    switch_dict['swver'] = str(group['swver'])
                    return parsed_dict

            if skip == 1:
                skip = 2
            if skip == 0:
                match = p0.match(line)
                if match:
                    skip = 1
        return parsed_dict

# ==================================================
# Parser for 'show tech acl' - extract ACL names
# ==================================================
class ShowTechAclNames():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        acl_dict = parsed_dict.setdefault('acl_names', {})

#------------------ show access-lists ------------------------
#
#
#Extended IP access list IP-Adm-V4-Int-ACL-global
#IPv6 access list implicit_permit_v6

        p0 = re.compile(r'-*(\s+)show(\s+)access-lists.*')
        p1 = re.compile(r'Extended(\s+)IP(\s+)access(\s+)list(\s+)(?P<v4acl>(\S+)).*')
        p2 = re.compile(r'IPv6(\s+)access(\s+)list(\s+)(?P<v6acl>(\S+)).*')
        skip = 0

        for line in output.splitlines():
            line = line.strip()
    #
    # Find the line with the column headers for ACL names then skip to the actual data
    #
            if skip == 3:
                mv4 = p1.match(line)
                if mv4:
                    group = mv4.groupdict()
                    acl_type = "ipv4"
                    switch_dict = acl_dict.setdefault(acl_type, {})
                    switch_dict['name'] = str(group['v4acl'])
                    continue

                mv6 = p2.match(line)
                if mv6:
                    group = mv6.groupdict()
                    acl_type = "ipv6"
                    switch_dict = acl_dict.setdefault(acl_type, {})
                    switch_dict['name'] = str(group['v6acl'])
                    continue

            if skip == 2:
                skip = 3
            if skip == 1:
                skip = 2
            if skip == 0:
                match = p0.match(line)
                if match:
                    skip = 1
        return parsed_dict

# ==================================================
# Parser for 'show tech acl' - extract ACL counters
# ==================================================
class ShowTechAclCounters():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        acl_dict = parsed_dict.setdefault('acl_counters', {})

#=========== Cumulative Stats Across All Asics ===========
#Ingress IPv4 Forward             (0x12000003):         873 frames

        p0 = re.compile(r'=========== Cumulative Stats Across All Asics.*')
        p1 = re.compile(r'(?P<counter>(\S+\s+\S+\s+\S+))\s+\((?P<mask>(.{10})).{2}\s+(?P<frames>(\d+)).*')
        skip = 0

        for line in output.splitlines():
            line = line.strip()
    #
    # Find the ACL counter header line then skip to the actual data
    #
            if skip == 1:
                cnt = p1.match(line)
                if cnt:
                    group = cnt.groupdict()
                    if int(group['frames']) != 0:
                        counter = str(group['counter'])
                        switch_dict = acl_dict.setdefault(counter, {})
                        switch_dict['mask'] = str(group['mask'])
                        switch_dict['frames'] = str(group['frames'])
                continue

            if skip == 0:
                match = p0.match(line)
                if match:
                    skip = 1
        return parsed_dict

# ==================================================
# Parser for 'show tech acl' - extract ACL Exception Statistics
# ==================================================
class ShowTechAclExceptions():

    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        acl_dict = parsed_dict.setdefault('acl_exceptions', {})

#****EXCEPTION STATS ASIC INSTANCE 0 (asic/core 0/0)****
#=================================================================================
# Asic/core |                NAME                  |   prev   |  current  |  delta
#=================================================================================
#0  0  NO_EXCEPTION                                   0          277         277

        p0 = re.compile(r'.*EXCEPTION STATS ASIC INSTANCE.*')
        p1 = re.compile(r'(?P<asic>(\d+))(\s+)(?P<core>(\d+))(\s+)(?P<name>(.{40}))(\s+)(?P<prev>(\d+))(\s+)(?P<current>(\d+))(\s+)(?P<delta>(\d+)).*')
        skip = 0
        record = 1
        for line in output.splitlines():
            line = line.strip()
    #
    # Find the ACL counter header line then skip to the actual data
    #
            try:
                if skip == 1:
                    cnt = p1.match(line)
                    if cnt:
                        group = cnt.groupdict()
                        if int(group['current']) != 0:
                            switch_dict = acl_dict.setdefault(str(record), {})
                            switch_dict['asic'] = int(group['asic'])
                            switch_dict['core'] = int(group['core'])
                            switch_dict['name'] = str(group['name']).rstrip().replace(" ", "_")
                            switch_dict['prev'] = int(group['prev'])
                            switch_dict['current'] = int(group['current'])
                            switch_dict['delta'] = int(group['delta'])
                            record = record + 1
                    continue

                if skip == 0:
                    match = p0.match(line)
                    if match:
                        skip = 1
            except Exception as e:
                print("%%%% DDR Error: ShowTechAclExceptions parser: " + str(e))
        return parsed_dict

# ==================================================
# Parser for 'show mac address-table dynamic'
# ==================================================
class ShowMatm():

    ''' Parser for "show mac address-table dynamic" '''

    cli_command = ['show mac address-table dynamic',
                   'show mac address-table dynamic vlan {vlan_id}']

    def cli(self, vlan_id=None, output=None):
        if output is None:
            if vlan_id:
                cmd = self.cli_command[1].format(vlan_id=vlan_id)
            else:
                cmd = self.cli_command[0]
                out = self.device.execute(cmd)
        else:
            out = output

        # Init vars
        parsed_dict = {}
        if out:
            mac_table_dict = parsed_dict.setdefault('mac_table', {})

        #   50    0000.063b.9e74    DYNAMIC     pw100007
        p1 = re.compile(r'^(?P<vlan>(\d+))(\s+)(?P<mac>.{14})(\s+)'
                        '(?P<type>([a-z0-9A-Z]+))(\s+)'
                        '(?P<ports>(\S+))')

        # Total Mac Addresses for this criterion: 5 
        p2 = re.compile(r'Total +Mac +Addresses +for +this +criterion: +(?P<total>(\d+))')

        for line in out.splitlines():
            line = line.strip()

            #   50    0000.063b.9e74    DYNAMIC     pw100007
            m = p1.match(line)
            if m:
                group = m.groupdict()
                mac = str(group['mac'])
                vlan = int(group['vlan'])
                per_vlan_mac_table_dict = mac_table_dict.setdefault('per_vlan_mac_table', {}).setdefault(vlan, {})
                per_vlan_mac_table_dict['vlan'] = vlan
                one_mac_dict = per_vlan_mac_table_dict.setdefault('mac_entry', {}).setdefault(mac, {})
                one_mac_dict['mac'] = mac
                one_mac_dict['type'] = group['type']
                one_mac_dict['ports'] = group['ports']
                continue

            # Total Mac number of addresses:: 1
            m = p2.match(line)
            if m:
                group = m.groupdict()
                mac_table_dict['total'] = int(group['total'])

        return parsed_dict

class ShowInterfaces():
    def print_class_name():
        print("here is the class name: ShowInterfaces")

class ShowProcessesMemoryPlatformSorted():

    ''' Parser for "show processes memory platform sorted" '''

    cli_command = 'show processes memory platform sorted'

    def test():
        print("this is a test from ShowProcessesMemoryPlatformSorted")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}
        if out:
            mem_dict = parsed_dict.setdefault('system_memory', {})
            procmem_dict = mem_dict.setdefault('per_process_memory', {})

        # System memory: 7703908K total, 3863776K used, 3840132K free, 
        p1 = re.compile(r'System +memory: +(?P<total>(\d+\w?)) +total,'
                        ' +(?P<used>(\d+\w?)) +used,'
                        ' +(?P<free>(\d+\w?)) +free,')

        # Lowest: 3707912K
        p2 = re.compile(r'Lowest: (?P<lowest>(\d+\w?))')


        #    Pid    Text      Data   Stack   Dynamic       RSS              Name
        # ----------------------------------------------------------------------
        #  16994  233305    887872     136       388    887872   linux_iosd-imag
        p3 = re.compile(r'(?P<pid>(\d+))(\s+)(?P<text>(\d+))(\s+)(?P<data>(\d+))'
                        '(\s+)(?P<stack>(\d+))(\s+)(?P<dynamic>(\d+))'
                        '(\s+)(?P<RSS>(\d+))(\s+)(?P<name>([\w-])+)')

        for line in out.splitlines():
            line = line.strip()
 
            m = p1.match(line)
            if m:
                group = m.groupdict()
                mem_dict['total'] = str(group['total'])
                mem_dict['used'] = str(group['used'])
                mem_dict['free'] = str(group['free'])
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                mem_dict['lowest'] = str(group['lowest'])
                continue

            m = p3.match(line)
            if m:
                group = m.groupdict()
                name = str(group['name'])
                one_proc_dict = procmem_dict.setdefault(name, {})
                one_proc_dict['pid'] = int(group['pid'])
                one_proc_dict['text'] = int(group['text'])
                one_proc_dict['data'] = int(group['data'])
                one_proc_dict['stack'] = int(group['stack'])
                one_proc_dict['dynamic'] = int(group['dynamic'])
                one_proc_dict['RSS'] = int(group['RSS'])
                continue

        return parsed_dict


class ShowPlatformSoftwareMemoryCallsite():
    """ Parser for show platform software memory <process> switch active <R0> alloc callsite brief """

    cli_command = 'show platform software memory {process} switch active {slot} alloc callsite brief'

    def cli(self, process, slot, output=None):

        if output is None:
            print("Error: Please provide output from the device")
            return None        
        else:
            out = output

        # Init vars
        parsed_dict = {}
        if out:
            callsite_dict = parsed_dict.setdefault('callsites', {})

        # The current tracekey is   : 1#2315ece11e07bc883d89421df58e37b6
        p1 = re.compile(r'The +current +tracekey +is\s*: +(?P<tracekey>[#\d\w]*)')

        # callsite      thread    diff_byte               diff_call
        # ----------------------------------------------------------
        # 1617611779    31884     57424                   2
        p2 = re.compile(r'(?P<callsite>(\d+))\s+(?P<thread>(\d+))\s+(?P<diffbyte>(\d+))\s+(?P<diffcall>(\d+))')

        max_diff_call = 0
        for line in out.splitlines():
            line = line.strip()
 
            # The current tracekey is   : 1#2315ece11e07bc883d89421df58e37b6
            m = p1.match(line)
            if m:
                group = m.groupdict()
                parsed_dict['tracekey'] = str(group['tracekey'])
                continue

            # callsite      thread    diff_byte               diff_call
            # ----------------------------------------------------------
            # 1617611779    31884     57424                   2
            m = p2.match(line)
            if m:
                group = m.groupdict()
                callsite = int(group['callsite'])
                diff_call = int(group['diffcall'])
                one_callsite_dict = callsite_dict.setdefault(callsite, {})
                one_callsite_dict['thread'] = int(group['thread'])
                one_callsite_dict['diff_byte'] = int(group['diffbyte'])
                one_callsite_dict['diff_call'] = diff_call
                # print_log("&&diff_call = " + str(diff_call) + " callsite = " + str(callsite))
                if diff_call > max_diff_call:
                    max_diff_call = diff_call
                    max_callsite = callsite
                continue
        parsed_dict['max_diff_call_callsite'] = max_callsite
        # print_log("&&&&&&max_diff_call_callsite = " + str(max_callsite) + " process = " + process)
        return parsed_dict


class ShowPlatformSoftwareMemoryBacktrace():
    """ Parser for show platform software memory <process> switch active <R0> alloc backtrace """

    cli_command = 'show platform software memory {process} switch active {slot} alloc backtrace'

    def cli(self, process, slot, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None 
        else:
            out = output

         # Init vars
        parsed_dict = {}
        if out:
            backtraces_dict = parsed_dict.setdefault('backtraces', {})

        # backtrace: 1#2315ece11e07bc883d89421df58e37b6   maroon:7F740DEDC000+61F6 tdllib:7F7474D05000+B2B46 ui:7F74770E4000+4639A ui:7F74770E4000+4718C cdlcore:7F7466A6B000+37C95 cdlcore:7F7466A6B000+37957 uipeer:7F747A7A8000+24F2A evutil:7F747864E000+7966 evutil:7F747864E000+7745
        p1 = re.compile(r'backtrace: (?P<backtrace>[\w#\d\s:+]+)$')

        #   callsite: 2150603778, thread_id: 31884
        p2 = re.compile(r'callsite: +(?P<callsite>\d+), +thread_id: +(?P<thread_id>\d+)')

        #   allocs: 1, frees: 0, call_diff: 1
        p3 = re.compile(r'allocs: +(?P<allocs>(\d+)), +frees: +(?P<frees>(\d+)), +call_diff: +(?P<call_diff>(\d+))')

        for line in out.splitlines():
            line = line.strip()
 
            # backtrace: 1#2315ece11e07bc883d89421df58e37b6   maroon:7F740DEDC000+61F6 tdllib:7F7474D05000+B2B46 ui:7F74770E4000+4639A ui:7F74770E4000+4718C cdlcore:7F7466A6B000+37C95 cdlcore:7F7466A6B000+37957 uipeer:7F747A7A8000+24F2A evutil:7F747864E000+7966 evutil:7F747864E000+7745
            m = p1.match(line)
            if m:
                group = m.groupdict()
                backtrace = str(group['backtrace'])#.replace(" ", "*")
                one_backtrace_dict = backtraces_dict.setdefault(backtrace, {})
                continue

            #   callsite: 2150603778, thread_id: 31884
            m = p2.match(line)
            if m:
                group = m.groupdict()
                one_backtrace_dict['callsite'] = int(group['callsite'])
                one_backtrace_dict['thread_id'] = int(group['thread_id'])
                continue

            #   allocs: 1, frees: 0, call_diff: 1
            m = p3.match(line)
            if m:
                group = m.groupdict()
                one_backtrace_dict['allocs'] = int(group['allocs'])
                one_backtrace_dict['frees'] = int(group['frees'])
                one_backtrace_dict['call_diff'] = int(group['call_diff'])
                continue

        return parsed_dict


class ShowMemoryDebugLeaksChunks():
    """ Parser for show show memory debug leaks chunks """

    cli_command = 'show memory debug leaks chunks'

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None 
        else:
            out = output

         # Init vars
        parsed_dict = {}
        section = ""
        match_found = False
        if out:
            addresses_dict = parsed_dict.setdefault('addresses', {})


        #   Address        Size    Parent     Name                Alloc_pc
        # 7EFFCC9AB728    28 7EFFCA3DF410 (MallocLite)     :55FAE8AC9000+897EB09
        p1 = re.compile(r'^(?P<address>\w+) +(?P<size>\d+) +(?P<parent>\w+) +(?P<name>\S+)\s* (?P<alloc_pc>:\w+\+\w+)')

        # Tracekey : 1#2b336c808e968add0d0ca6a35d7a1d82
        p2 = re.compile(r'Tracekey : (?P<tracekey>[#\w]+)')

        
        for line in out.splitlines():
            line = line.strip()
 
            m = p2.match(line)
            if m:
                group = m.groupdict()
                tracekey = str(group['tracekey'])
                parsed_dict["tracekey"] = tracekey
                continue

            if 'reserve Processor memory' in line:
                section = "reserve_processor_memory"
                continue
            elif 'lsmpi_io memory' in line:
                section = "lsmpi_io_memory"
                continue
            elif 'Processor memory' in line:
                section = "processor_memory"
                continue


            m = p1.match(line)
            if m:
                group = m.groupdict()
                address = str(group['address'])
                one_address_dict = addresses_dict.setdefault(address, {})
                one_address_dict["size"] = group['size']
                one_address_dict["parent"] = str(group['parent'])
                one_address_dict["name"] = str(group['name'])
                one_address_dict["alloc_pc"] = str(group['alloc_pc'])
                one_address_dict["memory_type"] = section
                one_address_dict["tracekey"] = tracekey
                match_found = True
                continue

        if match_found:
            return parsed_dict
        else:
            return {}

#####################################################################################
#
#  Parser for TCAM memory use
#
#  Sample show command data to match:
#
#  Table                  Subtype      Dir      Max     Used    %Used       V4       V6     MPLS    Other
#  ------------------------------------------------------------------------------------------------------
#  Mac Address Table      EM           I       32768       22       0%        0        0        0       22
#  Mac Address Table      TCAM         I        1024       21       2%        0        0        0       21
#  L3 Multicast           EM           I        8192        0       0%        0        0        0        0
#
#####################################################################################
class ShowPlatformHardwareFedSwActiveFwdasicResourceTcamUtilization():

    ''' Parser for "show platform hardware fed sw active fwd-asic resource tcam utilization" '''

    cli_command = 'show platform hardware fed sw active fwd-asic resource tcam utilization'

    def test():
        print("this is a test from ShowPlatformHardwareFedSwActiveFwdasicResourceTcamUtilization")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output
#            out = '''MacAddressTable      TCAM         I        1024       21       2%        0        0        0       21'''

        # Init vars
        parsed_dict = {}

        if out:
            tcam_dict = parsed_dict.setdefault('tcam_table', {})
            app_dict = tcam_dict.setdefault('application', {})

        #Table                  Subtype      Dir      Max     Used    %Used       V4       V6     MPLS    Other
        #------------------------------------------------------------------------------------------------------
        # Mac Address Table      EM           I       32768       26       0%        0        0        0       26

        try:
            p1 = re.compile(r'(?P<table>.{27})(\s+)(?P<dir>(\S+))(\s+)(?P<max>(\d+))(\s+)(?P<used>(\d+))(\s+)(?P<pused>(\d))\..{4}(\s+)(?P<v4>(\d+))(\s+)(?P<v6>(\d+))(\s+)(?P<mpls>(\d+))(\s+)(?P<other>(\d+)).*')
        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()
    #
    # remove % characters from line which prevent pattern match
    #
            line = line.replace('%', '')

            m = p1.match(line)
            if m:
                group = m.groupdict()
                name = str(group['table'])
                if "Label" in name:
                    name = 'CTSCellMatrixVPN' + name
                one_proc_dict = app_dict.setdefault(name.replace(' ', ''), {})
                one_proc_dict['dir'] = str(group['dir'])
                one_proc_dict['max'] = int(group['max'])
                one_proc_dict['used'] = int(group['used'])
                one_proc_dict['percent-used'] = int(group['pused'])
                one_proc_dict['v4'] = int(group['v4'])
                one_proc_dict['v6'] = int(group['v6'])
                one_proc_dict['mpls'] = int(group['mpls'])
                one_proc_dict['other'] = int(group['other'])
                continue
        return parsed_dict

########################################################################################
#
# ParseXRSyslogMessage parses an XR syslog message into a Python dictionary that
# can be asserted as a FACT in CLIPS
#
########################################################################################
class ParseXRSyslogMessage():

    def syslog(self, message=None):
        ''' Parser for XR Syslog messages with the form:
            RP/0/RSP0/CPU0:Apr 26 20:30:07.568 UTC: ifmgr[257]: %PKT_INFRA-LINEPROTO-5-UPDOWN : Line protocol Up 

            Syslog FACTS will have the form 'source':'date':'time':'component':'syslog':'content' '''
        # Init vars
        parsed_dict = {}
        one_proc_dict = parsed_dict.setdefault('syslog-message', {})

        try:
            p1 = re.compile(r'(?P<source>([^:]+))(?P<date>.{7})(?P<time>(.*:))'
                             '(\s+)(?P<component>(.*:))(\s+)(?P<syslog>(.*:))(\s+)(?P<content>(.*))')
        except Exception as e:
            print(">>>> re exception: " + str(e))
        m = p1.match(message)
        if m:
            group = m.groupdict()
            one_proc_dict['source'] = str(group['source']).lstrip().rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['date'] = str(group['date']).lstrip().rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['source'] = str(group['source']).lstrip().rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['time'] = str(group['time']).lstrip().rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['component'] = str(group['component']).lstrip().rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['syslog'] = str(group['syslog']).lstrip().rstrip().rstrip(":").lstrip(":").replace(" ", "_").rstrip("_")
            one_proc_dict['content'] = str(group['content']).lstrip().rstrip(":").lstrip(":").replace(" ", "_").replace(",", "").replace(")", "").replace("(", "")

        return parsed_dict


########################################################################################
#
# ParseXESyslogMessage parses an XR syslog message into a Python dictionary that
# can be asserted as a FACT in CLIPS
#
########################################################################################
class ParseXESyslogMessage():

    def syslog(self, message=None):
        ''' Parser for Xe Syslog messages with the form:
             *Apr 27 11:12:14.549: %SYS-5-CONFIG_I: Configured from console by admin on vty5 (10.24.105.165)
             *Apr 27 11:12:45.184: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback222, changed state to up
             *Apr 27 11:12:46.394: %SYS-5-CONFIG_I: Configured from console by admin on vty5 (10.24.105.165)

            Syslog FACTS will have the form 'source':'date':'time':'component':'syslog':'content' '''
        # Init vars
        parsed_dict = {}
        one_proc_dict = parsed_dict.setdefault('syslog-message', {})

        try:
            p1 = re.compile(r'(?P<date>.{8})(?P<time>(.*:))(\s+)()(?P<syslog>(.*:))(\s+)(?P<content>(.*))')

        except Exception as e:
            print(">>>> re exception: " + str(e))
        m = p1.match(message)
        if m:
            group = m.groupdict()
            one_proc_dict['source'] = 'source'
            one_proc_dict['date'] = str(group['date']).lstrip().lstrip("*").rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['time'] = str(group['time']).lstrip().rstrip(":").lstrip(":").replace(" ", "_")
            one_proc_dict['component'] = 'xe-syslog'
            one_proc_dict['syslog'] = str(group['syslog']).lstrip().rstrip().rstrip(":").lstrip(":").replace(" ", "_").rstrip("_")
            one_proc_dict['content'] = str(group['content']).lstrip().rstrip(":").lstrip(":").replace(" ", "_").replace(",", "").replace(")", "").replace("(", "")

        return parsed_dict

########################################################################################
#
# ParseRFC5277Message parses a NETCONF RFC5277 notification message into a Python dictionary that
# can be asserted as a FACT in CLIPS
#
########################################################################################
class ParseRFC5277Message():

    def rfc5277(self, message=None):
        messagexml = xml.dom.minidom.parseString(message)
        # Init vars
        parsed_dict = {}
        one_proc_dict = parsed_dict.setdefault('rfc5277-message', {})

        try:
            one_proc_dict['source'] = 'source'
            one_proc_dict['datetime'] = str(messagexml.getElementsByTagName('eventTime')[0].firstChild.nodeValue)
            one_proc_dict['component'] = str(messagexml.getElementsByTagName('clogHistFacility')[0].firstChild.nodeValue)
            one_proc_dict['severity'] = str(messagexml.getElementsByTagName('clogHistSeverity')[0].firstChild.nodeValue)            
            one_proc_dict['msgname'] = str(messagexml.getElementsByTagName('clogHistMsgName')[0].firstChild.nodeValue).lstrip().rstrip(":").lstrip(":").replace(" ", "_").replace(",", "").replace(")", "").replace("(", "")
            one_proc_dict['msgcontent'] = str(messagexml.getElementsByTagName('clogHistMsgText')[0].firstChild.nodeValue).lstrip().rstrip(":").lstrip(":").replace(" ", "_").replace(",", "").replace(")", "").replace("(", "")
        except Exception as e:
            print(">>>> rfc5277 exception: " + str(e))

        return parsed_dict

# ==================================================
# Parser for 'show platform software fed active matm macTable'
# ==================================================
class ShowPlatformSoftwareFedActiveMatmMactable():

    ''' Parser for "show platform software fed active matm macTable vlan {vlan_id}" '''

    cli_command = ['show platform software fed active matm macTable',
                   'show platform software fed active matm macTable vlan {vlan_id}']

    def cli(self, vlan_id=None, output=None):
        if output is None:
            if vlan_id:
                cmd = self.cli_command[1].format(vlan_id=vlan_id)
            else:
                cmd = self.cli_command[0]
            out = self.device.execute(cmd)
        else:
            out = output

        # Init vars
        parsed_dict = {}
        if out:
            mac_table_dict = parsed_dict.setdefault('mac_table', {})

        # 1      7488.bb78.37ff         0x1      2      0      0  0x7fde0972eb88      0x7fde0972e7d8      0x0                 0x7fde0899f078            300       17  HundredGigE1/0/11               Yes

        p1 = re.compile(r'^(?P<vlan>(\d+))(\s+)(?P<mac>.{14})(\s+)'
                        '(?P<type>(0[xX][a-f0-9A-F]+))(\s+)'
                        '(?P<seq>(\d+))(\s+)(?P<ec_bits>(\d+))(\s+)(?P<flags>(\d+))(\s+)'
                        '(?P<mac_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<si_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<ri_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<di_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<a_time>(\d+))(\s+)(?P<e_time>(\d+))(\s+)'
                        '(?P<ports>(\S+))(\s+)(?P<consistency>([a-zA-Z]+))')

        # Total Mac number of addresses:: 1
        p2 = re.compile(r'Total +Mac +number +of +addresses:: +(?P<total>(\d+))')

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                mac = str(group['mac'])
                vlan = int(group['vlan'])
                per_vlan_mac_table_dict = mac_table_dict.setdefault('per_vlan_mac_table', {}).setdefault(vlan, {})
                per_vlan_mac_table_dict['vlan'] = vlan
                one_mac_dict = per_vlan_mac_table_dict.setdefault('mac_entry', {}).setdefault(mac, {})
                #one_mac_dict['vlan'] = int(group['vlan'])
                one_mac_dict['mac'] = mac
                one_mac_dict['type'] = group['type']
                one_mac_dict['seq'] = int(group['seq'])
                one_mac_dict['ec_bits'] = int(group['ec_bits'])
                one_mac_dict['flags'] = int(group['flags'])
                one_mac_dict['mac_handle'] = group['mac_handle']
                one_mac_dict['si_handle'] = group['si_handle']
                one_mac_dict['ri_handle'] = group['ri_handle']
                one_mac_dict['di_handle'] = group['di_handle']
                one_mac_dict['a_time'] = int(group['a_time'])
                one_mac_dict['e_time'] = int(group['e_time'])
                one_mac_dict['ports'] = group['ports']
                one_mac_dict['consistency'] = group['consistency']
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                mac_table_dict['total'] = int(group['total'])

        return parsed_dict

# ==================================================
# Parser for 'show platform software fed switch active matm macTable'
# ==================================================
class ShowPlatformSoftwareFedSwitchActiveMatmMactable():

    ''' Parser for "show platform software fed switch active matm macTable vlan {vlan_id}" '''

    cli_command = ['show platform software fed switch active matm macTable',
                   'show platform software fed switch active matm macTable vlan {vlan_id}']

    def cli(self, vlan_id=None, output=None):
        if output is None:
            if vlan_id:
                cmd = self.cli_command[1].format(vlan_id=vlan_id)
            else:
                cmd = self.cli_command[0]
            out = self.device.execute(cmd)
        else:
            out = output

        # Init vars
        parsed_dict = {}
        if out:
            mac_table_dict = parsed_dict.setdefault('mac_table', {})

        # 1      7488.bb78.37ff         0x1      2      0      0  0x7fde0972eb88      0x7fde0972e7d8      0x0                 0x7fde0899f078            300       17  HundredGigE1/0/11               Yes

        p1 = re.compile(r'^(?P<vlan>(\d+))(\s+)(?P<mac>.{14})(\s+)'
                        '(?P<type>(0[xX][a-f0-9A-F]+))(\s+)'
                        '(?P<seq>(\d+))(\s+)(?P<ec_bits>(\d+))(\s+)(?P<flags>(\d+))(\s+)'
                        '(?P<mac_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<si_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<ri_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<di_handle>(0[xX][0-9a-fA-F]+))(\s+)'
                        '(?P<a_time>(\d+))(\s+)(?P<e_time>(\d+))(\s+)'
                        '(?P<ports>(\S+))(\s+)(?P<consistency>([a-zA-Z]+))')

        # Total Mac number of addresses:: 1
        p2 = re.compile(r'Total +Mac +number +of +addresses:: +(?P<total>(\d+))')

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                mac = str(group['mac'])
                vlan = int(group['vlan'])
                per_vlan_mac_table_dict = mac_table_dict.setdefault('per_vlan_mac_table', {}).setdefault(vlan, {})
                per_vlan_mac_table_dict['vlan'] = vlan
                one_mac_dict = per_vlan_mac_table_dict.setdefault('mac_entry', {}).setdefault(mac, {})
                #one_mac_dict['vlan'] = int(group['vlan'])
                one_mac_dict['mac'] = mac
                one_mac_dict['type'] = group['type']
                one_mac_dict['seq'] = int(group['seq'])
                one_mac_dict['ec_bits'] = int(group['ec_bits'])
                one_mac_dict['flags'] = int(group['flags'])
                one_mac_dict['mac_handle'] = group['mac_handle']
                one_mac_dict['si_handle'] = group['si_handle']
                one_mac_dict['ri_handle'] = group['ri_handle']
                one_mac_dict['di_handle'] = group['di_handle']
                one_mac_dict['a_time'] = int(group['a_time'])
                one_mac_dict['e_time'] = int(group['e_time'])
                one_mac_dict['ports'] = group['ports']
                one_mac_dict['consistency'] = group['consistency']
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                mac_table_dict['total'] = int(group['total'])

        return parsed_dict

class ShowHardwareAccessListResourceUtilization():

    ''' Parser for "show hardware access-list resource utilization" '''

    cli_command = 'show hardware access-list resource utilization'

    def test():
        print("this is a test from ShowHardwareAccessListResourceUtilization")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            acl_tcam_dict = parsed_dict.setdefault('acl_tcam', {})

#    Protocol CAM                            0       246     0.00   
#    Mac Etype/Proto CAM                     0       14      0.00   
#    L4 op labels, Tcam 0                    0       1023    0.00   

        try:
            p1 = re.compile(r'(?P<type>.{40})(?P<used>(\d+))(\s+)(?P<free>(\d+))(\s+)(?P<percentused>\d*\.?\d*$)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                name = str(group['type'])
                name = name.replace(' ', '').replace(',', '').replace('/', '')
                one_proc_dict = acl_tcam_dict.setdefault(name, {})
                one_proc_dict['used'] = int(group['used'])
                one_proc_dict['free'] = int(group['free'])
                one_proc_dict['percentused'] = float(group['percentused'])
                continue
        return parsed_dict
# ==================================================
# Parser for 'show vlan id <vlan id> Get first port associated if it exists
# ==================================================
class ShowSinglePortVlanId():

    def parse(self, output=None):

    # Init vars
        parsed_dict = {}
        dict = parsed_dict.setdefault('connected_ports', {})

    # VLAN Name Status Ports
    # ---- -------------------------------- --------- -------------------------------
    # 2 VLAN0002 active Gi1/0/1, Gi1/0/2

    # Expected dictionary output: {'connected_ports': {'Gi1/0/2': {'port': 'Gi1/0/2'}}}
    
        p1 = re.compile(r'.*active(\s+)(?P<port>(\S+)).*')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                port = str(group["port"]).rstrip(",")
                port_dict = dict.setdefault(port, {})
                port_dict['port'] = port
                break
        return parsed_dict
        # ==================================================
# Parser for 'show lisp instance {instance_id} ipv4'
# Used when LISP instance is initialized and active
# ==================================================
class ShowLoggingLast():

    ''' Parser for "show logging last {num_lines}" '''

    cli_command = 'show logging last {num_lines}'

##################################################################
#
# Selected fields from show command response
#
##################################################################

    def test(self):
        test_message = '''
Syslog logging: enabled (0 messages dropped, 2 messages rate-limited, 0 flushes, 0 overruns, xml disabled, filtering disabled)

    Console logging: level debugging, 258 messages logged, xml disabled,
                     filtering disabled, discriminator(nosel), 
                     0 messages rate-limited, 98 messages dropped-by-MD
    Monitor logging: level debugging, 218 messages logged, xml disabled,
                     filtering disabled, discriminator(nosel), 
                     0 messages rate-limited, 98 messages dropped-by-MD
    Buffer logging:  level debugging, 358 messages logged, xml disabled,
                    filtering disabled
    Exception Logging: size (4096 bytes)
    Count and timestamp logging messages: disabled
    File logging: disabled
    Persistent logging: disabled


Showing last 4 lines

Log Buffer (102400 bytes):

*Mar 29 17:01:20.953: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 172.20.86.186] [localport: 22] at 17:01:20 UTC Mon Mar 29 2021
*Mar 29 17:03:26.255: %SYS-6-LOGOUT: User admin has exited tty session 4(172.20.86.186)
*Mar 29 17:25:20.330: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 10.24.15.5] [localport: 22] at 17:25:20 UTC Mon Mar 29 2021
*Mar 29 17:26:49.017: %SYS-5-CONFIG_I: Configured from console by admin on vty3 (10.24.15.5)
'''
        expected_result='''{'log_instance': {'1': {'datetime': 'Mar 29 17:01:20.953: ', 'facility': 'SEC_LOGIN', 'level': 5, 'message': 'LOGIN_SUCCESS', 'note': ' Login Success [user: admin] [Source: 172.20.86.186] [localport: 22] at 17:01:20 UTC Mon Mar 29 2021'}, '2': {'datetime': 'Mar 29 17:03:26.255: ', 'facility': 'SYS', 'level': 6, 'message': 'LOGOUT', 'note': ' User admin has exited tty session 4(172.20.86.186)'}, '3': {'datetime': 'Mar 29 17:25:20.330: ', 'facility': 'SEC_LOGIN', 'level': 5, 'message': 'LOGIN_SUCCESS', 'note': ' Login Success [user: admin] [Source: 10.24.15.5] [localport: 22] at 17:25:20 UTC Mon Mar 29 2021'}, '4': {'datetime': 'Mar 29 17:26:49.017: ', 'facility': 'SYS', 'level': 5, 'message': 'CONFIG_I', 'note': ' Configured from console by admin on vty3 (10.24.15.5)'}}}
'''

        print("\n******* ShowLoggingLast Parser Test Function Result **************\n")
        try:
            parsed_fact = self.parse(output=test_message)
            print("\n%%%% Parsed canned ShowLoggingLast data\n")
            print(parsed_fact)
            if str(expected_result) != str(parsed_fact):
                print("\n%%%% Error testing ShowLoggingLast Parser\n")
                print("\nExpected ShowLoggingLast data: \n", expected_result)
                print("\nGenerated ShowLoggingLast data: \n", parsed_fact)
            else:
                print("\n%%%% ShowLoggingLast Parser Test Successful %%%%\n")
                
        except Exception as e:
            print("\n%%%% Exception testing ShowLoggingLast Parser: \n" + str(e))
#
# *Mar 29 17:01:20.953: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 172.20.86.186] [localport: 22] at 17:01:20 UTC Mon Mar 29 2021
# 
    def parse(self, num_lines=None, output=None, test=None, facility_filter=None):
        if output is None:
            if num_lines:
                cmd = self.cli_command[1].format(num_lines=num_lines)
            else:
                cmd = self.cli_command[0]
            if test is None:     # If testing parser do not execute device command
               out = self.device.execute(cmd)
        else:
            out = output
#
# The variable out contains the show command data either passed in to the instance or read from the device
#
        try:
            log_number = 1
            parsed_dict = {}
            instance_dict = parsed_dict.setdefault('log_instance', {}) # This is the name of the deftemplate that will contain the FACT
            for line in out.splitlines():
                line = line.strip()
                if num_lines != None:
                    if log_number > num_lines: break
#
# Compile regex for each of the lines in the output that contain required data
#
                p1 = re.compile(r'\*(?P<datetime>[^%]*)%(?P<facility>[^-]*)\-(?P<level>(\d+))\-(?P<message>[^:]*):(?P<note>.*$)') # Syslog message (see above) 
#
# Search through the output and if a match is found go to end of loop to get the next line
#
                m = p1.match(line)
                if m:
                    group = m.groupdict()
 #
 # Create a parsed dictionary instnace if the facility in the logging message matches the facility_filter
 #
                    if (str(group['facility']) == str(facility_filter)) or (facility_filter == None):
                        per_instance_dict = instance_dict.setdefault(str(log_number), {})
                        per_instance_dict['datetime'] = str(group['datetime']).rstrip(': ').replace(' ','_')
                        per_instance_dict['facility'] = str(group['facility'])
                        per_instance_dict['level'] = int(group['level'])
                        per_instance_dict['message'] = str(group['message'])
                        per_instance_dict['note'] = str(group['note']).replace(' ','_').replace('"','').replace("'","")
                        log_number = log_number + 1
                    continue

            return parsed_dict
        except Exception as e:
            print("\n%%%% Error processing ShowLoggingLast: " + str(e))
            print(instance_dict)

# ==================================================
# Parser for dmiauthd btace log - extract %DMI-5-CONFIG_I actions
# ==================================================

class BtraceDmiauthdConfigI():
#
# show command run to save dmiauthd log:
#   "show platform software trace message dmiauthd switch active R0 | redirect flash:/guest-share/btrace-file"
#
# Sample log message decoded from btrace file:
#
#   "2021/03/19 02:22:51.665178 {dmiauthd_R0-0}{1}: [errmsg] [14769]: (note): %DMI-5-CONFIG_I: R0/0: dmiauthd: Configured from NETCONF/RESTCONF by admin, transaction-id 3237
#    2021/03/19 02:22:52.665178 {dmiauthd_R0-0}{1}: [errmsg] [14769]: (note): %DMI-5-CONFIG_I: R0/0: dmiauthd: Configured from NETCONF/RESTCONF by admin, transaction-id 3238"
#
# Parser test function
#
    def test(self):
        test_message = '''
2021/03/19 02:22:51.665178 {dmiauthd_R0-0}{1}: [errmsg] [14769]: (note): %DMI-5-CONFIG_I: R0/0: dmiauthd: Configured from NETCONF/RESTCONF by admin, transaction-id 3237
2021/03/19 02:22:52.665178 {dmiauthd_R0-0}{1}: [errmsg] [14769]: (note): %DMI-5-CONFIG_I: R0/0: dmiauthd: Configured from NETCONF/RESTCONF by admin, transaction-id 3238'''

        expected_result='''{'config_transaction': {'3237': {'transaction_id': '3237', 'date': '2021/03/19', 'time': '02:22:51.665178', 'method': 'NETCONF/RESTCONF', 'config_by': 'admin'}, '3238': {'transaction_id': '3238', 'date': '2021/03/19', 'time': '02:22:52.665178', 'method': 'NETCONF/RESTCONF', 'config_by': 'admin'}}}'''

        print("\n******* BtraceDmiauthdConfigI Parser Test Function Result **************\n")
        try:
            parsed_fact = self.parse(output=test_message)
            print("\n%%%% Parsed canned ShowLispInstanceActive data\n")
            print(parsed_fact)
            if str(expected_result) != str(parsed_fact):
                print("\n%%%% Error testing BtraceDmiauthdConfigI Parser\n")
                print("\nExpected BtraceDmiauthdConfigI: \n", expected_result)
                print("\nGenerated BtraceDmiauthdConfigI: \n", parsed_fact)
            else:
                print("\n%%%% BtraceDmiauthdConfigI Parser Test Successful %%%%\n")
                
        except Exception as e:
            print("\n%%%% Exception testing BtraceDmiauthdConfigI Parser: \n" + str(e))
#
# parser for btrace log for configurations applied to the device
#
    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        trans_dict = parsed_dict.setdefault('config_transaction', {})

        p1 = re.compile(r'(?P<date>(\d{4}\/\d{2}\/\d{2})) (?P<time>(\S{15})).+Configured from (?P<method>(\S+)) by (?P<config_by>(\S+)) transaction\-id (?P<transaction_id>(\d+))')

        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                name = str(group['transaction_id'])
                per_instance_dict = trans_dict.setdefault(name, {})
                per_instance_dict['transaction_id'] = str(group['transaction_id'])
                per_instance_dict['date'] = str(group['date'])
                per_instance_dict['time'] = str(group['time'])
                per_instance_dict['method'] = str(group['method'])
                per_instance_dict['config_by'] = str(group['config_by']).rstrip(",")
        return parsed_dict
        
# ==================================================
# Parser for dmiauthd btace log - extract %DMI-5-CONFIG_I actions
# ==================================================

class BtraceDmiauthdConfigMode():
#
# show command run to save dmiauthd log:
#   "show platform software trace message dmiauthd switch active R0 | redirect flash:/guest-share/btrace-file"
#
# Sample log message decoded from btrace file:
#
#   "2021/04/12 04:45:30.449522340 {dmiauthd_R0-0}{1}: [dmid] [7897]: UUID: 0, ra: 0, TID: 0 (note): [iosp_thread] cli config mode handler: CLI config mode enter event (ttynum=14, mytty=64)"
#
# Parser test function
#
    def test(self):
        test_message = '''
2021/04/12 04:45:30.449522340 {dmiauthd_R0-0}{1}: [dmid] [7897]: UUID: 0, ra: 0, TID: 0 (note): [iosp_thread] cli config mode handler: CLI config mode enter event (ttynum=14, mytty=64)'''

        expected_result='''{'config_mode_event': {'1': {'date': '2021/04/12', 'time': '04:45:30.449522', 'event': 'CLI config mode enter event (ttynum=14, mytty=64)'}}}'''

        print("\n******* BtraceDmiauthdConfigMode Parser Test Function Result **************\n")
        try:
            parsed_fact = self.parse(output=test_message)
            print("\n%%%% Parsed canned ShowLispInstanceActive data\n")
            print(parsed_fact)
            if str(expected_result) != str(parsed_fact):
                print("\n%%%% Error testing BtraceDmiauthdConfigMode Parser\n")
                print("\nExpected BtraceDmiauthdConfigMode: \n", expected_result)
                print("\nGenerated BtraceDmiauthdConfigMode: \n", parsed_fact)
            else:
                print("\n%%%% BtraceDmiauthdConfigMode Parser Test Successful %%%%\n")
                
        except Exception as e:
            print("\n%%%% Exception testing BtraceDmiauthdConfigI Parser: \n" + str(e))
#
# parser for btrace log for configurations applied to the device
#
    def parse(self, output=None):

        # Init vars
        parsed_dict = {}
        trans_dict = parsed_dict.setdefault('config_mode_event', {})

        p1 = re.compile(r'(?P<datetime>[^{]*) .*config mode handler: (?P<event>[^(]*)\(ttynum=(?P<ttynum>(\d+)).*')

        counter = 1
        for line in output.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                per_instance_dict = trans_dict.setdefault(str(counter), {})
                per_instance_dict['datetime'] = str(group['datetime'])
                per_instance_dict['event'] = str(group['event'])
                per_instance_dict['ttynum'] = str(group['ttynum'])
                counter = counter + 1
        return parsed_dict

# ==================================================
# Parser for 'show interface {name}'
# ==================================================
class ShowInterfaceState():

    ''' Parser for "show interface {name}" '''

    cli_command = 'show interface {name}'

##################################################################
#
# Selected fields from show command response
#
##################################################################

    test_message = '''
GigabitEthernet0/0 is up, line protocol is up 
  Hardware is RP management port, address is a0f8.490e.4a80 (bia a0f8.490e.4a80)
  Internet address is 172.27.255.24/24
  MTU 1500 bytes, BW 100000 Kbit/sec, DLY 100 usec, 
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Full Duplex, 100Mbps, link type is auto, media type is RJ45
  output flow-control is unsupported, input flow-control is unsupported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 00:00:00, output 00:00:00, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/12474/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/40 (size/max)
  5 minute input rate 2000 bits/sec, 4 packets/sec
  5 minute output rate 2000 bits/sec, 2 packets/sec
     2215841 packets input, 147836031 bytes, 0 no buffer
     Received 0 broadcasts (0 IP multicasts)
     0 runts, 0 giants, 0 throttles 
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 watchdog, 0 multicast, 0 pause input
     297938 packets output, 49190986 bytes, 0 underruns
     Output 0 broadcasts (0 IP multicasts)
     0 output errors, 0 collisions, 0 interface resets
     1 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier, 0 pause output
     0 output buffer failures, 0 output buffers swapped out
     0 carrier transitions
'''
#
# The parse method inserts parameters if required into the show command and
# executes the show command and parses the response into a python dictionary
# 
    def parse(self, instance_id=None, output=None, test=None):
        if output is None:
            if instance_id:
                cmd = self.cli_command[1].format(instance_id=instance_id)
            else:
                cmd = self.cli_command[0]
            if test is None:     # If testing parser do not execute device command
               out = self.device.execute(cmd)
        else:
            out = output
#
# The variable out contains the show command data either passed in to the instance or read from the device
#
        try:
            parsed_dict = {}
            for line in out.splitlines():
                line = line.strip()
#
# Compile regex for each of the lines in the output that contain required data
#
                p1 = re.compile(r'(?P<intf_name>(\S+)).is\s(?P<admin_state>[^,]*).\sline protocol is\s(?P<line_state>(\S+))') # interface, admin and line state
#
# Search through the output and if a match is found go to end of loop to get the next line
#
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    parsed_dict['intf_name'] = group['intf_name']
                    parsed_dict['admin_state'] = group['admin_state']
                    parsed_dict['line_state'] = group['line_state']
                    break

            return parsed_dict
        except Exception as e:
            print("%%%% Error processing ShowInterfaceState: " + str(e))

class ShowIpInterfaceBrief():

    ''' Parser for "show ip interface brief <interface>" '''

    cli_command = 'show ip interface brief {interface}'

    def test():
        print("this is a test from ShowIpInterfaceBrief")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            intf_dict = parsed_dict.setdefault('interface_ip_address', {})

        #ddmi-cat9300-2#
        #Interface              IP-Address      OK? Method Status                Protocol
        #Vlan1                  19.1.1.1        YES manual up                    up

        try:
            p1 = re.compile(r'^(?P<interface>\w+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<ok>(YES|NO))\s+(?P<method>\w+)\s+(?P<status>\w+)\s+(?P<protocol>\w+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()
            
            m = p1.match(line)
            if m:
                group = m.groupdict()
                interface = str(group["interface"].lstrip('"').rstrip('"'))
                interface_dict = intf_dict.setdefault(interface, {})
                interface_dict['ip'] = str(group['ip'])
                interface_dict['ok'] = str(group['ok'])
                interface_dict['method'] = str(group['method'])
                interface_dict['status'] = str(group['status'])
                interface_dict['protocol'] = str(group['protocol'])
                continue

        return parsed_dict

class ShowIpInterfaceVlan():

    ''' Parser for "show ip interface vlan <vlan>" '''

    cli_command = 'show ip interface vlan {vlan}'

    def test():
        print("this is a test from ShowIpInterfaceVlan")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output



        if out:
            intf_dict = parsed_dict.setdefault('interf_ip_address', {})

       	#ddmi-cat9300-2#
	#Vlan1 is up, line protocol is up
  	# Internet address is 19.1.1.1/24
  	# Broadcast address is 255.255.255.255
  	# Address determined by setup command
  	# MTU is 1500 bytes
  	# Helper address is not set
  	# Directed broadcast forwarding is disabled 

        try:
            p1 = re.compile(r'^(?P<interface>[\w\/\.\-\:]+)\s+is\s+(?P<enabled>\w+)\,\s+line\s+protocol\sis\s(?P<status>\w+)')
            p2 = re.compile(r'^.*Internet\s+[A|a]ddress\s+is\s+(?P<ipv4>.*)\/(?P<prefix>[0-9]+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                interface = str(group["interface"].lstrip('"').rstrip('"'))
                interface_dict = intf_dict.setdefault(interface, {})
                interface_dict['enable'] = str(group["enabled"])
                continue
	
            m = p2.match(line)
            if m:
                group = m.groupdict()
                interface_dict['ipv4'] = str(group['ipv4'])
                interface_dict['prefix'] = str(group['prefix'])
                continue
            
        return parsed_dict

class ShowCtsRolebasedSgtmapVrfAll():

    ''' Parser for "show cts role-based sgt-map vrf <vrf> all" '''

    cli_command = 'show cts role-based sgt-map vrf {vrf} all'

    def test():
        print("this is a test from ShowCtsRolebasedSgtmapVrfAll")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            sgt_dict = parsed_dict.setdefault('ipv4_sgt_binding', {})

	#ddmi-cat9300-2#
	#Active IPv4-SGT Bindings Information
	#
	#IP Address              SGT     Source
	#============================================
	#19.0.0.0/24             35          CLI
	#19.100.100.100/24       36          LISP


        try:
            p1 = re.compile(r'^(?P<ip>.\d+\.\d+\.\d+\.\d+)\/(?P<prefix>.\d+)\s+(?P<sgt>\d+)\s+(?P<src>\w+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        i = 0
        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                id = f"bind{i}"
                sgtbind_dict = sgt_dict.setdefault(id, {})
                sgtbind_dict['ip'] = str(group["ip"])
                sgtbind_dict['prefix'] = str(group["prefix"])
                sgtbind_dict['sgt'] = str(group["sgt"])
                sgtbind_dict['src'] = str(group["src"])
                i += 1
                continue
        
        return parsed_dict

class ShowGrouppolicyTrafficsteeringPermissionsFromTo():

    ''' Parser for "show group-policy traffic-steering permissions from <no> to <no>" '''

    cli_command = 'show group-policy traffic-steering permissions from {no} to {no}'

    def test():
        print("this is a test from ShowGrouppolicyTrafficsteeringPermissionsFromTo")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            grppolicy_dict = parsed_dict.setdefault('group_policy_traffic_steering_permissions', {})

	#ddmi-cat9300-2#
	#Group Policy traffic-steering permissions
	#
	#Source SGT      Destination SGT      Steering Policy
	#-----------------------------------------------------
    	#35                36              contract_eng1-02

        try:
            p1 = re.compile(r'^(?P<srcsgt>\d+)\s+(?P<destsgt>\d+)\s+(?P<policy>.*)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                per_instance_dict = grppolicy_dict.setdefault('per_instance_dict', {})
                per_instance_dict['srcsgt'] = str(group["srcsgt"])
                per_instance_dict['destsgt'] = str(group["destsgt"])
                per_instance_dict['policy'] = str(group["policy"])
                continue        
        
        return parsed_dict

class ShowGrouppolicyTrafficsteeringPolicySgt():

    ''' Parser for "show group-policy traffic-steering policy sgt <sgt>" '''

    cli_command = 'show group-policy traffic-steering policy sgt {sgt}'

    def test():
        print("this is a test from ShowGrouppolicyTrafficsteeringPermissions")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            sgt_dict = parsed_dict.setdefault('sgt_policy', {})

	#ddmi-cat9300-2#
	#Traffic-Steering SGT Policy
	#===========================
	#SGT: 35-01
	#SGT Policy Flag: 0x41400001
	#Traffic-Steering Source List:
	#  Source SGT: 35-01, Destination SGT: 36-01
	#  steer_type = 80
	#  steer_index = 1
	#  name   = contract_eng1-02
	#  IP protocol version = IPV4
	#  refcnt = 1
	#  flag   = 0x41400000
	#  stale  = FALSE
	#  Traffic-Steering ACEs:
	#    1 redirect 6 any 23 service service_ENG1
	#    2 redirect 17 any 123 service service_ENG1

	#Traffic-Steering Destination List: Not exist
	#Traffic-Steering Multicast List: Not exist
	#Traffic-Steering Policy Lifetime = 86400 secs
	#Traffic-Steering Policy Last update time = 15:29:30 UTC Wed Jul 7 2021
	#Policy expires in 0:11:26:03 (dd:hr:mm:sec)
	#Policy refreshes in 0:11:26:03 (dd:hr:mm:sec)

        try:
            p1 = re.compile(r'^(?P<idx1>\d+)\s+redirect\s+(?P<idx2>\d+)\s+any\s+(?P<idx3>\d+)\s+service\s+(?P<ace>.*)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        i = 0
        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                id = f"ACE{i}"
                one_proc_dict = sgt_dict.setdefault(id, {})
                one_proc_dict['idx1'] = str(group['idx1'])
                one_proc_dict['idx2'] = str(group['idx2'])
                one_proc_dict['idx3'] = str(group['idx3'])
                one_proc_dict['ace'] = str(group['ace'])
                i += 1
                continue
        
        return parsed_dict

class ShowPdmSteeringPolicy():

    ''' Parser for "show pdm steering policy <policy>" '''

    cli_command = 'show pdm steering policy {policy}'

    def test():
        print("this is a test from ShowPdmSteeringPolicy")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            policy_dict = parsed_dict.setdefault('steering_policy', {})

	#ddmi-cat9300-2#
	#Steering Policy contract_eng1-02
	#    1 redirect protocol 6 src-port any dst-port eq 23 service service_ENG1 (625 matches)
	#    2 redirect protocol 17 src-port any dst-port eq 123 service service_ENG1 (0 match)

        try:
            p1 = re.compile(r'^Steering\s+Policy\s+(?P<name>.*)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                per_instance_dict = policy_dict.setdefault('per_instance_dict', {})
                per_instance_dict['policy-name'] = str(group['name'])
                continue
        
        return parsed_dict

class ShowPdmSteeringService():

    ''' Parser for "show pdm steering service" '''

    cli_command = 'show pdm steering service'

    def test():
        print("this is a test from ShowPdmSteeringService")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            pdm_dict = parsed_dict.setdefault('steering_service', {})

        #9400-vijacob#show pdm steering service
        #Steering Service service_ENG1  >>>> This has the VN name encoded
        #    mode routed address 192.102.0.2 selector 255 vnid 4099

        try:
            p1 = re.compile(r'^Steering\s+Service\s+(?P<svc>\w+)')
            p2 = re.compile(r'^.*mode\s+routed\s+address\s+(?P<ip>.\d+\.\d+\.\d+\.\d+).*(?P<vnid>\d{4})')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                ste_service = str(group["svc"])
                stebind_dict = pdm_dict.setdefault(ste_service, {})
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['ip'] = str(group["ip"])
                stebind_dict['vnid'] = str(group["vnid"])
                continue
        
        return parsed_dict

class ShowLispInstanceIdVnid():

    ''' Parser for "show lisp instance-id <vnid> ipv4 | i EID table" '''

    cli_command = 'show lisp instance-id {vnid} ipv4 | i EID table '

    def test():
        print("this is a test from ShowLispInstanceIdVnid")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            vnid_dict = parsed_dict.setdefault('vnid_vrf', {})

        #9400-vijacob#show lisp instance-id 4099 ipv4 | i EID table 
        #   EID table:                                vrf ENG1

        try:
            p = re.compile(r'^.*vrf\s+(?P<vrf>\w+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p.match(line)
            if m:
                group = m.groupdict()
                per_instance_dict = vnid_dict.setdefault('per_instance_dict', {})
                per_instance_dict['vrf'] = str(group["vrf"])
                continue

        return parsed_dict

class ShowPdmSteeringServiceDetail():

    ''' Parser for "show pdm steering service <service> detail " '''

    cli_command = 'show pdm steering service {service} detail  '

    def test():
        print("this is a test from ShowPdmSteeringServiceDetail")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            steering_dict = parsed_dict.setdefault('steering_detail', {})

        #9400-vijacob#show pdm steering service service_ENG1 detail
        #Service Name   : service_ENG1
        #Service ID     : 1419704521
        #Ref count      : 4
        #Stale          : FALSE
        #   Firewall mode      : routed
        #   Service IP         : 192.102.0.2
        #   Service Locator    : 255
        #   VRF ID             : 4
        #   Vnid               : 4099
        #   RLOC Status        : Received
        #   no.of rlocs        : 1
        #       *1. RLOC IP: 172.16.5.11    Weight: 10    Priority: 0
        #   Owner              : GPP

        try:
            p1 = re.compile(r'^Service\sName\s+:\s+(?P<srv_name>\w+)')
            p2 = re.compile(r'^Service\s+ID\s+:\s+(?P<srv_id>\d+)')
            p3 = re.compile(r'.RLOC\s+IP:\s+(?P<ip>\d+\.\d+\.\d+\.\d+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                service_name = str(group["srv_name"])
                per_instance_dict = steering_dict.setdefault(service_name, {})
                per_instance_dict['service_name'] = str(group["srv_name"])
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                per_instance_dict['service_id'] = str(group["srv_id"])

            m = p3.match(line)
            if m:
                group = m.groupdict()
                per_instance_dict['rloc_ip'] = str(group["ip"])

        return parsed_dict

class ShowPlatformSoftwareSteeringpolicyForwardingmanagerGlobal():

    ''' Parser for "show platform software steering-policy forwarding-manager R0 global " '''

    cli_command = 'show platform software steering-policy forwarding-manager R0 global'

    def test():
        print("this is a test from ShowPlatformSoftwareSteeringpolicyForwardingmanagerGlobal")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            steering_dict = parsed_dict.setdefault('steering_global', {})

        #9400-vijacob#show platform software steering-policy forwarding-manager R0 global
        #Global Enforcement: On

        try:
            p = re.compile(r'^Global\s+Enforcement:\s+(?P<mode>\w+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p.match(line)
            if m:
                group = m.groupdict()
                per_instance_dict = steering_dict.setdefault('per_instance_dict', {})
                per_instance_dict['mode'] = str(group["mode"])
                continue

        return parsed_dict

class ShowPlatformSoftwareSteeringpolicyForwardingmanagerServiceId():

    ''' Parser for "show platform software steering-policy forwarding-manager R0
        service-id <service_id>  " '''

    cli_command = 'show platform software steering-policy forwarding-manager R0 service-id {service_id} '

    def test():
        print("this is a test from ShowPlatformSoftwareSteeringpolicyForwardingmanagerServiceId")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            steering_dict = parsed_dict.setdefault('steering_service', {})

        #9400-vijacob#show platform software steering-policy forwarding-manager R0 service-id 1419704521 
        #Forwarding Manager policy-defn Redirect action metadata

        #Service ID: 1419704521, Service VRF ID: 4, Firewall mode: Routed
        #Service Selector: 255, Service IP address: 192.102.0.2
        #Number of RLOCs: 1
        #Priority    Weightage    VNID        RLOC IP address                      
        #------------------------------------------------------------------------
        #0                      10           4099        172.16.5.11               

        try:
            p1 = re.compile(r'^Service\s+ID:\s+(?P<svc_id>\d+)')
            p2 = re.compile(r'^.*Service\s+IP\s+address:\s+(?P<svc_ip>\d+\.\d+\.\d+\.\d+)')
            p3 = re.compile(r'\d.+\d\d\d\d\s+(?P<rloc_ip>\d+\.\d+\.\d+\.\d+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                ste_service = str(group["svc_id"])
                stebind_dict = steering_dict.setdefault(ste_service, {})
                stebind_dict['service_id'] = str(group["svc_id"])
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['service_ip'] = str(group["svc_ip"])
                continue

            m = p3.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['rloc_ip'] = str(group["rloc_ip"])
                continue

        return parsed_dict

class ShowPlatformSoftwareFedActiveSecurityfedSisredirectFirewallServiceidDetailed():

    ''' Parser for "show platform software fed active security-fed sis-redirect
        firewall service-id <service-id> detailed " '''

    cli_command = 'show platform software fed active security-fed sis-redirect firewall service-id {service-id} detailed '

    def test():
        print("this is a test from ShowPlatformSoftwareFedActiveSecurityfedSisredirectFirewallServiceidDetailed")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            security_dict = parsed_dict.setdefault('service_detail', {})

        #9400-vijacob#show platform software fed active security-fed sis-redirect firewall service-id 1419704521 detailed 
        #Service ID               : 1419704521
        #VRF ID                   : 4
        #IP                       : 192.102.0.2/32
        #Redirect Hdl             : 0x7f7e664452e8
        #HTM Hdl                  : 0x7f7e664455c8
        #Route Prefix             : 192.102.0.0/30 
        #Next Hop                 : 172.16.5.11 
        #Adj Last Modified        : 2021-07-30,13:32:07           

        try:
            p1 = re.compile(r'^Service\s+ID\s+:\s+(?P<svc_id>\d+)')
            p2 = re.compile(r'^IP\s+:\s+(?P<svc_ip>\d+\.\d+\.\d+\.\d+\/\d+)')
            p3 = re.compile(r'^Route\s+Prefix\s+:\s+(?P<rt_prefix>\d+\.\d+\.\d+\.\d+\/\d+)')
            p4 = re.compile(r'^Next\s+Hop\s+:\s+(?P<nxt_hop>\d+\.\d+\.\d+\.\d+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                ste_service = str(group["svc_id"])
                stebind_dict = security_dict.setdefault(ste_service, {})
                stebind_dict['service_id'] = str(group["svc_id"])
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['service_ip'] = str(group["svc_ip"])
                continue

            m = p3.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['route_prefix'] = str(group["rt_prefix"])
                continue

            m = p4.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['next_hop'] = str(group["nxt_hop"])
                continue

        return parsed_dict

class ShowPlatformSoftwareFedStandbySecurityfedSisredirectFirewallServiceidDetailed():

    ''' Parser for "show platform software fed standby security-fed sis-redirect
        firewall service-id <service-id> detailed " '''

    cli_command = 'show platform software fed standby security-fed sis-redirect firewall service-id {service-id} detailed '

    def test():
        print("this is a test from ShowPlatformSoftwareFedStandbySecurityfedSisredirectFirewallServiceidDetailed")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            security_dict = parsed_dict.setdefault('service_detail', {})

        #9400-vijacob#show platform software fed standby security-fed sis-redirect firewall service-id 1419704521 detailed 
        #Service ID               : 1419704521
        #VRF ID                   : 4
        #IP                       : 192.102.0.2/32
        #Redirect Hdl             : 0x7ff6fa445e18
        #HTM Hdl                  : 0x7ff6fa446028
        #Route Prefix             : 192.102.0.0/30 
        #Next Hop                 : 172.16.5.11 
        #Adj Last Modified        : 2021-07-30,13:32:07

        try:
            p1 = re.compile(r'^Service\s+ID\s+:\s+(?P<svc_id>\d+)')
            p2 = re.compile(r'^IP\s+:\s+(?P<svc_ip>\d+\.\d+\.\d+\.\d+\/\d+)')
            p3 = re.compile(r'^Route\s+Prefix\s+:\s+(?P<rt_prefix>\d+\.\d+\.\d+\.\d+\/\d+)')
            p4 = re.compile(r'^Next\s+Hop\s+:\s+(?P<nxt_hop>\d+\.\d+\.\d+\.\d+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                ste_service = str(group["svc_id"])
                stebind_dict = security_dict.setdefault(ste_service, {})
                stebind_dict['service_id'] = str(group["svc_id"])
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['service_ip'] = str(group["svc_ip"])
                continue

            m = p3.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['route_prefix'] = str(group["rt_prefix"])
                continue

            m = p4.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['next_hop'] = str(group["nxt_hop"])
                continue

        return parsed_dict

class ShowPlatformSoftwareSteeringpolicyForwardingmanagerPermissionsIpv4():

    ''' Parser for "show platform software steering-policy forwarding-manager R0
        permissions IPV4 <sgt> <dgt>  " '''

    cli_command = 'show platform software steering-policy forwarding-manager R0 permissions IPV4 {sgt} {dgt}'

    def test():
        print("this is a test from ShowPlatformSoftwareSteeringpolicyForwardingmanagerPermissionsIpv4")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            sgt_dict = parsed_dict.setdefault('sgt_dgt_policy', {})

        #9400-vijacob# show platform software steering-policy forwarding-manager R0 permissions IPV4 100 36
        #Forwarding Manager steering-policy cell Information
        #
        #  sgt       dgt      Policy ID
        #--------------------------------
        #  100        36      1419703961
        
        try:
            p = re.compile(r'(?P<sgt>\d+)\s+(?P<dgt>\d{1,3})\s+(?P<policy_id>\d+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p.match(line)
            if m:
                group = m.groupdict()
                stebind_dict = sgt_dict.setdefault('per_instance_dict', {})
                stebind_dict['sgt'] = str(group["sgt"])
                stebind_dict['dgt'] = str(group["dgt"])
                stebind_dict['policy_id'] = str(group["policy_id"])
                continue

        return parsed_dict

class ShowPlatformSoftwareSteeringpolicyForwardingmanagerCellinfoIpv4():

    ''' Parser for "show platform software steering-policy forwarding-manager F0 cell-info IPV4" '''

    cli_command = 'show platform software steering-policy forwarding-manager F0 cell-info IPV4'

    def test():
        print("this is a test from ShowPlatformSoftwareSteeringpolicyForwardingmanagerCellinfoIpv4")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            sgt_dict = parsed_dict.setdefault('sgt_dgt_policy', {})
            stebind_dict = sgt_dict.setdefault('per_instance_dict', {})


        #9400-vijacob show platform software steering-policy forwarding-manager F0 cell-info IPV4
        #Forwarding Manager FP steering-policy cell Information
        #
        #SGT: 100, DGT: 36
        #Template name: V4GRPPLC996?, No.of Policies: 1
        #  Policy IDs
        #  -----------
        #  1419703961
        
        try:
            p1 = re.compile(r'^SGT:\s+(?P<sgt>\d+),\s+DGT:\s+(?P<dgt>\d+)')
            p2 = re.compile(r'^(?P<policy_id>\d+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['sgt'] = str(group["sgt"])
                stebind_dict['dgt'] = str(group["dgt"])
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['policy_id'] = str(group["policy_id"])
                continue

        return parsed_dict

class ShowPlatformSoftwareFedActiveSecurityfedSisredirectAclAll():

    ''' Parser for "show platform software fed active security-fed sis-redirect acl all" '''

    cli_command = 'show platform software fed active security-fed sis-redirect acl all'

    def test():
        print("this is a test from ShowPlatformSoftwareFedActiveSecurityfedSisredirectAclAll")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            acl_dict = parsed_dict.setdefault('acl_all', {})

        #9400-vijacob#show platform software fed active security-fed sis-redirect acl all       
        #--------------------------------------------------------------------------
        #| ACL ID    | Seq no  | Firewall ID | Stats Handle |     Frame Count     |
        #--------------------------------------------------------------------------
        # 1419703961   1         1419704521    0x5d0000e8                      0
        # 1419703961   2         1419704521    0x270000e9                      8
        #--------------------------------------------------------------------------
        #--------------------------------------------------------------------------
        #| ACL ID    | Seq no  | Firewall ID | Stats Handle |     Frame Count     |
        #--------------------------------------------------------------------------
        # 1419704481   1         1419704521    0x520000ce                      0
        # 1419704481   2         1419704521    0x750000cf                     41
        #--------------------------------------------------------------------------
        #Number of ACE's: 4
        #Number of ACL's: 2

        try:
            p = re.compile(r'.(?P<acl_id>\d+)\s+(?P<seq_no>\d+)\s+\d+\s+\w+\s+(?P<frame_cnt>\d+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        i = 0
        for line in out.splitlines():
            line = line.strip()

            m = p.match(line)
            if m:
                group = m.groupdict()
                id = f"ACL{i}"
                stebind_dict = acl_dict.setdefault(id, {})
                stebind_dict['acl_id'] = str(group["acl_id"])
                stebind_dict['seq_no'] = str(group["seq_no"])
                stebind_dict['frame_count'] = str(group["frame_cnt"])
                i += 1
                continue

        return parsed_dict

class ShowPlatformSoftwareFedStandbySecurityfedSisredirectAclAll():

    ''' Parser for "show platform software fed standby security-fed sis-redirect acl all" '''

    cli_command = 'show platform software fed standby security-fed sis-redirect acl all'

    def test():
        print("this is a test from ShowPlatformSoftwareFedStandbySecurityfedSisredirectAclAll")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            acl_dict = parsed_dict.setdefault('acl_all', {})

        #9400-vijacob#show platform software fed standby security-fed sis-redirect acl all       
        #--------------------------------------------------------------------------
        #| ACL ID    | Seq no  | Firewall ID | Stats Handle |     Frame Count     |
        #--------------------------------------------------------------------------
        # 1419703961   1         1419704521    0x5d0000e8                      0
        # 1419703961   2         1419704521    0x270000e9                      0
        #--------------------------------------------------------------------------
        #--------------------------------------------------------------------------
        #| ACL ID    | Seq no  | Firewall ID | Stats Handle |     Frame Count     |
        #--------------------------------------------------------------------------
        # 1419704481   1         1419704521    0x520000ce                      0
        # 1419704481   2         1419704521    0x750000cf                      0
        #--------------------------------------------------------------------------
        #Number of ACE's: 4
        #Number of ACL's: 2

        try:
            p = re.compile(r'.(?P<acl_id>\d+)\s+(?P<seq_no>\d+)\s+\d+\s+\w+\s+(?P<frame_cnt>\d+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        i = 0
        for line in out.splitlines():
            line = line.strip()

            m = p.match(line)
            if m:
                group = m.groupdict()
                id = f"ACL{i}"
                stebind_dict = acl_dict.setdefault(id, {})
                stebind_dict['acl_id'] = str(group["acl_id"])
                stebind_dict['seq_no'] = str(group["seq_no"])
                stebind_dict['frame_count'] = str(group["frame_cnt"])
                i += 1
                continue

        return parsed_dict

class ShowRunLispInterface():

    ''' Parser for "show run interface lisp.<no> " '''

    cli_command = 'show run interface lisp {no}'

    def test():
        print("this is a test from ShowRunLispInterface")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            lisp_dict = parsed_dict.setdefault('lisp_interface', {})


        #interface LISP0.4099
        # ip policy route-map ssi_redirect_route_map-ENG1-8fba43e7        
        
        try:
            p = re.compile(r'ip\s+policy\s+route-map\s+(?P<policy_name>.+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p.match(line)
            if m:
                group = m.groupdict()
                stebind_dict = lisp_dict.setdefault('per_int_dict', {})
                stebind_dict['policy_name'] = str(group["policy_name"])
                continue

        return parsed_dict

class ShowLispSiteInstanceid():

    ''' Parser for "show lisp site <ip> instance-id <id> " '''

    cli_command = 'show lisp site {ip} instance-id {id}'

    def test():
        print("this is a test from ShowLispSiteInstanceid")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            lisp_dict = parsed_dict.setdefault('lisp_instance', {})
            stebind_dict = lisp_dict.setdefault('per_instance_dict', {})

        #9500H-FB1#show lisp site 48.1.1.100 instance-id 4099
        #LISP Site Registration Information
        #
        #Site name: site_uci
        #Description: map-server configured from Cisco DNA-Center
        #Allowed configured locators: any
        #Requested EID-prefix:
        #
        #  EID-prefix: 48.1.1.100/32 instance-id 4099 
        #    First registered:     23:51:28
        #    Last registered:      07:18:20
        #    Routing table tag:    0
        #    Origin:               Dynamic, more specific of 48.1.1.0/24
        #    Merge active:         No
        #    Proxy reply:          Yes
        #    Skip Publication:     No
        #    Force Withdraw:       No
        #    TTL:                  1d00h
        #    State:                complete
        #    Extranet IID:         Unspecified
        #    SGT:                  100
        #    Registration errors:  
        #      Authentication failures:   0
        #      Allowed locators mismatch: 0
        #    ETR 172.16.201.30:25784, last registered 07:18:20, proxy-reply, map-notify
        #                             TTL 1d00h, no merge, hash-function sha1, nonce 0x288FE03A-0x65D8E7C2
        #                             state complete, no security-capability
        #                             xTR-ID 0x3CD76593-0x5ADC928C-0xBC60FACE-0x52795862    
        #                             site-ID unspecified
        #                             Domain-ID 1953204162
        #                             Multihoming-ID unspecified
        #                             sourced by reliable transport
        #      Locator        Local  State      Pri/Wgt  Scope
        #      172.16.201.30  yes    up          10/10   IPv4 none
        
        try:
            p1 = re.compile(r'SGT:\s+(?P<sgt>\d+)')
            p2 = re.compile(r'^(?P<ip>\d+\.\d+\.\d+\.\d+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['sgt'] = str(group["sgt"])
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['ip'] = str(group["ip"])
                continue

        return parsed_dict

class ShowIpLispMapserver():

    ''' Parser for "show ip lisp | i Map-Server " '''

    cli_command = 'show ip lisp | i Map-Server'

    def test():
        print("this is a test from ShowIpLispMapserver")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            lisp_dict = parsed_dict.setdefault('lisp_instance', {})
            stebind_dict = lisp_dict.setdefault('per_instance_dict', {})

        #9400-vijacob#sh ip lisp | i Map-Server
        #  ETR Map-Server(s):                        172.16.5.11  

        try:
            p1 = re.compile(r'SGT:\s+(?P<sgt>\d+)')
            p2 = re.compile(r'^(?P<ip>\d+\.\d+\.\d+\.\d+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['sgt'] = str(group["sgt"])
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['ip'] = str(group["ip"])
                continue

        return parsed_dict

class ExecutePing():

    ''' Parser for "ping <ip> source <int> " '''

    cli_command = 'ping {ip} source {int}'

    def test():
        print("this is a test from ExecutePing")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            ping_dict = parsed_dict.setdefault('ping_instance', {})
            stebind_dict = ping_dict.setdefault('per_ping_dict', {})

        #9400-vijacob#ping 172.16.5.11 source loop0
        #Type escape sequence to abort.
        #Sending 5, 100-byte ICMP Echos to 172.16.5.11, timeout is 2 seconds:
        #Packet sent with a source address of 172.16.201.30 
        #!!!!!
        #Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/1 ms    

        try:
            p = re.compile(r'Success\s+rate\s+is\s+(?P<percent>\d+)\s+percent')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['ping_percent'] = str(group["percent"])
                continue

        return parsed_dict

class ShowLispSession():

    ''' Parser for "show lisp session " '''

    cli_command = 'show lisp session'

    def test():
        print("this is a test from ShowLispSession")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            lisp_dict = parsed_dict.setdefault('lisp_instance', {})
            stebind_dict = lisp_dict.setdefault('per_session_dict', {})

        #xtr1#sh lisp session
        #Sessions for VRF default, total: 1, established: 1
        #Peer                           State      Up/Down        In/Out    Users
        #15.15.15.15:4342               Up         21:59:07      117/37     8

        try:
            p = re.compile(r'(?P<peer_ip>\d+\.\d+\.\d+\.\d+):(?P<peer_port>\d+)\s+(?P<state>\w+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))
    
        i = 1
        for line in output.splitlines():
            line = line.strip()

            m = p.match(line)
            if m:
                group = m.groupdict()
                id = f'session_{i}_dict'
                stebind_dict = lisp_dict.setdefault(id, {})
                stebind_dict['peer_ip'] = str(group["peer_ip"])
                stebind_dict['peer_port'] = str(group["peer_port"])
                stebind_dict['lisp_state'] = str(group["state"])
                i += 1
                continue

        return parsed_dict

class ShowIpRouteVrf():

    ''' Parser for "show ip route vrf <vrf> <ip>" '''

    cli_command = 'show ip route vrf {vrf} {ip}'

    def test():
        print("this is a test from ShowIpRouteVrf")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            route_dict = parsed_dict.setdefault('route_instance', {})
            stebind_dict = route_dict.setdefault('per_vrf_dict', {})

        #9500H-FB1#show ip route vrf ENG1 192.102.0.4   >>> subnet of firewall
        #
        #Routing Table: ENG1
        #Routing entry for 192.102.0.4/30
        #  Known via "connected", distance 0, metric 0 (connected, via interface)
        #  Routing Descriptor Blocks:
        #  * directly connected, via Vlan2001
        #      Route metric is 0, traffic share count is 1

        try:
            p = re.compile(r'^Routing\s+entry\s+for\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\/(?P<prefix>\w+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['ip'] = str(group["ip"])
                stebind_dict['prefix'] = str(group["prefix"])
                continue

        return parsed_dict

class ShowIpCefVrf():

    ''' Parser for "show ip cef vrf <vrf> <ip>" '''

    cli_command = 'show ip cef vrf {vrf} {ip}'

    def test():
        print("this is a test from ShowIpCefVrf")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            cef_dict = parsed_dict.setdefault('cef_instance', {})
            stebind_dict = cef_dict.setdefault('per_cef_dict', {})

        #9500H-FB1#show ip cef vrf ENG1 192.102.0.6    >>>> IP address of firewall
        #192.102.0.6/32
        #  attached to Vlan2001

        try:
            p1 = re.compile(r'(?P<ip>\d+\.\d+\.\d+\.\d+)\/(?P<prefix>\w+)')
            p2 = re.compile(r'attached\s+to\s(?P<vlan>\w+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p1.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['ip'] = str(group["ip"])
                stebind_dict['prefix'] = str(group["prefix"])
                continue

            m = p2.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['vlan'] = str(group["vlan"])
                continue

        return parsed_dict

class ShowIpCefVrfInt():

    ''' Parser for "show ip cef vrf <vrf> <ip> int" '''

    cli_command = 'show ip cef vrf {vrf} {ip} int'

    def test():
        print("this is a test from ShowIpCefVrfInt")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            cef_dict = parsed_dict.setdefault('cefint_instance', {})
            stebind_dict = cef_dict.setdefault('per_cef_dict', {})

        #9500H-FB1#show ip cef vrf ENG1 192.102.0.6 int
        #192.102.0.6/32, epoch 0, flags [att, sc], refcnt 6, per-destination sharing
        #  sources: Adj, RR
        #  subblocks:
        #    SC inherited: LISP generalised SMR - [disabled, not inheriting, 0x7F0E7DC0F4E8 locks: 5]
        #    Adj source: IP adj out of Vlan2001, addr 192.102.0.6 7F0E83C9B600
        #      Dependent covered prefix type adjfib, cover 192.102.0.4/30
        #    1 RR source [no flags]
        #  ifnums:
        #    Vlan2001(98): 192.102.0.6
        #  path list 7F0E83ED9630, 2 locks, per-destination, flags 0x49 [shble, rif, hwcn]
        #    path 7F0E83E96870, share 1/1, type adjacency prefix, for IPv4
        #      attached to Vlan2001, IP adj out of Vlan2001, addr 192.102.0.6 7F0E83C9B600
        #  output chain:
        #    IP adj out of Vlan2001, addr 192.102.0.6 7F0E83C9B600 >>>> Will be populated with an outgoing interface if ARP is resolved for next hop ( VLAN interface should be the same number selected during the DNAC Hawkeye workflow i.e 2001 has to be picked from DNAC)

        try:
            p = re.compile(r'IP\s+adj\s+out\s+of\s+(?P<vlan>\w+)')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['vlan'] = str(group["vlan"])
                continue

        return parsed_dict

class ShowLispInstanceidIpv4Server():

    ''' Parser for "show lisp instance-id <id> ipv4 server <ip>" '''

    cli_command = 'show lisp instance-id {id} ipv4 server {ip}'

    def test():
        print("this is a test from ShowLispInstanceidIpv4Server")

    def cli(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            lisp_dict = parsed_dict.setdefault('lisp_instance', {})
            stebind_dict = lisp_dict.setdefault('per_instance_dict', {})

        #9500H-FB1#show lisp instance-id 4099 ipv4 server 192.102.0.4/30 >>> subnet of firewall
        #LISP Site Registration Information
        # 
        #Site name: site_uci
        #Description: map-server configured from Cisco DNA-Center
        #Allowed configured locators: any
        #Requested EID-prefix:
        # 
        #  EID-prefix: 192.102.0.4/30 instance-id 4099
        #    First registered:     1d01h
        #    Last registered:      1d01h
        #    Routing table tag:    0
        #    Origin:               Dynamic, more specific of 0.0.0.0/0
        #    Merge active:         No
        #    Proxy reply:          Yes
        #    Skip Publication:     No
        #    Force Withdraw:       No
        #    TTL:                  1d00h
        #    State:                complete
        #    Extranet IID:         Unspecified
        #    Registration errors: 
        #      Authentication failures:   0
        #      Allowed locators mismatch: 0
        #    ETR 172.16.5.11:21963, last registered 1d01h, proxy-reply, map-notify
        #                           TTL 1d00h, no merge, hash-function sha1, nonce 0xB75416A8-0x095D4D9C
        #                           state complete, no security-capability
        #                           xTR-ID 0x9B8717A7-0x90A6783E-0xA81C6987-0x1C0C3459
        #                           site-ID unspecified
        #                           Domain-ID 3988969097
        #                           Multihoming-ID 54921
        #                           sourced by reliable transport
        #                           ETR Type Service-ETR
        #                           SI Type Service-ETR Firewall Service Insertion
        #                           SI ID 1
        #      Locator      Local  State      Pri/Wgt  Scope
        #      172.16.5.11  yes    up          10/10   IPv4 none  >>>>> Should be Loopback 0 IP address of the SSN node ( that is the node connected to the firewall)
    
        try:
            p = re.compile(r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['ip'] = str(group["ip"])
                continue

        return parsed_dict

class ShowLispRemotelocatorsetServiceetrs():

    ''' Parser for "show lisp remote-locator-set service-etrs" '''

    cli_command = 'show lisp remote-locator-set service-etrs'

    def test():
        print("this is a test from ShowLispRemotelocatorsetServiceetrs")

    def parse(self, output=None):
        if output is None:
            print("Error: Please provide output from the device")
            return None
        else:
            out = output

        # Init vars
        parsed_dict = {}

        if out:
            lisp_dict = parsed_dict.setdefault('lispremote_instance', {})
            stebind_dict = lisp_dict.setdefault('per_instance_dict', {})

        #pxtr#sh lisp remote-locator-set service-etrs 
        #LISP remote-locator-set default-etr-locator-set-ipv4 Information
        #
        #Codes:
        #ETR = ETR Type (Default = Default-ETR, Service = Service-ETR)
        #SI  = Service Insertion Type
        #ID  = Service Insertion ID
        #-   = No service insertion config type defined
        #DS  = Default-ETR Firewall Service Insertion
        #SS  = Service-ETR Firewall Service Insertion
        #P   = Primary/Direct in use, Backup not available
        #PB  = Primary/Direct in use, Backup available
        #B   = Backup in use, Primary/Direct not available
        #BP  = Backup in use, Primary/Direct available
        # * = This locator has multiple service EID configured.
        #
        # RLOC         Pri/Wgt/Metric     Inst       Domain-ID/MH-ID  ETR       SI/ID          
        # 15.15.15.15   10/10 /-          4099               0/0      Service   SS/1

        try:
            p = re.compile(r'(?P<rloc_ip>\d+\.\d+\.\d+\.\d+)\s+(?P<priority>\w+)\/')

        except Exception as e:
            print(">>>> re exception: " + str(e))

        for line in out.splitlines():
            line = line.strip()

            m = p.match(line)
            if m:
                group = m.groupdict()
                stebind_dict['rloc_ip'] = str(group["rloc_ip"])
                stebind_dict['priority'] = str(group["priority"])
                continue

        return parsed_dict
