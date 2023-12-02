import argparse
import platform
import psutil
import time
import subprocess
#section 1 declaring functions
#
print("enumerating...")
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
def enumerator(process):
    print("perfoming system enumeration")
    print(f"current kernel running version: {platform.release()}")
    print(f"current cpu architecture: {platform.machine()}")
    print(f"hostname: {platform.node()}")
    print("enumerating process resources...")
    time.sleep(2)
    if args.process==None:
        pass
    else:
        process_psutils=psutil.Process(process)
        cpu_percent= psutil.cpu_percent()
        cpu_time= psutil.cpu_times()
        print(f"cpu percent of process {process_psutils}: {cpu_percent}")
        print(f"cpu time: {cpu_time}")
    print("enumerating memory utilization...")
    total_memory= psutil.virtual_memory().total
    readable_total=format_size(total_memory)
    free_memory= psutil.virtual_memory().free
    readable_free=format_size(free_memory)
    buffer_memory= psutil.virtual_memory().buffers
    readable_buffer=format_size(buffer_memory)
    print(f"total memory: {readable_total}\n free: {readable_free}\n buffer: {readable_buffer}")
    print(f"{psutil.virtual_memory().percent}%")
def software(package):
    print('enumerating installed softwares,note only rpm and dpkg packages are currently supported')
    installed_packages = get_installed_packages()
    print(f"Number of installed packages: {len(installed_packages)}")
    if packages!="":
        subprocess.run('sudo','dnf','install',package)
    else:
        pass
#Section 2 command argument section
parser= argparse.ArgumentParser(description="basic resource monitor and enumerator")
subperser= parser.add_subparsers(dest="operation",required=True)
subperser_system=subperser.add_parser("system",help="system reporting")
subperser_system.add_argument("-p","--process",help="monitoring per process",type=int)
subperser_network=subperser.add_parser("network",help="network reporting")
#any neccessary arguments
subperser_software=subperser.add_parser("software",help="software reporting")
subperser_software.add_argument('-i','--install',help='install package',type=str)
args=parser.parse_args()
if args.operation=="system":
    Pprocess=args.process
    enumerator(Pprocess)
elif args.operation=="network":
    print("coming soon")
elif args.operation=="software":
    packages=args.install
    software(packages)
else:
    print("invalid option")
