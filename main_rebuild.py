from collections import defaultdict
from datetime import datetime

import requests
import re
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
from functional_methods import *
from collect_data import *
from constants import *




# INSTANCE = ""
# TARGET_VIDEO = ""
# DETECTION_IMAGE = ""
# CALCULATING_HOSTNAME = SERVER_USER
# CALCULATING_INSTANCE = SERVER_IP
# POD_EXISTED = 0
# CALCULATION_TYPE = ""

# finished = False
timestamps = {}
# terminate_state = defaultdict(list)


def collect_life_cycle(event, target_pods: int, repetition: int):
    #NOTE: Null process 
    timestamps["null_state_start"]=time.time()
    collect_state(target_pods, repetition, NULL_STATE)
    timestamps["null_state_end"]=time.time()
    
   #NOTE: Warm disk process: here we'll apply deployment and wait until pod is deleted
    k8s_API.config_live_time(target_pods, 6) # change live-time to minimum value = 6s
    timestamps["null_to_warm_disk_process_start"]=time.time()
    k8s_API.deploy_pods() # deploy pod
    print("New deployment has been created.")
    collect_null_to_warm_disk_process(target_pods, repetition, NULL_TO_WARM_DISK_PROCESS)
    timestamps["null_to_warm_disk_process_end"]=time.time()

    #NOTE: Warm disk state
    while (k8s_API.get_number_pod(NAMESPACE) != 0):
        print("Pod number is: {}, Waiting for pod to be terminated".format(k8s_API.get_number_pod(NAMESPACE)))
        sleep(1)
    print("There is no pod in the system. Stablizing ...")
    sleep(5) # to stablize the system
    timestamps["warm_disk_state_start"]=time.time()
    collect_state(target_pods, repetition, WARM_DISK_STATE) # during warm-disk, service is already deployed, so we'll see how much resource the system consumes
    timestamps["warm_disk_state_end"]=time.time()

    #NOTE: Warm CPU process: we'll trigger warm CPU by editing the deployment file
    k8s_API.config_live_time(target_pods, LIVE_TIME) # change live-time to minimum value = 6s
    k8s_API.deploy_pods() # deploy pod
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
    exec_pod(CURL_ACTIVE_INST, "normal")
    print("Detection requests have arrived. Stablizing for at least 30 seconds ...")
    time.sleep(30) #Here sleeping to stablize the pod for active measurement
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
    while not k8s_API.is_pod_terminated():
        print("Waiting for pod to be terminated")
        sleep(0.5)
    
    timestamps["warm_CPU_to_warm_disk_process_start"]=time.time()
    collect_warm_CPU_to_warm_disk_process(target_pods, repetition, WARM_CPU_TO_WARM_DISK_PROCESS)
    timestamps["warm_CPU_to_warm_disk_process_end"]=time.time()
    print("There is no pod in the system.")

    #NOTE: Here we calculate the process warm disk to active, maybe change
    # to the older image (one that returns immediately after code is ready)
    # timestamps["warm_disk_to_active_start"]=time.time()
    # cal_warm_disk_to_active(target_pods, repetition, WARM_DISK_TO_ACTIVE_PROCESS)
    # timestamps["warm_disk_to_active_end"]=time.time()

    # wait until deployment scales down to zero
    while (k8s_API.get_number_pod(NAMESPACE) != 0):
        print("Waiting for pod to be terminated")
        sleep(1)
    print("There is no pod in the system.")

    #NOTE: warm disk to cold by deleting image
    print("Deleting image ..., may take up to 10 seconds")
    remote_worker_call(DELETE_IMAGE_CMD)
    sleep(10)
    print("Image is deleted")

    #NOTE: Cold state for 30 seconds
    timestamps["cold_state_start"]=time.time()
    collect_state(target_pods, repetition, COLD_STATE)
    timestamps["cold_state_end"]=time.time()

    #NOTE: Cold state to warm disk by downloading image
    k8s_API.config_live_time(target_pods, 6) # change live-time to minimum value = 6s
    k8s_API.deploy_pods() # reconfigure deployment
    timestamps["cold_to_warm_disk_start"]=time.time()
    collect_null_to_warm_disk_process(target_pods, repetition, COLD_TO_WARM_DISK_PROCESS)
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
    timestamps_to_file(timestamps, target_pods, repetition)
    event.set()
    print("Finished!")

if __name__ == "__main__":
    
    target_pods_scale = sys.argv[1] # number of scaling pod
    repeat_time = sys.argv[2]
    INSTANCE = sys.argv[3] # jetson
    # this P0 process runs infintely, detect and manual terminate "terminating" pods 
    event = Event() # the event is unset when created
    p0 = Process(target=auto_delete, args=(event, ))
    p0.start()
    collect_life_cycle(event, int(target_pods_scale), int(repeat_time))
    # p1 = Process(target=collect_life_cycle, args=(event, int(target_pods_scale), repeat_time, ), daemon = True)
    print("Start calculate job on {}".format(INSTANCE))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    # p1.start()
    p0.join()
    # p1.join()    

