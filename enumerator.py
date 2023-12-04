#!/usr/bin/python3
import argparse
import platform
import psutil
import time
import subprocess
import re
import netifaces
import sys
from colorama import Fore,Style
import socket
import os
#in this code you may see escape character \n i used it in place of instead of using print repeatly in order to improve the code
#first it must be verifyed if the envirnment the script running on is linux specifically redhat and debian based distro if you are 
#want to use for software management
def target_os_verification():
    if platform.system()=="Linux":
        print(f'{Fore.GREEN} all good to go{Style.RESET_ALL}')
    else:
        print(f'{Fore.RED} Error: target is {platform.system()} is not supported {Style.RESET_ALL}')
        sys.exit(2)
#when reading memory psutils prints the size by bytes and there is no way to make it readable so the function 
# below doing the job by converting the size in from bytes to more human readable size
def format_size(size):
    power = 2**10
    n = 0
    size_labels = ['B', 'KB', 'MB', 'GB', 'TB']
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {size_labels[n]}"
def user_checking():
    uid=os.getuid()
    gid=os.getgid()
    if uid and gid == 0:
        print(f'{Fore.RED} it is not recommended to run the script with root unless we explicitly ask you to do{Style.RESET_ALL}')
        print('exiting...')
        sys.exit(2)
    
#the above must be declared all ficility non-component functions and all below functions in this comment must be script component functions
def system(process,user,current_user):
    print(Fore.YELLOW + "perfoming system enumeration" + Style.RESET_ALL)
    print(f"current kernel running version:{Fore.GREEN} {platform.release()} {Style.RESET_ALL}")
    print(f"current cpu architecture:{Fore.GREEN}{platform.machine()} {Style.RESET_ALL}")
    print(f"hostname:{Fore.GREEN}{platform.node()} {Style.RESET_ALL}")
    print(f"number of processors:{Fore.GREEN} {psutil.cpu_count()} {Style.RESET_ALL}")
    print(f"number of cores: {Fore.GREEN} {psutil.cpu_count(logical=False)} {Style.RESET_ALL}")
    print("enumerating users...")
    if args.user==None:
        print(f"{Fore.YELLOW}no argument:passing... defaulting to all users with login shell{Style.RESET_ALL}")
        search_string = "bash"
        file_path = '/etc/passwd'
        with open(file_path, 'r') as file:
            for line in file:
                if search_string in line:
                    print(line.strip())
    else:
        passwd=open('/etc/passwd','r')
        search_pattern=re.escape(user)
        for line in passwd:
            if re.search(search_pattern,line):
                print(line)
            else:
                pass
        
    time.sleep(2)
    if args.process==None:
        pass
    else:
        print("enumerating process resources...")
        process_psutils=psutil.Process(process)
        cpu_percent= psutil.cpu_percent()
        cpu_time= psutil.cpu_times()
        print(f"cpu percent of process{Fore.GREEN} {Fore.GREEN} {process_psutils}: {cpu_percent} {Style.RESET_ALL}")
        print(f"cpu time: {cpu_time}")
    print(Fore.YELLOW + "enumerating memory utilization..." + Style.RESET_ALL)
    total_memory= psutil.virtual_memory().total
    readable_total=format_size(total_memory)
    free_memory= psutil.virtual_memory().free
    readable_free=format_size(free_memory)
    buffer_memory= psutil.virtual_memory().buffers
    readable_buffer=format_size(buffer_memory)
    available_memory= psutil.virtual_memory().available
    readable_available=format_size(available_memory)
    used_memory= psutil.virtual_memory().used
    readable_used=format_size(used_memory)
    print(f"{Fore.GREEN}total memory: {readable_total}\n free: {readable_free}\n buffer: {readable_buffer}\n available: {readable_available}\n used memory {readable_used} {Style.RESET_ALL}")
    print(f"memory utilization percent: {psutil.virtual_memory().percent}%")

def network(interface):
    print(f"{Fore.MAGENTA} performing network enumeration{Style.RESET_ALL}")
    time.sleep(2)
    print(f'{Fore.YELLOW}looking for interface {interface} {Style.RESET_ALL}')
    interfaces= netifaces.interfaces()
    if interface in interfaces:
        try:
            addresses=netifaces.ifaddresses(interface).get(netifaces.AF_INET)
            for address in addresses:
                print(f"ip address: {address['addr']}")
                print(f"netmask: {address['netmask']}")
                if "broadcast" in address:
                    print(f"broadcast address:{address['broadcast']}")
                elif "peer" in address:
                    print(f"peer connection: {address['peer']}")
        except TypeError:
            print(f'{Fore.RED} error: may be interface link is down {Style.RESET_ALL}')
    else:
        print(f'{Fore.RED}ivalid interface{Style.RESET_ALL}')
    print(Fore.YELLOW + 'dumping routing table...' + Style.RESET_ALL)
    subprocess.run(['ip','route','show'])
    print(Fore.YELLOW + 'dumping arp table...' + Style.RESET_ALL)
    subprocess.run(['arp','-n'])
    print(f'{Fore.MAGENTA} enumerating most common tcp ports...{Style.RESET_ALL}')
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
def software(search_packages):
    command = ['which', 'rpm', 'dpkg']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    package_manager=result.stdout.strip()
    if "rpm" in package_manager:
        rpm=subprocess.run([package_manager,'-aq'], stdout=subprocess.PIPE)
        packages=rpm.stdout
        result=len(packages.splitlines())
    elif "dpkg" in package_manager:
        dpkg=subprocess.run([package_manager,'list','--installed'],stdout=subprocess.PIPE)
        packages=dpkg.stdout
        result=len(packages.splitlines())
    else:
        print("supported packages didn't found")
    print(f' installed packages: {Fore.GREEN}{result}{Style.RESET_ALL}')
    if search_packages !=None:
        if search_packages in result.stdout:
            print(f'{Fore.GREEN}{search_packages} package present {Style.RESET_ALL}')
        else:
            print(f'{Fore.GREEN}{search_packages} package is not present {Style.RESET_ALL}')
            
#Section 2 command argument section
parser= argparse.ArgumentParser(description="basic resource monitor and enumerator")
subperser= parser.add_subparsers(dest="operation",required=True)
subperser_system=subperser.add_parser("system",help="system reporting")
subperser_system.add_argument("-p","--process",help="monitoring per process",type=int)
subperser_system.add_argument("-u","--user",help="output only specific user",type=str)
subperser_network=subperser.add_parser("network",help="network reporting")
subperser_network.add_argument('-i','--interface',help="choose interface",required=True)
#any neccessary arguments
subperser_software=subperser.add_parser("software",help="software reporting")
subperser_software.add_argument('-s','--search',help='search installed packages',type=str)
args=parser.parse_args()
#here we call the fucntion specified above in order to check target os
target_os_verification()
user_checking
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