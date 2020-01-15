import json
import sys

#
#
#
# Setup for the NVIDIA-SMI reporter. This should be run first!
# 
#
#

def isIP(inpstr):
    if inpstr == 'localhost':
        return True

    cache = ''
    numdots = 0
    for i in inpstr:    
        if i == '.':
            cache = ''
            numdots += 1
            if numdots == 4:
                return False
        else:
            cache += i
            try:
                x = int(cache)
                if x > 255:
                    raise ValueError
            except Exception as e:
                return False

    return numdots == 3

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

serverPort = input("[+] Enter the port this machine listens on (default: 13768): ")

# Validate data.

if not isIP(host):
    print("[x] Invalid host, defaulting to localhost")
    host = "localhost"


try:
    port = int(port)
    if port > 65536 or port < 1:
        raise ValueError
except Exception:
    print("[x] Invalid port number, defaulting to 8086")
    port = 8086


try:
    serverPort = int(port)
    if serverPort > 65536 or serverPort < 1:
        raise ValueError
except Exception:
    print("[x] Invalid server port number, defaulting to 13768")
    serverPort = 13768


if len(database) < 1:
    print("[x] Invalid database name, defaulting to nvidia_smi")
    database = "nvidia_smi"


setupdict = {
    "host": host,
    "port": port,
    "database": database,
    "server_port": serverPort
}

with open('./config.json', 'w') as conf:
    conf.write(json.dumps(setupdict, sort_keys=True, indent='    '))

