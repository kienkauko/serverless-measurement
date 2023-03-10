from variables import *
import time
from functional_methods import *
import k8s_API
import threading 


def collect_null_state(target_pods:int, repetition: int, state:str):
    print("Scenario: Measure NULL state - started")
    count = 0
    while jobs_status[state]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.5)
        count = count + 0.5
        if count == int(STATE_COLLECT_TIME):
            jobs_status[state] = False
    print("Scenario: Measure NULL state - Ended")

# def collect_warm_CPU_state(target_pods:int, repetition: int, state:str):
#     print("Scenario: WARM CPU state - Started")
#     while jobs_status[state]:
#         get_prometheus_values_and_update_job(target_pods, WARM_JOB, repetition)
#         time.sleep(0.5)
#     print("Scenario: WARM CPU state - Ended")

# def collect_cold_state(target_pods:int, repetition: int, state: str):
#     print("Scenario: COLD state - Started")
#     while jobs_status[COLD_CPU_STATE]:
#         get_prometheus_values_and_update_job(target_pods, COLD_CPU_STATE, repetition)
#         time.sleep(0.5)
#     print("Scenario: COLD state - Ended")

# def collect_active_state(target_pods:int, repetition: int, state:str):
#     print("Scenario: ACTIVE - Started")
#     active_calculation_time_count = 0
#     while jobs_status[state]:
#         get_prometheus_values_and_update_job(target_pods, state, repetition)
#         time.sleep(0.5)
#         active_calculation_time_count = active_calculation_time_count + 0.5
#         if active_calculation_time_count == int(ACTIVE_CALCULATION_TIME):
#             # multiservice_pods.delete_pods()
#             jobs_status[state] = False
#     print("Scenario: ACTIVE - Ended")

#NOTE: this function general represents the STATE collection functions 
def collect_state(target_pods:int, repetition: int, state:str):
    print("Scenario: Measure {} - started".format(state))
    count = 0
    while jobs_status[state]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.5)
        count = count + 0.5
        if count == int(STATE_COLLECT_TIME):
            jobs_status[state] = False
    print("Scenario: Measure {} - Ended".format(state))

def collect_warm_disk_to_warm_CPU_process(target_pods:int, repetition: int, state:str):
    print("Scenario: Warm disk to warm CPU - Started")
    while jobs_status[state]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.3)
        if k8s_API.get_number_running_pod() == target_pods and k8s_API.is_all_con_ready() == True: # detect status 2/2 ready
            jobs_status[state] = False
    print("Scenario: Warm disk to warm CPU - Ended")

# def collect_active_to_warm_disk_process(target_pods:int, repetition:int, state:str):
#     print("Scenario: Active to warm disk - Started")
#     while jobs_status[state]:
#         get_prometheus_values_and_update_job(target_pods, state, repetition)
#         time.sleep(0.3)
#         if k8s_API.get_number_pod(NAMESPACE) == 0:  # detect if no pod exists
#             jobs_status[state] = False
#     print("Scenario: Active to warm disk - Ended")

def collect_warm_CPU_to_warm_disk_process(target_pods:int, repetition:int, state:str):
    print("Scenario: {} - Started".format(state))
    while jobs_status[state]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.3)
        if k8s_API.get_number_pod(NAMESPACE) == 0:  # detect if no pod exists
            jobs_status[state] = False
    print("Scenario: {} - Ended".format(state))

#NOTE: general function for active/warmCPU to warm disk/null
def collect_term_process(target_pods:int, repetition:int, state:str):
    print("Scenario: {} - Started".format(state))
    while jobs_status[state]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.3)
        if k8s_API.get_number_pod(NAMESPACE) == 0:  # detect if no pod exists
            jobs_status[state] = False
    print("Scenario: {} - Ended".format(state))

def collect_null_to_warm_disk_process(target_pods:int, repetition:int, state:str):
    print("Scenario: {} - Started".format(state))
    while jobs_status[state]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.3)
        if  k8s_API.is_image_available("random", ) == True:  # detect if image has been pulled successfully
            jobs_status[state] = False
    print("Scenario: {} - Ended".format(state))

def collect_null_to_cold_process(target_pods:int, repetition:int, state:str):
    print("Scenario: {} - Started".format(state))
    while jobs_status[state]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.3)
        if  k8s_API.is_endpoint_available() == True:  # detect if image has been pulled successfully
            jobs_status[state] = False
    print("Scenario: {} - Ended".format(state))

def collect_cold_to_null_process(target_pods:int, repetition:int, state:str):
    print("Scenario: {} - Started".format(state))
    while jobs_status[state]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.3)
        if  not k8s_API.is_endpoint_available():  # detect if image has been pulled successfully
            jobs_status[state] = False
    print("Scenario: {} - Ended".format(state))

def collect_warm_disk_to_cold_process(target_pods:int, repetition:int, state:str, event):
    print("Scenario: {} - Started".format(state))
    while jobs_status[state]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.3)
        if  event.is_set():  # detect if image has been pulled successfully
            jobs_status[state] = False
    print("Scenario: {} - Ended".format(state))