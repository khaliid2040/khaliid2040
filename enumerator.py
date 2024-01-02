#!/usr/bin/python3
import argparse
import platform
import psutil, psutil._common
import time 
import subprocess
import json, pwd
import netifaces
import sys
from colorama import Fore,Style
import socket
import os
from datetime import datetime, timedelta
#in this code you may see escape character \n i used it in place of instead of using print repeatly in order to improve the code
#first it must be verifyed if the envirnment the script running on is linux specifically redhat and debian based distro if you are 
#want to use for software management
def general_verification():
    if platform.system()=="Linux":
        print(f'{Fore.GREEN}all good to go{Style.RESET_ALL}')
    else:
        print(f'{Fore.RED}Error: target is {platform.system()} is not supported {Style.RESET_ALL}')
        sys.exit(2)
# check host network interfaces
def get_network_interfaces(interface):
    addresses = netifaces.ifaddresses(interface)
    gateways= netifaces.gateways()
    if netifaces.AF_INET in addresses:
        ipv4_addresses = addresses[netifaces.AF_INET]
        for address in ipv4_addresses:
            print("Interface:", interface)
            print("  - IPv4 Address:", address['addr'])
            print("  - Broadcast Address:", address.get('broadcast'))
            print("  - Subnet Mask:", address['netmask'])
            print("  - Gateway info:", gateways[2][0])

    if netifaces.AF_INET6 in addresses:
        ipv6_addresses = addresses[netifaces.AF_INET6]
        for address in ipv6_addresses:
            #print("Interface:", interface)
            print("  - IPv6 Address:", address['addr'])

    mtu = netifaces.ifaddresses(interface).get(netifaces.AF_LINK, [])
    if mtu:
        mtu_value = mtu[0].get('mtu')
        if mtu_value is not None:
            print("Interface:", interface)
            print("  - MTU:", mtu_value)

    vendor = netifaces.ifaddresses(interface).get(netifaces.AF_LINK, [])
    if vendor:
        vendor_name = vendor[0].get('vendor')
        if vendor_name is not None:
            print("Interface:", interface)
            print("  - Vendor:", vendor_name)
    else:
        mac_address = vendor[0].get('addr')
        print("Interface:", interface)
        print("  - MAC Address:", mac_address)
def mandetory_access_control_identify():
    try:
        import selinux
        import apparmor
        selinux_status= selinux.security_getenforce()
        if selinux_status==0:
            print(f'{Fore.RED}selinux is disabled{Style.RESET_ALL}')
        elif selinux_status==1:
            print(f'{Fore.GREEN}selinux is in enforcing mode{Style.RESET_ALL}')
        else:
            print(f'{Fore.YELLOW}selinux is in permisive mode')
        
    except ModuleNotFoundError:
        pass
    except FileNotFoundError:
        pass

def network_services_checking():
    # List of network services to filter
    network_services = [
    "sshd", "httpd","nginx", 
    "mysqld", "named", "dhcpd", "vsftpd", "smbd", 
    "postfix", "dovecot",   "telnet", "nfs",
    "snmpd","cups","squid",
    "ircd","openvpn", "pptpd",
    "nfs-kernel-server",
    "samba",
]

    # Run the systemctl command to list specific active network services
    command = ['systemctl', 'list-units', '--type=service', '--no-pager', '--no-legend']
    output = subprocess.check_output(command, universal_newlines=True)

# Process the output and extract service and status
    lines = output.strip().split('\n')
    for line in lines:
        parts = line.split()
        if parts and len(parts) >= 3:
            service = parts[0]
            status = parts[2]
        # Remove the ".service" extension from the service name
            service_name = service.split('.', 1)[0]
        # Check if the service is in the network services list
            if service_name in network_services:
                print(f'{service_name} is {status}')

#the above must be declared all ficility non-component functions and all below functions in this comment must be script component functions
def system(process,user):
    print(Fore.YELLOW + "perfoming system enumeration" + Style.RESET_ALL)
    print(f"current kernel running version:{Fore.GREEN} {platform.release()} {Style.RESET_ALL}")
    print(f"current cpu architecture:{Fore.GREEN}{platform.machine()} {Style.RESET_ALL}")
    print(f"hostname:{Fore.GREEN}{platform.node()} {Style.RESET_ALL}")
    print(f"number of processors:{Fore.GREEN} {psutil.cpu_count()} {Style.RESET_ALL}")
    print(f"number of cores: {Fore.GREEN} {psutil.cpu_count(logical=False)} {Style.RESET_ALL}")
    mandetory_access_control_identify()
    print("enumerating users...")
    if user is not None:
        try:
            user = pwd.getpwnam(user)
            keys = ['user', 'password', 'uid', 'gid', 'comment', 'home', 'shell']
            user_dict = {key: value for key, value in zip(keys, user)}
            print(json.dumps(user_dict, indent=3))
        except KeyError:
            pass
    else:
        for uid in range(2000):
            try:
                user = pwd.getpwuid(uid)
                keys = ['user', 'password', 'uid', 'gid', 'comment', 'home', 'shell']
                user_dict = {key: value for key, value in zip(keys, user)}
                if user_dict['shell'] == '/bin/bash':
                    print(json.dumps(user_dict, indent=3))
            except KeyError:
                continue
    boot_time = psutil.boot_time()
    current_time = datetime.now().timestamp()
    uptime = current_time - boot_time
    uptime_readable = str(timedelta(seconds=uptime))
    uptime_readable_hours= uptime_readable[0]
    uptime_readable_minutes= uptime_readable[2:4]
    print(f'uptime: {Fore.GREEN}{uptime_readable_hours} hours and {uptime_readable_minutes} minutes{Style.RESET_ALL}')
    print(f'{Fore.YELLOW}current cpu utilization {Style.RESET_ALL}')
    cpu_utilization= psutil.cpu_percent(interval=7)
    print(f"{Fore.GREEN}cpu utilization percentage: {cpu_utilization}% {Style.RESET_ALL}")
    if args.process==None:
        pass
    else:
        print("enumerating process resources...")
        try:
            percent = psutil.Process(process)
            cpu_times = psutil.cpu_times()

            process_dump = {
                "PID": percent.pid,
                "command": percent.name(),
                "state": percent.status(),
                "cpu_times": {
                    "user": cpu_times.user,
                    "system": cpu_times.system,
                    "idle": cpu_times.idle,
        
                }
            }
            # Convert the dictionary to JSON-like output
            json_output = json.dumps(process_dump, indent=4)
            # Print the JSON-like output
            print(json_output)
        except psutil.NoSuchProcess:
            print(f"{Fore.RED} process id {process} not found {Style.RESET_ALL}")
    print(Fore.YELLOW + "enumerating memory utilization..." + Style.RESET_ALL)
    total_memory= psutil.virtual_memory().total
    readable_total=psutil._common.bytes2human(total_memory)
    free_memory= psutil.virtual_memory().free
    readable_free=psutil._common.bytes2human(free_memory)
    buffer_cache_memory= psutil.virtual_memory().buffers + psutil.virtual_memory().cached
    readable_buffer=psutil._common.bytes2human(buffer_cache_memory)
    available_memory= psutil.virtual_memory().available
    readable_available=psutil._common.bytes2human(available_memory)
    used_memory= psutil.virtual_memory().used
    readable_used=psutil._common.bytes2human(used_memory)
    print(f"total memory: {readable_total}\nfree: {readable_free}\nbuffer/cache: {readable_buffer}\navailable: {readable_available}\nused memory: {readable_used}")
    print(f"{Fore.GREEN}memory utilization percent: {psutil.virtual_memory().percent}% {Style.RESET_ALL}")
    print(f'{Fore.YELLOW}disk usage per partition {Style.RESET_ALL}')
    disk_partitions = psutil.disk_partitions()
    # Print header
    print("{:<15} {:<15} {:<10}".format("Device", "Mountpoint", "Size"))

    for partition in disk_partitions:
        partition_device = partition.device
        partition_mountpoint = partition.mountpoint
        # Get disk usage for the current partition
        disk_usage = psutil.disk_usage(partition_mountpoint)
        readable = psutil._common.bytes2human(disk_usage.total)
        print("{:<15} {:<15} {:<10}".format(partition_device, partition_mountpoint, readable))
        interval = 1  # Interval in seconds
    #checking disk io statistics may not be reliable it adds up the total disk i/o operations happened for 5 second
    print(f'{Fore.YELLOW}checking disk and network i/o statistics {Style.RESET_ALL}')
    duration=0
    total_read_ops = 0
    total_write_ops = 0

    while duration<=5:
        disk_io = psutil.disk_io_counters()
        read_ops = disk_io.read_count
        write_ops = disk_io.write_count

        total_read_ops += read_ops
        total_write_ops += write_ops

        human_total_read_ops = psutil._common.bytes2human(total_read_ops)
        human_total_write_ops = psutil._common.bytes2human(total_write_ops)
        duration+=1
        time.sleep(interval)
    print(f"Total Read Operations: {human_total_read_ops}")
    print(f"Total Write Operations: {human_total_write_ops}")
    print()
    # network i/o statistics
    net_io = psutil.net_io_counters()
    readable_bytes_sent= psutil._common.bytes2human(net_io.bytes_sent)
    readable_bytes_recv= psutil._common.bytes2human(net_io.bytes_recv)
    readable_packet_sent= psutil._common.bytes2human(net_io.packets_sent)
    readable_packets_recv= psutil._common.bytes2human(net_io.packets_recv)

    print("Bytes Sent:", readable_bytes_sent)
    print("Bytes Received:", readable_bytes_recv)
    print("Packets Sent:", readable_packet_sent)
    print("Packets Received:", readable_packets_recv)

def network(interface):
    print(f"{Fore.MAGENTA}performing network enumeration{Style.RESET_ALL}")
    time.sleep(2)
    print(f'{Fore.YELLOW}looking for interface {interface} {Style.RESET_ALL}')
    interfaces= netifaces.interfaces()
    if interface in interfaces:
        try:
            get_network_interfaces(interface)
        except ValueError:
            print(f'{Fore.RED}invalid interface,{Style.RESET_ALL}')
    elif interface is not interfaces:
        print(f'{Fore.RED}invalid interface,{Style.RESET_ALL} listing other interfaces')
        interfaces= netifaces.interfaces()
        for interface in interfaces:
            get_network_interfaces(interface)
    print(Fore.YELLOW + 'dumping routing table...' + Style.RESET_ALL)
    subprocess.run(['ip','route','show'])
    print(Fore.YELLOW + 'dumping arp table...' + Style.RESET_ALL)
    try:
        subprocess.run(['arp','-n'])
    except FileNotFoundError:
        print(f'{Fore.RED}command not found arp {Style.RESET_ALL}')
    print(f'{Fore.MAGENTA}enumerating most common tcp ports...{Style.RESET_ALL}')
    def check_port(host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # Set a timeout value for the connection
            result = sock.connect_ex((host, port))
            if result == 0:
                print(f"TCP/{port} on {host} is open")
            sock.close()
        except socket.error:
            print(f"Could not connect to TCP/{host}:{port}")
    host = "localhost"
    common_tcp_ports = [80, 443, 22, 3389, 445, 139, 53, 21, 23, 25, 110, 143, 8080, 25, 587, 993, 5900, 1723, 111, 995, 3306, 5901, 123, 161, 69, 389, 587, 8000, 8008, 8443]
    # Checking TCP ports
    for port in common_tcp_ports:
        check_port(host,port)
    # checking running network services the function is declared above
    print(f'{Fore.MAGENTA}checking active network services{Style.RESET_ALL}')
    network_services_checking()
def software(search_packages):
    print(f'{Fore.MAGENTA}performing software enumeration{Style.RESET_ALL}')
    command = ['which', 'rpm', 'apt']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    package_manager=result.stdout.strip()
    if "rpm" in package_manager:
        rpm=subprocess.run([package_manager,'-aq'], stdout=subprocess.PIPE, text=True)
        packages=rpm.stdout
        result=len(packages.splitlines())
        results= packages.splitlines()
    elif "apt" in package_manager:
        apt=subprocess.run([package_manager,'list','--installed'],stdout=subprocess.PIPE)
        packages=apt.stdout
        result=len(packages.splitlines())
        results= packages.splitlines()
    else:
        print("supported packages didn't found")
    print(f'installed packages: {Fore.GREEN}{result}{Style.RESET_ALL}')
    if search_packages !=None:
        try:
            if search_packages in results:
                print(f'{Fore.GREEN}{search_packages} package present {Style.RESET_ALL}')
            else:
                print(f'{Fore.YELLOW}{search_packages} package is not present {Style.RESET_ALL}')
                print('please provide the complete package name, if you think the package is present')
        except KeyboardInterrupt:
            print(f'{Fore.RED} keyboard interrupt exiting....{Style.RESET_ALL}')        
#Section 2 command argument section
parser= argparse.ArgumentParser(description="basic resource monitor and enumerator")
subperser= parser.add_subparsers(dest="operation",required=True)
subperser_system=subperser.add_parser("system",help="system reporting")
subperser_system.add_argument("-p","--process",help="monitoring per process",type=int)
subperser_system.add_argument("-u","--user",help="output only specific user",type=str)
subperser_network=subperser.add_parser("network",help="network reporting")
subperser_network.add_argument('-i','--interface',help="choose interface")
#any neccessary arguments
subperser_software=subperser.add_parser("software",help="software reporting")
subperser_software.add_argument('-s','--search',help='search installed packages',type=str)
args=parser.parse_args()
#here we call the fucntion specified above in order to check target os
general_verification()
if args.operation=="system":
    Pprocess=args.process
    users=args.user
    system(Pprocess,users)
elif args.operation=="network":
     inet=args.interface
     network(inet)
elif args.operation=="software":
    search_packages=args.search
    software(search_packages)
else:
    print("invalid option")