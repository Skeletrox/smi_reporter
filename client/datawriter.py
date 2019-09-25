import json
import requests



def writePoints(body):
    data = None
    try:
        with open('./config.json') as config:
            data = json.loads(config.read())
    
    except Exception:
        raise Exception("Error reading config file, please run setup.py again!")
        
    
    id = data.get("deviceid", None)
    database = data.get("database", None)
    host = data.get("host", None)
    port = data.get("port", None)

    if id is None or database is None or host is None or port is None:
        raise Exception("Missing fields in config, please run setup.py again!")
    client = None
    try:
        client = getClient(host, port, database)
    except Exception as e:
        print(e)
        raise e

    oldData = []
    try:
        with open('./queue.json', 'r') as queue:
            vals = queue.read()
            readVal = None
            readVal = json.loads(vals)
            oldData = readVal["points"]
    except Exception as e:
        print(e)
    finally:
        with open('./queue.json', 'w') as queue:
            queue.write(json.dumps({
                "points": []
            }))

    writableBodies = oldData
    for p in body["processes"]:
        writableBody = {
            "measurement": "gpu_reports",
            "tags": {
                "time": body["time"],
                "deviceid": id,
                "p_name": p["pname"],
            },
            "fields": {
                "temperature": body["temperature"],
                "memory_total": body["memory_total"],
                "memory_used": body["memory_used"],
                "gpu_perc": body["gpu_perc"],
                "mem_perc": body["mem_perc"],
                "p_id": p["pid"],
                "p_memory" : p["memory"]
            }
        }
        writableBodies.append(writableBody)
    try:
        client.write_points(writableBodies)
    except Exception:
        # Write these points to a file, then upload when possible
        with open('./queue.json', 'r') as queue:
            vals = queue.read()
            readVal = None
            try:
                readVal = json.loads(vals)
                readVal["points"].extend(writableBodies)
            except Exception:
                readVal = {
                    "points": [writableBodies]
                }
        with open('./queue.json', 'w') as queue:
            queue.write(json.dumps(readVal))       
    
    client.close()