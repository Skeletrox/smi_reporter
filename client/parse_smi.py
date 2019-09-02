import subprocess
import logging
import time
from influxwriter import writePoints
from xml.etree import ElementTree as ET
#
# Our goal is to parse the XML output of nvidia-smi
#

NVIDIA_CMD = ["nvidia-smi -q -x"]


def parseXML(xmlDump):
    tree = ET.fromstring(xmlDump)
    return tree


def loadCommand(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    return p.stdout.read()


def truncate(string, length):
    if len(string) < length:
        return string
    return string[:length-3] + "..."



def parse_smi():
    result = loadCommand(NVIDIA_CMD)
    root = parseXML(result)

    '''

    Someday when I get to work with multiple GPUs, I'll add multi-GPU support

    try:
        num_gpus = int(root.find('attached_gpus').text)
    except Exception as e:
        logging.critical("Error in getting number of GPUs: {}".format(e))

    '''

    gpu = root.find("gpu")

    #
    # The temperature is stored in root -> gpu -> temperature -> gpu_temp
    #


    temp = gpu.find("temperature").find("gpu_temp").text
    temp = int(temp[:-2]) if temp[-1] == 'C' else int((int(temp[:-2]) - 32) * 5 / 9) # Celsius vs Fahrenheit

    #
    # The used and total memory are in gpu -> fb_memory_usage
    #

    memory_usage = gpu.find("fb_memory_usage")
    total = memory_usage.find("total").text
    used = memory_usage.find("used").text

    total = int(total[:-3])
    used = int(used[:-3])

    #
    # The used percentages are in gpu -> utilization
    #

    used_perc = gpu.find("utilization")
    used_gpu = used_perc.find("gpu_util").text
    used_mem = used_perc.find("memory_util").text

    used_gpu = int(used_gpu[:-1])
    used_mem = int(used_mem[:-1])


    #
    # The processes are in gpu -> processes
    #

    processList = []
    processes = gpu.find("processes").findall("process_info")
    for p in processes:
        pid = int(p.find("pid").text)
        pname = truncate(p.find("process_name").text, 64)
        usedMemory = int(p.find("used_memory").text[:-3])
        currProcDict = {
            "pid": pid,
            "pname": pname,
            "memory": usedMemory
        }
        processList.append(currProcDict)

    valuedict = {
        "temperature": temp,
        "memory_total": total,
        "memory_used": used,
        "gpu_perc": used_gpu,
        "mem_perc": used_mem,
        "processes": processList
    }

    writePoints(valuedict)
    logging.info("Points written")

    
while True:
    try:
        parse_smi()
    except Exception as e:
        print("Error in parsing:",e)
        print(traceback.format_exc())
    time.sleep(1800)

