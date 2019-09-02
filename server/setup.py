import json
import sys

#
#
# Setup for the NVIDIA-SMI reporter. This should be run first!
# 
#
#

#
# Check for the config file. If it exists, terminate
#

try:
    z = open('./config.json')
    print("[!] Config file already exists! Modify config.json to add your new changes.")
    z.close()
    sys.exit(0)

except Exception:
    pass

# Take inputs for database name, database port and host

host = input("[+] Enter the IP address of the host (default: localhost): ")
port = input("[+] Enter the port the database listens on (default: 8086): ")

database = input("[+] Enter the name of the database (default: nvidia_smi): ")

# Validate data. TODO: Check for host IP?

if len(host) < 1:
    host = "localhost"

if len(port) < 1:
    port = "8086"

try:
    port = int(port)
except Exception:
    print("[x] Invalid port number, defaulting to 8086")
    port = 8086

if len(database) < 1:
    database = "nvidia_smi"


setupdict = {
    "host": host,
    "port": port,
    "database": database
}

with open('./config.json', 'w') as conf:
    conf.write(json.dumps(setupdict, sort_keys=True, indent='    '))

