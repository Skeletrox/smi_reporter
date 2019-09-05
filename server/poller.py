import threading
import time
import json
import traceback
import pandas as pd
from influxdb import DataFrameClient
from collections import OrderedDict
import datetime
import pickle
import matplotlib.pyplot as plt

class InfluxPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            try:
                message, deviceID = pollInflux()
                if message is not None:
                    updateUser(message, deviceID)
            except Exception as e:
                print("Error in polling:",e)
                print(traceback.format_exc())
            time.sleep(1800)

def generateMessage(gpuUsage, appUsage):
    gpuLogs = OrderedDict(sorted([(k, v) for k, v in gpuUsage.items()], key= lambda x: x[0]))

    texts = []
    for (key, val) in gpuLogs.items():
        currentString = "Alert! At {}, GPU usage was {}% and GPU Memory usage was {}%\n".format(key, val["proc"], val["mem"])
        texts.append(currentString)

    texts.append("\n-------\nApp Logs\n--------\n")
    for app, appValues in appUsage.items():
        appLogs = OrderedDict(sorted([(k, v) for k, v in appValues.items()], key= lambda x: x[0]))
        for (key, val) in appLogs.items():
            currentString = "At {}, app {} was using {} MiB on the GPU\n".format(key, app, val["mem"])
            texts.append(currentString)

    returnable = "\n".join(texts)
    return returnable




def pollInflux():
    configData = None
    with open("./config.json") as config:
        configData = json.loads(config.read())
        
    host = configData["host"]
    port = configData["port"]
    database = configData["database"]
    client = DataFrameClient(host=host, port=port, database=database)
    results = client.query("SELECT time, deviceid, gpu_perc, mem_perc, memory_total, memory_used, p_id, p_memory, p_name, temperature FROM gpu_reports WHERE time > now() - 30m")
    df = None
    try:
        df = pd.DataFrame(results["gpu_reports"])
    except Exception as e:
        return None, None
    deviceID = ""
    gpuUsageDict = {}
    appUsageDict = {}
    df["time"] = df.index
    df.reset_index(drop=True, inplace=True)
    deviceID = df.iloc[0].deviceid
    for row in df.itertuples():
        if row.gpu_perc >= 75 or row.mem_perc >= 75:
            currTime = row.time.strftime("%m/%d/%Y %H:%M:%S %Z")
            gpuUsageDict[currTime] = {"mem": row.mem_perc, "proc": row.gpu_perc}
            application = row.p_name
            usage = row.p_memory
            currAppUsageDict = appUsageDict.get(application,{})
            currAppUsageDict[currTime] = {"mem": row.p_memory}
            appUsageDict[application] = currAppUsageDict
    
    if len(gpuUsageDict) == 0:
        return None, deviceID
    message = generateMessage(gpuUsageDict, appUsageDict)
    return message, deviceID


def updateUser(message, deviceID):
    chatID = None
    try:
        with open("./device_to_chat.json", 'r') as dtc:
            chatID = json.loads(dtc.read())[deviceID]
    except Exception as e:
        print("Device not registered yet.")
        raise e
    
    botAndUpdate = {}
    with open("./botAndUpdate_{}.bau".format(chatID), "rb") as bau:
        botAndUpdate = pickle.loads(bau.read())
    
    bot = botAndUpdate["bot"]
    update = botAndUpdate["update"]
    bot.sendMessage(chat_id=chatID, text=message)


def pollForGraphs(deviceID, timeRange):
    configData = None
    with open("./config.json") as config:
        configData = json.loads(config.read())
        
    host = configData["host"]
    port = configData["port"]
    database = configData["database"]
    client = DataFrameClient(host=host, port=port, database=database)
    query = "SELECT gpu_perc, mem_perc FROM gpu_reports WHERE deviceid='{}' AND time > now() - {}".format(deviceID, timeRange)
    client.close()
    results = client.query(query)
    df = None
    try:
        df = pd.DataFrame(results["gpu_reports"])
    except Exception as e:
        return None
    needed_df_subset = df[["gpu_perc", "mem_perc"]]
    needed_df_subset.plot()
    plt.savefig("./{}.png".format(deviceID))
    return deviceID


def pollForTemperature(deviceID, timeRange):
    configData = None
    with open("./config.json") as config:
        configData = json.loads(config.read())
        
    host = configData["host"]
    port = configData["port"]
    database = configData["database"]
    client = DataFrameClient(host=host, port=port, database=database)
    query = "SELECT temperature FROM gpu_reports WHERE deviceid='{}' AND time > now() - {}".format(deviceID, timeRange)
    client.close()
    results = client.query(query)
    df = None
    try:
        df = pd.DataFrame(results["gpu_reports"])
    except Exception as e:
        return None
    df.plot()
    plt.savefig("./{}_temp.png".format(deviceID))
    return deviceID