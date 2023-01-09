from collections import defaultdict
from datetime import datetime

import requests
from constants import *
import re
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
import change_pod_info
import functional_methods
import collect_data
from tinkerforge import pw




# INSTANCE = ""
# TARGET_VIDEO = ""
# DETECTION_IMAGE = ""
# CALCULATING_HOSTNAME = SERVER_USER
# CALCULATING_INSTANCE = SERVER_IP
# POD_EXISTED = 0
# CALCULATION_TYPE = ""

finished = False
timestamps = {}
# terminate_state = defaultdict(list)


def collect_life_cycle(target_pods:int, repetition: int):
    #NOTE: Null process 
    timestamps["null_state_start"]=time.time()
    collect_state(target_pods, repetition, NULL_STATE)
    timestamps["null_state_end"]=time.time()
    
   #NOTE: Warm disk process: here we'll apply deployment and wait until pod is deleted
    k8s_API.config_live_time(, target_pods, ,6) # change live-time to minimum value = 6s
    timestamps["null_to_warm_disk_process_start"]=time.time()
    k8s_API.deploy_pods() # deploy pod
    print("New deployment has been created.")
    collect_null_to_warm_disk_process(target_pods, repetition, NULL_TO_WARM_DISK_PROCESS)
    timestamps["null_to_warm_disk_process_end"]=time.time()

    #NOTE: Warm disk state
    while (k8s_API.get_number_pod(NAMESPACE) != 0):
        print("Waiting for pod to be terminated")
        sleep(1)
    print("There is no pod in the system.")
    sleep(5) # to stablize the system
    timestamps["warm_disk_state_start"]=time.time()
    collect_state(target_pods, repetition, WARM_DISK_STATE) # during warm-disk, service is already deployed, so we'll see how much resource the system consumes
     timestamps["warm_disk_state_end"]=time.time()

    #NOTE: Warm CPU process: we'll trigger warm CPU by editing the deployment file
    k8s_API.config_live_time(, target_pods, ,100) # change live-time to minimum value = 6s
    timestamps["warm_disk_to_warm_CPU_process_start"]=time.time()
    collect_warm_disk_to_warm_CPU_process(target_pods, repetition, WARM_DISK_TO_WARM_CPU_PROCESS)
    timestamps["warm_disk_to_warm_CPU_process_end"]=time.time() 

    #NOTE: Warm CPU state, must measure time < live time
    timestamps["warm_CPU_state_start"]=time.time()
    collect_state(target_pods, repetition, WARM_CPU_STATE)
    timestamps["warm_CPU_state_end"]=time.time()

    #NOTE: this process may happen within ms, so consider ignoring it
    # in that case, comment the following block + let the code sleep for a few seconds
    # timestamps["warm_CPU_to_active_start"]=time.time()
    # jobs_status[COLD_START_PROCESSING] = True
    # calculate_warm_CPU_2_active(target_pods, repetition, WARM_CPU_2_ACTIVE)
    # timestamps["warm_CPU_to_active_end"]=time.time()

    #NOTE: Here we create a curl request towards the running pod
    create_request_thread(target_pods, "detection")
    print("Detection requests have arrived. ")
    time.sleep(10) #Here sleeping to stablize the pod for active measurement
    timestamps["active_state_start"]=time.time()
    collect_state(target_pods, repetition, ACTIVE_STATE) # 30 seconds, this time must be lower than requested time
    timestamps["active_state_end"]=time.time()

    #NOTE: Here we'll force terminate a pod after its time_window runs out.
    # Pre-condition: processing time of task must > time_window
    # force_terminate(target_pods)
    # timestamps["active_to_warm_disk_start"]=time.time()
    # calculate_active_2_warm_disk(target_pods, repetition)
    # timestamps["active_to_warm_disk_end"]=time.time()

    #NOTE: Warm CPU to warm disk: How to detect the pod is staying at warm CPU or active?: Check status terminating
    if is_pod_terminated(NAMESPACE):
        timestamps["warm_CPU_to_warm_disk_process_start"]=time.time()
        collect_warm_CPU_to_warm_disk_process(target_pods, repetition, WARM_CPU_TO_WARM_DISK_PROCESS)
        timestamps["warm_CPU_to_warm_disk_process_end"]=time.time()
    else:
        print("Waiting for pod to be terminated")
        sleep(0.5)
    print("There is no pod in the system.")

    #NOTE: Here we calculate the process warm disk to active, maybe change
    # to the older image (one that returns immediately after code is ready)
    timestamps["warm_disk_to_active_start"]=time.time()
    cal_warm_disk_to_active(target_pods, repetition, WARM_DISK_TO_ACTIVE_PROCESS)
    timestamps["warm_disk_to_active_end"]=time.time()

    # wait until deployment scales down to zero
    while (k8s_API.get_number_pod(NAMESPACE) != 0):
        print("Waiting for pod to be terminated")
        sleep(1)
    print("There is no pod in the system.")

    #NOTE: warm disk to cold by deleting image
    print("Deleting image ...")
    remote_worker_call(DELETE_IMAGE_CMD)
    sleep(10)
    print("Image is deleted")

    #NOTE: Cold state for 30 seconds
    timestamps["cold_state_start"]=time.time()
    collect_state(target_pods, repetition, COLD_STATE)
    timestamps["cold_state_end"]=time.time()

    #NOTE: Cold state to warm disk by downloading image
    k8s_API.config_live_time(, target_pods, , 6) # change live-time to minimum value = 6s
    timestamps["cold_to_warm_disk_start"]=time.time()
    collect_cold_to_warm_disk_process(target_pods, repetition, COLD_TO_WARM_DISK_PROCESS)
    timestamps["cold_to_warm_disk_end"]=time.time()
    
    #NOTE: Now we consider from warm_disk/CPU to NULL state
    timestamps["warm_disk_to_null_start"]=time.time()
    k8s_API.delete_pods() # deploy pod
    remote_worker_call(DELETE_IMAGE_CMD)
    collect_term_process(target_pods, repetition, WARM_DISK_TO_NULL_PROCESS)
    timestamps["warm_disk_to_null_end"]=time.time()

    # Maybe multiprocessing should be considered here
    # timestamps["warm_disk_to_null_start"]=time.time()
    # p0=Process(target=remote_worker_call, args=(DELETE_IMAGE.format(image), ))
    # p0.start()
    # multiservice_pods.delete_pods()
    # calculate_warm_disk_2_null_process(target_pods, repetition)
    # timestamps["warm_disk_to_null_end"]=time.time()

    print("Measurement finished.")
    print("Saving timestamps..")
    timestamps_to_file(target_pods, repetition)
    print("Done")
    global finished
    finished = True
    return

if __name__ == "__main__":
    
    target_pods_scale = sys.argv[1] # number of scaling pod
    repeat_time = sys.argv[2]
    INSTANCE = sys.argv[3] # jetson
    # this P0 process runs infintely, detect and manual terminate "terminating" pods 
    p0 = Process(target=functional_methods.auto_delete, args=(NAMESPACE),))
    p1 = Process(target=calculate_jobs, args=(int(target_pods_scale), repeat_time, ), daemon = True)
    print("Start calculate job on {}".format(INSTANCE))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    p0.start()
    p1.start()
    p1.join()
    p0.join()    
    print("Every process is done.")

