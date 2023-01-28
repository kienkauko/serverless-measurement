from collections import defaultdict
from datetime import datetime
import requests
import variables
import urllib.request
import json
import time
import csv
import paramiko
import sys
import threading
from multiprocessing import Event, Process
from multiprocessing.pool import ThreadPool
import subprocess
import os
import signal
from power import pw
from variables import *
import k8s_API
from time import sleep
import re

def thread_remote(cmd : str):
    thread = threading.Thread(target=remote_worker_call, args=(cmd, )).start()
    return thread
    
def remote_worker_call(command:str, event = None):
    print("Trying to connect to remote host {}, IP: {}".format(JETSON_USERNAME, JETSON_IP))
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(JETSON_IP, username=JETSON_USERNAME, password=JETSON_PASSWORD)
    except paramiko.AuthenticationException:
        print("Authentication failed when connecting to %s" % JETSON_IP)
        sys.exit(1)
    except:
        print("Could not SSH to %s, waiting for it to start" % JETSON_IP)
    print(command)
    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    stdin.write(JETSON_PASSWORD +'\n')
    stdin.flush()
    for line in stdout:
        print (line.strip('\n'))
    client.close()
    if event is not None:
        event.set()

def get_data_from_api(query:str):
    url_data = PROMETHEUS_DOMAIN + query
    try:
        contents = urllib.request.urlopen(url_data).read().decode('utf-8')
        values=json.loads(contents)["data"]["result"][0]['value']
    except:
        values = -1
    return values

# def get_power():
#     # print(pw.get_power()/1000.0)
#     return pw.get_power()/1000.0

# def is_pod_terminating(): # check pod is terminating? consider replacing this function with Py-python
#     status = str(subprocess.run(['deployments/get_pod_status.sh', '-l'], stdout=subprocess.PIPE).stdout.decode('utf-8')).strip()
#     return status == TERMINATING_STATUS

def get_prometheus_values_and_update_job(target_pods:int, job:str, repetition: int):
    values_power = pw.get_power()/1000.0
    values_per_cpu_in_use = get_data_from_api(VALUES_CPU_QUERY.format(JETSON_IP))
    values_per_gpu_in_use = get_data_from_api(VALUES_GPU_QUERY.format(JETSON_IP))
    # values_network_receive = get_data_from_api(VALUES_NETWORK_RECEIVE_QUERY)
    values_memory = get_data_from_api(VALUES_MEMORY_QUERY.format(JETSON_IP,JETSON_IP,JETSON_IP))
    # print(values_memory)
    values_running_pods = k8s_API.get_number_pod() 
    # print(values_running_pods)

    #write values to file
    try:
        writer = csv.writer(open(DATA_PROMETHEUS_FILE_DIRECTORY.format(
            str(WORKER_HOST),str(target_pods),str(repetition),str(TARGET_VIDEO),generate_file_time), 'a'))
        writer.writerow([values_memory[0], datetime.utcfromtimestamp(values_memory[0]).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], values_running_pods, 
            values_power, values_per_cpu_in_use[1], values_per_gpu_in_use[1], values_memory[1], job])
    except:
        print("Error") 
    # if TEST_MODE: print("Current pods: %s, target: %d" % (curr_pods, (int(target_pods)+POD_EXSISTED)))

    

# def update_job_status(state:str, values_running_pods, target_pods:int):
#     #+2 on target pods for the default pods
#     curr_running_pods = int(values_running_pods[1])
#     # print(state, values_running_pods, target_pods, POD_EXISTED)
#     if WARM_DISK_2_WARM_CPU_PROCESS == state or "cold_start:curl" == state:
#         if curr_running_pods == POD_EXISTED + target_pods:
#             jobs_status[WARM_DISK_TO_WARM_CPU_PROCESS] = False
#     elif WARM_CPU_STATE == state:
#         if curr_running_pods == POD_EXISTED: # it means pods have been deleted 
#             jobs_status[WARM_CPU_STATE] = False
#     elif DELETE_JOB == state:
#         if curr_running_pods == POD_EXISTED:
#             jobs_status[DELETE_PROCESSING] = False

#NOTE: Tung will handle this function
# def create_request(url:str): # Here change to kubectl exec command by k8s python
#     #rs_response = requests.get(url)
#     rs_response = kubectl exec -it ubuntu -- "url"
#     print(rs_response.content)

def bash_cmd(cmd:str):
    result = subprocess.run([cmd], stderr=subprocess.PIPE, text=True)
    print("Bash output: {}".format(result.stderr))

# def create_request_thread(target_pods: int, request_type: str):
#     for i in range(target_pods):
#         print("Start thread :", i + 1)
#         if request_type == "start":
#             threading.Thread(target=create_request, args=("http://detection"+str(i+1)+".default.svc.cluster.local/{}/api/stream/{}/{}".format(STREAMING_IP, DETECTION_TIME))).start()
#         else if request_type == "stop":
#             threading.Thread(target=create_request, args=("http://detection"+str(i+1)+".default.svc.cluster.local/api/terminate")).start()
#         else:
#             break
            
def timestamps_to_file(timestamps: dict, target_pods:int, repetition:int):
    # print(timestamps)
    with open(DATA_TIMESTAMP_FILE_DIRECTORY.format(
        str(WORKER_HOST), str(target_pods), str(repetition), str(TARGET_VIDEO), generate_file_time), 'w') as f:
        # for key, value in terminate_state.items():
        #     timestamps[key+"_start"]=min(value)
        #     timestamps[key+"_end"]=max(value)
        for key in timestamps.keys():
            if "_start" in key:
                job_key = re.search('(.*)_start',key).group(1)
            if "_end" in key:
                job_key = re.search('(.*)_end',key).group(1)
            f.write("%s,%s,%s\n"%(key,timestamps[key],job_key))

#NOTE: the following function auto terminate pods
def auto_delete(event):
    token = True
    while not event.is_set():
        if k8s_API.is_pod_terminated() and not k8s_API.is_all_con_not_ready() and token:
            print("Detect terminating pod, it'll be deleted shortly")
            if exec_pod(CURL_TERM, "auto_delete"):
                token = False
            else:
                print("Try to terminate pod, but IP returns None, will try again!")
                token = True
        elif not k8s_API.is_pod_terminated():
            # print("Status is: {}, token is: {}".format(k8s_API.is_pod_terminated(), token))
            token = True
        else:
        # print("Status is: {}, token is: {}".format(k8s_API.is_pod_terminated(), token))
            sleep(1)
    print("Overwatch for termination finished!")

def exec_pod(cmd:str, type: str = "normal"):
    if type == "auto_delete":
        list_pod = k8s_API.get_list_term_pod(NAMESPACE)
        # print("listpodsize: {}".format(len(list_pod)))
    else:
        list_pod = k8s_API.list_namespaced_pod_status(NAMESPACE)
    for i in list_pod:
        IP = i.pod_ip
        if(IP is None):
            return False
        threading.Thread(target= k8s_API.connect_pod_exec, args=(cmd.format(IP), )).start()
        print("CMD: " + cmd.format(IP) + " has been sent.")
    return True

def config_deploy(cmd: str):
    Process(target= k8s_API.config_deploy, args=(cmd, )).start()
    # threading.Thread(target= k8s_API.config_deploy, args=(cmd, )).start()

if __name__ == "__main__":
    # print(pw.get_power()/1000.0)
    remote_worker_call("sudo ls -a")
    sleep(100)
    #sudo ctr images remove docker.io/kienkauko/nettools:latest@sha256:573c90a86216c26c02b27ce4105ea7cbf09016659fd30e8f8f61f67fab324620