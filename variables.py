from lib2to3.pgen2.token import COLON, SLASH
from kubernetes import client, config
from datetime import datetime
import os
INSTANCE = 'mec'
# INSTANCE = 'jetson'
WORKER_HOST = INSTANCE

# HOST IP
MASTER_HOST = "localhost"
END_HOST = "jetson"  # Khong dung
MEC_HOST = "mec"  # Khong dung
MASTER_USERNAME = "master"  # Khong dung
MASTER_PASSWORD = "kienlu123"
PROM_IP = "172.16.42.11"
JETSON_IP = "172.16.42.12"
# JETSON_IP = '192.168.1.2'
JETSON_USERNAME = "mec"
# JETSON_USERNAME = 'end'
JETSON_PASSWORD = "1"
# STREAMING_IP = "172.16.42.11"
STREAMING_IP = "192.168.2.2"
NAMESPACE = "serverless"


# PORT
PROMETHEUS_PORT = "9090"
STREAMING_PORT = "1935"
# STREAMING_PORT = "12345"
# Common
COLON = ":"
SLASH = "/"
TEST_MODE = False

# Network interfacte
NETWORK_INTERFACE = "eth0"
PROMETHEUS_DOMAIN = "http://" + PROM_IP + COLON + \
    PROMETHEUS_PORT + "/api/v1/query?query="
# SERVICE_DOMAIN = "http://serverless.default.svc.cluster.local"  # Khong dung
HEAVY_DNS = "http://detection{}.serverless.svc.cluster.local"
# constant values
# CALCULATION_TYPE = "normal"     # revert_lifecircle
# TARGET_VIDEO = "detection"  # Khong dung
STATE_COLLECT_TIME = 60  # 60
CURL_COLLECT_TIME = 10
NULL_CALCULATION_TIME = 10
# ACTIVE_CALCULATION_TIME = 30
DETECTION_TIME = 200  # 200
LIVE_TIME = 300  # 240
IMAGE_QUALITY = "2K"

# QUERY
VALUES_CPU_QUERY = "100-(avg%20by%20(instance,job)(irate(node_cpu_seconds_total{{mode='idle',job='prometheus',instance='{}:9100'}}[30s])*100))"
# 100-(avg%20by%20(instance,job)(irate(node_cpu_seconds_total{mode='idle',job='prometheus',instance='172.16.42.12:9100'}[30s])*100))
VALUES_MEMORY_QUERY = "((node_memory_MemTotal_bytes{{job='prometheus',instance='{}:9100'}}-node_memory_MemAvailable_bytes{{job='prometheus',instance='{}:9100'}})/(node_memory_MemTotal_bytes{{job='prometheus',instance='{}:9100'}}))*100"
VALUES_NETWORK_RECEIVE_QUERY = "rate(node_network_receive_bytes_total{{device='" + \
    NETWORK_INTERFACE+"',instance='{}:9100'}}[1m])/(1024*1024)"
# VALUES_GPU_QUERY = "gpu_utilization{{device='jetson',instance='{}:9100',job='prometheus'}}"
if JETSON_IP == '172.16.42.12':
    VALUES_GPU_QUERY = "nvidia_smi_utilization_gpu_ratio{{instance='{}:9835'}}"
else:
    VALUES_GPU_QUERY = "gpu_utilization_percentage_Hz{{instance='{}:9200',nvidia_gpu='utilization'}}"
# SERVER_FOLDER = "server"
DATA_UMMETER_FOLDER = "data_ummeter"
PULLING_TIME_FOLDER = "pulling_time"
PI4_FOLDER = "pi4"

# FILE NAME
POD_START_TIME_FILENAME = "pod_start_time_{}_{}.csv"
DATA_PROMETHEUS_AT_PI4_FILENAME = "data-prometheus_{}_{}_pi4.csv"
TIMESTAMP_FILENAME = "timestamps_{}_{}_server.csv"
DATA_UMMETER_FILENAME = "data_ummeter_{}_{}.csv"
DATA_PULLING_IMAGE_FILENAME = "data_pulling_image_{}_{}.csv"

# DIRECTORIES
DEFAULT_DIRECTORY = os.getcwd()
DATA_DIRECTORY = DEFAULT_DIRECTORY + "/data/"
POD_START_TIME_DATA_FILE_DIRECTOR = DATA_DIRECTORY + POD_START_TIME_FILENAME
DEPLOYMENT_PATH = DEFAULT_DIRECTORY + "/deploy.yaml"
TEMPLATE_PATH = DEFAULT_DIRECTORY + "/template.yaml"

BASH_PATH = DEFAULT_DIRECTORY + "/deployments"
DATA_PROMETHEUS_AT_PI4_FILE_DIRECTORY = DATA_DIRECTORY + \
    PI4_FOLDER + SLASH + DATA_PROMETHEUS_AT_PI4_FILENAME
DATA_UMMETER_FILE_DIRECTORY = DATA_DIRECTORY + \
    DATA_UMMETER_FOLDER + SLASH + DATA_UMMETER_FILENAME
PULLING_TIME_DATA_FILE_DIRECTORY = DATA_DIRECTORY + \
    PULLING_TIME_FOLDER + SLASH + DATA_PULLING_IMAGE_FILENAME

DATA_PROMETHEUS_FILE_DIRECTORY = DEFAULT_DIRECTORY + \
    "/data/resource/{}/{}_pod_{}_rep_{}_{}.csv"
DATA_TIMESTAMP_FILE_DIRECTORY = DEFAULT_DIRECTORY + \
    "/data/timestamp/{}/time_{}_pod_{}_rep_{}_{}.csv"
DATA_CURL_FILE_DIRECTORY = DEFAULT_DIRECTORY + \
    "/data/curl/{}/{}_pod_{}_rep_{}_{}.csv"
# CMD

# IMAGE_NAME = "hctung57/object-detection-arm:4.6.1.10@sha256:7361b88965a4bb39a693450902ad660e1722f4a9da677b36374318cc0023d771" #SHA code is required
HEAVY_IMAGE_NAME_ARM = "docker.io/kiemtcb/detection-object:4.2arm@sha256:9161d9188d1c196ade0e3555a2618bee41cfae9ac713a62e7b6c8419bb59e081"  # SHA code is required
HEAVY_WRONG_IMAGE_NAME_ARM = "docker.io/kiemtcb/detection-ob:4.2arm@sha256:9161d9188d1c196ade0e3555a2618bee41cfae9ac713a62e7b6c8419bb59e081"  # SHA code is required
HEAVY_IMAGE_NAME_X86 = "docker.io/kiemtcb/detection-object:4.2x86@sha256:326e47e0290094fcfe71e14674173b156bac7e12d211051d77c6e78d37a55d04"  # SHA code is required
HEAVY_WRONG_IMAGE_NAME_X86 = "docker.io/kiemtcb/detection-ob:4.2x86@sha256:326e47e0290094fcfe71e14674173b156bac7e12d211051d77c6e78d37a55d04"  # SHA code is required
LIGHT_IMAGE_NAME_X86 = "docker.io/mc0137/detect_abnormal:v1.6@sha256:7c9e3763d0d532d5976e37ff309eea6fe446b7242570f92bc4d2c760abb46a3a"  # SHA code is required
LIGHT_WRONG_IMAGE_NAME_X86 = "docker.io/mc0137/detect_ab:v1.4@sha256:3ba0c98c26a48d6afe4df6945551f4ac956f8c1fcb9f1837b3e9a8187f09d2d8"  # SHA code is required
LIGHT_IMAGE_NAME_ARM = "docker.io/mc0137/detect_abnormal:arm1.4@sha256:0e8ee05c5d256abc89f6f98fb3b4f40863a97ff7b43dfb6c92f7a8024cc049f4"  # SHA code is required
LIGHT_WRONG_IMAGE_NAME_ARM = "docker.io/mc0137/detect_ab:arm1.1@sha256:ea4866fffee1c5536c59e0850b4d8acbbdb655a4a575f6fbbe904a0e38e23a27"  # SHA code is required
PROXY_IMAGE_NAME = "b371fa5b70540"


WRONG_IMAGE_NAME = HEAVY_WRONG_IMAGE_NAME_X86
# WRONG_IMAGE_NAME = HEAVY_WRONG_IMAGE_NAME_ARM
# WRONG_IMAGE_NAME = LIGHT_WRONG_IMAGE_NAME_X86
# WRONG_IMAGE_NAME = LIGHT_WRONG_IMAGE_NAME_ARM
IMAGE_NAME = HEAVY_IMAGE_NAME_X86
# IMAGE_NAME = HEAVY_IMAGE_NAME_ARM
# IMAGE_NAME = LIGHT_IMAGE_NAME_X86
# IMAGE_NAME = LIGHT_IMAGE_NAME_ARM
DELETE_IMAGE_CMD = "sudo crictl rmi " + IMAGE_NAME
DELETE_PROXY_IMAGE_CMD = "sudo crictl rmi " + PROXY_IMAGE_NAME
DELETE_GW = "sudo route del default"
ADD_GW = "sudo ip route add default via 172.16.42.1"
CURL_TERM = "curl http://{}:8080/api/terminate" # When pod is terminated, DNS may be gone, thus IP is preferred
CURL_ACTIVE = "curl " + HEAVY_DNS + "/api/stream/" + STREAMING_IP + ":" + STREAMING_PORT + "/" + str(DETECTION_TIME)
# CURL_ACTIVE_INST = "curl http://{}:8080/api/stream/" + \
#     "{}:{}/{}/1".format(STREAMING_IP, STREAMING_PORT, DETECTION_TIME)
CURL_ACTIVE_INST = "curl " + HEAVY_DNS + "/api/stream/active/" + STREAMING_IP + ":" + STREAMING_PORT + "/" + str(DETECTION_TIME)
CURL_TRIGGER = "curl " + HEAVY_DNS + "/api/active"
CURL_TRIGGER_TIME = "curl -w \"@curl-time.txt\" -s " + HEAVY_DNS + "/api/active"
CURL_RESPONSE_TIME = "curl -F upload=@{}.jpg -w \"@curl-time.txt\" -s " + HEAVY_DNS + "/api/picture"
# STATE
NULL_STATE = "null_state"
WARM_DISK_STATE = "warm_disk_state"
WARM_CPU_STATE = "warm_cpu_state"
WARM_MEM_STATE = "warm_mem_state"
COLD_STATE = "cold_state"
ACTIVE_STATE = "active_state"

# ACTION
NULL_TO_WARM_DISK_PROCESS = "null_to_warm_disk_process"
NULL_TO_COLD_PROCESS = "null_to_cold_process"
COLD_TO_NULL_PROCESS = "cold_to_null_process"
WARM_DISK_TO_WARM_CPU_PROCESS = "warm_disk_to_warm_cpu_process"
WARM_CPU_TO_WARM_DISK_PROCESS = "warm_cpu_to_warm_disk_process"
WARM_DISK_TO_ACTIVE_PROCESS = "warm_disk_to_active_process"
COLD_TO_WARM_DISK_PROCESS = "cold_to_warm_disk_process"
WARM_DISK_TO_COLD_PROCESS = "warm_disk_to_cold_process"
WARM_DISK_TO_NULL_PROCESS = "warm_disk_to_null_process"
WARM_CPU_TO_ACTIVE_PROCESS = "warm_cpu_to_active_process"
ACTIVE_TO_WARM_DISK_PROCESS = "active_to_warm_disk_process"
WARM_MEM_TO_WARM_DISK_PROCESS = "warm_mem_to_warm_disk_process"
RESPOND_TIME_WARM_CPU = "respond_time_warm_cpu"
RESPOND_TIME_WARM_DISK = "respond_time_warm_disk"

image_quality = {
    "SD": "./image/SD.jpg",
    "HD": "./image/HD.jpg",
    "FHD": "./image/FHD.jpg",
    "2K": "./image/2K.jpg",
    "4K": "./image/4K.jpg"

}

#######################################################
###### changable variables#############################
jobs_status = {
    # STATE
    NULL_STATE: True,
    WARM_DISK_STATE: True,
    WARM_CPU_STATE: True,
    WARM_MEM_STATE: True,
    COLD_STATE: True,
    ACTIVE_STATE: True,
    # ACTION
    NULL_TO_WARM_DISK_PROCESS: True,
    NULL_TO_COLD_PROCESS: True,
    COLD_TO_NULL_PROCESS: True,
    WARM_DISK_TO_WARM_CPU_PROCESS: True,
    WARM_CPU_TO_WARM_DISK_PROCESS: True,
    WARM_DISK_TO_ACTIVE_PROCESS: True,
    ACTIVE_TO_WARM_DISK_PROCESS: True,
    COLD_TO_WARM_DISK_PROCESS: True,
    WARM_DISK_TO_COLD_PROCESS: True,
    WARM_DISK_TO_NULL_PROCESS: True,
    WARM_CPU_TO_ACTIVE_PROCESS: True,
    WARM_MEM_TO_WARM_DISK_PROCESS: True,
    RESPOND_TIME_WARM_CPU: True,
    RESPOND_TIME_WARM_DISK: True,
}

config.load_kube_config()
ApiV1 = client.CoreV1Api()
AppV1 = client.AppsV1Api()

localdate = datetime.now()
generate_file_time = "{}_{}_{}_{}h{}".format(
    localdate.day, localdate.month, localdate.year, localdate.hour, localdate.minute)


def reload():
    global jobs_status, localdate, generate_file_time
    jobs_status[NULL_STATE] = True
    jobs_status[WARM_DISK_STATE] = True
    jobs_status[WARM_CPU_STATE] = True
    jobs_status[WARM_MEM_STATE] = True
    jobs_status[ACTIVE_STATE] = True
    jobs_status[COLD_STATE] = True
    jobs_status[NULL_TO_WARM_DISK_PROCESS] = True
    jobs_status[NULL_TO_COLD_PROCESS] = True
    jobs_status[COLD_TO_NULL_PROCESS] = True
    jobs_status[WARM_DISK_TO_WARM_CPU_PROCESS] = True
    jobs_status[WARM_CPU_TO_WARM_DISK_PROCESS] = True
    jobs_status[WARM_CPU_TO_ACTIVE_PROCESS] = True
    jobs_status[WARM_DISK_TO_ACTIVE_PROCESS] = True
    jobs_status[ACTIVE_TO_WARM_DISK_PROCESS] = True
    jobs_status[COLD_TO_WARM_DISK_PROCESS] = True
    jobs_status[WARM_DISK_TO_COLD_PROCESS] = True
    jobs_status[WARM_MEM_TO_WARM_DISK_PROCESS] = True
    jobs_status[RESPOND_TIME_WARM_CPU] = True
    jobs_status[RESPOND_TIME_WARM_DISK] = True

    localdate = datetime.now()
    generate_file_time = "{}_{}_{}_{}h{}".format(
        localdate.day, localdate.month, localdate.year, localdate.hour, localdate.minute)
