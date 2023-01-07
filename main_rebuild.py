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

localdate = datetime.now()
generate_file_time = "{}_{}_{}_{}h{}".format(localdate.day, localdate.month, localdate.year, localdate.hour, localdate.minute)

ACTIVE_CALCULATION_TIME = 0
NULL_CALCULATION_TIME = 0
COLD_CALCULATION_TIME = 0
INSTANCE = ""
TARGET_VIDEO = ""
DETECTION_IMAGE = ""
CALCULATING_HOSTNAME = SERVER_USER
CALCULATING_INSTANCE = SERVER_IP
POD_EXISTED = 0
CALCULATION_TYPE = ""

finished = False
timestamps={}
terminate_state = defaultdict(list)


def calculate_jobs(target_pods:int, repetition: int):
    #NOTE: Null process 
    timestamps["null_state_start"]=time.time()
    calculate_null_job(target_pods, repetition, NULL_STATE)
    timestamps["null_state_end"]=time.time()
    
   #NOTE: Warm disk process: here we'll apply deployment and wait until pod is deleted
    k8s-info.config_live_time(6) # change live-time to minimum value = 6s
    timestamps["null_to_warm_disk_process_start"]=time.time()
    k8s-info.deploy_pods() # deploy pod
    calculate_null_to_warm_disk_process(target_pods, repetition, NULL_TO_WARM_DISK_PROCESS)
    timestamps["null_to_warm_disk_process_end"]=time.time()

    #NOTE: Warm disk state
    timestamps["warm_disk_state_start"]=time.time()
    calculate_warm_disk(target_pods, repetition, NULL_STATE) # during warm-disk, service is already deployed, so we'll see how much resource the system consumes
     timestamps["warm_disk_state_end"]=time.time()

    #NOTE: Warm CPU process: we'll trigger warm CPU by editing the deployment file
    multiservice_pods.config_live_time(target_pods, INSTANCE, 300) # last argument is live-time of a warm pod, current value is set manually
    timestamps["warm_disk_to_warm_CPU_process_start"]=time.time()
    calculate_warm_disk_2_warm_CPU_process(target_pods, repetition, WARM_DISK_2_WARM_CPU_PROCESS)
    timestamps["warm_disk_to_warm_CPU_process_end"]=time.time() # detect status 2/2 ready

    #NOTE: Warm CPU state, must measure time < live time
    timestamps["warm_CPU_state_start"]=time.time()
    calculate_warm_CPU_state(target_pods, repetition, WARM_CPU_STATE)
    timestamps["warm_CPU_state_end"]=time.time()

    #NOTE: this process may happen within ms, so consider ignoring it
    # in that case, comment the following block + let the code sleep for a few seconds
    # timestamps["warm_CPU_to_active_start"]=time.time()
    # jobs_status[COLD_START_PROCESSING] = True
    # calculate_warm_CPU_2_active(target_pods, repetition, WARM_CPU_2_ACTIVE)
    # timestamps["warm_CPU_to_active_end"]=time.time()

    #NOTE: Here we create a curl request towards the running pod
    print("Detection requests have arrived. ")
    create_request_thread(target_pods, "detection")
    time.sleep(10) #Here sleeping to stablize the pod for active measurement
    timestamps["active_state_start"]=time.time()
    calculate_active_job(target_pods, repetition, 30) # 30 seconds, this time must be lower than requested time
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
        calculate_warm_CPU_to_warm_disk(target_pods, repetition)
        timestamps["warm_CPU_to_warm_disk_process_end"]=time.time()
    else:
        print("Waiting for pod to be terminated")
        sleep(0.5)
    print("There is no pod in the system.")

    #NOTE: Here we calculate the process warm disk to active, maybe change
    # to the older image (one that returns immediately after code is ready)
    timestamps["warm_disk_to_active_start"]=time.time()
    cal_warm_disk_2_active(target_pods, repetition)
    timestamps["warm_disk_to_active_end"]=time.time()

    # wait until deployment scales down to zero
    scale_to_zero(target_pods)
    #NOTE: warm disk to cold by deleting image
    print("Deleting image ...")
    remote_worker_call(DELETE_IMAGE_CMD)
    sleep(5)
    print("Image is deleted ...")

    #NOTE: Cold state for 60 seconds
    timestamps["cold_state_start"]=time.time()
    calculate_cold_state(target_pods, repetition, COLD_STATE)
    timestamps["cold_state_end"]=time.time()

    #NOTE: Cold state to warm disk by downloading image

    
    #NOTE: Now we consider from warm disk to NULL state


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
    
    """ 
    call: python3 main.py [COMMAND] [TARGET_PODS] [MINUTES_WARM] 
    """
    target_pods_scale = sys.argv[2] # number of scaling pod
    # ACTIVE_CALCULATION_TIME = sys.argv[3] # active period
    repeat_time = sys.argv[4]
    INSTANCE = sys.argv[5] # jetson
    TARGET_VIDEO = sys.argv[6]
    DETECTION_IMAGE = sys.argv[7]
    # NULL_CALCULATION_TIME = sys.argv[8]
    COLD_CALCULATION_TIME = sys.argv[3]
    CALCULATION_TYPE = sys.argv[9]
    if sys.argv[1] == "master":
        # Call to source code at pi4 
        # if INSTANCE == "jetson":
        #     print("Start calculate power on jetson")
        #     CALCULATING_HOSTNAME = PI4_USER
        #     CALCULATING_INSTANCE = PI4_IP    
        # P0 is power measurement process
        # p0=Process(target=start_pi4, args=(RUN_UMMETER_AT_PI4_CMD.format(int(target_pods_scale), repeat_time, TARGET_VIDEO, generate_file_time), ))
        print("Start calculate job on {}".format(INSTANCE))
        POD_EXISTED = get_pods_existed() # initial number of pod
        calculate_jobs()
        # p1=Process(target=calculate_jobs, args=(int(target_pods_scale), repeat_time, ), daemon = True)
        # p0.start()
        # time.sleep(8) # wait for power measurement code to start
        # p1.start()
        # p1.join()
        # p0.join()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
        print("Every process is done.")

    else: print("Not recognized command")