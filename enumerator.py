#!/usr/bin/python3
import argparse
import platform
import psutil
import time
import subprocess
import re
import netifaces
from colorama import Fore,Style
#in this code you may see escape character \n i used it in place of instead of using print repeatly in order to improve the code
def format_size(size):
    power = 2**10
    n = 0
    size_labels = ['B', 'KB', 'MB', 'GB', 'TB']
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {size_labels[n]}"
def get_installed_packages():
    result = subprocess.run(['rpm', '-qa'], capture_output=True, text=True)
    output_lines = result.stdout.splitlines()
    packages = [line for line in output_lines]
    return packages

#the above must be declared all ficility non-component functions and all below functions in this comment must be script component functions
def enumerator(process,user):
    print(Fore.YELLOW + "perfoming system enumeration" + Style.RESET_ALL)
    print(f"current kernel running version:{Fore.GREEN} {platform.release()} {Style.RESET_ALL}")
    print(f"current cpu architecture:{Fore.GREEN}{platform.machine()} {Style.RESET_ALL}")
    print(f"hostname:{Fore.GREEN}{platform.node()} {Style.RESET_ALL}")
    print(f"number of processors:{Fore.GREEN} {psutil.cpu_count()} {Style.RESET_ALL}")
    print(f"number of cores: {Fore.GREEN} {psutil.cpu_count(logical=False)} {Style.RESET_ALL}")
    print("enumerating process resources...")
    print("enumerating users...")
    if args.user==None:
        print(f"{Fore.YELLOW}no argument:passing...{Style.RESET_ALL}")
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
    print(f"{Fore.GREEN}total memory: {readable_total}\n free: {readable_free}\n buffer: {readable_buffer}\n available: {readable_available} {Style.RESET_ALL}")
    print(f"{psutil.virtual_memory().percent}%")

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
subperser_software.add_argument('-i','--install',help='install package',type=str)
args=parser.parse_args()
if args.operation=="system":
    Pprocess=args.process
    users=args.user
    enumerator(Pprocess,users)
elif args.operation=="network":
     inet=args.interface
     network(inet)
else:
    print("invalid option")