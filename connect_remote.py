import paramiko
import yaml
import getpass
import sys
import argparse
import json

class EnumerateHost:
    def __init__(self, hosts, user, password, key):
        self.hosts = hosts
        self.user = user
        self.password = password
        self.key = key
        self.clients = []
        
        for host in self.hosts:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.clients.append(client)

            try:
                if password is not None:
                    client.connect(hostname=host, username=self.user, password=self.password)
                elif key is not None:
                    client.connect(hostname=host, username=self.user, key_filename=self.key)
            except paramiko.AuthenticationException:
                print(f'Authentication error for host: {host}')
                sys.exit(2)
            except paramiko.ssh_exception.NoValidConnectionsError:
                print(f'Failed to connect to host: {host}')
                sys.exit(2)
            except TimeoutError:
                print(f'Connection timed out for host: {host}')
                sys.exit(2)

    def execute_commands(self, yaml_filename):
        yaml_file = open(yaml_filename, 'r')
        loaded_yaml_file = yaml.safe_load(yaml_file.read())
        tasks_json_loads = {}

        for host in self.hosts:
            tasks_json_loads[host] = {}

            for task in loaded_yaml_file['tasks']:
                stdin, stdout, stderr = self.clients[self.hosts.index(host)].exec_command(task)
                output = stdout.read().decode('utf-8')
                error = stderr.read().decode('utf-8')

                if error:
                    print(f"Error occurred on host {host}: {error}")

                tasks_json_loads[host][task] = output

        print(json.dumps(tasks_json_loads, indent=3))

        for client in self.clients:
            client.close()

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', help="host to connect via ssh", nargs='+')
parser.add_argument('-u', '--user', help="user to authenticate with", required=True)
parser.add_argument('-p', '--password', help="the password for the user", action="store_true")
parser.add_argument('-k', '--key', help="the ssh key file to authenticate instead of password")
parser.add_argument('-f', '--file', help="YAML file containing the list of hosts", required=True)
args = parser.parse_args()

host = args.host
user = args.user
yam_file = args.file

if args.password:
    password = getpass.getpass('Enter your password: ')
    key = None
elif args.key:
    key = args.key
    password = None
else:
    print("Please specify either a password or key for authentication.")
    sys.exit(2)

hosts_file = open(args.file, 'r')
loaded_hosts_file = yaml.safe_load(hosts_file.read())
hosts = loaded_hosts_file['hosts']

enumeratehost = EnumerateHost(hosts=hosts, user=user, password=password, key=key)
enumeratehost.execute_commands(yam_file)