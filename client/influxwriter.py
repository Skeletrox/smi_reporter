import json
from influxdb import InfluxDBClient


def getClient(host, port, database):
    client = InfluxDBClient(host=host, port=port, database=database)
    return client



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

    client = getClient(host, port, database)
    writableBodies = []
    for p in body["processes"]:
        writableBody = {
            "measurement": "gpu_reports",
            "tags": {
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
    client.write_points(writableBodies)
    client.close()