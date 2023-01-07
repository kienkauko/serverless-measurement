from constants import *
import time

jobs_status = {
    NULL_PROCESSING : True,
    WARM_DISK : True,
    COLD_START_PROCESSING : True,
    WARM_PROCESSING : True,
    COLD_PROCESSING : True,
    ACTIVE_PROCESSING : True,
    DELETE_PROCESSING : True}

def calculate_null_job(target_pods:int, repetition: int, state:str):
    print("Scenario: Measure NULL state - starting ...")
    count = 0
    while jobs_status[NULL_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.5)
        count = count + 0.5
        if count == int(NULL_CALCULATION_TIME):
            jobs_status[NULL_PROCESSING] = False
    print("Scenario: Measure NULL state - Ended!")

def calculate_warm_disk_2_warm_CPU_process(target_pods:int, repetition: int, state:str):
    print("Scenario: Warm disk to warm CPU - Started...")
    while jobs_status[WARM_DISK_2_WARM_CPU_PROCESS]:
        get_prometheus_values_and_update_job(target_pods, state, repetition)
        time.sleep(0.5)
    print("Scenario: Warm disk to warm CPU - Ended...")

def calculate_warm_CPU_state(target_pods:int, repetition: int):
    print("Scenario: WARM CPU state - Started...")
    while jobs_status[WARM_CPU_STATE]:
        get_prometheus_values_and_update_job(target_pods, WARM_JOB, repetition)
        time.sleep(0.5)
    print("Scenario: WARM CPU state - Ended...")

def WARM_CPU_2_ACTIVE(target_pods:int, repetition: int):
    print("Scenario: COLD - Started...")
    cold_caculation_time_count = 0
    while jobs_status[WARM_CPU_2_ACTIVE_PROCESS]:
        get_prometheus_values_and_update_job(target_pods, COLD_STATE, repetition)
        time.sleep(0.5)
        cold_caculation_time_count = cold_caculation_time_count + 0.5
        if cold_caculation_time_count == int(COLD_CALCULATION_TIME):
            jobs_status[WARM_CPU_2_ACTIVE_PROCESS] = False
    print("Scenario: COLD - Ended...")

def calculate_active_job(target_pods:int, repetition: int):
    print("Scenario: ACTIVE - Started...")
    active_calculation_time_count = 0
    while jobs_status[ACTIVE_PROCESSING]:
        get_prometheus_values_and_update_job(target_pods, ACTIVE_JOB, repetition)
        time.sleep(0.5)
        active_calculation_time_count = active_calculation_time_count + 0.5
        if active_calculation_time_count == int(ACTIVE_CALCULATION_TIME):
            # multiservice_pods.delete_pods()
            jobs_status[ACTIVE_PROCESSING] = False
    print("Scenario: ACTIVE - Ended...")

def calculate_active_2_warm_disk(target_pods:int, repetition: int):
    print("Scenario: Active to warm disk - Started...")
    while jobs_status[ACTIVE_2_WARM_DISK_PROCESS]:
        get_prometheus_values_and_update_job(target_pods, DELETE_JOB, repetition)
        time.sleep(0.5)
        if k8s_API.get_number_pod(NAMESPACE) == 0:  # detect if no pod exists
            jobs_status[ACTIVE_2_WARM_DISK_PROCESS] = False
    print("Scenario: Active to warm disk - Ended...")

def calculate_warm_CPU_to_warm_disk(target_pods:int, repetition:int):
    print("Scenario: Warm CPU to warm disk - Started...")
    while jobs_status[WARM_CPU_TO_WARM_DISK_PROCESS]:
        get_prometheus_values_and_update_job(target_pods, DELETE_JOB, repetition)
        time.sleep(0.5)
        if k8s_API.get_number_pod(NAMESPACE) == 0:  # detect if no pod exists
            jobs_status[WARM_CPU_TO_WARM_DISK_PROCESS] = False
    print("Scenario: Warm CPU to warm disk - Ended...")
