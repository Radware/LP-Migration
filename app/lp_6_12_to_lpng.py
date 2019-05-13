#!/usr/bin/python

##############################
#### Modules Import Start ####
##############################

from flask import Flask, render_template, request, redirect, send_file
from werkzeug import secure_filename
from app import app
import global_variables

from sys import argv
#script, filename = argv
import os.path
#if os.path.isfile("%s" % (filename)) == False: # If file doesn't exist, exit the script
#    print 'File "%s" doesn\'t exist.' % (filename)
#    file_note = raw_input('Press <Enter> to exit the script.\n')
#    quit()
import time
import zipfile
import tarfile
import re
import operator
import ipaddress
from datetime import datetime
import math
import readline
readline.set_completer_delims("$")

############################
#### Modules Import End ####
############################

######################################
#### Script Beginning Notes Start ####
######################################

#@app.route('/')
#@app.route('/index')
@app.route('/lp_6_12_index', methods=['GET', 'POST'])
def index():
    reload(global_variables)
    global_variables.counter += 1
    user_ip = request.remote_addr
    users_ips_log = open("app/users_ips_logs", "a") # This is the access logs file
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    print >>users_ips_log, '\033[1m%s\033[0m #User_Logged_In: User with IP %s logged in.' % (current_time, user_ip)
    users_ips_log.close()
    #if global_variables.counter > 1:
        #return "Too many users connected, try again later."
    #else:
    return render_template('index.html')

@app.route('/validate_file', methods=['POST'])
@app.route('/validate_file.js')
def validate_js():
    if request.method == 'GET':
        return send_file('validate_file.js')
    elif request.method == 'POST':
       check_user_file = str(request.form['user_output_file'])
       if not check_user_file:
           return render_template('file_status.html', file_status="empty")
       elif os.path.isfile("app/%s_config" % (check_user_file)) == True:
           return render_template('file_status.html', file_status="error")
       else:
           return render_template('file_status.html', file_status="ok")

@app.route('/jquery-1.11.2.min.js')
def jquery():
    return send_file('jquery-1.11.2.min.js')

@app.route('/getfile', methods=['GET','POST'])
def getfile():
    if request.method == 'POST':

        # for secure filenames. Read the documentation.
        lp_config_file = request.files['myfile']
        lp_config_filename = secure_filename(lp_config_file.filename)

        # os.path.join is used so that paths work in every operating system
        lp_config_file.save(os.path.join(lp_config_filename))

        # You should use os.path.join here too.
        with open(lp_config_filename) as lp_to_lpng:
            lp_to_lpng = lp_to_lpng.read()
            lp_to_lpng = lp_to_lpng.replace(' \\\r\n', " ") # In case there's a white space before the "\"
            lp_to_lpng = lp_to_lpng.replace('\\\r\n ', " ") # In case there's a white space after the "\"
            lp_to_lpng = lp_to_lpng.replace('\\\r\n', " ") # In case there's no white space between the "\" and the next line
            lp_to_lpng = lp_to_lpng.split('\r\n')
        lp_to_lpng = [var + " " for var in lp_to_lpng] # Adds a white space in the end of each list object
        global lp_to_lpng
        ######################################
        #### Script Beginning Notes Start ####
        ######################################

        for line in lp_to_lpng: # Loops over the LP configuration
            if "Software Version" in line: # LP software version check
                def find_sw_version( line, first, last):
                    try:
                        start = line.index( first ) + len( first )
                        end = line.index( last, start )
                        return line[start:end]
                    except ValueError:
                        return "error"
                sw_version = find_sw_version( line, "!Software Version: ", ")" )
                #if "6.12" not in sw_version or "6.13" not in sw_version: # If the LP software version is 6.20 or 6.21, the script exists
                if not sw_version.startswith("6.12") and not sw_version.startswith("6.13"):
                    return render_template('sw_version_error.html', sw_version=sw_version)
        return render_template('startnotes.html')
        #return redirect('/startnotes')

#@app.route('/startnotes')
#def startnotes():
    #return render_template('startnotes.html')

@app.route('/page1', methods=['GET','POST'])
def page1():

    global user_output_file
    global output_file
    global migration_errors
    global ingress_vlan
    global ingress_ports
    global hc_note
    global hc_fqdn1
    global hc_fqdn2
    global hc_dns1
    global hc_dns2
    user_output_file = str(request.form['user_output_file'])
    #if os.path.isfile("app/%s_config" % (user_output_file)) == True:
    #    error = 'File %s already exists.' % (user_output_file)
    #    return render_template('startnotes.html', error=error)
    #else:
    output_file = open("app/%s_config" % (user_output_file), "abc") # This is the target Alteon configuration file
    migration_errors = open("app/%s_logs" % (user_output_file), "w") # This is the logs file
    ingress_vlan = str(request.form['vlan_id'])
    if ingress_vlan == "0":
        ingress_vlan = "any"
    ingress_ports = request.form['ingress_ports']
    ingress_ports = str(ingress_ports).split(',') # Creates list of ingress ports
    ingress_ports = [p.replace(' ', '') for p in ingress_ports] # Removes white spaces
    egress_ports = request.form['egress_ports']
    egress_ports = str(egress_ports).split(',') # Creates list of egress ports
    egress_ports = [p.replace(' ', '') for p in egress_ports] # Removes white spaces
    hc_note = str(request.form['hc_types'])
    hc_fqdn1 = str(request.form['fqdn1'])
    hc_fqdn2 = str(request.form['fqdn2'])
    hc_dns1 = str(request.form['dns1'])
    hc_dns2 = str(request.form['dns2'])

    global allports
    allports = ingress_ports + egress_ports # Creates a list of all ports, ingress and egress
    allports = list(set(allports)) # This list will be used later on when configuring filters
    allports = sorted(allports)

    ####################################
    #### Script Beginning Notes End ####
    ####################################

    #########################
    #### Main Code Start ####
    #########################

    ##################################
    #### Interfaces Section Start ####
    ##################################

    ###                        ###
    #    L2 Interface Section    #
    ###                        ###

    for line in lp_to_lpng:
        if "net l2-interface" in line:
            l2_if_id = global_variables.find_fnc( line, "set ", " " ) # Find interface ID
            l2_if_admin_status = global_variables.find_fnc( line, "-ad ", " " ) # Find interface admin status
            if l2_if_admin_status == "down": # If admin status is down, populates a dictionary with the following values: # ---->
                                             # L2 interface ID as a key # ---->
                                             # The admin status (always "down") as a value # ---->
                                             # This is used later on to create another dictionary that maps the L3 interface ID and the admin status
                l2_if_admin_status_dcn_key = "%s" % (l2_if_id)
                global_variables.l2_if_admin_status_dcn.setdefault(l2_if_admin_status_dcn_key, [])
                global_variables.l2_if_admin_status_dcn[l2_if_admin_status_dcn_key].append('%s' % (l2_if_admin_status))

    ###                        ###
    #    L3 Interface Section    #
    ###                        ###

        if "ip-interface" in line and "MNG" not in line:
            if_ip = global_variables.find_fnc( line, "create ", " " ) # Finds L3 interface IP
            global_variables.own_addresses_lst.append(if_ip) # Populates a list with the interface IPs as objects # ---->
                                            # This is used later on when creating Smart NAT objects, to check for unsupported addresses
            if_mask = global_variables.find_fnc( line, "%s " % (if_ip), " " ) # Finds L3 interface mask
            l3_if_id = global_variables.find_fnc( line, "%s " % (if_mask), " " ) # Finds L3 interface ID
            if_vlan = global_variables.find_fnc( line, "-v ", " " ) # Finds L3 interface VLAN
            if_pa = global_variables.find_fnc( line, "-pac ", " " ) # Finds L3 interface peer IP
            if_ip_to_peer_key = "%s" % (if_ip) # This dictionary is not in use
            global_variables.if_ip_to_peer_dcn.setdefault(if_ip_to_peer_key, [])
            global_variables.if_ip_to_peer_dcn[if_ip_to_peer_key].append('%s' % (if_pa))
            if if_pa != 'error': # If interface peer IP exists, populates a dictionary with the following values: # ---->
                                 # Interface IP as a key # ---->
                                 # Interface peer IP as a value # ---->
                                 # This is used later on to create SLB sync and HA configuration
                if_ip_to_peer_no_error_key = "%s" % (if_ip)
                global_variables.if_ip_to_peer_no_error_dcn.setdefault(if_ip_to_peer_no_error_key, [])
                global_variables.if_ip_to_peer_no_error_dcn[if_ip_to_peer_no_error_key].append('%s' % (if_pa))
                global_variables.own_addresses_lst.append(if_pa) # Populates a list with the interface peer IPs as objects # ---->
                                                # This is used later on when creating Smart NAT objects, to check for unsupported addresses
            global_variables.if_number += 1 # Used for Alteon L3 interface ID
            global_variables.if_numbers_lst.append("%s" % (global_variables.if_number))
            if l3_if_id in global_variables.l2_if_admin_status_dcn.keys(): # If admin status is down, populates a dictionary with the following values: # ---->
                                                          # L3 interface ID as a key # ---->
                                                          # The admin status (always "down") as a value # ---->
                                                          # This is used later on to configure the admin status of the L3 interface
                l3_if_admin_status_dcn_key = "%s" % (global_variables.if_number)
                global_variables.l3_if_admin_status_dcn.setdefault(l3_if_admin_status_dcn_key, [])
                global_variables.l3_if_admin_status_dcn[l3_if_admin_status_dcn_key].append('%s' % (global_variables.l2_if_admin_status_dcn[l3_if_id][0]))

            print >>output_file, "/c/l3/if %s" % (global_variables.if_number) # Starts printing the L3 interface commands
            if str(global_variables.if_number) in global_variables.l3_if_admin_status_dcn.keys():
                print >>output_file, "        dis"
            else:
                print >>output_file, "        ena"
            print >>output_file, "        addr %s" % (if_ip)
            print >>output_file, "        mask %s" % (if_mask)
            if if_vlan != "error":
                print >>output_file, "        vlan %s" % (if_vlan)
            if if_pa != "error":
                print >>output_file, "        peer %s" % (if_pa)

            ipnet = ipaddress.ip_network('%s/%s' % (if_ip, if_mask), strict=False)
            only_ipnet = str(ipnet).split('/')[0] # Finds the network address
            last_host = [int(s) for s in str(list(ipaddress.ip_network('%s' % (ipnet)).hosts())[-1]).split('.')] # Finds the last host
            ipbroad = '.'.join([str(s) for s in last_host[:-1] + [last_host[-1] + 1]]) # Finds the broadcast address
            global_variables.own_addresses_lst.append(only_ipnet) # Populates a list with the network addresses as objects # ---->
                                                 # This is used later on when creating Smart NAT objects, to check for unsupported addresses
            global_variables.own_addresses_lst.append(ipbroad) # Same as above, with broadcast addresses
            subnet_to_new_ifs_key = "%s" % (ipnet) # Populates a dictionary with the following values: # ---->
                                                   # The network address as a key # ---->
                                                   # The L3 interface ID as a value # ---->
                                                   # This is used later on to map the static routes to the correct L3 interface IDs
            global_variables.subnet_to_new_ifs_dcn.setdefault(subnet_to_new_ifs_key, [])
            global_variables.subnet_to_new_ifs_dcn[subnet_to_new_ifs_key].append('%s' % (global_variables.if_number))
            int_subnet_to_new_ifs_dcn = {k:int(v[0]) for k, v in global_variables.subnet_to_new_ifs_dcn.iteritems()} # Maps the dictionary values to integers
            sorted_int_subnet_to_new_ifs_dcn = sorted(int_subnet_to_new_ifs_dcn.items(), key=operator.itemgetter(1)) # Converts the dictionary to a list of tuples and sorts it
            subnet_to_mask_dcn_key = "%s" % (only_ipnet) # Populates a dictionary with the following values: # ---->
                                                         # The network address as a key # ---->
                                                         # The network mask as a value # ---->
                                                         # This is used later on to create a network class to allow traffic to local networks
            global_variables.subnet_to_mask_dcn.setdefault(subnet_to_mask_dcn_key, [])
            global_variables.subnet_to_mask_dcn[subnet_to_mask_dcn_key].append('%s' % (if_mask))

    ################################
    #### Interfaces Section End ####
    ################################

    ###############################
    #### Routing Section Start ####
    ###############################

    for line in lp_to_lpng: # Loops over the LP configuration again for the routing table command
        if "net route table create" in line and "0.0.0.0" not in line and "MNG" not in line:
            print >>output_file, "/c/l3/route/ip4/"
            break # Breaks the loop in order to print the routing table commmand only once

    for line in lp_to_lpng: # Loops over the LP configuration again to continue with the code
        if "net route table create" in line and "0.0.0.0" not in line and "MNG" not in line:
            find_route_ips = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the route destination network, mask and next hop
            for subnet, if_var in sorted_int_subnet_to_new_ifs_dcn:
                if ipaddress.ip_address('%s' % (find_route_ips[2])) in ipaddress.ip_network('%s' % (subnet)): # Checks if the next hop belongs to one of the subnets in the dictionary
                    print >>output_file, "        add %s %s %s %s" % (find_route_ips[0], find_route_ips[1], find_route_ips[2], if_var) # If it belongs, prints the static route with the correct L3 interface ID

    for line in lp_to_lpng:
        if "net route table create" in line and "0.0.0.0" in line and "MNG" not in line:
            find_route_ips2 = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the default route next hop
            print >>output_file, "/c/l3/gw 1" # Starts printing the GW
            print >>output_file, "        ena"
            print >>output_file, "        ipver v4"
            print >>output_file, "        addr %s" % (find_route_ips2[2])
            break # Breaks the loop in order to print the gateway only once

    #############################
    #### Routing Section End ####
    #############################

    ##########################
    #### HA Section Start ####
    ##########################

    global alt_ha_mode
    for line in lp_to_lpng:
        if "redundancy mode set" in line:
            ha_mode = global_variables.find_fnc( line, "set ", " " )
            if ha_mode == "VRRP": # If LP redundancy mode is "VRRP", Alteon HA flag is on with 1
                alt_ha_mode = 1
                break
            elif ha_mode == "Proprietary": # If LP redundancy mode is "Proprietary", Alteon HA flag is on with 2
                alt_ha_mode = 2
                break
            else: # If HA mode is set to disable, Alteon HA flag is off
                alt_ha_mode = 0
        else: # If the redundancy mode command is not in the configuration, Alteon HA flag is off
            alt_ha_mode = 0

    for line in lp_to_lpng:

    ###                          ###
    #    Create Shared IPs List    #
    ###                          ###

        ##                                                                                                                    ##
        #    This is used to check if there are VRRP associated IP addresses that are not present in NAT/DNS VIP/Remote VIP    #
        #    Addresses that are not present will be used as HA floating IP if HA is used                                       #
        ##                                                                                                                    ##

        if alt_ha_mode == 1:
            if "smartnat dynamic-nat" in line:
                find_snd_ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the SND addresses
                if find_snd_ip[3] not in global_variables.lp_shared_ips_lst: # Populates a list with the SND addresses as objects
                    global_variables.lp_shared_ips_lst.append("%s" % (find_snd_ip[3]))
            if "smartnat static-nat" in line:
                find_sns_ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the SNS addresses
                if find_sns_ip[3] == find_sns_ip[4]: # If both from and to SNS addresses are the same
                    if find_sns_ip[3] not in global_variables.lp_shared_ips_lst: # Populates a list with the SNS addresses as objects
                        global_variables.lp_shared_ips_lst.append("%s" % (find_sns_ip[3]))
                else: # If from and to SNS addresses are different
                    sns_natip_range = global_variables.ipRange_fnc(find_sns_ip[3], find_sns_ip[4]) # Executes the "ipRange" function to find all IPs
                    for sns in sns_natip_range: # Populates a list with the SNS addresses as objects
                        if sns not in global_variables.lp_shared_ips_lst:
                            global_variables.lp_shared_ips_lst.append("%s" % (sns))
            if "smartnat static-pat" in line:
                find_snp_ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the SNP addresses
                if find_snp_ip[0] not in global_variables.lp_shared_ips_lst: # Populates a list with the SNP addresses as objects
                    global_variables.lp_shared_ips_lst.append("%s" % (find_snp_ip[0]))
            if "lp dns virtual-ip create" in line:
                dns_vip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the DNS VIPs
                if dns_vip[0] not in global_variables.lp_shared_ips_lst: # Populates a list with the DNS VIPs as objects
                    global_variables.lp_shared_ips_lst.append("%s" % (dns_vip[0]))
            if "lp remote-vip create" in line:
                find_float_ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the remote VIPs
                if find_float_ip[0] not in global_variables.lp_shared_ips_lst: # Populates a list with the remove VIPs as objects
                    global_variables.lp_shared_ips_lst.append("%s" % (find_float_ip[0]))

    ###                     ###
    #    Global HA Section    #
    ###                     ###

    for line in lp_to_lpng:
        if "redundancy mode set" in line:
            ha_mode = global_variables.find_fnc( line, "set ", " " )
            if ha_mode == "VRRP" or ha_mode == "Proprietary": # If LP redundancy mode is VRRP or Proprietary
                print >>output_file, "/c/l3/hamode switch" # Starts printing the global HA configuration
                print >>output_file, "/c/l3/ha/switch"
                print >>output_file, "        srvpbkp dis"
                print >>output_file, "        filtpbkp dis"
                print >>output_file, "        def 1"
                print >>output_file, "/c/l3/ha/switch/trigger/ifs"
                for subnet, if_var in sorted_int_subnet_to_new_ifs_dcn: # Prints all L3 interfaces as HA triggers
                    print >>output_file, "        add %s" % (if_var)

    ###                           ###
    #    HA Floating IPs Section    #
    ###                           ###

        if alt_ha_mode == 1 or alt_ha_mode == 2:
            if "lp remote-vip create" in line: # Configures LP remote-vips as Alteon HA floating IPs
                find_float_ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the remove VIP
                global_variables.float_id += 1
                print >>output_file, "/c/l3/ha/floatip %s" % (global_variables.float_id) # Starts printing the HA floating IP
                print >>output_file, "        ena"
                print >>output_file, "        ipver v4"
                print >>output_file, "        addr %s" % (find_float_ip[0])
                for subnet, if_var in sorted_int_subnet_to_new_ifs_dcn:
                    if ipaddress.ip_address('%s' % (find_float_ip[0])) in ipaddress.ip_network('%s' % (subnet)): # Checks if the floating IP belongs to one of the subnets in the dictionary
                        print >>output_file, "        if %s" % (if_var) # If it belongs, prints the correct L3 interface ID
        if "redundancy vrrp associated-ip" in line and alt_ha_mode == 1: # Configures standalone LP assoicated IPs as floating IPs
            find_associated_ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the associated IP
            if find_associated_ip[0] not in global_variables.lp_shared_ips_lst: # If the associated IP is not in the shared IPs list
                for subnet, if_var in sorted_int_subnet_to_new_ifs_dcn:
                    if ipaddress.ip_address('%s' % (find_associated_ip[0])) in ipaddress.ip_network('%s' % (subnet)): # Checks if the associated IP belongs to one of the subnets in the dictionary and if it is, prints the correct L3 interface ID
                        global_variables.float_id += 1
                        print >>output_file, "/c/l3/ha/floatip %s" % (global_variables.float_id) # Starts printing the floating IP
                        print >>output_file, "        ena"
                        print >>output_file, "        ipver v4"
                        print >>output_file, "        addr %s" % (find_associated_ip[0])
                        print >>output_file, "        if %s" % (if_var)

    ###                    ###
    #    SLB Sync Section    #
    ###                    ###

    for line in lp_to_lpng:
        if (alt_ha_mode == 1 or alt_ha_mode == 2) and len(global_variables.if_ip_to_peer_no_error_dcn) > 0: # If peer IP addresses are present in the LP configuration
            print >>output_file, "/c/slb/sync" # Starts printing the SLB sync configuration
            print >>output_file, "        prios d"
            print >>output_file, "        pips e"
            print >>output_file, "        certs e"
            print >>output_file, "        state e"
            print >>output_file, "        if e"
            print >>output_file, "        gw e"
            print >>output_file, "        ddstore ena"
            print >>output_file, "/c/slb/sync/peer 1"
            print >>output_file, "        ena"
            for pac in global_variables.if_ip_to_peer_no_error_dcn.values():
                print >>output_file, "        addr %s" % (pac[0])
                break
            print >>output_file, "/c/slb/sync/ucast"
            print >>output_file, "        ena"
            print >>output_file, "        primif %s" % (global_variables.if_numbers_lst[0])
            if len(global_variables.if_numbers_lst) > 1:
                print >>output_file, "        secif %s" % (global_variables.if_numbers_lst[1])
            break

    ########################
    #### HA Section End ####
    ########################

    #########################################
    #### Preliminary Farms Section Start ####
    #########################################

    ###                                   ###
    #    Finds "NAT Mode Disabled" Farms    #
    ###                                   ###
     
        ##                                                                                                         ##
        #    This is used to find the farms that are "NAT Mode Disabled"                                            #
        #    Later on, the objects created here will be used to configure the real servers with "PIP Mode NoNAT"    #
        ##                                                                                                         ##

    for line in lp_to_lpng:
        if "farms table setCreate" in line:
            farm_name_nonat = global_variables.find_fnc( line, ' setCreate "', '"' ) # Finds the farm name
            if farm_name_nonat == 'error': # If there are no double quotes in the farm name
                farm_name_nonat = global_variables.find_fnc( line, ' setCreate ', ' ' ) # Finds the farm name again
            nat_mode = global_variables.find_fnc( line, " -nm ", " " ) # Finds the NAT mode
            if nat_mode == 'error': # If NAT mode is set to "Disable", adds the farm name to a list
                global_variables.farms_nonat_lst.append("%s" % (farm_name_nonat))

    ###                                                  ###
    #    Finds DNS Rules with "NAT Mode Disabled" Farms    #
    ###                                                  ###

        ##                                                                            ##
        #    This is used to create specific regular groups for DNS resolution         #
        #    This is in case that the real servers are part of NAT and NoNAT groups    #
        ##                                                                            ##

    global dns_ttl
    for line in lp_to_lpng:
        if "name-to-ip" in line:
            dns_farm_name_nonat = global_variables.find_fnc( line, ' -fn "', '"' ) # Finds the farm name associated with the DNS rule
            if dns_farm_name_nonat == 'error': # If there are no double quotes in the farm name
                dns_farm_name_nonat = global_variables.find_fnc( line, ' -fn ', ' ' ) # Finds the farm name associated with the DNS rule again
            if dns_farm_name_nonat != 'error' and dns_farm_name_nonat in global_variables.farms_nonat_lst and dns_farm_name_nonat not in global_variables.dns_farms_nonat_lst: # If the farm is a No NAT farm and it's not already in the DNS No NAT list, adds it to the list
                global_variables.dns_farms_nonat_lst.append("%s" % (dns_farm_name_nonat))

    ###                                   ###
    #    Finds Farms - Farm Flow Section    #
    ###                                   ###

        ##                                                                            ##
        #    This is the section used to find the farm flows and farms associations    #
        ##                                                                            ##

        if "farms-flow-table" in line:
            farm_flow = global_variables.find_fnc( line, 'setCreate "', '"' ) # Finds the farm flow
            if farm_flow == 'error': # If there are no double quotes in the farm flow name
                farm_flow = global_variables.find_fnc( line, "setCreate ", " " ) # Finds the farm flow again
            farm_in_fc = global_variables.find_fnc( line, '%s" "' % (farm_flow), '" -id' ) # Finds the farm associated with the farm flow
            if farm_in_fc == 'error': # if there are no double quotes in the farm flow name and in the farm name
                farm_in_fc = global_variables.find_fnc( line, '%s "' % (farm_flow), '" -id' ) # Finds the farm associated with the farm flow again
                if farm_in_fc == 'error': # If there are no double quotes in the farm name
                    farm_in_fc = global_variables.find_fnc( line, '%s" ' % (farm_flow), " -id" ) # Finds the farm associated with the farm flow again
                    if farm_in_fc == 'error': # If there are no double quotes in the farm flow name
                        farm_in_fc = global_variables.find_fnc( line, ' %s ' % (farm_flow), " -id" ) # Finds the farm associated with the farm flow again
            for unsupported_char, supported_char in global_variables.special_characters_dcn.iteritems():
                farm_in_fc = farm_in_fc.replace ('%s' % (unsupported_char), "%s" % (supported_char))
            if farm_in_fc != 'error':
                farm_flow_to_farm_dcn_key = "%s" % (farm_flow)
                global_variables.farm_flow_to_farm_dcn.setdefault(farm_flow_to_farm_dcn_key, [])
                global_variables.farm_flow_to_farm_dcn[farm_flow_to_farm_dcn_key].append('%s' % (farm_in_fc))

    #######################################
    #### Preliminary Farms Section End ####
    #######################################

    ###########################################
    #### DNS Global Settings Section Start ####
    ###########################################

    ###                        ###
    #    Finds DNS TTL and RR    #
    ###                        ###

        ##                                                              ##
        #    This section is used to find the DNS TTL and RR             #
        #    These parameters will later on be used on the GSLB rules    #
        ##                                                              ##

        if "dns response-ttl" in line: # Finds the global DNS TTL
            dns_ttl = global_variables.find_fnc( line, "set ", " " )
            break
        elif "dns response-ttl" not in line: # If no DNS TTL command, default TTL (0)
            dns_ttl = '0'

    global dns_rr
    for line in lp_to_lpng:
        if "dns two-records" in line: # Finds the global DNS RR
            dns_rr = global_variables.find_fnc( line, "set ", " " )
            if dns_rr == 'disable': # If disable, RR = 1
                dns_rr = '1'
            else: # If enabled, RR = 2
                dns_rr = '2'
            break
        elif "dns two-records" not in line: # If no DNS RR command, default RR (1)
            dns_rr = '1'

    #########################################
    #### DNS Global Settings Section End ####
    #########################################

    #################################################
    #### Proximity Global Settings Section Start ####
    #################################################

    ###                            ###
    #    Finds proximity settings    #
    ###                            ###

        ##                                                                      ##
        #    This section is used to find the proximity settings                 #
        #    These parameters will later on be used on GSLB rules and filters    #
        ##                                                                      ##

    global proximity_mode
    for line in lp_to_lpng:
        if "lp proximity mode" in line: # Finds the proximity mode
            proximity_mode = global_variables.find_fnc( line, 'set "', '"' )
            if proximity_mode == 'Full Proximity Inbound' or proximity_mode == 'Full Proximity Both':
                current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                print >>migration_errors, '%s #Unsupported_feature: the following command is partly supported by LP NG:' % (current_time)
                print >>migration_errors, "    Command: %s" % (line)
                print >>migration_errors, "    Details: LP NG only supports outbound proximity with Smart NAT, inbound is not supported."
                print >>migration_errors, '             Therefore, on the GSLB rules, "gmetric proximity" has not been configured.'
            break
        elif "lp proximity mode" not in line: # If no proximity mode command, use default (no proximity)
            proximity_mode = "No Proximity"

    if proximity_mode != "No Proximity": # If proximity not disabled, find other proximity settings
        global proximity_mask
        for line in lp_to_lpng:
            if "lp proximity subnet-mask" in line: # Finds the proximity mask
                proximity_mask = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
                proximity_mask = proximity_mask[0]
                break
            else:
                proximity_mask = "255.255.255.0"
        global proximity_main_dns
        for line in lp_to_lpng:
            if "lp proximity main-dns-address" in line: # Dinds the proximity main DNS server
                proximity_main_dns = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
                proximity_main_dns = proximity_main_dns[0]
                break
            else:
                proximity_main_dns = "0.0.0.0"
        global proximity_backup_dns
        for line in lp_to_lpng:
            if "lp proximity backup-dns-address" in line: # Finds the proximity backup DNS server
                proximity_backup_dns = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
                proximity_backup_dns = proximity_backup_dns[0]
                break
            else:
                proximity_backup_dns = "0.0.0.0"
        global proximity_aging
        for line in lp_to_lpng:
            if "lp proximity aging-period" in line: # Finds the proximity aging
                 proximity_aging = [int(s) for s in line.split() if s.isdigit()]
                 proximity_aging = proximity_aging[0]
                 break
            else:
                proximity_aging = 2800
        global proximity_retries
        for line in lp_to_lpng:
            if "lp proximity check-retries" in line: # Finds the proximity checks retries
                proximity_retries = [int(s) for s in line.split() if s.isdigit()]
                proximity_retries = proximity_retries[0]
                break
            else:
                proximity_retries = 2
        global proximity_interval
        for line in lp_to_lpng:
            if "lp proximity check-interval" in line: # Finds the proximity checks interval
                proximity_interval = [int(s) for s in line.split() if s.isdigit()]
                proximity_interval = proximity_interval[0]
                break
            else:
                proximity_interval = 5

    ###############################################
    #### Proximity Global Settings Section End ####
    ###############################################

    ######################################
    #### Router Servers Section Start ####
    ######################################

    ###                                       ###
    #    Finds Router Servers - Main Section    #
    ###                                       ###

        ##                                                                            ##
        #    This is the main section used to find the router servers configuration    #
        #    In this section, we only find the router servers, we don't print them     #
        ##                                                                            ##

    for line in lp_to_lpng:
        if "router-servers" in line:
            wl_farm_name = global_variables.find_fnc( line, 'setCreate "', '"' ) # Finds the router server's associated farm
            if wl_farm_name == 'error': # If no double quotes in the farm name
                wl_farm_name = global_variables.find_fnc( line, "setCreate ", " " ) # Finds the router server's associated farm again
            new_wl_farm_name = wl_farm_name
            for unsupported_char, supported_char in global_variables.special_characters_dcn.iteritems():
                new_wl_farm_name = new_wl_farm_name.replace ('%s' % (unsupported_char), "%s" % (supported_char))
            wl_name = global_variables.find_fnc( line, '%s" "' % (wl_farm_name), '"' ) # Finds the router server name
            if wl_name == 'error': # If there are no double quotes in the farm name and router server name
                wl_name = global_variables.find_fnc( line, '%s "' % (wl_farm_name), '"') # Finds the router server name again
                if wl_name == 'error': # If there are no double quotes in the router server name
                    wl_name = global_variables.find_fnc( line, '%s" ' % (wl_farm_name), ' ') # Finds the router server name again
                    if wl_name == 'error': # If there are no double quotes in the farm name
                        wl_name = global_variables.find_fnc( line, '%s ' % (wl_farm_name), ' ') # Finds the router server name again
            new_wl_name = wl_name
            for unsupported_char, supported_char in global_variables.special_characters_dcn.iteritems():
                new_wl_name = new_wl_name.replace ('%s' % (unsupported_char), "%s" % (supported_char))
            find_wl_ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the router server IP
            wl_ip = find_wl_ip[0]
            if wl_ip != 'error': # Populates a dictionary with the following values: # ---->
                                 # Router server IP as a key # ---->
                                 # Router server name as a value # ---->
                                 # This is used later on to check if a router server IP has different names
                duplicate_wls_dcn_key = "%s" % (wl_ip)
                global_variables.duplicate_wls_dcn.setdefault(duplicate_wls_dcn_key, [])
                global_variables.duplicate_wls_dcn[duplicate_wls_dcn_key].append('%s' % (new_wl_name))
                if wl_ip not in global_variables.own_addresses_lst:
                    global_variables.own_addresses_lst.append(wl_ip)
            if wl_ip != 'error' and wl_farm_name not in global_variables.farms_nonat_lst: # If the farm has NAT mode enabled, populates a dictionary with the following: # ---->
                                                                         # Farm name with NAT mode enable as a key # ---->
                                                                         # A list of its associated router servers as values # ---->
                                                                         # This is used later on to create the groups
                group_to_routers_dcn_key = "%s" % (new_wl_farm_name)
                global_variables.group_to_routers_dcn.setdefault(group_to_routers_dcn_key, [])
                global_variables.group_to_routers_dcn[group_to_routers_dcn_key].append('%s' % (wl_ip))
            elif wl_ip != 'error' and wl_farm_name in global_variables.farms_nonat_lst: # If the farm has NAT mode disabled, populates a dictionary with the following: # ---->
                                                                       # Farm name with NAT mode disable as a key # ---->
                                                                       # A list of its associated router servers as values # ---->
                                                                       # This is used later on to create the No NAT groups
                group_to_routers_nonat_dcn_key = "%s" % (new_wl_farm_name)
                global_variables.group_to_routers_nonat_dcn.setdefault(group_to_routers_nonat_dcn_key, [])
                global_variables.group_to_routers_nonat_dcn[group_to_routers_nonat_dcn_key].append('%s' % (wl_ip))

            if wl_ip != 'error': # Populates a dictionary of all group to routers for all types of farms
                group_to_routers_all_dcn_key = "%s" % (new_wl_farm_name)
                global_variables.group_to_routers_all_dcn.setdefault(group_to_routers_all_dcn_key, [])
                global_variables.group_to_routers_all_dcn[group_to_routers_all_dcn_key].append('%s' % (wl_ip))

            operation_mode = global_variables.find_fnc( line, ' -om ' , ' ' ) # Finds the router server operation mode (regular or backup)
            if operation_mode != 'error': # Populates a dictionary with the following values: # ---->
                                          # Farm name as a key # ---->
                                          # A list with the operation mode and router server IP as a value # ---->
                                          # This is used later on to map IP to name and configure the real server in mode backup
                om_key = "%s" % (new_wl_farm_name)
                global_variables.operation_mode_dcn.setdefault(om_key, [])
                global_variables.operation_mode_dcn[om_key].append('%s' % (operation_mode))
                global_variables.operation_mode_dcn[om_key].append('%s' % (wl_ip))

                bck_dcn_key = "%s" % (new_wl_farm_name) # Populates a dictionary with the following values: # ---->
                                                        # Farm name as a key # ---->
                                                        # The router server IP as a value # ---->
                                                        # This is used later on when creating the backup groups
                global_variables.bck_dcn.setdefault(bck_dcn_key, [])
                global_variables.bck_dcn[bck_dcn_key].append('%s' % (wl_ip))

            admin_status = global_variables.find_fnc( line, ' -as ' , ' ' ) # Finds the rotuer server admin status
            if admin_status != 'error': # Populates a dictionary with the following values: # ---->
                                        # Farm name as a key # ---->
                                        # A list with the admin status and router server IP as a value # ---->
                                        # This is used later on to map IP to name and disable the real server in the relevant group
                as_key = "%s" % (new_wl_farm_name)
                global_variables.admin_status_dcn.setdefault(as_key, [])
                global_variables.admin_status_dcn[as_key].append('%s' % (admin_status))
                global_variables.admin_status_dcn[as_key].append('%s' % (wl_ip))

    ####################################
    #### Router Servers Section End ####
    ####################################

    ########################################
    #### Main Finds Farms Section Start ####
    ########################################

    ###                              ###
    #    Finds Farms - Main Section    #
    ###                              ###

        ##                                                                             ##
        #    This is the main section used to find the farms and their configuration    #
        #    In this section, we only find the farms, we don't print them               #
        ##                                                                             ##

        if "farms table setCreate" in line:
            # print(line)
            farm_name = global_variables.find_fnc( line, 'setCreate "', '"' ) # Finds the farm name
            if farm_name == 'error': # If no double quotes in farm name
                farm_name = global_variables.find_fnc( line, "setCreate ", " " ) # Finds the farm name again
            new_farm_name = farm_name
            for unsupported_char, supported_char in global_variables.special_characters_dcn.iteritems():
                new_farm_name = new_farm_name.replace ('%s' % (unsupported_char), "%s" % (supported_char))
            if new_farm_name not in global_variables.default_group_lst:
                global_variables.default_group_lst.append(new_farm_name)
            if new_farm_name not in global_variables.all_farms_lst: # Populates a list of all farms
                global_variables.all_farms_lst.append(new_farm_name)

            dispatch_method = global_variables.find_fnc( line, '-dm "', '"' ) # Finds the farm's dispatch method
            if dispatch_method == "Least Amount of Traffic": # Each statement below maps the dispatch method to Alteon metric
                metric = "bandwidth"
            elif dispatch_method in ["Least Amount of Local Traffic", "Least Amount of Bytes", "Least Number of Bytes", "Least Amount of Local Bytes"]:
                metric = "bandwidth"
            elif dispatch_method == "Fewest Number of Users":
                metric = "leastconns"
            elif dispatch_method == "Fewest Number of Local Users":
                metric = "svcleast"
            elif dispatch_method in ["Source IP Hashing", "Destination IP Hashing", "Layer-3 Hashing"]:
                metric = "phash 255.255.255.255"
            elif dispatch_method == "Response Time":
                metric = "response"
            elif dispatch_method == "error": # If no double quotes in the dispatch method
                dispatch_method = global_variables.find_fnc( line, '-dm ', ' ' ) # Finds the dispatch method again (can be only "Hashing")
                if dispatch_method == "Hashing":
                    metric = "phash 255.255.255.255"
                else: # If no dispatch method found, use the LP default ("Cyclic", in Alteon, "roundrobin")
                    metric = "roundrobin"

            aging_time = global_variables.find_fnc( line, '-cl ', ' ' ) # Finds the farm's client aging time
            if aging_time == 'error': # If nothing found, use the LP default (60 seconds) # ---->
                                      # Converting to minutes, this is 1 minute. # ---->
                                      # We add 1 since Alteon doesn't support odd minutes # ----->
                                      # We add 2 for the Alteon's slowstart algorithm, we end up with 4 minutes
                new_aging_time = 4
            else: # if client aging time is found - non default
                new_aging_time = int(math.ceil(float(aging_time)/60)) # We convert to minutes, then float and round the number
                if (new_aging_time % 2 == 0):
                    new_aging_time = new_aging_time
                    if new_aging_time == 0: # If we end up with 0, we use 4
                        new_aging_time = 4
                    else: # Else, we add 2 minutes for the Alteon's slowstart algorithm
                        new_aging_time += 2
                else: # If number is odd, we add 1 to use even number, then add 2 for the Alteon's slowstart algorithm
                    new_aging_time = int(new_aging_time)+1
                    new_aging_time += 2

            farm_parameters_dcn_key = "%s" % (new_farm_name) # Populates a dictionary with the following values: # ---->
                                         # The new farm name as a key # ---->
                                         # The farm's metric as a value # ---->
                                         # This is used later on to configure the metric when creating the group # ---->
                                         # This is also used later on to configure the gmetric when creating the GSLB rule
            global_variables.farm_parameters_dcn.setdefault(farm_parameters_dcn_key, [])
            global_variables.farm_parameters_dcn[farm_parameters_dcn_key].append('%s' % (metric))
            #global_variables.farm_parameters_dcn[farm_parameters_dcn_key].append('%s' % (aging_time))

            orig_farm_parameters_dcn_key = "%s" % (farm_name) # Populates a dictionary with the following values: # ---->
                                         # The original farm name as a key # ---->
                                         # The farm's original dispatch method as a value # ---->
                                         # This is used later on to generate a log when the dispatch method can't be used as gmetric
            global_variables.orig_farm_parameters_dcn.setdefault(orig_farm_parameters_dcn_key, [])
            global_variables.orig_farm_parameters_dcn[orig_farm_parameters_dcn_key].append('%s' % (dispatch_method))

            orig_dm_dcn_key = "%s" % (new_farm_name) # Populates a dictionary with the following values: # ---->
                                                     # The farm name as a key # ---->
                                                     # The original dispatch method as a value # ---->
                                                     # This is used later on to configure the pbind/thash on filters if needed
            global_variables.orig_dm_dcn.setdefault(orig_dm_dcn_key, [])
            global_variables.orig_dm_dcn[orig_dm_dcn_key].append('%s' % (dispatch_method))

            global_variables.farms_aging_times_lst.append("%s" % (new_aging_time)) # Populates a list with the new client aging times as objects # ---->
                                                                  # This is used later on to compare with application aging times

        if "client-table application-aging-time" in line:
            app_aging_time = global_variables.find_fnc( line, ' -at ', ' ' ) # Finds the application aging time
                                                            # We use the same calculation as with the farm client aging time
            if app_aging_time == 'error':
                new_app_aging_time = 4
            else:
                new_app_aging_time = int(math.ceil(float(app_aging_time)/60))
                if (new_app_aging_time % 2 == 0):
                    new_app_aging_time = new_app_aging_time
                    if new_app_aging_time == 0:
                        new_app_aging_time = 4
                    else:
                        new_app_aging_time += 2
                else:
                    new_app_aging_time = int(new_app_aging_time)+1
                    new_app_aging_time += 2

            global_variables.app_aging_times_lst.append("%s" % (new_app_aging_time)) # Populates a list with the new app aging times as objects # ---->
                                                                    # This is used later on to compare with farm client aging times
    farms_aging_times_lst = map(int, global_variables.farms_aging_times_lst)
    app_aging_times_lst = map(int, global_variables.app_aging_times_lst)
    for line in lp_to_lpng:
        farms_max_aging_time = max(farms_aging_times_lst)
        if len(app_aging_times_lst) > 0:
            app_max_aging_time = max(app_aging_times_lst)
            break
        else:
            app_max_aging_time = 0
    global max_aging_time
    max_aging_time = max(farms_max_aging_time, app_max_aging_time) # Finds the maximum aging time among the client and app aging times
                                                                   # This is done since Alteon doesn't support tmout on LLB filter
                                                                   # and doesn't support app aging time
                                                                   # Therefore, we use the highest aging time on all real servers
    #####################################
    #### Main Find Farms Section End ####
    #####################################

    #############################################
    #### Real Servers Creation Section Start ####
    #############################################

    ###                                        ###
    #    Real Servers Creation - Main Section    #
    ###                                        ###

        ##                                                                              ##
        #    This is the main section used to create the real servers configuraiton      #
        #    In this section, we use the dictionaries populated in the find section      #
        #                                                                                #
        #    Rules:                                                                      #
        #                                                                                #
        #    1.) We check if the router server IP has multiple names                     #
        #        If it has, we ask the user to choose one of the names or a new name     #
        #        If it has a single name, we use it and we don't ask the user            #
        #    2.) We always disable real servers in the group level                       #
        #    3.) When creating "No NAT" groups, we check the following:                  #
        #        a. If the real server belongs to another regular group:                 #
        #           We create it again with the same name with "_NAT" appended           #
        #           PIP mode will be "nonat"                                             #
        #        b. If the real server only belongs to a "No NAT group":                 #
        #           We create it with the chosen name, we do not append "_NAT"           #
        #           PIP mode will be "nonat"                                             #
        #        c. If a DNS rule uses a "No NAT" farm, and:                             #
        #           Its real servers belong also to a regular farm                       #
        #           This means that the real servers have "_NAT" appended, therefore:    #
        #           In this case, we create a special group for GSLB                     #
        #           The group will have the regular real server names                    #
        #           It'll only be used in GSLB rules                                     #
        #           This behavior will be changed soon as it doesn't conform with LP     #
        ##                                                                              ##

    ###                                   ###
    #    WAN Link Name Selection Section    #
    ###                                   ###

        ##                                                                                                             ##
        #    This is a section used to prompt the user to select names for the WAN links                                #
        #    This section will be shown to the user only if there is at least one router server with multiuple names    #
        ##                                                                                                             ##

    #for orig_wl_ip, orig_wl_name in global_variables.duplicate_wls_dcn.iteritems(): # Loops over the dictionary that contains the IP to real names mapping

        #wl_names_equal_status = global_variables.all_same(orig_wl_name) # For each real server IP, we check if all of its values are the same
        #if wl_names_equal_status == False: # If they're not the same, we prompt the user with the WAN link selection screen

    equal_status = 0
    for orig_wl_ip, orig_wl_name in global_variables.duplicate_wls_dcn.iteritems(): # Loops over the dictionary that contains the IP to real names mapping
        wl_names_equal_status = global_variables.all_same(orig_wl_name) # For each real server IP, we check if all of its values are the same
        if wl_names_equal_status == False: # If they're not the same, we prompt the user with the WAN link selection screen
            equal_status = 1
            uniq_unequal_wl_names = list(set(orig_wl_name)) # Remove duplicate unequal names
            unequal_wl_names = ', '.join(uniq_unequal_wl_names) # Creates a visible list of unequal names, comma separated
            global_variables.isp_id += 1 # ISP ID for showing the user ISPs with multiple names

            unequal_wl_names_to_html_dcn = {}
            unequal_wl_names_to_html_dcn['id'] = '%s' % (global_variables.isp_id)
            unequal_wl_names_to_html_dcn['ip'] = '%s' % (orig_wl_ip)
            #unequal_wl_names_to_html_dcn['wl_names'] = '%s' % (uniq_unequal_wl_names)
            for a in uniq_unequal_wl_names:
                unequal_wl_names_to_html_dcn.setdefault("wl_names", []).append(a)
            global_variables.unequal_wls_lst.append(unequal_wl_names_to_html_dcn)

    if equal_status == 1:
        return render_template('isps.html', title='ISPs', unequal_wls_lst=global_variables.unequal_wls_lst)
    else:
        return redirect('/page3')

@app.route('/page2', methods=['GET','POST'])
@app.route('/page3', methods=['GET','POST'])
def page2():

    def print_adv_hc_fnc(hc_name, hc_destIP, hc_dname):
        '''Prints the script's predefined advanced HCs for WLs.
        Takes the HC name, HC destination IP and HC domain name as arguments.
        '''
        print >>output_file, "/c/slb/advhc/health %s DNS" % (hc_name)
        print >>output_file, "        dport 53"
        print >>output_file, "        dest 4 %s" % (hc_destIP)
        print >>output_file, "        transp enabled"
        print >>output_file, "        retry 2"
        print >>output_file, "        timeout 4"
        print >>output_file, "        downtime 5"
        print >>output_file, "/c/slb/advhc/health %s DNS/dns" % (hc_name)
        print >>output_file, '        domain "%s"' % (hc_dname)

    def print_real_hc_fnc(hc_type, hc_real_name, hc_rip):
        '''Prints the WL direct HC and the LOGEXP that binds it with the advanced HCs.
        Takes the HC type (predefined or user-defined), WL name and WL IP as arguments.
        '''
        if hc_type == "Y" or hc_type == "y" or hc_type == "Setup":
            print >>output_file, "/c/slb/advhc/health %s_ICMP ICMP" % (hc_real_name) # Prints the direct HC
            print >>output_file, "        dest 4 %s" % (hc_rip)
            print >>output_file, "        retry 2"
            print >>output_file, "        timeout 4"
            print >>output_file, "        downtime 5"
            print >>output_file, "/c/slb/advhc/health %s_HCs LOGEXP" % (hc_real_name) # Prints the LOGEXP that binds the predefined HCs and the direct 
        if hc_type == "Y" or hc_type == "y":
            print >>output_file, '        logexp "(%s_ICMP)&(Yahoo_DNS1|CNN_DNS1|Yahoo_DNS2|CNN_DNS2)"' % (hc_real_name)
        elif hc_type == "Setup":
            print >>output_file, '        logexp "(%s_ICMP)&(%s_DNS1|%s_DNS1|%s_DNS2|%s_DNS2)"' % (hc_real_name, hc_fqdn1, hc_fqdn2, hc_fqdn1, hc_fqdn2)

    def print_real_fnc(real_type, real_name, rip, max_aging_time):
        '''Prints the WL real server.
        Takes the real type, WL name, WL IP and max aging time as arguments.
        Real server types defined in this script are:
        1.) Regular.
        2.) nonat_not_in_regular (No NAT that doesn't belong also to a regular farm).
        3.) nonat_no_regular (No NAT while there are no regular farms in the configuration).
        4.) nonat_in_regular (NO NAT that also belongs to a regular farm).
        '''
        if real_type == "nonat_in_regular": # If the real server is no NAT but there also a regular server in another farm
            print >>output_file, "/c/slb/real %s_NoNAT" % (real_name) # We print the name and append "_NoNAT"
        else: # If it's a regular server, or "no NAT" that is not also regular, or "no NAT" while there are no regular servers
            print >>output_file, "/c/slb/real %s" % (real_name) # We print the regular name
        print >>output_file, "        ena"
        print >>output_file, "        ipver v4"
        print >>output_file, "        rip %s" % (rip)
        print >>output_file, "        type wanlink"
        print >>output_file, "        maxcon 0 logical"
        print >>output_file, "        tmout %s" % (max_aging_time)
        if hc_note == "Y" or hc_note == "y" or hc_note == "Setup": # Binds the LOGEXP HC if the user chose the predefined HC or the HC setup
            print >>output_file, "        health WLs_HCs"
        else: # Uses "health icmp" if the user chose to not configure HCs
            print >>output_file, "        health icmp"
        if real_type == "nonat_in_regular": # Mode "nonat" configuration for "no NAT" real servers
            print >>output_file, "/c/slb/real %s_NoNAT/adv/pip" %  (real_name)
            print >>output_file, "        mode nonat"
        elif real_type == "nonat_not_in_regular" or real_type == "nonat_no_regular":
            print >>output_file, "/c/slb/real %s/adv/pip" %  (real_name)
            print >>output_file, "        mode nonat"

    def add_servers_to_regular_group_fnc(wl_ip, wl_name):
        '''Adds regular WL servers to a WL group.
        Takes WL IP and WL name as arguments.
        '''
        if server == wl_ip: # We validate that the IP in the regular farm is the same as the IP in the user chosen WL names dict
            if farm in global_variables.gbck_dcn.keys(): # If the farm has a backup group
                if farm not in global_variables.back_added_lst: # Checking if we didn't yet add the backup group, then add it
                    print >>output_file, "        backup g%s" % (global_variables.gbck_dcn[farm][0])
                    global_variables.back_added_lst.append(farm) # Add the farm to the list so we know a backup group was already added to it
                if server not in global_variables.operation_mode_dcn[farm]: # Adding other servers if they're not backup
                    print >>output_file, "        add %s" % (wl_name)
                    if farm in global_variables.admin_status_dcn.keys(): # Disables the real server if needed
                        if server in global_variables.admin_status_dcn[farm]:
                            print >>output_file, "        dis %s" % (wl_name)
            elif farm in global_variables.operation_mode_dcn.keys() and len(global_variables.operation_mode_dcn[farm]) == 2: # If the farm has one backup server
                if server in global_variables.operation_mode_dcn[farm]: # We check if the server is a backup server and if so, add it as backup
                    print >>output_file, "        backup r%s" % (wl_name)
                    if farm in global_variables.admin_status_dcn.keys(): # Disables the real server if needed
                        if server in global_variables.admin_status_dcn[farm]:
                            print >>output_file, "        dis %s" % (wl_name)
                else: # If this server is not a backup server, we add it regularly
                    print >>output_file, "        add %s" % (wl_name)
                    if farm in global_variables.admin_status_dcn.keys(): # Disables the real server if needed
                        if server in global_variables.admin_status_dcn[farm]:
                            print >>output_file, "        dis %s" % (wl_name)
            elif farm not in global_variables.operation_mode_dcn.keys() and farm not in global_variables.gbck_dcn.keys(): # If the farm has no backup server, we add the real server regularly
                print >>output_file, "        add %s" % (wl_name)
                if farm in global_variables.admin_status_dcn.keys(): # Disables the real server if needed
                    if server in global_variables.admin_status_dcn[farm]:
                        print >>output_file, "        dis %s" % (wl_name)

    def add_servers_to_nonat_group_fnc(nonat_wl_ip, nonat_wl_name):
        '''Adds No NAT WL servers to a WL group.
        Takes WL IP and WL name as arguments.
        '''
        if server == nonat_wl_ip: # We validate that the IP in the No NAT farm is the same as the IP in the user chosen WL names dict
            if farm in global_variables.gbck_dcn.keys(): # If the farm has a backup group
                if farm not in global_variables.back_added_lst: # Checking if we didn't yet add the backup group, then add it
                    print >>output_file, "        backup g%s" % (global_variables.gbck_dcn[farm][0])
                    global_variables.back_added_lst.append(farm) # Add the farm to the list so we know a backup group was already added to it
                if server not in global_variables.operation_mode_dcn[farm]: # Adding other servers if they're not backup
                    if len(global_variables.group_to_routers_dcn) > 0: # If there are regular farms
                        if server in group_to_routers_values: # if the server is also in a regular farm
                            print >>output_file, "        add %s_NoNAT" % (nonat_wl_name[0]) # Adds the server and appends "_NoNAT"
                        else: # if the server is not in a regular farm
                            print >>output_file, "        add %s" % (nonat_wl_name[0]) # Adds the server with the user chosen name
                    else: # If there are no regular farms
                        print >>output_file, "        add %s" % (nonat_wl_name[0]) # Adds the server with the user chosen name
                    if farm in global_variables.admin_status_dcn.keys(): # If the farm is in the admin state dictionary keys
                        if server in global_variables.admin_status_dcn[farm]: # Validates if the current real server is disabled
                            if len(global_variables.group_to_routers_dcn) > 0: # If there are regular farms
                                if server in group_to_routers_values: # If the server is also in a regular farm
                                    print >>output_file, "        dis %s_NoNAT" % (nonat_wl_name[0]) # Disables the server and appends "_NoNAT"
                                else: # If the server is not in a regular farm
                                    print >>output_file, "        dis %s" % (nonat_wl_name[0]) # Disables the server with the user chosen name
                            else: # If there are no regular farms
                                print >>output_file, "        dis %s" % (nonat_wl_name[0]) # Disables the server with the user chosen name
            elif farm in global_variables.operation_mode_dcn.keys() and len(global_variables.operation_mode_dcn[farm]) == 2: # If the farm has one backup server
                if server in global_variables.operation_mode_dcn[farm]: # We check if the server is a backup server
                    if len(global_variables.group_to_routers_dcn) > 0: # If there are regular farms
                        if server in group_to_routers_values: # If the server is also in a regular farm
                            print >>output_file, "        backup r%s_NoNAT" % (nonat_wl_name[0]) # Adds the server as a backup and appends "_NoNAT"
                        else: # If the server is not in a regular farm
                            print >>output_file, "        backup r%s" % (nonat_wl_name[0]) # Adds the server as a backup with the user chosen name
                    else: # If there are no regular farms
                        print >>output_file, "        backup r%s" % (nonat_wl_name[0]) # Adds the server as a backup with the user chosen name
                    if farm in global_variables.admin_status_dcn.keys(): # If the farm is in the admin state dictionary keys
                        if server in global_variables.admin_status_dcn[farm]: # Validates if the current real server is disabled
                            if len(global_variables.group_to_routers_dcn) > 0: # If there are regular farms
                                if server in group_to_routers_values: # If the server is also in a regular farm
                                    print >>output_file, "        dis %s_NoNAT" % (nonat_wl_name[0]) # Disables the server and appends "_NoNAT"
                                else: # If the server is not in a regular farm
                                    print >>output_file, "        dis %s" % (nonat_wl_name[0]) # Disables the server with the user chosen name
                            else: # If there are no regular farms
                                print >>output_file, "        dis %s" % (nonat_wl_name[0]) # Disables the server with the user chosen name
                else: # If farm has backup at least one backup server, but this specific server is not a backup server
                    if len(global_variables.group_to_routers_dcn) > 0: # if there are regular farms
                        if server in group_to_routers_values: # If the server is also in a regular farm
                            print >>output_file, "        add %s_NoNAT" % (nonat_wl_name[0]) # Adds the server and appends "_NoNAT"
                        else: # If the server is not in a regular farm
                            print >>output_file, "        add %s" % (nonat_wl_name[0]) # Adds the server with the user chosen name
                    else: # If there are not regular farms
                        print >>output_file, "        add %s" % (nonat_wl_name[0]) # Adds the server with the user chosen name
                    if farm in global_variables.admin_status_dcn.keys(): # If the farm is in the admin state dictionary keys
                        if server in global_variables.admin_status_dcn[farm]: # Validates if the current real server is disabled
                            if len(global_variables.group_to_routers_dcn) > 0: # If there are regular farms
                                if server in group_to_routers_values: # If the server is also in a regular farm
                                    print >>output_file, "        dis %s_NoNAT" % (nonat_wl_name[0]) # Disables the server and appends "_NoNAT"
                                else: # If the server is not ina regular farm
                                    print >>output_file, "        dis %s" % (nonat_wl_name[0]) # Disables the server with the user chosen name
                            else: # If there are no regular farms
                                print >>output_file, "        dis %s" % (nonat_wl_name[0]) # Disables the server with the user chosen name
            elif farm not in global_variables.operation_mode_dcn.keys() and farm not in global_variables.gbck_dcn.keys(): # If the farm has no backup servers
                if len(global_variables.group_to_routers_dcn) > 0: # If there are regular farms
                    if server in group_to_routers_values: # If the server is also in a regular farm
                        print >>output_file, "        add %s_NoNAT" % (nonat_wl_name[0]) # Adds the server and appends "_NoNAT"
                    else: # If the server is not in a regular farm
                        print >>output_file, "        add %s" % (nonat_wl_name[0]) # Adds the server with the user chosen name
                else: # If there are no regular farms
                    print >>output_file, "        add %s" % (nonat_wl_name[0]) # Adds the server with the user chosen name
                if farm in global_variables.admin_status_dcn.keys(): # If the farm is in the admin state dictionary keys
                    if server in global_variables.admin_status_dcn[farm]: # Validates if the current real server is disabled
                        if len(global_variables.group_to_routers_dcn) > 0: # If there are regular farms
                            if server in group_to_routers_values: # If the server is also in a regular farm
                                print >>output_file, "        dis %s_NoNAT" % (nonat_wl_name[0]) # Disables the server and appends "_NoNAT"
                            else: # if the server is not in a regular farm
                                print >>output_file, "        dis %s" % (nonat_wl_name[0]) # Disables the server with the user chosen name
                        else: # If there are no regular farms
                            print >>output_file, "        dis %s" % (nonat_wl_name[0]) # Disables the server with the user chosen name

    def add_servers_to_bck_group_fnc(bck_wl_ip, bck_wl_name):
        '''Adds WL servers to a WL backup group.i
        Takes WL IP and WL name as arguments.
        '''
        if bserver == bck_wl_ip: # We validate that the IP in the backup farm is the same as the IP in the user chosen WL names dict
            if len(global_variables.group_to_routers_nonat_dcn) > 0: # If there are "No NAT" farms
                if bfarm in global_variables.group_to_routers_nonat_dcn.keys(): # If the current backup farm name is a No NAT farm
                    if len(global_variables.group_to_routers_dcn) > 0: # If there are regular farms
                        if bserver in group_to_routers_values: # If the current WAN link IP is in a regular farm
                            print >>output_file, "        add %s_NoNAT" % (bck_wl_name[0]) # We add the WAN link and append "_NoNAT"
                        else: # If the current WAN link IP is not in a regular farm 
                            print >>output_file, "        add %s" % (bck_wl_name[0]) # We add the WAN link with its user chosen name
                    else: # If there are no regular farms
                        print >>output_file, "        add %s" % (bck_wl_name[0]) # We add the WAN link with its user chosen name
                else: # If the current backup farm name is a regular farm
                    print >>output_file, "        add %s" % (bck_wl_name[0]) # We add the WAN link with its user chosen name
            else: # If there are no "No NAT" farms
                print >>output_file, "        add %s" % (bck_wl_name[0]) # We add the WAN link with its user chosen name
            if bfarm in global_variables.admin_status_dcn.keys(): # Loops over the admin status dictionary keys
                if bserver in global_variables.admin_status_dcn[bfarm]: # Validates if the current real server is disabled 
                    if len(global_variables.group_to_routers_nonat_dcn) > 0: # If there are "No NAT" farms
                        if bfarm in global_variables.group_to_routers_nonat_dcn.keys(): # If the current backup farm name is a No NAT farm
                            if len(global_variables.group_to_routers_dcn) > 0: # If there are regular farms
                                if bserver in group_to_routers_values: # If the current WAN link IP is in a regular farm
                                    print >>output_file, "        dis %s_NoNAT" % (bck_wl_name[0]) # We disable the WAN link and append "_NoNAT"
                                else: # If the current WAN link IP is not in a regular farm 
                                    print >>output_file, "        dis %s" % (bck_wl_name[0]) # We disable the WAN link with its user chosen name
                            else: # If there are no regular farms
                                print >>output_file, "        dis %s" % (bck_wl_name[0]) # We disable the WAN link with its user chosen name
                        else: # If the current backup farm name is a regular farm
                            print >>output_file, "        dis %s" % (bck_wl_name[0]) # We disable the WAN link with its user chosen name
                    else: # If there are no "No NAT" farms
                        print >>output_file, "        dis %s" % (bck_wl_name[0]) # We add the WAN link with its user chosen name

    if request.path == '/page2':
        chosen_wl_names = str(request.form['new_isps'])
        chosen_wl_names = chosen_wl_names.split(",")
        for isp in chosen_wl_names:
            user_new_wl_names_dcn_key = "%s" % (isp.split("&")[0])
            global_variables.user_new_wl_names_dcn.setdefault(user_new_wl_names_dcn_key, [])
            global_variables.user_new_wl_names_dcn[user_new_wl_names_dcn_key].append('%s' % (isp.split("&")[1]))

    ###                         ###
    #    Health Checks Section    #
    ###                         ###

        ##                                                                                                   ##
        #    This is a section used to prompt the user that health checks will not be migrated                #
        #    The user will have the following choices:                                                        #
        #                                                                                                     #
        #    1.) Use a predefined advanced HC configuration                                                   #
        #    2.) Go to a setup screen to create his own advanced HC configration (DNS based health checks)    #
        #    3.) Not create any advanced HC configuration                                                     #
        #        In this case, the script will create "health icmp" on each real server                       #
        #        It'll also prompt the user to migrate the LP HC configuration manually                       #
        ##                                                                                                   ##

    if hc_note == "Y" or hc_note == "y": # If the user chose "Y/y", we'll use the predefined HC configuration
        print_adv_hc_fnc("CNN_DNS1", "8.8.8.8", "www.cnn.com")
        print_adv_hc_fnc("CNN_DNS2", "209.244.0.3", "www.cnn.com")
        print_adv_hc_fnc("Yahoo_DNS1", "8.8.8.8", "www.yahoo.com")
        print_adv_hc_fnc("Yahoo_DNS2", "209.244.0.3", "www.yahoo.com")
        print >>output_file, "/c/slb/advhc/health WLs_HCs LOGEXP"
        print >>output_file, '        logexp "(icmp)&(Yahoo_DNS1|CNN_DNS1|Yahoo_DNS2|CNN_DNS2)"'
    elif hc_note == "Setup": # If the user chose "Setup", we'll present the HC setup menu
        # Starts printing the HCs that the user created
        print_adv_hc_fnc("%s_DNS1" % (hc_fqdn1), hc_dns1, hc_fqdn1)
        print_adv_hc_fnc("%s_DNS2" % (hc_fqdn1), hc_dns2, hc_fqdn1)
        print_adv_hc_fnc("%s_DNS1" % (hc_fqdn2), hc_dns1, hc_fqdn2)
        print_adv_hc_fnc("%s_DNS2" % (hc_fqdn2), hc_dns2, hc_fqdn2)
        print >>output_file, "/c/slb/advhc/health WLs_HCs LOGEXP"
        print >>output_file, '        logexp "(icmp)&(%s_DNS1|%s_DNS1|%s_DNS2|%s_DNS2)"' % (hc_fqdn1, hc_fqdn2, hc_fqdn1, hc_fqdn2)

    ###                                         ###
    #    WAN Link Real Server Creation Section    #
    ###                                         ###

        ##                                                                                        ##
        #    This is a section used to create the WAN link real servers and their direct HCs       #
        #    In this section we perform the following:                                             #
        #                                                                                          #
        #    1.) Check if there are WAN links with different names and use the user chosen name    #
        #    2.) Check if there are WAN links with a single name and use it                        #
        #    3.) If the WAN link is No NAT, we check the following:                                #
        #        a. If it's also part of a NAT farm, we print it with "NoNAT" appended             #
        #        b. If it's not part of a NAT farm, we print the regular name                      # 
        ##                                                                                        ##

    group_to_routers_values =  ','.join(str(v) for v in global_variables.group_to_routers_dcn.values()) # Creates a large string that contains all of the real servers IP addresses that belong to farms that have NAT mode enabled # ---->
                                                                                       # It'll be used later on to check if a No NAT router server also belongs to a NAT mode enabled farm
    group_to_routers_nonat_values = ','.join(str(v) for v in global_variables.group_to_routers_nonat_dcn.values())

        ##                                                                                              ##
        #    This section creates the WAN links that have different names, using the user chosen name    #
        ##                                                                                              ##

    if global_variables.user_new_wl_names_dcn != '': # If the user chosen WL names dictionary is not empty
        for user_wl_ip, user_wl_name in global_variables.user_new_wl_names_dcn.iteritems(): # Loops over the dictionary to create direct HCs and real servers
            #print_real_hc_fnc(hc_note, user_wl_name[0], user_wl_ip) # Executes the function that prints the direct HC 
            if user_wl_ip in group_to_routers_values: # If the router server IP is in the regular WAN links list, we print the real server with the user chosen name
                print_real_fnc("regular", user_wl_name[0], user_wl_ip, max_aging_time)
            if user_wl_ip in group_to_routers_nonat_values: # If the router server IP in in the no NAT WAN links
                if len(global_variables.group_to_routers_dcn) > 0: # If the dictionary of the regular WAN links to groups is not empty
                    if user_wl_ip in group_to_routers_values: # If the router server IP is in the regular WAN links list too, we append "_NoNAT" to the real server name
                        print_real_fnc("nonat_in_regular", user_wl_name[0], user_wl_ip, max_aging_time)
                    else: # If the router server IP is not in the regular WAN links list, we use the regular name
                        print_real_fnc("nonat_not_in_regular", user_wl_name[0], user_wl_ip, max_aging_time)
                else: # If the dictionary of the regular WAN links to group is empty (meaning there's only No NAT farms), we use the regular real server name
                    print_real_fnc("nonat_no_regular", user_wl_name[0], user_wl_ip, max_aging_time)

        ##                                                                                          ##
        #    This section creates the WAN links that have a single name, using their regular name    #
        ##                                                                                          ##

    for orig_wl_ip, orig_wl_name in global_variables.duplicate_wls_dcn.iteritems(): # Loops over the dictionary to create direct HCs and real servers
        wl_names_equal_status = global_variables.all_same(orig_wl_name)
        if wl_names_equal_status == True: # If the router names are the same
            #print_real_hc_fnc(hc_note, orig_wl_name[0], orig_wl_ip)
            if orig_wl_ip in group_to_routers_values: # If the router server IP is in the WAN links list, we print the regular real server name
                print_real_fnc("regular", orig_wl_name[0], orig_wl_ip, max_aging_time)
                user_equal_wl_names_dcn_key = "%s" % (orig_wl_ip) # Populates a dictionary with the following values: # ---->
                                  # The real server IP as a key # ---->
                                  # The real server name as a value # ---->
                                  # This is used later on to add the real servers to the group
                global_variables.user_equal_wl_names_dcn.setdefault(user_equal_wl_names_dcn_key, [])
                global_variables.user_equal_wl_names_dcn[user_equal_wl_names_dcn_key].append('%s' % (orig_wl_name[0]))
            if orig_wl_ip in group_to_routers_nonat_values: # If the router server IP is in the no NAT WAN links
                if len(global_variables.group_to_routers_dcn) > 0: # If the dictionary of the regular WAN links to groups is not empty
                    if orig_wl_ip in group_to_routers_values: # If the router server IP is in the regular WAN links list too, we append "_NoNAT" to the real server name
                        print_real_fnc("nonat_in_regular", orig_wl_name[0], orig_wl_ip, max_aging_time)
                        user_equal_wl_names_dcn_key = "%s" % (orig_wl_ip)
                        global_variables.user_equal_wl_names_dcn.setdefault(user_equal_wl_names_dcn_key, [])
                        global_variables.user_equal_wl_names_dcn[user_equal_wl_names_dcn_key].append('%s' % (orig_wl_name[0]))
                    else: # If the router server IP is not in the regular WAN links list, we use the regular name
                        print_real_fnc("nonat_not_in_regular", orig_wl_name[0], orig_wl_ip, max_aging_time)
                        user_equal_wl_names_dcn_key = "%s" % (orig_wl_ip)
                        global_variables.user_equal_wl_names_dcn.setdefault(user_equal_wl_names_dcn_key, [])
                        global_variables.user_equal_wl_names_dcn[user_equal_wl_names_dcn_key].append('%s' % (orig_wl_name[0]))
                else: # If the dictionary of the regular WAN links to group is empty (meaning there's only No NAT farms), we use the regular real server name
                    print_real_fnc("nonat_no_regular", orig_wl_name[0], orig_wl_ip, max_aging_time)
                    user_equal_wl_names_dcn_key = "%s" % (orig_wl_ip)
                    global_variables.user_equal_wl_names_dcn.setdefault(user_equal_wl_names_dcn_key, [])
                    global_variables.user_equal_wl_names_dcn[user_equal_wl_names_dcn_key].append('%s' % (orig_wl_name[0]))

    ###########################################
    #### Real Servers Creation Section End ####
    ###########################################

    #######################################
    #### Groups Creation Section Start ####
    #######################################

    ###                                  ###
    #    Groups Creation - Main Section    #
    ###                                  ###

        ##                                                                                   ##
        #    This is the main section used to create the groups configuraiton                 #
        #    In this section, we use the following dictionaries:                              #
        #                                                                                     #
        #    1.) Dictionaries populated in the real servers find section                      #
        #    2.) Dictionaries populated in the real servers creation section                  #
        #                                                                                     #
        #    Rules:                                                                           #
        #                                                                                     #
        #    1.) We create the following:                                                     #
        #        a. Regular groups                                                            #
        #        b. A "backup r" if we find only one backup real server in the farm           #
        #        c. A backup group if we find more than one backup real server in the farm    #
        #        d. No NAT groups                                                             #
        #    2.) We always disable real servers in the group level                            #
        #    3.) When creating "No NAT" groups, we check the following:                       #
        #        a. A backup group is created with the following name convention:             #
        #           The regular group name and "_BCK" appended                                #
        #        b. If a DNS rule uses a "No NAT" farm, and:                                  #
        #           Its real servers also belong to a regular farm                            #
        #           This means that the real servers have "_NAT" appended, therefore:         #
        #           In this case, we create a special group for GSLB                          #
        #           The group will have the regular real server names                         #
        #           It'll only be used in GSLB rules                                          #
        #           This behavior will be changed soon as it doesn't conform with LP          #
        ##                                                                                   ##

    ###                                           ###
    #    Groups Creation - Backup Groups Section    #
    ###                                           ###

    group_to_routers_values =  ','.join(str(v) for v in global_variables.group_to_routers_dcn.values())
    for bfarm, bservers in global_variables.bck_dcn.iteritems(): # Looping over the backup group to routers dictionary
        if len(bservers) > 1: # If the amount of real servers is more than 1, we know we need a backup group
            gbck = "%s_BCK" % (bfarm) # Creates the backup group ID
            print >>output_file, "/c/slb/group %s_BCK" % (bfarm) # Prints the general backup group general configuration
            print >>output_file, "        ipver v4"
            print >>output_file, "        type wanlink"
            print >>output_file, "        metric %s" % (global_variables.farm_parameters_dcn[bfarm][0]) # We use the metric of the regular group
            gbck_dcn_key = "%s" % (bfarm) # Populates a dictionary with the following values: # ---->
                                          # The regular group ID as a key # ---->
                                          # The backup group ID as a value # ---->
                                          # This is used later on to associate the backup group to the regular group
            global_variables.gbck_dcn.setdefault(gbck_dcn_key, [])
            global_variables.gbck_dcn[gbck_dcn_key].append('%s' % (gbck))
            for bserver in bservers: # Loop over the real servers in the backup farm
                for bck_user_wl_ip, bck_user_wl_name in global_variables.user_new_wl_names_dcn.iteritems(): # Loop over the user chosen WL IPs and names
                    add_servers_to_bck_group_fnc(bck_user_wl_ip, bck_user_wl_name) # Executes the function that adds the reals to the group
                for bck_orig_wl_ip, bck_orig_wl_name in global_variables.user_equal_wl_names_dcn.iteritems(): # Loops over the equal WL IPs and names
                    add_servers_to_bck_group_fnc(bck_orig_wl_ip, bck_orig_wl_name) # Executes the function that adds the reals to the group

    ###                                            ###
    #    Groups Creation - Regular Groups Section    #
    ###                                            ###

    group_to_routers_nonat_values =  ','.join(str(v) for v in global_variables.group_to_routers_nonat_dcn.values())
    if len(global_variables.group_to_routers_dcn) > 0:
        for farm, servers in global_variables.group_to_routers_dcn.iteritems(): # Loops over the regular group to routers dictionary
            print >>output_file, "/c/slb/group %s" % (farm) # Prints the general group configuration
            print >>output_file, "        ipver v4"
            print >>output_file, "        type wanlink"
            if farm in global_variables.farm_parameters_dcn.keys():
                print >>output_file, "        metric %s" % (global_variables.farm_parameters_dcn[farm][0])
            for server in servers: # Loops over the real servers in the regular farm
                for user_wl_ip, user_wl_name in global_variables.user_new_wl_names_dcn.iteritems(): # Loop over the user chosen WL IPs and names
                    add_servers_to_regular_group_fnc(user_wl_ip, user_wl_name[0]) # Executes the function that adds the reals to the group
                for orig_wl_ip, orig_wl_name in global_variables.user_equal_wl_names_dcn.iteritems(): # Loops over the equal WL IPs and names
                    add_servers_to_regular_group_fnc(orig_wl_ip, orig_wl_name[0]) # Executes the function that adds the reals to the group

    ###                                           ###
    #    Groups Creation - No NAT Groups Section    #
    ###                                           ###

    for farm, servers in global_variables.group_to_routers_nonat_dcn.iteritems(): # Loops over the No NAT group to routers dictionary
        print >>output_file, "/c/slb/group %s" % (farm) # Prints the general group configuration
        print >>output_file, "        ipver v4"
        print >>output_file, "        type wanlink"
        if farm in global_variables.farm_parameters_dcn.keys():
            print >>output_file, "        metric %s" % (global_variables.farm_parameters_dcn[farm][0])
        for server in servers: # Loops over the real servers in the No NAT farm
            for nonat_user_wl_ip, nonat_user_wl_name in global_variables.user_new_wl_names_dcn.iteritems(): # Loop over the user chosen WL IPs and names
                add_servers_to_nonat_group_fnc(nonat_user_wl_ip, nonat_user_wl_name) # Executes the function that adds the reals to the group
            for nonat_orig_wl_ip, nonat_orig_wl_name in global_variables.user_equal_wl_names_dcn.iteritems():
                add_servers_to_nonat_group_fnc(nonat_orig_wl_ip, nonat_orig_wl_name) # Executes the function that adds the reals to the group

    for farm in global_variables.all_farms_lst: # Loops over the list of farms
        if farm not in global_variables.group_to_routers_all_dcn.keys(): # If the farm has no servers, prints the group with no servers
            print >>output_file, "/c/slb/group %s" % (farm)
            print >>output_file, "        ipver v4"
            print >>output_file, "        type wanlink"

    #####################################
    #### Groups Creation Section End ####
    #####################################

    ############################################################
    #### Default Farm, SLB Ports and DNS VIPs Section Start ####
    ############################################################

    for line in lp_to_lpng: # Loops over the LP configuration
        if "farms default-farm set" in line:
            default_farm = global_variables.find_fnc( line, '-fn "', '"' ) # Finds the default farm
            if default_farm == 'error': # If no double quotes in the default farm
                default_farm = global_variables.find_fnc( line, '-fn ', ' ' ) # Finds the default farm again
            for unsupported_char, supported_char in global_variables.special_characters_dcn.iteritems():
                default_farm = default_farm.replace ('%s' % (unsupported_char), "%s" % (supported_char))
            if default_farm not in global_variables.default_farm_lst:
                global_variables.default_farm_lst.append(default_farm)

    ###                                  ###
    #    Default Farm Selection Section    #
    ###                                  ###

        ##                                                                                                 ##
        #    This is a section used to prompt the user to select the default farm for the default filter    #
        #    This section will be shown to the user only if the LP's default farms are different            #
        ##                                                                                                 ##

    default_farm_equal_status = global_variables.all_same(global_variables.default_farm_lst) # Checks is all default farms are the same
    if default_farm_equal_status == False: # If all default farms are not the same
        return render_template('default_filter.html', title='Default Filter', default_group_lst=global_variables.default_group_lst)
    else:
        return redirect('/page5')

@app.route('/page4', methods=['GET','POST'])
@app.route('/page5', methods=['GET','POST'])
def page4():

    def print_dummy_slb_fnc(dns_local_ip, dns_dummy_vip, gslb_network_id):
        '''Prints dummy real server, group and virt.
        Takes the DNS rule local IP, DNS dummy VIP and GSLB network ID as arguments.
        This fucntion is used for cases where Alteon needs to respond to DNS queries with the local IP.
        IP range 169.254.0.1 to 169.254.7.254 is used for the dummy VIP.
        IP 169.254.254.253 is used for the dummy local real server and IP 169.254.254.254 is used for the dummy WL real server.
        '''
        if global_variables.dummy_status == 0:
            print >>output_file, "/c/slb/real Dummy_Local_Srv"
            print >>output_file, "        ena"
            print >>output_file, "        ipver v4"
            print >>output_file, "        rip 169.254.254.253"
            print >>output_file, "        health NoCheck"
            print >>output_file, '        name "Dummy Real for DNS Resolution"'
            print >>output_file, "/c/slb/real Dummy_WL"
            print >>output_file, "        ena"
            print >>output_file, "        ipver v4"
            print >>output_file, "        rip 169.254.254.254"
            print >>output_file, "        type wanlink"
            print >>output_file, "        health NoCheck"
            print >>output_file, '        name "Dummy WL for DNS Resolution"'
            print >>output_file, "/c/slb/group Dummy_Local_GRP"
            print >>output_file, "        ipver v4"
            print >>output_file, "        add Dummy_Local_Srv"
            print >>output_file, '        name "Dummy Group for DNS Resolution"'

        print >>output_file, "/c/slb/virt Local_%s" % (dns_local_ip)
        print >>output_file, "        ena"
        print >>output_file, "        ipver v4"
        print >>output_file, "        vip %s" % (dns_dummy_vip)
        print >>output_file, "        nat %s" % (dns_local_ip)
        print >>output_file, "        rtsrcmac ena"
        print >>output_file, '        vname "Dummy VIP for IP %s"' % (dns_local_ip)
        print >>output_file, '        dname "inherit"'
        print >>output_file, '        wanlink "Dummy_WL"'
        print >>output_file, "/c/slb/virt Local_%s/service 1234 basic-slb" % (dns_local_ip)
        print >>output_file, '        name "Dummy Service for DNS Resolution"'
        print >>output_file, "        group Dummy_Local_GRP"
        print >>output_file, "        rport 1234"

        print >>output_file, "/c/slb/gslb/network %s" % (gslb_network_id)
        print >>output_file, "        ena"
        print >>output_file, "        addvirt Local_%s 65535" % (dns_local_ip)
        global_variables.nonat_gslb_nets_lst.append(gslb_network_id)

    def create_smartat_local_range(nat_type):
        '''This function is used to check if the No NAT local IP range includes unusable addresses.
        We loop over all local IPs, then we check against the dictionary that includes all unusable IPs.
        If we find that an unusable IP is in the local IP range, we remove it.
        We then create the repsective local IP network class.
        The function takes the NAT type as an argument.
        '''
        smartnat_local_range_new_lst1 = [] # Creates No NAT local IPs lists # ---->
                                      # These lists are then used to hold to usable local IPs for Smart NAT entry
                                      # Usable local IPs include any IP which is not network, broadcast, interface IP or peer interface IP
        smartnat_local_range_new_lst2 = []
        smartnat_local_range_new_lst3 = []
        smartnat_local_range_new_lst4 = []
        smartnat_local_range_new_lst5 = []
        smartnat_local_range_new_lst6 = []
        smartnat_local_range_new_lst7 = []
        smartnat_local_range_lst_idx = 0
        smartnat_local_nwclss_net_id = 0
        smartnat_local_loop_status = ""
        for x, smartnat_local_addr in enumerate(smartnat_localip_range): # Loop over the local IPs list
            if smartnat_local_addr not in global_variables.own_addresses_lst: # If the local IP is not in the unsupported IPs list
                smartnat_local_range_new_lst1.append(smartnat_local_addr) # We add it to the range of supported addresses
                if x == len(smartnat_localip_range) - 1: # If we're in the end of the local IPs list, we mark it as last
                    smartnat_local_loop_status = "last"
            else: # If the local IP is in the unsupported IPs list
                smartnat_local_range_lst_idx = x + 1 # We increment the last list index by 1 and break the loop
                break
        if smartnat_local_loop_status != "last": # We check if we're in the end of the local IPs list and if not, continue
            for x, smartnat_local_addr in enumerate(smartnat_localip_range[smartnat_local_range_lst_idx:]): # Loop again over the local IPs list, strating from the last non looped index
                if smartnat_local_addr not in global_variables.own_addresses_lst: # If the local IP is not in the unsupported IPs list
                    smartnat_local_range_new_lst2.append(smartnat_local_addr) # We add it to the range of supported addresses
                    if smartnat_local_range_lst_idx + x == len(smartnat_localip_range) - 1: # If we're in the end of the local IPs list, we mark it as last
                        smartnat_local_loop_status = "last"
                else: # If the local IP is in the unsupported IPs list
                    smartnat_local_range_lst_idx = x + smartnat_local_range_lst_idx + 1 # We increment the last list index by 1 and break the loop
                    break
        if smartnat_local_loop_status != "last": # Repeat the same logic again as per the amount of unsupported IPs + 1
            for x, smartnat_local_addr in enumerate(smartnat_localip_range[smartnat_local_range_lst_idx:]):
                if smartnat_local_addr not in global_variables.own_addresses_lst:
                    smartnat_local_range_new_lst3.append(smartnat_local_addr)
                    if smartnat_local_range_lst_idx + x == len(smartnat_localip_range) - 1:
                        smartnat_local_loop_status = "last"
                else:
                    smartnat_local_range_lst_idx = x + smartnat_local_range_lst_idx + 1
                    break
        if smartnat_local_loop_status != "last":
            for x, smartnat_local_addr in enumerate(smartnat_localip_range[smartnat_local_range_lst_idx:]):
                if smartnat_local_addr not in global_variables.own_addresses_lst:
                    smartnat_local_range_new_lst4.append(smartnat_local_addr)
                    if smartnat_local_range_lst_idx + x == len(smartnat_localip_range) - 1:
                        smartnat_local_loop_status = "last"
                else:
                    smartnat_local_range_lst_idx = x + smartnat_local_range_lst_idx + 1
                    break
        if smartnat_local_loop_status != "last":
            for x, smartnat_local_addr in enumerate(smartnat_localip_range[smartnat_local_range_lst_idx:]):
                if smartnat_local_addr not in global_variables.own_addresses_lst:
                    smartnat_local_range_new_lst5.append(smartnat_local_addr)
                    if smartnat_local_range_lst_idx + x == len(smartnat_localip_range) - 1:
                        smartnat_local_loop_status = "last"
                else:
                    smartnat_local_range_lst_idx = x + smartnat_local_range_lst_idx + 1
                    break
        if smartnat_local_loop_status != "last":
            for x, smartnat_local_addr in enumerate(smartnat_localip_range[smartnat_local_range_lst_idx:]):
                if smartnat_local_addr not in global_variables.own_addresses_lst:
                    smartnat_local_range_new_lst6.append(smartnat_local_addr)
                    if smartnat_local_range_lst_idx + x == len(smartnat_localip_range) - 1:
                        smartnat_local_loop_status = "last"
                else:
                    smartnat_local_range_lst_idx = x + smartnat_local_range_lst_idx + 1
                    break
        if smartnat_local_loop_status != "last":
            for x, smartnat_local_addr in enumerate(smartnat_localip_range[smartnat_local_range_lst_idx:]):
                if smartnat_local_addr not in global_variables.own_addresses_lst:
                    smartnat_local_range_new_lst7.append(smartnat_local_addr)

        if nat_type == "SNN":
            smartnat_local_nwclss_id = global_variables.locl_snn_nwclss_id
        else:
            smartnat_local_nwclss_id = global_variables.locl_snd_nwclss_id
        if smartnat_local_range_new_lst1: # If the first supported local IP list is not empty
            if smartnat_local_nwclss_net_id == 0: # We check if the net ID is 0, this way we know that we didn't yet create the network class
                print >>output_file, "/c/slb/nwclss %s_Local_%s" % (nat_type, smartnat_local_nwclss_id) # We then create the general network class configuration
                print >>output_file, '        type "address"'
            print >>output_file, "/c/slb/nwclss %s_Local_%s/network %s" % (nat_type, smartnat_local_nwclss_id, smartnat_local_nwclss_net_id) # We create the first net
            print >>output_file, "        net range %s %s include" % (smartnat_local_range_new_lst1[0], smartnat_local_range_new_lst1[-1])
            smartnat_local_nwclss_net_id += 1 # We increment the net ID
        if smartnat_local_range_new_lst2: # If the 2nd supported local IP list is not empty
            if smartnat_local_nwclss_net_id == 0: # We repeat the same logic for all local IPs lists
                print >>output_file, "/c/slb/nwclss %s_Local_%s" % (nat_type, smartnat_local_nwclss_id)
                print >>output_file, '        type "address"'
            print >>output_file, "/c/slb/nwclss %s_Local_%s/network %s" % (nat_type, smartnat_local_nwclss_id, smartnat_local_nwclss_net_id)
            print >>output_file, "        net range %s %s include" % (smartnat_local_range_new_lst2[0], smartnat_local_range_new_lst2[-1])
            smartnat_local_nwclss_net_id += 1
        if smartnat_local_range_new_lst3:
            if smartnat_local_nwclss_net_id == 0:
                print >>output_file, "/c/slb/nwclss %s_Local_%s" % (nat_type, smartnat_local_nwclss_id)
                print >>output_file, '        type "address"'
            print >>output_file, "/c/slb/nwclss %s_Local_%s/network %s" % (nat_type, smartnat_local_nwclss_id, smartnat_local_nwclss_net_id)
            print >>output_file, "        net range %s %s include" % (smartnat_local_range_new_lst3[0], smartnat_local_range_new_lst3[-1])
            smartnat_local_nwclss_net_id += 1
        if smartnat_local_range_new_lst4:
            if smartnat_local_nwclss_net_id == 0:
                print >>output_file, "/c/slb/nwclss %s_Local_%s" % (nat_type, smartnat_local_nwclss_id)
                print >>output_file, '        type "address"'
            print >>output_file, "/c/slb/nwclss %s_Local_%s/network %s" % (nat_type, smartnat_local_nwclss_id, smartnat_local_nwclss_net_id)
            print >>output_file, "        net range %s %s include" % (smartnat_local_range_new_lst4[0], smartnat_local_range_new_lst4[-1])
            smartnat_local_nwclss_net_id += 1
        if smartnat_local_range_new_lst5:
            if smartnat_local_nwclss_net_id == 0:
                print >>output_file, "/c/slb/nwclss %s_Local_%s" % (nat_type, smartnat_local_nwclss_id)
                print >>output_file, '        type "address"'
            print >>output_file, "/c/slb/nwclss %s_Local_%s/network %s" % (nat_type, smartnat_local_nwclss_id, smartnat_local_nwclss_net_id)
            print >>output_file, "        net range %s %s include" % (smartnat_local_range_new_lst5[0], smartnat_local_range_new_lst5[-1])
            smartnat_local_nwclss_net_id += 1
        if smartnat_local_range_new_lst6:
            if smartnat_local_nwclss_net_id == 0:
                print >>output_file, "/c/slb/nwclss %s_Local_%s" % (nat_type, smartnat_local_nwclss_id)
                print >>output_file, '        type "address"'
            print >>output_file, "/c/slb/nwclss %s_Local_%s/network %s" % (nat_type, smartnat_local_nwclss_id, smartnat_local_nwclss_net_id)
            print >>output_file, "        net range %s %s include" % (smartnat_local_range_new_lst6[0], smartnat_local_range_new_lst6[-1])
            smartnat_local_nwclss_net_id += 1
        if smartnat_local_range_new_lst7:
            if smartnat_local_nwclss_net_id == 0:
                print >>output_file, "/c/slb/nwclss %s_Local_%s" % (nat_type, smartnat_local_nwclss_id)
                print >>output_file, '        type "address"'
            print >>output_file, "/c/slb/nwclss %s_Local_%s/network %s" % (nat_type, smartnat_local_nwclss_id, smartnat_local_nwclss_net_id)
            print >>output_file, "        net range %s %s include" % (smartnat_local_range_new_lst7[0], smartnat_local_range_new_lst7[-1]) 

    if request.path == '/page4':
        default_group = str(request.form['default_group'])

    else: # If all default farms are the same, we will use the default farm for the default filter and only present the below note for the user
        default_group = global_variables.default_farm_lst[0] # Creates a variable which is the default farm bame, will be used later on the default filter

    ###                     ###
    #    SLB Ports Section    #
    ###                     ###

        ##                                                                                                              ##
        #    This is a section used to create the SLB ports configuration and enable filter processing                   #
        #    In this section we loop over all of the ports that was chosen by the user in the beginning of the script    #
        #    We then use these ports when creating the SLB ports configuration                                           #
        ##                                                                                                              ##

    for port in allports: # Loops over the list of all user chosen ports
        print >>output_file, '/c/slb/port "%s"' % (port) # Prints the SLB ports configuration
        print >>output_file, "        filt ena"

    for line in lp_to_lpng: # Loops over the LP configuration

    ###                    ###
    #    DNS VIPs Section    #
    ###                    ###

        ##                                                                                                                       ##
        #    This is a section used to create the DNS VIPs configuration                                                          #
        #    In this section we look for the DNS VIPs in the LP configuration and print the corresponding Alteon configuration    #
        ##                                                                                                                       ##

        if "lp dns virtual-ip create" in line:
            dns_vip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the DNS VIP
            print >>output_file, "/c/slb/gslb/dnsresvip DnsResp%s,DnsResp%s" % (global_variables.dns_vip_id1, global_variables.dns_vip_id2) # Prints the DNS VIP configuration
            print >>output_file, "        ipver v4"
            print >>output_file, "        vip %s" % (dns_vip[0])
            print >>output_file, "        ena"
            print >>output_file, "        rtsrcmac ena"
            if dns_vip[0] not in global_variables.own_addresses_lst:
                global_variables.own_addresses_lst.append(dns_vip[0])
            global_variables.dns_vip_id1 += 2 # used to increment the first DNS VIP ID
            global_variables.dns_vip_id2 += 2 # Used to increment the second DNS VIP ID

    ##########################################################
    #### Default Farm, SLB Ports and DNS VIPs Section End ####
    ##########################################################

    #################################
    #### Smart NAT Section Start ####
    #################################

    for line in lp_to_lpng: # Loops over the LP configuration

    ###                                          ###
    #    Smart NAT Configuration - Main Section    #
    ###                                          ###

        ##                                                                                           ##
        #    This is the main section used to configure all of the Smart NAT configuration            #
        #    In this section, we fine the Smart NAT configuration and print the Alteon equivalent     #
        #                                                                                             #
        #    Rules:                                                                                   #
        #                                                                                             #
        #    1.) We configure the following Smart NAT types:                                          #
        #        a. Dynamic NAT                                                                       #
        #        b. Static NAT                                                                        #
        #        c. No NAT                                                                            #
        #        d. Static PAT (using virts)                                                          #
        #    2.) On dynamic NAT, we treat the following loca IPs as "any" in Alteon:                  #
        #        a. 0.0.0.0                                                                           #
        #        b. 0.0.0.1                                                                           #
        #        c. 1.0.0.0                                                                           #
        #        d. 1.0.0.1                                                                           #
        #    3.) On No NAT, we check the if the local IP range has the following IP addresses:        #
        #        a. Network address of any network on the LP                                          #
        #        b. Broadcast address of any network on the LP                                        #
        #        c. Any interface IP on the LP                                                        #
        #        d. Any peer interface IP on the LP                                                   #
        #        The above IP addresses are not supported as local IPs in Smart NAT entry             #
        #        If we find them, we remove them and create the network class without them            #
        ##                                                                                           ##

    ###                                 ###
    #    Smart NAT Dynamic NAT Section    #
    ###                                 ###

        ##                                                                          ##
        #    This section is used to find and configure the Smart NAT dynamic NAT    # 
        ##                                                                          ##

        if "smartnat dynamic-nat" in line:
            find_snd_ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds all relevant IP addresses (local from, local to, WAN link, NAT)
            if find_snd_ip[0] == find_snd_ip[1]: # If the "Local IP From" is the same as the "Local IP To", uses mode address
                snd_local_ip = "%s 255.255.255.255" % (find_snd_ip[0]) # The local IP
            elif find_snd_ip[0] == '0.0.0.0': # If the "Local IP From" is one of the below options, we use "any" in Alteon
                snd_local_ip = 'any'
            elif find_snd_ip[0] == '0.0.0.1':
                snd_local_ip = 'any'
            elif find_snd_ip[0] == '1.0.0.0':
                snd_local_ip = 'any'
            elif find_snd_ip[0] == '1.0.0.1':
                snd_local_ip = 'any'
            elif find_snd_ip[0] == find_snd_ip[1]:
                snd_local_ip = "%s 255.255.255.255" % (find_snd_ip[0])
            else: # If the "Local IP From" is not one of the above, we define a network class for the local IP range
                smartnat_localip_range = global_variables.ipRange_fnc(find_snd_ip[0], find_snd_ip[1]) # Finds all IP addresses in the local IP range 
                global_variables.locl_snd_nwclss_id += 1
                global_variables.smartnat_local_nwclss_id += 1
                create_smartat_local_range("SND") # Executes the function that creates the network classes
                snd_local_ip = "SND_Local_%s" % (global_variables.locl_snd_nwclss_id) # This is the local IP network class name

            wan_ip_nat = find_snd_ip[2] # Defines the WAN link IP
            if wan_ip_nat in global_variables.user_new_wl_names_dcn: # Loops for the WAN link IP in the user chosen WL names dictionary in order to map it to the WAN link name
                if len(global_variables.user_new_wl_names_dcn[wan_ip_nat]) > 0:
                    wanlink = global_variables.user_new_wl_names_dcn[wan_ip_nat][0] # We then define the WAN link name to be associated with the Smart NAT entry
            elif wan_ip_nat in global_variables.duplicate_wls_dcn: # If the WAN link IP is not in the user chosen WL names, we loop in the single WL names dictionary to find it
                if len(global_variables.duplicate_wls_dcn[wan_ip_nat]) > 0:
                    wanlink = global_variables.duplicate_wls_dcn[wan_ip_nat][0] # We then define the WAN link name to be associated with the Smart NAT entry

            global_variables.smartnat_id += 1 # Smart NAT ID will be incremented by 1 for each entry
            print >>output_file, "/c/slb/lp/nat %s" % (global_variables.smartnat_id) # Prints the Smart NAT dynamic NAT configuration 
            print >>output_file, "        type dynamic"
            print >>output_file, "        wanlink %s" % (wanlink)
            print >>output_file, "        locladd %s" % (snd_local_ip)
            print >>output_file, "        natadd %s 255.255.255.255" % (find_snd_ip[3])

    ###                                ###
    #    Smart NAT Static NAT Section    #
    ###                                ###

        ##                                                                         ##
        #    This section is used to find and configure the Smart NAT static NAT    # 
        ##                                                                         ##

        if "smartnat static-nat" in line:
            find_sns_ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds all relevant IP addresses (local from, local to, WAN link, NAT IP from, NAT IP to)
            if find_sns_ip[0] == find_sns_ip[1]: # If the "Local IP From" is the same as the "Local IP To" and if it is, uses mode address
                sns_local_ip = "%s 255.255.255.255" % (find_sns_ip[0]) # The local IP
                sns_nat_ip = "%s 255.255.255.255" % (find_sns_ip[3]) # The NAT IP
                if find_sns_ip[0] not in global_variables.smart_nat_local_ips_lst: # Appends the local IP to a list with all Smart NAT local IPs # ---->
                                                                  # This is later on used to check if a DNS rule local IP is not in this list and in this case, the DNS rule won't be configured
                    global_variables.smart_nat_local_ips_lst.append("%s" % (find_sns_ip[0]))
            else: # If the "Local IP From" is not the same as the "Local IP To", users mode nwclss
                sns_localip_range = global_variables.ipRange_fnc(find_sns_ip[0], find_sns_ip[1]) # Finds all IP addresses in the local IP range
                for localip in sns_localip_range: # Appends each local IP to a list with all Smart NAT local IPs # ---->
                                                  # This is later on used to check if a DNS rule local IP is not in this list and in this case, the DNS rule won't be configured
                    if localip not in global_variables.smart_nat_local_ips_lst:
                        global_variables.smart_nat_local_ips_lst.append("%s" % (localip))

                current_sns_local_range = "%s_%s" % (find_sns_ip[0], find_sns_ip[1])

                for sns_local_range_key, sns_nwclss_id_value in global_variables.sns_local_range_to_nwclss_dcn.iteritems():
                    if sns_local_range_key == current_sns_local_range:
                       sns_local_ip = sns_nwclss_id_value[0]
                       break
                else:
                    global_variables.locl_sns_nwclss_id += 1 # Increments the local IP network class ID
                    sns_local_ip = "SNS_Local_%s" % (global_variables.locl_sns_nwclss_id) # This is the local IP netowrk class name
                    print >>output_file, "/c/slb/nwclss SNS_Local_%s" % (global_variables.locl_sns_nwclss_id) # Prints the local IP network class
                    print >>output_file, '        type "address"'
                    print >>output_file, "/c/slb/nwclss SNS_Local_%s/network 0" % (global_variables.locl_sns_nwclss_id)
                    print >>output_file, "        net range %s %s include" % (find_sns_ip[0], find_sns_ip[1])

                    sns_local_range_to_nwclss_dcn_key = "%s" % (current_sns_local_range)
                    global_variables.sns_local_range_to_nwclss_dcn.setdefault(sns_local_range_to_nwclss_dcn_key, [])
                    global_variables.sns_local_range_to_nwclss_dcn[sns_local_range_to_nwclss_dcn_key].append('%s' % (sns_local_ip))


                global_variables.nat_sns_nwclss_id += 1 # Increments the NAT IP network class ID
                sns_nat_ip = "SNS_NAT_%s" % (global_variables.nat_sns_nwclss_id) # This is the NAT IP network class
                print >>output_file, "/c/slb/nwclss SNS_NAT_%s" % (global_variables.nat_sns_nwclss_id) # Prints the NAT IP network class
                print >>output_file, '        type "address"'
                print >>output_file, "/c/slb/nwclss SNS_NAT_%s/network 0" % (global_variables.nat_sns_nwclss_id)
                print >>output_file, "        net range %s %s include" % (find_sns_ip[3], find_sns_ip[4])

            wan_ip_nat = find_sns_ip[2] # Defines the WAN link IP, then extracts the WAN link name from the dictionaries
            if wan_ip_nat in global_variables.user_new_wl_names_dcn:
                if len(global_variables.user_new_wl_names_dcn[wan_ip_nat]) > 0:
                    wanlink = global_variables.user_new_wl_names_dcn[wan_ip_nat][0]
            elif wan_ip_nat in global_variables.duplicate_wls_dcn:
                if len(global_variables.duplicate_wls_dcn[wan_ip_nat]) > 0:
                    wanlink = global_variables.duplicate_wls_dcn[wan_ip_nat][0]

            global_variables.smartnat_id += 1 # Increments the Smart NAT ID
            print >>output_file, "/c/slb/lp/nat %s" % (global_variables.smartnat_id) # Prints the Smart NAT static NAT configuration
            print >>output_file, "        type static"
            print >>output_file, "        wanlink %s" % (wanlink)
            print >>output_file, "        locladd %s" % (sns_local_ip)
            print >>output_file, "        natadd %s" % (sns_nat_ip)

    ###                            ###
    #    Smart NAT No NAT Section    #
    ###                            ###

        ##                                                                     ##
        #    This section is used to find and configure the Smart NAT No NAT    # 
        ##                                                                     ##

        if "smartnat no-nat" in line:
            find_snn_ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds all relevant IP addresses (local from, local to and WAN link)
            if find_snn_ip[0] == find_snn_ip[1]: # If the "Local IP From" is the same as the "Local IP To" and if it is, uses mode address
                snn_local_ip = "%s 255.255.255.255" % (find_snn_ip[0]) # The local IP
                if find_snn_ip[0] not in global_variables.smart_nat_local_ips_lst:
                    global_variables.smart_nat_local_ips_lst.append("%s" % (find_snn_ip[0]))
            else: # If the "Local IP From" is not the same as the "Local IP To", users mode nwclss
                smartnat_localip_range = global_variables.ipRange_fnc(find_snn_ip[0], find_snn_ip[1]) # Finds all IP addresses in the local IP range # ---->
                                                                                     # Specifically for No NAT, this is later on used to find if any of these IPs is network, broadcast, interface or peer interface
                for localip in smartnat_localip_range:
                    if localip not in global_variables.smart_nat_local_ips_lst:
                        global_variables.smart_nat_local_ips_lst.append("%s" % (localip))

                global_variables.locl_snn_nwclss_id += 1
                global_variables.smartnat_local_nwclss_id += 1
                create_smartat_local_range("SNN") # Executes the function that creates the network class
                snn_local_ip = "SNN_Local_%s" % (global_variables.locl_snn_nwclss_id) # This is the local IP network class name

            wan_ip_nat = find_snn_ip[2] # Defines the WAN link IP, then extracts the WAN link name from the dictionaries
            if wan_ip_nat in global_variables.user_new_wl_names_dcn:
                if len(global_variables.user_new_wl_names_dcn[wan_ip_nat]) > 0:
                    wanlink = global_variables.user_new_wl_names_dcn[wan_ip_nat][0]
            elif wan_ip_nat in global_variables.duplicate_wls_dcn:
                if len(global_variables.duplicate_wls_dcn[wan_ip_nat]) > 0:
                    wanlink = global_variables.duplicate_wls_dcn[wan_ip_nat][0]

            global_variables.smartnat_id += 1 # Increments the Smart NAT ID
            print >>output_file, "/c/slb/lp/nat %s" % (global_variables.smartnat_id) # Prints the Smart NAT No NAT configuration
            print >>output_file, "        wanlink %s" % (wanlink)
            print >>output_file, "        locladd %s" % (snn_local_ip)

            nonat_port = [int(s) for s in line.split() if s.isdigit()]
            if nonat_port[0] != 0:
                current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                print >>migration_errors, '\033[1m%s\033[0m #Unsupported_flag_option: the following command contains a flag with an unsupported option:' % (current_time)
                print >>migration_errors, '    Command: %s' % (line)
                print >>migration_errors, '    Unsupported flag option: No NAT Destination Port which is not 0.'
                print >>migration_errors, '    Alteon will treat it as 0 (any).'

    ###                                ###
    #    Smart NAT Static PAT Section    #
    ###                                ###

        ##                                                                         ##
        #    This section is used to find and configure the Smart NAT Static PAT    # 
        ##                                                                         ##

        if "smartnat static-pat" in line:
            find_snp_ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds all relevant IP addresses (internal, external, WAN link)
            global_variables.type_group_local_lst.append("%s" % (find_snp_ip[0])) # Populates a list with the internal IPs as objects # ---->
                                                                 # This is later on used to identify that it's a PAT, to create GSLB network of type "group"
            if find_snp_ip[0] not in global_variables.smart_nat_local_ips_lst: # Appends the local IP to a list with all Smart NAT local IPs # ---->
                                                              # This is later on used to check if a DNS rule local IP is not in this list and in this case, the DNS rule won't be configured
                global_variables.smart_nat_local_ips_lst.append("%s" % (find_snp_ip[0]))
            find_snp_ports = [int(s) for s in line.split() if s.isdigit()] # Finds the internal and external ports

            wan_ip_nat = find_snp_ip[1] # Defines the WAN link IP, then extracts the WAN link name from the dictionaries
            if wan_ip_nat in global_variables.user_new_wl_names_dcn:
                if len(global_variables.user_new_wl_names_dcn[wan_ip_nat]) > 0:
                    wanlink = global_variables.user_new_wl_names_dcn[wan_ip_nat][0]
            elif wan_ip_nat in global_variables.duplicate_wls_dcn:
                if len(global_variables.duplicate_wls_dcn[wan_ip_nat]) > 0:
                    wanlink = global_variables.duplicate_wls_dcn[wan_ip_nat][0]

            snp_protocol = global_variables.find_fnc( line, "%s " % (find_snp_ports[0]), " " ) # Finds the PAT protocol
            snp_name = global_variables.find_fnc( line, ' -pn "', '"' ) # Finds the PAT name
            if snp_name == 'error': # If no double quotes, finds it again
                snp_name = global_variables.find_fnc( line, " -pn ", " " )

            snp_real_to_virt_dcn_key = "%s" % (find_snp_ip[0]) # Populates a dictionary with the following values: # ---->
                                                               # The internal IP as a key # ---->
                                                               # The external IP as a value # ---->
                                                               # This is later on used to add the correct virt to the GSLB network
            global_variables.snp_real_to_virt_dcn.setdefault(snp_real_to_virt_dcn_key, [])
            global_variables.snp_real_to_virt_dcn[snp_real_to_virt_dcn_key].append('%s' % (find_snp_ip[2]))

            snp_virt_to_service_dcn_key = "%s" % (find_snp_ip[2]) # Populates a dictionary with the following values: # ---->
                                                                  # The external IP as a key
                                                                  # The external port as a value
                                                                  # This is used later on to print the correct service on the GSLB rule
            global_variables.snp_virt_to_service_dcn.setdefault(snp_virt_to_service_dcn_key, [])
            global_variables.snp_virt_to_service_dcn[snp_virt_to_service_dcn_key].append('%s' % (find_snp_ports[1]))

            print >>output_file, "/c/slb/real Srv_%s" % (find_snp_ip[0]) # Starts printing the real server (the internal IP)
            print >>output_file, "        ena"
            print >>output_file, "        ipver v4"
            print >>output_file, "        rip %s" % (find_snp_ip[0])
            print >>output_file, "        health NoCheck"
            print >>output_file, '        name "PAT Srv %s"' % (find_snp_ip[0])
            print >>output_file, "/c/slb/group Srv_%s" % (find_snp_ip[0]) # Starts printing the group (for the internal IP)
            print >>output_file, "        ipver v4"
            print >>output_file, "        add Srv_%s" % (find_snp_ip[0])
            print >>output_file, '        name "Group 4 PAT Srv %s"' % (find_snp_ip[0])
            print >>output_file, "/c/slb/virt PAT_%s" %  (find_snp_ip[2]) # Starts printing the virt (the external IP)
            print >>output_file, "        ena"
            print >>output_file, "        ipver v4"
            print >>output_file, "        vip %s" % (find_snp_ip[2])
            print >>output_file, "        rtsrcmac ena"
            print >>output_file, '        vname "PAT %s"' % (find_snp_ip[2])
            print >>output_file, '        dname "inherit"'
            print >>output_file, '        wanlink "%s"' % (wanlink) # Associates the WAN link
            if str(find_snp_ports[1]) in global_variables.port_to_service_dcn.keys(): # If the external port is a well-known port, we print the known service
                print >>output_file, "/c/slb/virt PAT_%s/service %s %s" %  (find_snp_ip[2], find_snp_ports[1], global_variables.port_to_service_dcn[str(find_snp_ports[1])])
            else: # If it's not a well-known port, we print >>output_file, "basic-slb"
                print >>output_file, "/c/slb/virt PAT_%s/service %s basic-slb" %  (find_snp_ip[2], find_snp_ports[1])
            if snp_name == 'error':
                print >>output_file, '        name "PAT %s, %s"' % (find_snp_ip[2], find_snp_ports[1])
            else:
                print >>output_file, '        name "PAT %s"' % (snp_name)
            print >>output_file, "        group Srv_%s" % (find_snp_ip[0]) # Assicates the group (the internal IP)
            print >>output_file, "        rport %s" % (find_snp_ports[0]) # Configures the rport (the internal port)
            print >>output_file, "        protocol %s" % (snp_protocol) # Configuration the protocol
            print >>output_file, "        tmout %s" % (max_aging_time)
            if alt_ha_mode == 1 or alt_ha_mode == 2:
                print >>output_file, "        mirror ena"

    ###############################
    #### Smart NAT Section End ####
    ###############################

    #######################################
    #### Network Classes Section Start ####
    #######################################

    for line in lp_to_lpng: # Loops over the LP configuration

    ###                                                ###
    #    Network Classes Configuration - Main Section    #
    ###                                                ###

        ##                                                                                 ##
        #    This is the main section used to find and configure all the network classes    #
        ##                                                                                 ##

        if "classes modify network" in line:
            class_name = global_variables.find_fnc( line, 'setCreate "', '"' ) # Finds the network class name
            if class_name == 'error': # If no double qoutes, finds again
                class_name = global_variables.find_fnc( line, 'setCreate ', ' ' )
            new_class_name = class_name
            for unsupported_char, supported_char in global_variables.special_characters_dcn.iteritems(): 
                new_class_name = new_class_name.replace ('%s' % (unsupported_char), "%s" % (supported_char))
            class_id = global_variables.find_fnc( line, '%s" ' % (class_name), " " ) # Finds the network class ID
            if class_id == 'error': # If not double quotes in the network class name, finds again
                class_id = global_variables.find_fnc( line, '%s ' % (class_name), " " )

            print >>output_file, "/c/slb/nwclss %s" % (new_class_name) # Starts printing the network class general configuration
            print >>output_file, '        type "address"'
            class_mode = global_variables.find_fnc( line, ' -m "', '"' ) # Finds the network class mode
            if class_mode == 'IP Mask': # If the network class mode is "IP Mask"
                class_addr = global_variables.find_fnc( line, " -a ", " " ) # Finds the network class address
                class_mask = global_variables.find_fnc( line, " -s ", " " ) # Finds the network class mask
                print >>output_file, "/c/slb/nwclss %s/network %s" % (new_class_name, class_id) # Starts printing the net, in mode subnet
                print >>output_file, "        net subnet %s %s include" % (class_addr, class_mask)
            elif class_mode == 'IP Range': # If the network class mode is "IP Range"
                class_from = global_variables.find_fnc( line, " -f ", " " ) # Finds the network class range start
                class_to = global_variables.find_fnc( line, " -t ", " " ) # Finds the network class range end
                print >>output_file, "/c/slb/nwclss %s/network %s" % (new_class_name, class_id) # Starts printing the net, in mode range
                print >>output_file, "        net range %s %s include" % (class_from, class_to)

    #####################################
    #### Network Classes Section End ####
    #####################################

    #####################################################
    #### Outbound Policies and Filters Section Start ####
    #####################################################

    ###                                               ###
    #    Outbound Policies and filters - Filters 1-3    #
    ###                                               ###

        ##                                                                                                    ##
        #    This is the section used to configure filters 1-3                                                 #
        #    These filters are used to catch important traffic, so it won't mistakenly match other filters:    #
        #                                                                                                      #
        #    1.) Filter 1 - Catch broadcasts and allow                                                         #
        #    2.) Filter 2 - Catch multicasts and allow                                                         #
        #    3.) Filter 3 - Catch traffic to local networks and allow                                          #
        ##                                                                                                    ##

    print >>output_file, "/c/slb/filt 1" # Starts printing filter 1
    print >>output_file, '        name "Broadcasts"'
    print >>output_file, "        ena"
    print >>output_file, "        action allow"
    print >>output_file, "        ipver v4"
    print >>output_file, "        sip any"
    print >>output_file, "        smask 0.0.0.0"
    print >>output_file, "        dmac ff:ff:ff:ff:ff:ff"
    print >>output_file, "        group 1"
    print >>output_file, "        rport 0"
    print >>output_file, "        vlan any"
    for port in allports: # Loops over all ports list to add all ports
        print >>output_file, "        add %s" % (port)
    print >>output_file, "/c/slb/filt 1/adv"
    print >>output_file, "        cache dis"
    print >>output_file, "        reverse ena"

    print >>output_file, "/c/slb/nwclss Multicast" # Starts printing the multicast network class
    print >>output_file, '        type "address"'
    print >>output_file, "        ipver v4"
    print >>output_file, "/c/slb/nwclss Multicast/network 0"
    print >>output_file, "        net subnet 224.0.0.0 240.0.0.0 include"

    print >>output_file, "/c/slb/filt 2" # Starts printing filter 2
    print >>output_file, '        name "Multicast"'
    print >>output_file, "        ena"
    print >>output_file, "        action allow"
    print >>output_file, "        ipver v4"
    print >>output_file, "        sip any"
    print >>output_file, "        smask 0.0.0.0"
    print >>output_file, "        dip Multicast"
    print >>output_file, "        group 1"
    print >>output_file, "        rport 0"
    print >>output_file, "        vlan any"
    for port in allports: # Loops over all ports list to add all ports
        print >>output_file, "        add %s" % (port)
    print >>output_file, "/c/slb/filt 2/adv"
    print >>output_file, "        cache dis"
    print >>output_file, "        reverse ena"

    print >>output_file, "/c/slb/nwclss Local_Networks" # Starts printing the local networks network class general configuration
    print >>output_file, '        type "address"'
    for subnet, mask in global_variables.subnet_to_mask_dcn.iteritems(): # Loops over the local subnets to mask dictionary
        print >>output_file, "/c/slb/nwclss Local_Networks/net %s" % (global_variables.local_nets_nwclss_net_id) # For each local subnet, prints net
        print >>output_file, "        net subnet %s %s include" % (subnet, mask[0])
        global_variables.local_nets_nwclss_net_id += 1

    print >>output_file, "/c/slb/filt 3" # Starts printing filter 3
    print >>output_file, '        name "Allow Local Networks"'
    print >>output_file, "        ena"
    print >>output_file, "        action allow"
    print >>output_file, "        ipver v4"
    print >>output_file, "        sip any"
    print >>output_file, "        smask 0.0.0.0"
    print >>output_file, "        dip Local_Networks"
    print >>output_file, "        group 1"
    print >>output_file, "        rport 0"
    print >>output_file, "        vlan any"
    for port in allports: # Loops over all ports list to add all ports
        print >>output_file, "        add %s" % (port)
    print >>output_file, "/c/slb/filt 3/adv"
    print >>output_file, "        cache dis"
    print >>output_file, "        reverse ena"

    for line in lp_to_lpng: # Loops over the LP configuration

    ###                                                                ###
    #    Outbound Policies and filters - Finding the services classes    #
    ###                                                                ###

        ##                                                                    ##
        #    This is the section used to find the services classes             #
        #    In this section, we find only the basic services and or-groups    #
        #    They're later on used on the filters                              #
        ##                                                                    ##

        if "classes modify service basic" in line:
            basic_service_name = global_variables.find_fnc( line, ' setCreate "', '"' ) # Finds the basic service name
            if basic_service_name == 'error': # If no double quotes, find again
                basic_service_name = global_variables.find_fnc( line, " setCreate ", " " )
            basic_service_protocol = global_variables.find_fnc( line, " -pr ", " " ) # Finds the basic service protocol
            basic_service_dport = global_variables.find_fnc( line, " -dp ", " " ) # Finds the basic service destination port
            user_defined_basic_services_key = "%s" % (basic_service_name) # Populates a dictionary with the following values: # ---->
                                                                              # Basic services name as a key # ---->
                                                                              # A list containing the protocol and dport as values # ---->
                                                                              # This is later on used to configure the dport on the filters
            global_variables.user_defined_basic_services_dcn.setdefault(user_defined_basic_services_key, [])
            global_variables.user_defined_basic_services_dcn[user_defined_basic_services_key].append('%s' % (basic_service_protocol))
            global_variables.user_defined_basic_services_dcn[user_defined_basic_services_key].append('%s' % (basic_service_dport))

    ###                                                ###
    #    Outbound Policies and filters - Main Section    #
    ###                                                ###

        ##                                                                                                         ##
        #    This is the main section used to find the outbound policies and print the filters                      #
        #    In this section, we find the outbound policies configuraiton and we print the filters accordingly      #
        #                                                                                                           #
        #    Rules:                                                                                                 #
        #                                                                                                           #
        #    1.) Even if the policies we not ordered in the LP configuration, we print them in the correct order    #
        #    2.) We always start with filter index 101                                                              #
        #        This means that the original policy ID will have its index incremented by 100 on the Alteon        #
        #        This is because the first filters (1-3) are for the broadcasts, multicasts and local networks      #
        #    3.) We convert only policies with basic services, or-groups or no service                              #
        #        We will convert the following services:                                                            #
        #        a. User defined basic services                                                                     #
        #        b. Default system basic services                                                                   #
        #        c. Default system or-groups                                                                        #
        #                                                                                                           #
        #        We will not convert user defined or-groups and any and-groups                                      #
        #    4.) For policies with services that have more than one service port which is not continuous:           #
        #        a. We duplicate the filter per the amount of services                                              #
        #        b. We append the following to the end of the original policy name                                  #
        #           i. An underscore ("_")                                                                          #
        #           ii. An incermenting number (starting from 1) to the end of the original policy name             #
        #        c. We retain the original gap between the policies                                                 #
        ##                                                                                                         ##

        if "modify-policy-table" in line:
            policy_id = global_variables.find_fnc( line, " -i ", " " ) # Finds the policy ID
            key_outbound_pols_dcn = "%s" % (line) # Populates a dictionary with the following values: # ---->
                                                  # The complete policy configuration line as a key # ---->
                                                  # The policy ID as a value # ---->
                                                  # This is used later on to sort the policies based on their IDs
            global_variables.outbound_pols_dcn.setdefault(key_outbound_pols_dcn, [])
            global_variables.outbound_pols_dcn[key_outbound_pols_dcn].append('%s' % (policy_id))
            int_outbound_pols_dcn = {k:int(v[0]) for k, v in global_variables.outbound_pols_dcn.iteritems()} # Converts the values to integers
            sorted_int_outbound_pols_dcn = sorted(int_outbound_pols_dcn.items(), key=operator.itemgetter(1)) # Converts the dictionary to a list of tuples and sorts it

    for cmd, pol_id in sorted_int_outbound_pols_dcn: # Loops over the sorted policy configuration

    ###                                     ###
    #    Find Policy Configuration Section    #
    ###                                     ###

        policy_id = global_variables.find_fnc( cmd, " -i ", " " ) # Finds the policy ID
        policy_id = int(policy_id) # Converts the policy ID to an integer
        new_policy_id = policy_id - global_variables.static_pol_id # Not in use anymore
        policy_name = global_variables.find_fnc( cmd, "setCreate ", " -i" ) # Finds the policy name
        policy_name = policy_name.replace ('"', "")
        policy_dst = global_variables.find_fnc( cmd, ' -dst "', '" ' ) # Finds policy destination port
        if policy_dst == 'error': # If no double quotes, finds again
            policy_dst = global_variables.find_fnc( cmd, ' -dst ', ' ' )
            if policy_dst == 'error': # If no destination port, it's "any"
                policy_dst = 'any'
        if policy_dst != 'error':
            for unsupported_char, supported_char in global_variables.special_characters_dcn.iteritems():
                policy_dst = policy_dst.replace ('%s' % (unsupported_char), "%s" % (supported_char))
        policy_src = global_variables.find_fnc( cmd, ' -src "', '" ' ) # Finds the policy source port
        if policy_src == 'error': # If no double quotes, find again
            policy_src = global_variables.find_fnc( cmd, ' -src ', ' ' )
            if policy_src == 'error': # If not source port, it's "any"
                policy_src = 'any'
        if policy_src != 'error':
            for unsupported_char, supported_char in global_variables.special_characters_dcn.iteritems():
                policy_src = policy_src.replace ('%s' % (unsupported_char), "%s" % (supported_char))
        policy_fc = global_variables.find_fnc( cmd, ' -fc "', '"' ) # Finds the policy farm flow
        if policy_fc == 'error': # If no double quotes, find again
            policy_fc = global_variables.find_fnc( cmd, " -fc ", " " )
        if policy_fc != 'error': # If the farm flow exists
            policy_farm = global_variables.farm_flow_to_farm_dcn[policy_fc][0] # Extracts the associated farm, will be used as the group in the filter
        else: # If no farm flow is associated to the policy
            policy_farm = default_group # Uses the deafult group and will associate it to the filter
        policy_service_type = global_variables.find_fnc( cmd, ' -pt "', '"' ) # Finds the policy services type
        if policy_service_type == "Basic Filter" or policy_service_type == "OR Group": # If it's "Basic Filter" or "OR Group"
            policy_service = global_variables.find_fnc( cmd, ' -p "', '"' ) # Finds the policy service
            if policy_service == 'error': # If no double quotes, find again
                policy_service = global_variables.find_fnc( cmd, ' -p ', ' ' )
        policy_operational_status = global_variables.find_fnc( cmd, ' -os ', ' ' ) # Finds the policy operational status

    ###                         ###
    #    Print Filters Section    #
    ###                         ###

        def print_filt_fnc(proto):
            '''Prints the filter configuration.
            Takes the service protocol as an argument.
            '''
            print >>output_file, "/c/slb/filt %s" % (new_policy_id2) # Starts printing the filter
            if ((' -pt "Basic Filter"' in cmd or ' -pt "OR Group"' in cmd) and proto == "single") or (proto == "noService"):
                print >>output_file, '        name "%s"' % (policy_name)
            elif (' -pt "Basic Filter"' in cmd or ' -pt "OR Group"' in cmd):
                print >>output_file, '        name "%s_%s"' % (policy_name, filt_name_index)
            if policy_operational_status == 'error':
                print >>output_file, "        ena"
            else:
                print >>output_file, "        dis"
            print >>output_file, "        action outbound-llb"
            print >>output_file, "        ipver v4"
            find_policy_src_ip = re.findall( r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",policy_src)
            if len(find_policy_src_ip) == 1: # If policy source is an IP address, use "sip" and "smask"
                print >>output_file, "        sip %s" % (find_policy_src_ip[0])
                print >>output_file, "        smask 255.255.255.255"
            else: # If policy source is a network class, use "sip" without "smask"
                print >>output_file, "        sip %s" % (policy_src)
            find_policy_dst_ip = re.findall( r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",policy_dst)
            if len(find_policy_dst_ip) == 1:
                print >>output_file, "        dip %s" % (find_policy_dst_ip[0])
                print >>output_file, "        dmask 255.255.255.255"
            else:
                print >>output_file, "        dip %s" % (policy_dst)
            if (' -pt "Basic Filter"' in cmd or ' -pt "OR Group"' in cmd) and proto == "single": # Services conditions for single services
                if policy_service_type == "Basic Filter" and policy_service == "icmp":
                    print >>output_file, "        proto icmp"
                elif policy_service_type == "Basic Filter" and policy_service == "tcp":
                    print >>output_file, "        proto tcp"
                elif policy_service_type == "Basic Filter" and policy_service == "udp":
                    print >>output_file, "        proto udp"
                elif policy_service_type == "Basic Filter" and policy_service == "sctp":
                    print >>output_file, "        proto 132"
                elif policy_service_type == "Basic Filter" and policy_service != "ip":
                    if policy_service in global_variables.basic_services_dcn.keys():
                        print >>output_file, "        proto %s" % (global_variables.basic_services_dcn[policy_service][0])
                        print >>output_file, "        dport %s" % (global_variables.basic_services_dcn[policy_service][1])
                    elif policy_service in global_variables.user_defined_basic_services_dcn.keys():
                        if global_variables.user_defined_basic_services_dcn[policy_service][0] == "TCP":
                            print >>output_file, "        proto tcp"
                        elif global_variables.user_defined_basic_services_dcn[policy_service][0] == "UDP":
                            print >>output_file, "        proto udp"
                        print >>output_file, "        dport %s" % (global_variables.user_defined_basic_services_dcn[policy_service][1])
            elif (' -pt "Basic Filter"' in cmd or ' -pt "OR Group"' in cmd): # If services have multiple ports
                print >>output_file, "        proto %s" % (proto)
                print >>output_file, "        dport %s" % (port_service)
            print >>output_file, "        group %s" % (policy_farm)
            print >>output_file, "        rport 0"
            print >>output_file, "        vlan %s" % (ingress_vlan)
            for port in ingress_ports:
                print >>output_file, "        add %s" % (port)
            print >>output_file, "/c/slb/filt %s/adv" % (new_policy_id2)
            if policy_farm in global_variables.orig_dm_dcn.keys():
                if global_variables.orig_dm_dcn[policy_farm][0] == "Hashing" or global_variables.orig_dm_dcn[policy_farm][0] == "Layer-3 Hashing":
                    print >>output_file, "        thash both"
                elif global_variables.orig_dm_dcn[policy_farm][0] == "Destination IP Hashing":
                    print >>output_file, "        thash dip32"
            print >>output_file, "        rtsrcmac ena"
            print >>output_file, "        reverse ena"
            if alt_ha_mode == 1 or alt_ha_mode == 2:
                print >>output_file, "        mirror ena"
            if proximity_mode == 'Full Proximity Outbound' or proximity_mode == 'Full Proximity Both':
                print >>output_file, "        prximity ena"
            print >>output_file, "/c/slb/filt %s/adv/layer7" % (new_policy_id2)
            print >>output_file, "        ftpa ena"
            if policy_farm in global_variables.orig_dm_dcn.keys():
                if global_variables.orig_dm_dcn[policy_farm][0] != "Hashing" and global_variables.orig_dm_dcn[policy_farm][0] != "Layer-3 Hashing" and global_variables.orig_dm_dcn[policy_farm][0] != "Source IP Hashing" and global_variables.orig_dm_dcn[policy_farm][0] != "Destination IP Hashing":
                    print >>output_file, "/c/slb/filt %s/adv/redir" % (new_policy_id2)
                    print >>output_file, "        pbind e"



        if "modify-policy-table" in cmd and "-i 0" not in cmd and (' -pt "Basic Filter"' in cmd or ' -pt "OR Group"' in cmd): # If the policy has a basic filter or an OR group
            if "%s" % (policy_service) in global_variables.basic_multi_services_ports_dcn.keys(): # If the service in the policy is one of the system default basic filters with more than one service port which is not continuous
                for x, port_service in enumerate(global_variables.basic_multi_services_ports_dcn[policy_service]): # Loops over the ports of the multi service basic filter
                    filt_name_index = global_variables.basic_multi_services_ports_dcn[policy_service].index('%s' % (port_service))
                    filt_name_index = filt_name_index + 1
                    new_policy_id2 = policy_id + global_variables.new_filt_id_diff + global_variables.multi_pol_id
                    diff_orig = policy_id - global_variables.last_orig_pol_id
                    diff_new = new_policy_id2 - global_variables.last_new_pol_id
                    new_policy_id2 = global_variables.last_new_pol_id + diff_orig + global_variables.multi_pol_id
                    print_filt_fnc(global_variables.basic_multi_services_protocols_dcn[policy_service]) # Executes the print filter fuction
                    global_variables.multi_pol_id = 1
                    global_variables.last_orig_pol_id = policy_id
                    global_variables.last_new_pol_id = new_policy_id2
                    last = len(global_variables.basic_multi_services_ports_dcn[policy_service]) - 1
                    if x == last:
                        global_variables.multi_pol_id = 0
            elif "%s" % (policy_service) in global_variables.or_groups_multi_services_ports_dcn.keys(): # If the service in the policy is one of the system default OR-Groups with more than one service port which is not continuous
                for x, port_service in enumerate(global_variables.or_groups_multi_services_ports_dcn[policy_service]): # Loops over the ports of the multi service OR-Group
                    filt_name_index = global_variables.or_groups_multi_services_ports_dcn[policy_service].index('%s' % (port_service))
                    filt_name_index = filt_name_index + 1
                    new_policy_id2 = policy_id + global_variables.new_filt_id_diff + global_variables.multi_pol_id
                    diff_orig = policy_id - global_variables.last_orig_pol_id
                    diff_new = new_policy_id2 - global_variables.last_new_pol_id
                    new_policy_id2 = global_variables.last_new_pol_id + diff_orig + global_variables.multi_pol_id
                    print_filt_fnc(global_variables.or_groups_multi_services_protocols_dcn[policy_service]) # Executes the print filter fuction
                    global_variables.multi_pol_id = 1
                    global_variables.last_orig_pol_id = policy_id
                    global_variables.last_new_pol_id = new_policy_id2
                    last = len(global_variables.or_groups_multi_services_ports_dcn[policy_service]) - 1
                    if x == last:
                        global_variables.multi_pol_id = 0
            else: # If the service in the policy is one of the system default single service basic filters or one of the user define single service basic filters
                diff_orig = policy_id - global_variables.last_orig_pol_id
                new_policy_id2 = policy_id + global_variables.new_filt_id_diff
                diff_new = new_policy_id2 - global_variables.last_new_pol_id
                if diff_orig != diff_new:
                    new_policy_id2 = global_variables.last_new_pol_id + diff_orig
                print_filt_fnc("single") # Executes the print filter fuction
                global_variables.last_orig_pol_id = policy_id
                global_variables.last_new_pol_id = new_policy_id2
        elif "modify-policy-table" in cmd and "-i 0" not in cmd: # If the policy has no service associated
            diff_orig = policy_id - global_variables.last_orig_pol_id
            new_policy_id2 = policy_id + global_variables.new_filt_id_diff
            diff_new = new_policy_id2 - global_variables.last_new_pol_id
            if diff_orig != diff_new:
                new_policy_id2 = global_variables.last_new_pol_id + diff_orig
            print_filt_fnc("noService") # Executes the print filter fuction
            global_variables.last_orig_pol_id = policy_id
            global_variables.last_new_pol_id = new_policy_id2

    ###                          ###
    #    Default Filter Section    #
    ###                          ###

    if len(default_group) != 0:
        print >>output_file, "/c/slb/filt 2048"
        print >>output_file, '        name "Default Filter"'
        print >>output_file, "        ena"
        print >>output_file, "        action outbound-llb"
        print >>output_file, "        ipver v4"
        print >>output_file, "        sip any"
        print >>output_file, "        dip any"
        print >>output_file, "        group %s" % (default_group)
        print >>output_file, "        rport 0"
        print >>output_file, "        vlan %s" % (ingress_vlan)
        for port in ingress_ports:
            print >>output_file, "        add %s" % (port)
        print >>output_file, "/c/slb/filt 2048/adv"
        if default_group in global_variables.orig_dm_dcn.keys():
            if global_variables.orig_dm_dcn[default_group][0] == "Hashing" or global_variables.orig_dm_dcn[default_group][0] == "Layer-3 Hashing":
                print >>output_file, "        thash both"
            elif global_variables.orig_dm_dcn[default_group][0] == "Destination IP Hashing":
                print >>output_file, "        thash dip32"
        print >>output_file, "        reverse ena"
        print >>output_file, "        rtsrcmac ena"
        if alt_ha_mode == 1 or alt_ha_mode == 2:
            print >>output_file, "        mirror ena"
        if proximity_mode == 'Full Proximity Outbound' or proximity_mode == 'Full Proximity Both':
            print >>output_file, "        prximity ena"
        print >>output_file, "/c/slb/filt 2048/adv/layer7"
        print >>output_file, "        ftpa ena"
        if default_group in global_variables.orig_dm_dcn.keys():
            if global_variables.orig_dm_dcn[default_group][0] != "Hashing" and global_variables.orig_dm_dcn[default_group][0] != "Layer-3 Hashing" and global_variables.orig_dm_dcn[default_group][0] != "Source IP Hashing" and global_variables.orig_dm_dcn[default_group][0] != "Destination IP Hashing":
                print >>output_file, "/c/slb/filt 2048/adv/redir"
                print >>output_file, "        pbind e"

    ###################################################
    #### Outbound Policies and Filters Section End ####
    ###################################################

    ###############################################
    #### Proximity Configuraiton Section Start ####
    ###############################################

        ##                                                                                                ##
        #    This is the main section used to configure proximity                                          #
        #    In this section we use information collected ealier and print the proximity configuration     #
        ##                                                                                                ##

    for line in lp_to_lpng: # Loops over the LP configuration
        if "lp proximity mode" in line and proximity_mode != 'No Proximity': # If proximity is configured
            print >>output_file, "/cfg/slb/prximity/" # Starts printing the proximity configuration
            if proximity_aging == 2800:
                print >>output_file, "        aging 2800"
            elif proximity_aging > 2880:
                print >>output_file, "        aging 2880"
            else:
                print >>output_file, "        aging %s" % (proximity_aging)
            if proximity_interval != 5:
                print >>output_file, "        inter %s" % (proximity_interval)
            if proximity_retries != 3:
                print >>output_file, "        retry %s" % (proximity_retries)
            if proximity_mask != '255.255.255.0':
                print >>output_file, "        v4mask %s" % (proximity_mask)
            print >>output_file, "        on"
            if proximity_main_dns != '0.0.0.0':
                print >>output_file, "/cfg/slb/prximity/localdns/add %s" % (proximity_main_dns)
            if proximity_backup_dns != '0.0.0.0':
                print >>output_file, "/cfg/slb/prximity/localdns/add %s" % (proximity_backup_dns)

    #############################################
    #### Proximity Configuraiton Section End ####
    #############################################

    ############################
    #### GSLB Section Start ####
    ############################

    ###                       ###
    #    GSLB - Main Section    #
    ###                       ###

        ##                                                                                                            ##
        #    This is the main section used to find and configure all of the GSLB configuration                         #
        #    In this section, we fine the DNS configuration and print the Alteon equivalent                            #
        #                                                                                                              #
        #    Rules:                                                                                                    #
        #                                                                                                              #
        #    1.) We don't repeat GSLB networks with the same configuration                                             #
        #        The key for not repeating is always the local IP + WAN link group                                     #
        #    2.) We check if the local IP is static NAT, no NAT or PAT                                                 #
        #        If it's static NAT or no NAT, we use GSLB network of type server                                      #
        #        If it's PAT, we use GSLB rule of type group                                                           #
        #    3.) If the local IP doesn't exist in any Smart NAT object, we don't print the GSLB network and rule       #
        #    4.) We currently do NOT support modes "Always Local IP" or "Always NAT Address"                           #
        #    5.) When detecting a farm with NAT mode disable, we currently associate the specfial "_GSLB" WAN group    #
        #        This is not the desired behaviour and will be changed soon                                            #
        ##                                                                                                            ##

    ###                               ###
    #    GSLB - GSLB Networks Section   #
    ###                               ###

    for line in lp_to_lpng: # Loops over the LP configuration
        if "lp dns response-mode" in line:
            dns_response_mode = global_variables.find_fnc( line, 'set "', '"' ) # Finds the DNS response mode
            break
        else:
            dns_response_mode = "According To SmartNat Mode"

    dummy_vip_range = global_variables.ipRange_fnc("169.254.0.1", "169.254.7.254")
    for line in lp_to_lpng: # Loops over the LP configuration
        if "name-to-ip create" in line:
            dns_lia = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the local IP
            dns_lia = dns_lia[0]
            dns_farm = global_variables.find_fnc( line, ' -fn "', '"' ) # Finds the associated farm
            if dns_farm == 'error': # If no double quotes, try again
                dns_farm = global_variables.find_fnc( line, " -fn ", " " )
            new_dns_farm = dns_farm
            for unsupported_char, supported_char in global_variables.special_characters_dcn.iteritems():
                new_dns_farm = new_dns_farm.replace ('%s' % (unsupported_char), "%s" % (supported_char))

            if dns_response_mode == "According To SmartNat Mode":
                if "%s_%s" % (dns_lia, dns_farm) not in global_variables.lia_to_gslb_nets_dcn.keys():
                    if dns_lia in global_variables.smart_nat_local_ips_lst: # If there's a Smart NAT entry for the local IP
                        if dns_lia in global_variables.type_group_local_lst: # If local IP is in Smart NAT static PAT entry
                            if dns_farm != 'error': # If a farm is associated to the DNS entry
                                if dns_farm in global_variables.dns_farms_nonat_lst: # If the associated farm is a no NAT farm
                                    global_variables.gslb_net_id += 1
                                    lia_to_gslb_nets_dcn_key = "%s_%s" % (dns_lia, dns_farm)
                                    global_variables.lia_to_gslb_nets_dcn.setdefault(lia_to_gslb_nets_dcn_key, [])
                                    global_variables.lia_to_gslb_nets_dcn[lia_to_gslb_nets_dcn_key].append('%s' % (global_variables.gslb_net_id))
                                    print_dummy_slb_fnc(dns_lia, dummy_vip_range[global_variables.dummy_vip_id], global_variables.gslb_net_id)
                                    global_variables.dummy_vip_id += 1
                                    global_variables.dummy_status = 1
                                else: # If the associated farm is a NAT farm
                                    for real, virt in global_variables.snp_real_to_virt_dcn.iteritems(): # Loops over the real to virt mapping dictionary
                                        if real == dns_lia: # If the local IP is the same as the real
                                            for virt3 in virt:
                                                if virt3 not in global_variables.virts_to_gslb_nets_dcn.keys(): # If this GSLB network wasn't configured yet
                                                    global_variables.gslb_net_id += 1 # Increments the GSLB network ID by 1
                                                    virts_to_gslb_nets_dcn_key = "%s" % (virt3) # Adds the GSLB network to the dictionary, so we don't configure it again
                                                    global_variables.virts_to_gslb_nets_dcn.setdefault(virts_to_gslb_nets_dcn_key, [])
                                                    global_variables.virts_to_gslb_nets_dcn[virts_to_gslb_nets_dcn_key].append('%s' % (global_variables.gslb_net_id))
                                                    print >>output_file, "/c/slb/gslb/network %s" % (global_variables.gslb_net_id) # Starts printing the GSLB network
                                                    print >>output_file, "        ena"
                                                    print >>output_file, "        servtyp group"
                                                    for real, virt in global_variables.snp_real_to_virt_dcn.iteritems(): # Loops over the real to virt mapping dictionary
                                                        if real == dns_lia: # If the real is the same as the local IP
                                                            for virt in virt: # Loops over the virts mapped to this real
                                                                print >>output_file, "        addvirt PAT_%s 1" % (virt) # Adds each virt to the GSLB network
                                                    break
                                                break
                                            break
                                        break
                            else: # If no farm is associated to the DNS entry, the LP behaviour is complicated to predict # ---->
                                  # The script will behave as if the DNS resolution is with the Smart NAT entry
                                for real, virt in global_variables.snp_real_to_virt_dcn.iteritems(): # Loops over the real to virt mapping dictionary
                                    if real == dns_lia: # If the local IP is the same as the real
                                        for virt3 in virt:
                                            if virt3 not in global_variables.virts_to_gslb_nets_dcn.keys(): # If this GSLB network wasn't configured yet
                                                global_variables.gslb_net_id += 1 # Increments the GSLB network ID by 1
                                                virts_to_gslb_nets_dcn_key = "%s" % (virt3) # Adds the GSLB network to the dictionary, so we don't configure it again
                                                global_variables.virts_to_gslb_nets_dcn.setdefault(virts_to_gslb_nets_dcn_key, [])
                                                global_variables.virts_to_gslb_nets_dcn[virts_to_gslb_nets_dcn_key].append('%s' % (global_variables.gslb_net_id))
                                                print >>output_file, "/c/slb/gslb/network %s" % (global_variables.gslb_net_id) # Starts printing the GSLB network
                                                print >>output_file, "        ena"
                                                print >>output_file, "        servtyp group"
                                                for real, virt in global_variables.snp_real_to_virt_dcn.iteritems(): # Loops over the real to virt mapping dictionary
                                                    if real == dns_lia: # If the real is the same as the local IP
                                                        for virt in virt: # Loops over the virts mapped to this real
                                                            print >>output_file, "        addvirt PAT_%s 1" % (virt) # Adds each virt to the GSLB network
                                                break
                                            break
                                        break
                                    break
                        else: # If the local IP is in Smart NAT static NAT or "no NAT" entry
                            if dns_farm != 'error': # If a farm is associated to the DNS entry
                                if dns_farm in global_variables.dns_farms_nonat_lst: # If the associated farm is a no NAT farm
                                    global_variables.gslb_net_id += 1
                                    lia_to_gslb_nets_dcn_key = "%s_%s" % (dns_lia, dns_farm)
                                    global_variables.lia_to_gslb_nets_dcn.setdefault(lia_to_gslb_nets_dcn_key, [])
                                    global_variables.lia_to_gslb_nets_dcn[lia_to_gslb_nets_dcn_key].append('%s' % (global_variables.gslb_net_id))
                                    print_dummy_slb_fnc(dns_lia, dummy_vip_range[global_variables.dummy_vip_id], global_variables.gslb_net_id)
                                    global_variables.dummy_vip_id += 1
                                    global_variables.dummy_status = 1
                                else: # If the associated farm is a NAT farm
                                    global_variables.gslb_net_id += 1 # Increments the GSLB network ID by 1
                                    lia_to_gslb_nets_dcn_key = "%s_%s" % (dns_lia, dns_farm) # Adds the GSLB Network to the dictionary, so we don't configure it again
                                    global_variables.lia_to_gslb_nets_dcn.setdefault(lia_to_gslb_nets_dcn_key, [])
                                    global_variables.lia_to_gslb_nets_dcn[lia_to_gslb_nets_dcn_key].append('%s' % (global_variables.gslb_net_id))
                                    print >>output_file, "/c/slb/gslb/network %s" % (global_variables.gslb_net_id) # Starts printing the GSLB network
                                    print >>output_file, "        ena"
                                    print >>output_file, "        servtyp server"
                                    print >>output_file, "        servip %s" % (dns_lia)
                                    print >>output_file, "        wangrp %s" % (new_dns_farm)
                            else: # If no farm is associated to the DNS entry, the LP behaviour is complicated to predict # ---->
                                  # The script will behave as if the DNS resolution is with the the Smart entry
                                global_variables.gslb_net_id += 1 # Increments the GSLB network ID by 1
                                lia_to_gslb_nets_dcn_key = "%s_%s" % (dns_lia, dns_farm) # Adds the GSLB Network to the dictionary, so we don't configure it again
                                global_variables.lia_to_gslb_nets_dcn.setdefault(lia_to_gslb_nets_dcn_key, [])
                                global_variables.lia_to_gslb_nets_dcn[lia_to_gslb_nets_dcn_key].append('%s' % (global_variables.gslb_net_id))
                                print >>output_file, "/c/slb/gslb/network %s" % (global_variables.gslb_net_id) # Starts printing the GSLB network
                                print >>output_file, "        ena"
                                print >>output_file, "        servtyp server"
                                print >>output_file, "        servip %s" % (dns_lia)
                    else: # If there's no Smart NAT entry for the local IP
                        if dns_farm != 'error': # If a farm is associated to the DNS entry
                            if dns_farm in global_variables.dns_farms_nonat_lst: # If the associated farm is a no NAT farm
                                global_variables.gslb_net_id += 1
                                lia_to_gslb_nets_dcn_key = "%s_%s" % (dns_lia, dns_farm)
                                global_variables.lia_to_gslb_nets_dcn.setdefault(lia_to_gslb_nets_dcn_key, [])
                                global_variables.lia_to_gslb_nets_dcn[lia_to_gslb_nets_dcn_key].append('%s' % (global_variables.gslb_net_id))
                                print_dummy_slb_fnc(dns_lia, dummy_vip_range[global_variables.dummy_vip_id], global_variables.gslb_net_id)
                                global_variables.dummy_vip_id += 1
                                global_variables.dummy_status = 1
                            else:
                                current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                                print >>migration_errors, '%s #Command_not_migrated: the following command has not been migrated:' % (current_time)
                                print >>migration_errors, "    Command: %s" % (line)
                                print >>migration_errors, '    Reason: Local IP %s in this DNS rule, is not in the Smart NAT table, response mode is "According to SmartNAT Mode" and the associated farm is a "NAT Mode Enabled" farm.' % (dns_lia)
                                print >>migration_errors, '            Therefore, this DNS rule is not migrated.'
                        #else: # If no farm is associated to the DNS entry
                            #global_variables.gslb_net_id += 1
                            #lia_to_gslb_nets_dcn_key = "%s_%s" % (dns_lia, dns_farm)
                            #global_variables.lia_to_gslb_nets_dcn.setdefault(lia_to_gslb_nets_dcn_key, [])
                            #global_variables.lia_to_gslb_nets_dcn[lia_to_gslb_nets_dcn_key].append('%s' % (global_variables.gslb_net_id))
                            #print_dummy_slb_fnc(dns_lia, dummy_vip_range[global_variables.dummy_vip_id], global_variables.gslb_net_id)
                            #global_variables.dummy_vip_id += 1
                            #global_variables.dummy_status = 1
            elif dns_response_mode == "Always Local IP Address":
                if "%s_%s" % (dns_lia, dns_farm) not in global_variables.lia_to_gslb_nets_dcn.keys():
                    global_variables.gslb_net_id += 1
                    lia_to_gslb_nets_dcn_key = "%s_%s" % (dns_lia, dns_farm)
                    global_variables.lia_to_gslb_nets_dcn.setdefault(lia_to_gslb_nets_dcn_key, [])
                    global_variables.lia_to_gslb_nets_dcn[lia_to_gslb_nets_dcn_key].append('%s' % (global_variables.gslb_net_id))
                    print_dummy_slb_fnc(dns_lia, dummy_vip_range[global_variables.dummy_vip_id], global_variables.gslb_net_id)
                    global_variables.dummy_vip_id += 1
                    global_variables.dummy_status = 1
            elif dns_response_mode == "Always NAT IP Address":
                if "%s_%s" % (dns_lia, dns_farm) not in global_variables.lia_to_gslb_nets_dcn.keys():
                    if dns_lia in global_variables.smart_nat_local_ips_lst: # If there's a Smart NAT entry for the local IP
                        if dns_lia in global_variables.type_group_local_lst: # If local IP is in Smart NAT static PAT entry
                            for real, virt in global_variables.snp_real_to_virt_dcn.iteritems(): # Loops over the real to virt mapping dictionary
                                if real == dns_lia: # If the local IP is the same as the real
                                    for virt3 in virt:
                                        if virt3 not in global_variables.virts_to_gslb_nets_dcn.keys(): # If this GSLB network wasn't configured yet
                                            global_variables.gslb_net_id += 1 # Increments the GSLB network ID by 1
                                            virts_to_gslb_nets_dcn_key = "%s" % (virt3) # Adds the GSLB network to the dictionary, so we don't configure it again
                                            global_variables.virts_to_gslb_nets_dcn.setdefault(virts_to_gslb_nets_dcn_key, [])
                                            global_variables.virts_to_gslb_nets_dcn[virts_to_gslb_nets_dcn_key].append('%s' % (global_variables.gslb_net_id))
                                            print >>output_file, "/c/slb/gslb/network %s" % (global_variables.gslb_net_id) # Starts printing the GSLB network
                                            print >>output_file, "        ena"
                                            print >>output_file, "        servtyp group"
                                            for real, virt in global_variables.snp_real_to_virt_dcn.iteritems(): # Loops over the real to virt mapping dictionary
                                                if real == dns_lia: # If the real is the same as the local IP
                                                    for virt in virt: # Loops over the virts mapped to this real
                                                        print >>output_file, "        addvirt PAT_%s 1" % (virt) # Adds each virt to the GSLB network
                                            break
                                        break
                                    break
                                break
                        else: # If the local IP is in Smart NAT static NAT or "no NAT" entry
                            global_variables.gslb_net_id += 1 # Increments the GSLB network ID by 1
                            lia_to_gslb_nets_dcn_key = "%s_%s" % (dns_lia, dns_farm) # Adds the GSLB Network to the dictionary, so we don't configure it again
                            global_variables.lia_to_gslb_nets_dcn.setdefault(lia_to_gslb_nets_dcn_key, [])
                            global_variables.lia_to_gslb_nets_dcn[lia_to_gslb_nets_dcn_key].append('%s' % (global_variables.gslb_net_id))
                            print >>output_file, "/c/slb/gslb/network %s" % (global_variables.gslb_net_id) # Starts printing the GSLB network
                            print >>output_file, "        ena"
                            print >>output_file, "        servtyp server"
                            print >>output_file, "        servip %s" % (dns_lia)
                            if dns_farm != 'error': # If a farm is associated to the DNS entry
                                print >>output_file, "        wangrp %s" % (new_dns_farm)
                    else: # If there's no Smart NAT entry for the local IP
                        if dns_farm == 'error': # If no farm is associated to the DNS entry
                            global_variables.gslb_net_id += 1
                            lia_to_gslb_nets_dcn_key = "%s_%s" % (dns_lia, dns_farm)
                            global_variables.lia_to_gslb_nets_dcn.setdefault(lia_to_gslb_nets_dcn_key, [])
                            global_variables.lia_to_gslb_nets_dcn[lia_to_gslb_nets_dcn_key].append('%s' % (global_variables.gslb_net_id))
                            print_dummy_slb_fnc(dns_lia, dummy_vip_range[global_variables.dummy_vip_id], global_variables.gslb_net_id)
                            global_variables.dummy_vip_id += 1
                            global_variables.dummy_status = 1
                        else:
                            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                            print >>migration_errors, '%s #Command_not_migrated: the following command has not been migrated:' % (current_time)
                            print >>migration_errors, "    Command: %s" % (line)
                            print >>migration_errors, '    Reason: Local IP %s in this DNS rule, is not in the Smart NAT table, response mode is "Always NAT IP Address" and there is a farm associated.' % (dns_lia)
                            print >>migration_errors, '            Therefore, this DNS rule is not migrated.'

    ###                            ###
    #    GSLB - GSLB Rules Section   #
    ###                            ###

    for line in lp_to_lpng: # Loops over the LP configuration
        if "name-to-ip create" in line:
            dns_name = global_variables.find_fnc( line, "create ", " -lia" ) # Finds the domain name
            dns_farm2 = global_variables.find_fnc( line, ' -fn "', '"' ) # Finds the farm associated with the DNS rule
            if dns_farm2 == 'error': # If no double quotes, find again
                dns_farm2 = global_variables.find_fnc( line, " -fn ", " " )
            new_dns_farm2 = dns_farm2
            for unsupported_char, supported_char in global_variables.special_characters_dcn.iteritems():
                new_dns_farm2 = new_dns_farm2.replace ('%s' % (unsupported_char), "%s" % (supported_char))
            if new_dns_farm2 in global_variables.farm_parameters_dcn.keys(): # Defines the gmetric according to the farm's metric
                if global_variables.farm_parameters_dcn[new_dns_farm2][0] == "roundrobin" or global_variables.farm_parameters_dcn[new_dns_farm2][0] == "leastconns" or global_variables.farm_parameters_dcn[new_dns_farm2][0] == "bandwidth":
                    net_gmetric3 = global_variables.farm_parameters_dcn[new_dns_farm2][0]
                else: # If the farm has a metric which is not supported as gmetric, use bandwidth
                    net_gmetric3 = "bandwidth"
                    if dns_farm2 in global_variables.orig_farm_parameters_dcn.keys():
                        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                        print >>migration_errors, '\033[1m%s\033[0m #Unsupported_flag_option: the following command contains a flag with an unsupported option:' % (current_time)
                        print >>migration_errors, '    Unsupported flag option: the farm associated with the DNS rule has a metric which is not supported as gmetric.'
                        print >>migration_errors, '    Command: %s' % (line)
                        print >>migration_errors, '    Farm: %s.' % (dns_farm2)
                        print >>migration_errors, '    Metric: %s.' % (global_variables.orig_farm_parameters_dcn[dns_farm2][0])
                        print >>migration_errors, '    Alteon will use "gmetric bandwidth".'
            else: # If no farm associated, uses gmetric bandwidth
                net_gmetric3 = "bandwidth"

            dns_lia2 = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line ) # Finds the local IP
            dns_lia2 = dns_lia2[0]
            dns_lia_and_farm = "%s_%s" % (dns_lia2, dns_farm2) # Binds the local IP and farm
            if dns_lia2 in global_variables.smart_nat_local_ips_lst: # If the local IP is in Smart NAT
                if dns_lia_and_farm in global_variables.lia_to_gslb_nets_dcn: # If the local IP and farm are already define in a GSLB network
                    if len(global_variables.lia_to_gslb_nets_dcn[dns_lia_and_farm]) > 0: # Validate that the value (the GSLB network ID) is not empty
                        net_rule = global_variables.lia_to_gslb_nets_dcn[dns_lia_and_farm][0] # Uses the GSLB network ID in this GSLB rule
                        global_variables.gslb_rule_id += 1 # Increment the GSLB rule ID by 1
                elif dns_lia2 in global_variables.type_group_local_lst: # If the local IP is in PAT
                    for real, virt in global_variables.snp_real_to_virt_dcn.iteritems(): # Loops over the real to virt mapping dictionary
                        if real == dns_lia2: # If the real server is the same as the local IP
                            for virt4 in virt: # Loops over the associated virts
                                if virt4 in global_variables.virts_to_gslb_nets_dcn.keys(): # If the virt is already defined in a GSLB network
                                    if len(global_variables.virts_to_gslb_nets_dcn[virt4]) > 0: # Validates that the value (the GSLB network ID) is not empty
                                        net_rule = global_variables.virts_to_gslb_nets_dcn[virt4][0] # Uses the GSLB network ID in this GSLB rule
                                        global_variables.gslb_rule_id += 1 # Increments the GSLB rule ID by 1
                print >>output_file, "/c/slb/gslb/rule %s" % (global_variables.gslb_rule_id) # Starts printing the GSLB rule
                print >>output_file, "        ena"
                if dns_lia2 in global_variables.type_group_local_lst: # If the local IP is in PAT
                    for real, virt in global_variables.snp_real_to_virt_dcn.iteritems(): # Loops over the real to virt mapping dictionary
                        if real == dns_lia2: # If the real is the same as the local IP
                            for virt in virt: # Loops over the associated virts
                                for virt2, service in global_variables.snp_virt_to_service_dcn.iteritems(): # Loops over the virt to service dictionary
                                    if virt2 == virt: # If the virt in the dictionary is the same as the virt associated to this local IP
                                        print >>output_file, "        type inbound-llb %s" % (service[0]) # Prints the inbound LLB rule command with the correct service
                                        break
                                    break
                                break
                else: # If the local IP is in static NAT or no NAT
                    if int(net_rule) in global_variables.nonat_gslb_nets_lst:
                        print >>output_file, "        type inbound-llb 1234"
                    else:
                        print >>output_file, "        type inbound-llb 0" # prints the inbound LLB command with "0"
                print >>output_file, "        ttl %s" % (dns_ttl) # Continues printing the rest of the general GSLB rule commands
                print >>output_file, "        rr %s" % (dns_rr)
                print >>output_file, "        dname %s" % (dns_name)
                print >>output_file, "/c/slb/gslb/rule %s/metric 1" % (global_variables.gslb_rule_id)
                print >>output_file, "        gmetric network"
                print >>output_file, "        addnet %s" % (net_rule)
                #if proximity_mode == 'Full Proximity Inbound' or proximity_mode == 'Full Proximity Both':
                    #print >>output_file, "/c/slb/gslb/rule %s/metric 2" % (global_variables.gslb_rule_id)
                    #print >>output_file, "        gmetric proximity"
                print >>output_file, "/c/slb/gslb/rule %s/metric 3" % (global_variables.gslb_rule_id)
                print >>output_file, "        gmetric %s" % (net_gmetric3)

    ##########################
    #### GSLB Section End ####
    ##########################

    #######################
    #### Main Code End ####
    #######################

    #############################
    ### Logging Section Start ###
    #############################

    def unsupported_commands_global_log_fnc(command):
        '''Used to log a global message when finding and unsupported command.
        Takes the beginning of the command as an argument.
        '''
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        print >>migration_errors, '\033[1m%s\033[0m #Unsupported_command: all commands starting with "%s" are unsupported by this script.' % (current_time, command)
        print >>migration_errors, "    Unsupported commands in your configuration:"

    def unsupported_commands_specific_log_fnc():
        '''Used to log the specific unsupported command.
        Takes no arguments.
        '''
        print >>migration_errors, '    Command: %s' % (line)

    def unsupported_flag_global_log_fnc(command):
        '''Used to log a global message when finding and unsupported flag.
        Takes the command as an argument.
       '''
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        print >>migration_errors, '\033[1m%s\033[0m #Unsupported_flag: the following command contains a flag which is not supported by this script:' % (current_time)
        print >>migration_errors, '    Command: %s' % (line)

    def unsupported_flag_specific_log_fnc(flag):
        '''Used to log the specific unsupported flag.
        Takes no arguments.
        '''
        print >>migration_errors, '    Unsupported flag: %s' % (flag)

    ###                        ###
    #    Unsupported Commands    #
    ###                        ###

    for line in lp_to_lpng:
        if line.startswith( 'classes modify service and-group' ):
            unsupported_commands_global_log_fnc('classes modify service and-group')
            break
    for line in lp_to_lpng:
        if line.startswith( 'classes modify service and-group' ):
            unsupported_commands_specific_log_fnc()
    for line in lp_to_lpng:
        if line.startswith( 'lp dns server' ):
            unsupported_commands_global_log_fnc('lp dns server')
            break
    for line in lp_to_lpng:
        if line.startswith( 'lp dns server' ):
            unsupported_commands_specific_log_fnc()
    for line in lp_to_lpng:
        if line.startswith( 'lp dns host-to-ip-tables dynamic-name-to-ip' ):
            unsupported_commands_global_log_fnc('lp dns host-to-ip-tables dynamic-name-to-ip')
            break
    for line in lp_to_lpng:
        if line.startswith( 'lp dns host-to-ip-tables dynamic-name-to-ip' ):
            unsupported_commands_specific_log_fnc()
    for line in lp_to_lpng:
        if line.startswith( 'lp content-lb-parameters' ):
            unsupported_commands_global_log_fnc('lp content-lb-parameters')
            break
    for line in lp_to_lpng:
        if line.startswith( 'lp content-lb-parameters' ):
            unsupported_commands_specific_log_fnc()
    for line in lp_to_lpng:
        if line.startswith( 'bwm' ):
            unsupported_commands_global_log_fnc('bwm')
            break
    for line in lp_to_lpng:
        if line.startswith( 'bwm' ):
            unsupported_commands_specific_log_fnc()

    ###                     ###
    #    Unsupported Flags    #
    ###                     ###

    for line in lp_to_lpng:
        if "servers router-servers" in line:
            for flag in global_variables.lp_servers_unsupported_flags:
                if " %s " % (flag) in line:
                    unsupported_flag_global_log_fnc(line)
                    break
            for flag in global_variables.lp_servers_unsupported_flags:
                if " %s " % (flag) in line:
                    unsupported_flag_specific_log_fnc(flag)
        if "net ip-interface" in line:
            for flag in global_variables.lp_netip_unsupported_flags:
                if " %s " % (flag) in line:
                    unsupported_flag_global_log_fnc(line)
                    break
            for flag in global_variables.lp_netip_unsupported_flags:
                if " %s " % (flag) in line:
                    unsupported_flag_specific_log_fnc(flag)
        if "flow-management modify-policy-table" in line:
            for flag in global_variables.lp_traffic_pols_unsupported_flags:
                if " %s " % (flag) in line:
                    unsupported_flag_global_log_fnc(line)
                    break
            for flag in global_variables.lp_traffic_pols_unsupported_flags:
                if " %s " % (flag) in line:
                    unsupported_flag_specific_log_fnc(flag)

    ###                            ###
    #    Unsupported Flag Options    #
    ###                            ###

        if 'flow-management modify-policy-table' in line and ' -pt "AND Group"' in line:
            print >>migration_errors, '\033[1m%s\033[0m #Unsupported_flag_option: the following command contains a flag with an option which is not supported by this script:' % (current_time)
            print >>migration_errors, '    Command: %s' % (line)
            print >>migration_errors, '    Unsupported flag option: "Service type AND Group".'

    ###########################
    ### Logging Section End ###
    ###########################

    output_file.close()
    migration_errors.close()

    tar = tarfile.open("app/%s_files.tar.gz" % (user_output_file), "w:gz")
    tar.add("app/%s_config" % (user_output_file), arcname="%s_config" % (user_output_file))
    tar.add("app/%s_logs" % (user_output_file), arcname="%s_logs" % (user_output_file))
    tar.close()

    return render_template('end.html', user_output_file=user_output_file)
    #return redirect('%s_files.tar.gz' % (user_output_file))

@app.route('/<path:dummy>' , methods=['GET', 'POST'])
def download(dummy):
    if dummy.endswith("_files.tar.gz"):
        return send_file('%s' % (dummy), as_attachment=True)
    elif dummy.endswith("favicon.ico"):
        return render_template('dummy.html'), 404
