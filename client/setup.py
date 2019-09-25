import json
import sys
from uuid import uuid4

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

# Give a unique uuid for this client
deviceUUID = uuid4()

# Take inputs for host IP address, and host port

host = input("[+] Enter the IP address of the host (default: localhost): ")
port = input("[+] Enter the port the server listens on (default: 13768): ")

# Validate data. TODO: Check for host IP?

if len(host) < 1:
    host = "localhost"

if len(port) < 1:
    port = "13768"

try:
    port = int(port)
except Exception:
    print("[x] Invalid port number, defaulting to 13768")
    port = 13768




setupdict = {
    "deviceid": str(deviceUUID),
    "host": host,
    "port": port,
}

with open('./config.json', 'w') as conf:
    conf.write(json.dumps(setupdict, sort_keys=True, indent='    '))

