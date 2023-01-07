
from collections import defaultdict
from datetime import datetime
import requests
from constants import *
import urllib.request
import json
import time
import csv
import paramiko
import pods
import sys
import threading
from multiprocessing import Event, Process
from multiprocessing.pool import ThreadPool
from pods import *
import subprocess
import os
import signal
import multiservice_pods
from tinkerforge import pw

def force_terminate(target_pods:int):
    count = 0
    while get_pods_status(NAMESPACE, "terminating") != target_pods:
        if(count % 10)
            print("waiting for pod to be terminated by the system, wating time is: {}s".format(count))
        count = count + 1
        sleep(1)
    print("Termination cmd has been sent by the system, perform force delete now ...")
    create_request_thread(target_pods, "terminating")
    print("Force termination cmd has been sent")

# def start_master(command:str):
 
#     client = paramiko.SSHClient()
#     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     client.connect(MASTER_HOST, username=MASTER_USERNAME, password=MASTER_PASSWORD)
#     print(command)
#     stdin, stdout, stderr = client.exec_command(command)
#     for line in stdout:
#         print (line.strip('\n'))
#     client.close()

def remote_worker_call(command:str):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(JETSON_IP, username=JETSON_USERNAME, password=JETSON_PASSWORD)
    print(command)
    stdin, stdout, stderr = client.exec_command(command)

    for line in stdout:
        print (line.strip('\n'))

    client.close()

def get_data_from_api(query:str):
    url_data = PROMETHEUS_DOMAIN + query
    try:
        contents = urllib.request.urlopen(url_data).read().decode('utf-8')
        values=json.loads(contents)["data"]["result"][0]['value']
    except:
        values = -1
    return values

def get_power():
    return pw.get_power()/1000.0

# def is_pod_terminating(): # check pod is terminating? consider replacing this function with Py-python
#     status = str(subprocess.run(['deployments/get_pod_status.sh', '-l'], stdout=subprocess.PIPE).stdout.decode('utf-8')).strip()
#     return status == TERMINATING_STATUS

def get_prometheus_values_and_update_job(target_pods:int, job:str, repetition: int):
    values_power = get_power()
    values_per_cpu_in_use = get_data_from_api(VALUES_CPU_QUERY.format(CALCULATING_INSTANCE))
    values_memory = get_data_from_api(VALUES_MEMORY_QUERY.format(CALCULATING_INSTANCE,CALCULATING_INSTANCE,CALCULATING_INSTANCE))
    values_running_pods = get_data_from_api(VALUES_PODS_QUERY.format(CALCULATING_HOSTNAME))    
    update_job_status(job, values_running_pods, target_pods)
    # if is_pod_terminating():
    #     if WARM_STATE != job or (WARM_STATE == job and ((int(values_running_pods[1])-int(POD_EXISTED)) <= target_pods)):
    #         job = job + ":terminating"
    #         terminate_state[job].append(time.time())
    #write values to file
    try:
        writer = csv.writer(open(DATA_PROMETHEUS_FILE_DIRECTORY.format(
            str(INSTANCE),str(CALCULATION_TYPE),str(target_pods),str(repetition),str(TARGET_VIDEO),str(INSTANCE),generate_file_time), 'a'))
        writer.writerow([values_running_pods[0],datetime.utcfromtimestamp(values_running_pods[0]).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], values_running_pods[1], values_power, values_per_cpu_in_use[1], values_memory[1], job])
    except:
        print("Error") 
    # if TEST_MODE: print("Current pods: %s, target: %d" % (curr_pods, (int(target_pods)+POD_EXSISTED)))

    

def update_job_status(state:str, values_running_pods, target_pods:int):
    #+2 on target pods for the default pods
    curr_running_pods = int(values_running_pods[1])
    # print(state, values_running_pods, target_pods, POD_EXISTED)
    if WARM_DISK_2_WARM_CPU_PROCESS == state or "cold_start:curl" == state:
        if curr_running_pods == POD_EXISTED + target_pods:
            jobs_status[WARM_DISK_2_WARM_CPU_PROCESS] = False
    elif WARM_CPU_STATE == state:
        if curr_running_pods == POD_EXISTED: # it means pods have been deleted 
            jobs_status[WARM_CPU_STATE] = False
    elif DELETE_JOB == state:
        if curr_running_pods == POD_EXISTED:
            jobs_status[DELETE_PROCESSING] = False

#NOTE: Tung will handle this function
def create_request(url: str): # Here change to kubectl exec command by k8s python
    #rs_response = requests.get(url)
    rs_response = kubectl exec -it ubuntu -- "url"
    print(rs_response.content)

def create_request_thread(target_pods: int, request_type: str):
    for i in range(target_pods):
        print("Start thread :", i + 1)
        if request_type == "start":
            threading.Thread(target=create_request, args=("http://detection"+str(i+1)+".default.svc.cluster.local/{}/api/stream/{}/{}".format(STREAMING_IP, DETECTION_TIME)).start()
        else if request_type == "stop":
            threading.Thread(target=create_request, args=("http://detection"+str(i+1)+".default.svc.cluster.local/{}/api/terminate").start()
        else:
            break
            
def timestamps_to_file(target_pods:int, repetition:int):
    print(timestamps)
    with open(DATA_TIMESTAMP_FILE_DIRECTORY.format(
        str(INSTANCE), str(CALCULATION_TYPE), str(target_pods), str(repetition), str(TARGET_VIDEO), str(INSTANCE), generate_file_time), 'w') as f:
        for key, value in terminate_state.items():
            timestamps[key+"_start"]=min(value)
            timestamps[key+"_end"]=max(value)

        for key in timestamps.keys():
            if "_start" in key:
                job_key = re.search('(.*)_start',key).group(1)
            if "_end" in key:
                job_key = re.search('(.*)_end',key).group(1)
            f.write("%s,%s,%s\n"%(key,timestamps[key],job_key))

def 