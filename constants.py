from lib2to3.pgen2.token import COLON, SLASH
import os


# HOST IP
MASTER_HOST = "localhost"
WORKER_HOST = "jetson"
MASTER_USERNAME = "controller"
MASTER_PASSWORD = "1"
PROM_IP ="172.16.36.101"
JETSON_IP = "172.16.42.10"
JETSON_USERNAME = "jetson"
JETSON_PASSWORD = "1"
STREAMING_IP = "172.16.36.101"
NAMESPACE = "serverless"


# PORT
PROMETHEUS_PORT = "9090"
STREAMING_PORT = "1936"
# Common
COLON = ":"
SLASH = "/"
TEST_MODE = False

# Network interfacte
NETWORK_INTERFACE = "ens33"
PROMETHEUS_DOMAIN = "http://"+ PROM_IP + COLON + PROMETHEUS_PORT +"/api/v1/query?query="
SERVICE_DOMAIN = "http://serverless.default.svc.cluster.local"

# constant values
# CALCULATION_TYPE = "normal"     # revert_lifecircle
TARGET_VIDEO = "detection"
STATE_COLLECT_TIME = 60
NULL_CALCULATION_TIME = 10
ACTIVE_CALCULATION_TIME = 30
DETECTION_TIME = 200
LIVE_TIME = 240

# QUERY
VALUES_CPU_QUERY = "100-(avg%20by%20(instance,job)(irate(node_cpu_seconds_total{{mode='idle',job='node_exporters',instance='{}:9100'}}[30s])*100))"
VALUES_MEMORY_QUERY = "((node_memory_MemTotal_bytes{{job='node_exporters',instance='{}:9100'}}-node_memory_MemAvailable_bytes{{job='node_exporters',instance='{}:9100'}})/(node_memory_MemTotal_bytes{{job='node_exporters',instance='{}:9100'}}))*100"
VALUES_NETWORK_RECEIVE_QUERY = "rate(node_network_receive_bytes_total{{device='"+NETWORK_INTERFACE+"',instance='{}:9100'}}[1m])/(1024*1024)"

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
BASH_PATH = DEFAULT_DIRECTORY + "/deployments"
DATA_PROMETHEUS_AT_PI4_FILE_DIRECTORY = DATA_DIRECTORY + PI4_FOLDER + SLASH +DATA_PROMETHEUS_AT_PI4_FILENAME
DATA_UMMETER_FILE_DIRECTORY = DATA_DIRECTORY + DATA_UMMETER_FOLDER + SLASH + DATA_UMMETER_FILENAME
PULLING_TIME_DATA_FILE_DIRECTORY = DATA_DIRECTORY + PULLING_TIME_FOLDER + SLASH + DATA_PULLING_IMAGE_FILENAME

DATA_PROMETHEUS_FILE_DIRECTORY = DEFAULT_DIRECTORY + "/data/{}/data_prom_target_pod_{}_repeat_time_{}_type_{}_{}.csv"
DATA_TIMESTAMP_FILE_DIRECTORY = DEFAULT_DIRECTORY + "/data/timestamp/{}/data_timestamp_target_pod_{}_repeat_time_{}_type_{}_{}.csv"

# CMD

# IMAGE_NAME = "hctung57/object-detection-arm:4.6.1.10@sha256:7361b88965a4bb39a693450902ad660e1722f4a9da677b36374318cc0023d771" #SHA code is required
IMAGE_NAME = "docker.io/hctung57/object-detection-arm:4.6.1.12@sha256:34a3936e2ca92ba65a3ced21008e29367e2345d1c1bd4e2c19d751c48009ad2b" #SHA code is required
DELETE_IMAGE_CMD = "sudo crictl rmi " + IMAGE_NAME
CURL_TERM = "curl http://{}:8080/api/terminate"
CURL_ACTIVE = "curl http://{}:8080/api/stream/" + "{}:{}/{}".format(STREAMING_IP, STREAMING_PORT, DETECTION_TIME)
CURL_ACTIVE_INST = "curl http://{}:8080/api/stream/active/" + "{}:{}/{}".format(STREAMING_IP, STREAMING_PORT, DETECTION_TIME)
CURL_TRIGGER = "curl http://{}:8080/api/active"

# STATE
NULL_STATE = "null_state"
WARM_DISK_STATE = "warm_disk_state"
WARM_CPU_STATE = "warm_cpu_state"
COLD_STATE = "cold_state"
ACTIVE_STATE = "active_state"

# ACTION
NULL_TO_WARM_DISK_PROCESS = "null_to_warm_disk_process"
WARM_DISK_TO_WARM_CPU_PROCESS = "warm_disk_to_warm_cpu_process"
WARM_CPU_TO_WARM_DISK_PROCESS = "warm_cpu_to_warm_disk_process"
WARM_DISK_TO_ACTIVE_PROCESS = "warm_disk_to_active_process"
COLD_TO_WARM_DISK_PROCESS = "cold_to_warm_disk_process"
WARM_DISK_TO_NULL_PROCESS = "warm_disk_to_null_process"