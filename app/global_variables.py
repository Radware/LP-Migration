from datetime import datetime

############################################
#### Static Variables Definitions Start ####
############################################

counter = 0
#bck_status = 0
#last_policy_id = 0
multi_pol_id = 0
static_pol_id = 0
new_filt_id_diff = 100
gslb_net_id = 0
gslb_rule_id = 1
smartnat_id = 0
locl_snd_nwclss_id = 0
locl_sns_nwclss_id = 0
locl_snn_nwclss_id = 0
nat_sns_nwclss_id = 0
dns_vip_id1 = 1
dns_vip_id2 = 2
isp_id = 0
if_number = 0
#gw_id = 0
float_id = 0
#gbck_id = 0
last_orig_pol_id = 0
last_new_pol_id = 100
#snn_local_nwclss_net_id = 0
local_nets_nwclss_net_id = 0
dummy_vip_id = 0
dummy_status = 0
smartnat_local_nwclss_id = 0

##########################################
#### Static Variables Definitions End ####
##########################################

###############################################
#### Static Dictionaries Definitions Start ####
###############################################

special_characters_dcn = {
    '`': '_',
    '~': '_',
    '!': '_',
    '@': '_',
    '#': '_',
    '$': '_',
    '%': '_',
    '^': '_',
    '&': '_and_',
    '*': '_',
    '(': '_',
    ')': '_',
    '[': '_',
    ']': '_',
    '{': '_',
    '}': '_',
    '+': '_and_',
    '=': '_',
    '<': '_',
    '>': '_',
    ',': '_',
    '/': '_',
    '\\': '_',
    ';': '_',
    '?': '_',
    '|': '_',
    ':': '_',
    ' ': '_'
}

port_to_service_dcn = {
    '20': 'ftp-data',
    '21': 'ftp',
    '22': 'ssh',
    '23': 'telnet',
    '25': 'smtp',
    '37': 'time',
    '42': 'name',
    '43': 'whois',
    '53': 'dns',
    '69': 'tftp',
    '70': 'gopher',
    '79': 'finger',
    '80': 'http',
    '109': 'pop2',
    '110': 'pop3',
    '111': 'sunrpc',
    '119': 'nntp',
    '123': 'ntp',
    '143': 'imap',
    '144': 'news',
    '161': 'snmp',
    '162': 'snmptrap',
    '179': 'bgp',
    '194': 'irc',
    '220': 'imap3',
    '389': 'ldap',
    '443': 'https',
    '520': 'rip',
    '554': 'rtsp',
    '1812': 'radius-auth',
    '1813': 'radius-acc',
    '1985': 'hsrp',
    '5060': 'sip'
}

mask_to_prefix_dcn = {
    '255.0.0.0': '8',
    '255.128.0.0': '9',
    '255.192.0.0': '10',
    '255.224.0.0': '11',
    '255.240.0.0': '12',
    '255.248.0.0': '13',
    '255.252.0.0': '14',
    '255.254.0.0': '15',
    '255.255.0.0': '16',
    '255.255.128.0': '17',
    '255.255.192.0': '18',
    '255.255.224.0': '19',
    '255.255.240.0': '20',
    '255.255.248.0': '21',
    '255.255.252.0': '22',
    '255.255.254.0': '23',
    '255.255.255.0': '24',
    '255.255.255.128': '25',
    '255.255.255.192': '26',
    '255.255.255.224': '27',
    '255.255.255.240': '28',
    '255.255.255.248': '29',
    '255.255.255.252': '30',
    '255.255.255.254': '31',
    '255.255.255.255': '32'
}

prefix_to_mask_dcn = {
    '8': '255.0.0.0',
    '9': '255.128.0.0',
    '10': '255.192.0.0',
    '11': '255.224.0.0',
    '12': '255.240.0.0',
    '13': '255.248.0.0',
    '14': '255.252.0.0',
    '15': '255.254.0.0',
    '16': '255.255.0.0',
    '17': '255.255.128.0',
    '18': '255.255.192.0',
    '19': '255.255.224.0',
    '20': '255.255.240.0',
    '21': '255.255.248.0',
    '22': '255.255.252.0',
    '23': '255.255.254.0',
    '24': '255.255.255.0',
    '25': '255.255.255.128',
    '26': '255.255.255.192',
    '27': '255.255.255.224',
    '28': '255.255.255.240',
    '29': '255.255.255.248',
    '30': '255.255.255.252',
    '31': '255.255.255.254',
    '32': '255.255.255.255'
}

basic_services_dcn = {
    'aol-msg': ['tcp', '5190-5193'],
    'citrix-admin': ['tcp', '2513'],
    'citrix-ica': ['tcp', '1494'],
    'citrix-ima': ['tcp', '2512'],
    'citrix-ma-client': ['tcp', '2598'],
    'citrix-rtmp': ['tcp', '2897'],
    'diameter': ['tcp', '3868'],
    'dns': ['udp', '53'],
    'ftp-session': ['tcp', '21'],
    'h.225-session': ['tcp', '1720'],
    'http': ['tcp', '80'],
    'http-alt': ['tcp', '8080'],
    'https': ['tcp', '443'],
    'icq': ['tcp', '5190'],
    'imap': ['tcp', '143'],
    'ldap': ['tcp', '389'],
    'ldaps': ['tcp', '636'],
    'lrp': ['udp', '2090'],
    'msn-msg': ['tcp', '1863'],
    'mssql-server': ['tcp', '1433'],
    'mssql-monitor': ['tcp', '1434'],
    'nntp': ['tcp', '119'],
    'oracle-server1': ['tcp', '1525'],
    'oracle-server2': ['tcp', '1527'],
    'oracle-server3': ['tcp', '1529'],
    'oracle-v1': ['tcp', '66'],
    'oracle-v2': ['tcp', '1521'],
    'pop3': ['tcp', '110'],
    'prp': ['udp', '2091'],
    'rexec': ['tcp', '512'],
    'rshell': ['tcp', '514'],
    'rtsp': ['tcp', '554'],
    'sap': ['tcp', '3300-3301'],
    'smtp': ['tcp', '25'],
    'snmp': ['udp', '161'],
    'snmp-trap': ['udp', '162'],
    'ssh': ['tcp', '22'],
    'telnet': ['tcp', '23'],
    'tftp': ['udp', '69']
}

basic_multi_services_protocols_dcn = {
    'radius': 'udp'
}

basic_multi_services_ports_dcn = {
    'radius': ['1645-1646', '1812-1813']
}

or_groups_multi_services_protocols_dcn = {
    'citrix': 'tcp',
    'mail': 'tcp',
    'mssql': 'tcp',
    'oracle': 'tcp'
}

or_groups_multi_services_ports_dcn = {
    'citrix': ['2513', '1494', '2512', '2598', '2897'],
    'mail': ['143', '110'],
    'mssql': ['1433', '1434'],
    'oracle': ['1525', '1527', '1529', '66', '1521']
}

#############################################
#### Static Dictionaries Definitions End ####
#############################################

################################################
#### Dynamic Dictionaries Definitions Start ####
################################################

dcn = {}
lia_to_gslb_nets_dcn = {}
virts_to_gslb_nets_dcn = {}
farm_flow_to_farm_dcn = {}
group_to_routers_dcn = {}
group_to_routers_nonat_dcn = {}
duplicate_wls_dcn = {}
user_new_wl_names_dcn = {}
user_equal_wl_names_dcn = {}
farm_parameters_dcn = {}
user_defined_basic_services_dcn = {}
operation_mode_dcn = {}
#wl_to_at_dcn = {}
outbound_pols_dcn = {}
admin_status_dcn = {}
subnet_to_new_ifs_dcn = {}
if_ip_to_peer_dcn = {}
if_ip_to_peer_no_error_dcn = {}
snp_real_to_virt_dcn = {}
snp_virt_to_service_dcn = {}
bck_dcn = {}
gbck_dcn = {}
orig_dm_dcn = {}
l2_if_admin_status_dcn = {}
l3_if_admin_status_dcn = {}
subnet_to_mask_dcn = {}
group_to_routers_all_dcn = {}
orig_farm_parameters_dcn = {}
sns_local_range_to_nwclss_dcn = {}

##############################################
#### Dynamic Dictionaries Definitions End ####
##############################################

#########################################
#### Static Lists Definitions Start #####
#########################################

lp_servers_unsupported_flags = ['-w', '-cl', '-b', '-i', '-o']
lp_traffic_pols_unsupported_flags = ['-mrk']
lp_netip_unsupported_flags = ['-oi']

######################################
#### Static Lists Definitions End ####
######################################

#########################################
#### Dynamic Lists Definitions Start ####
#########################################

lp_shared_ips_lst = []
if_numbers_lst = []
farms_aging_times_lst = []
app_aging_times_lst = []
type_group_local_lst = []
farms_nonat_lst = []
dns_farms_nonat_lst = []
smart_nat_local_ips_lst = []
#snn_local_range_orig_lst = []
own_addresses_lst = []
#all_routers_lst = []
back_added_lst = []
nonat_gslb_nets_lst = []
default_farm_lst = []
default_group_lst = []
all_farms_lst = []
unequal_wls_lst = []

#######################################
#### Dynamic Lists Definitions End ####
#######################################

#####################################
#### Functions Definitions Start ####
#####################################


def find_fnc(line, first, last):
    '''Find a string between two strings.
    Takes a string as the 1st parameter.
    The 2nd and 3rd parameters are the strings between which the search will be performed.
    '''
    try:
        start = line.index(first) + len(first)
        end = line.index(last, start)
        return line[start:end]
    except ValueError:
        return "error"


def ipRange_fnc(start_ip, end_ip):
    '''Find all IP addresses in a range.
    Parameters given are the start IP and end IP.
    All IP addresses in the range (including start and end) are appended to a list.
    '''
    start = list(map(int, start_ip.split(".")))
    end = list(map(int, end_ip.split(".")))
    temp = start
    ip_range = []
    ip_range.append(start_ip)
    while temp != end:
        start[3] += 1
        for i in (3, 2, 1):
            if temp[i] == 256:
                temp[i] = 0
                temp[i - 1] += 1
        ip_range.append(".".join(map(str, temp)))

    return ip_range


def all_same(v):
    '''Checks if all values in a list are the same.
    Takes list as a parameter.
    '''
    return all(x == v[0] for x in v)

###################################
#### Functions Definitions End ####
###################################

###################################
#### Classes Definitions Start ####
###################################


class color:  # Colours Definition
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

#################################
#### Classes Definitions End ####
#################################
