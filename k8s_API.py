from kubernetes import client, config
import subprocess
import random

config.load_kube_config()
ApiV1 = client.CoreV1Api()
AppV1 = client.AppsV1Api()


class KubernetesPod:
    def __init__(self, pod_name, pod_status, pod_ip, node_name, sum_pod_container, number_container_ready):
        self.pod_name = pod_name
        self.pod_status = pod_status
        self.pod_ip = pod_ip
        self.node_name = node_name
        self.sum_pod_container = sum_pod_container
        self.number_container_ready = number_container_ready


def list_namespaced_pod_status(target_namespace: str = "default"):
    list_pod_status = []
    api_get_pods_response = ApiV1.list_namespaced_pod(target_namespace)
    for pod in api_get_pods_response.items:
        current_pod_name = pod.metadata.name
        current_node_name = pod.spec.node_name
        current_pod_ip = pod.status.pod_ip
        current_pod_state = ""
        if pod.metadata.deletion_timestamp != None and (pod.status.phase == 'Running' or pod.status.phase == 'Pending'):
            current_pod_state = 'Terminating'
        elif pod.status.phase == 'Pending':
            for container in pod.status.container_statuses:
                if container.state.waiting != None:
                    current_pod_state = container.state.waiting.reason
        else:
            current_pod_state = str(pod.status.phase)
        sum_pod_container = len(pod.status.container_statuses)
        number_container_ready = 0
        for container in pod.status.container_statuses:
            if container.ready == True:
                number_container_ready += 1
        list_pod_status.append(KubernetesPod(
            current_pod_name, current_pod_state, current_pod_ip, current_node_name, sum_pod_container, number_container_ready))
    return list_pod_status


def get_number_namespaced_pod_through_status(target_status: str, target_namespace: str = "default"):
    count = 0
    list_pod = list_namespaced_pod_status(target_namespace)
    for pod in list_pod:
        if pod.pod_status == target_status:
            count += 1
    return count

# NOTE: get event of pod over  pod's name
#      return array of PodEvents class
def list_namespaced_event(target_pod_name: str, target_namespace: str = "default"):
    list_pod_event = []
    events_response = ApiV1.list_namespaced_event(
        target_namespace, field_selector=f'involvedObject.name={target_pod_name}')
    for event in events_response.items:
        current_event_time = event.first_timestamp
        current_event = event.reason
        current_event_message = event.message
        if current_event_time != None:
            current_event_time = current_event_time.timestamp()
        list_pod_event.append(PodEvents(target_pod_name, current_event_time,
                                        current_event, current_event_message))
    return list_pod_event

# NOTE:- check if the image image in the pod pulled since pod started
#      - check if the image image in the pod pulled since a timestamp (optional)
#      - return True or False
def is_image_available(target_pod: str, start_timeline: datetime = None):
    name = ""
    if target_pod == "random":
        name = random.choice(list_namespaced_pod_status()).pod_name:
    else:
        name = target_pod
    
    is_pulled = False
    events = list_namespaced_event(name)
    for event in events:
        if start_timeline != None and event.event_time != None:
            if event.event_time < start_timeline.timestamp():
                continue
        if event.event == "Pulled":
            is_pulled = True
            break
    return is_pulled

def create_namespaced_service(target_service: str, target_ID: str,
                              target_service_port: int, target_namespace: str = "default"):
    service_name = target_service + "-" + target_ID + "-service"
    service_selector = target_service + "-" + target_ID + "-deployment"
    body = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(name=service_name),
        spec=client.V1ServiceSpec(
            selector={"app": service_selector, "ID": target_ID},
            type="ClusterIP",
            ports=[client.V1ServicePort(
                port=target_service_port,
                target_port="container-port")]))
    try:
        response = ApiV1.create_namespaced_service(
            namespace=target_namespace, body=body)
    except:
        return ("There is unknown error when deploy {}.".format(service_name))
    return ("Deploy {} succesfully.".format(service_name))


def create_namespaced_deployment(target_deployment: str, target_ID: str, target_image: str,
                                 target_container_port: int, target_env, target_namespace: str = "default"):
    deployment_name = target_deployment + "-" + target_ID + "-deployment"
    body = (
        client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(
                name=deployment_name
            ),
            spec=client.V1DeploymentSpec(
                selector=client.V1LabelSelector(
                    match_labels={"app": deployment_name, "ID": target_ID}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": deployment_name, "ID": target_ID}
                    ),
                    spec=client.V1PodSpec(
                        containers=[client.V1Container(
                            name=target_deployment,
                            image=target_image,
                            ports=[client.V1ContainerPort(
                                container_port=target_container_port,
                                name="container-port"
                            )],
                            env=target_env
                        )]
                    )
                )
            )

        )
    )
    try:
        response = AppV1.create_namespaced_deployment(
            body=body, namespace=target_namespace)
    except:
        return ("There is unknown error when deploy {}.".format(deployment_name))
    return ("Deploy {} succesfully.".format(deployment_name))


def delete_namespaced_deployment(target_deployment: str, target_ID: str, target_namespace: str = "default"):
    deployment_name = target_deployment + "-" + target_ID + "-deployment"
    try:
        AppV1.delete_namespaced_deployment(deployment_name, target_namespace)
    except:
        return ("There is unknown error when delete {}.".format(deployment_name))
    return ("Delete {} succesfully.".format(deployment_name))


def delete_namespaced_service(target_service: str, target_ID: str, target_namespace: str = "default"):
    service_name = target_service + "-" + target_ID + "-service"
    try:
        ApiV1.delete_namespaced_service(service_name, target_namespace)
    except:
        return ("There is unknown error when delete {}.".format(service_name))
    return ("Delete {} succesfully.".format(service_name))

#NOTE: Consider rewriting the following functions by Python-k8s
def deploy_pods(path_file_output : str = DEPLOYMENT_PATH):
    subprocess.call('echo {} | sudo -S kubectl apply -f {}'.format(MASTER_PASSWORD, path_file_output), shell=True)
    print("Service deployed")

def delete_pods(path_file_output : str = DEPLOYMENT_PATH):
    subprocess.call('echo {} | sudo -S kubectl delete -f {}'.format(MASTER_PASSWORD, path_file_output), shell=True)
    print("Service deleted")

def connect_pod_exec(target_name: str = "ubuntu", target_command: str):
    command = "kubectl exec -it {} -- {} ".format(target_name, target_command)
    output = subprocess.check_output(['/bin/bash', '-c', command])
    print(output)

def is_pod_terminated(namespace:str = NAMESPACE):
    list_pod = list_namespaced_pod_status(namespace)
    i:KubernetesPod
        for i in list_pod:
            if i.pod_status == "Terminating":
                return True

def get_number_pod(namespace:str = NAMESPACE):
    return len(list_namespaced_pod_status(namespace))

def get_number_running_pod(namespace:str = NAMESPACE):
    count = 0
    list_pod = list_namespaced_pod_status(namespace)
    i:KubernetesPod
        for i in list_pod:
            if i.pod_status == "Running":
                count = count + 1
    return count

def get_list_term_pod(namespace:str = NAMESPACE):
    count = 0
    list_pod = list_namespaced_pod_status(namespace)
    list_term_pod = []
    i:KubernetesPod
        for i in list_pod:
            if i.pod_status == "Terminating":
                list_term_pod.append(i)
    return list_term_pod

def update_replicas(path_file_deploy: str = DEPLOYMENT_PATH, target_pods_scale: int, instance: str = WORKER_HOST, detection_image: str):
#opens the capture file and updates the replica values
    try:  
        new_deployment = []
        for target_pod in range(0, target_pods_scale, 1):
            docs = list(yaml.load_all(open(path_file_deploy, "r"), Loader=yaml.SafeLoader))
            for doc in docs:
                for key, value in doc.items():
                    if value == "serving.knative.dev/v1":
                        doc["metadata"]["name"] = "detection"+str(target_pod+1)
                        doc["spec"]["template"]["spec"]["nodeSelector"]["kubernetes.io/hostname"] = str(instance)
                        doc["spec"]["template"]["spec"]["containers"][0]["image"] = str(detection_image)
                        break
                new_deployment.insert(target_pod,doc)

        with open(path_file_output, 'w') as yaml_file:
            yaml.dump_all(new_deployment, yaml_file, default_flow_style=False)
    except yaml.YAMLError as exc:
        print(exc)

def config_live_time(path_file_deploy: str = DEPLOYMENT_PATH, target_pods_scale: int, instance: str = WORKER_HOST, time: int): #, detection_image: str
    #opens the capture file and updates the replica values
    try:  
        new_deployment = []
        for target_pod in range(0, target_pods_scale, 1):
            docs = list(yaml.load_all(open(path_file_deploy, "r"), Loader=yaml.SafeLoader))
            for doc in docs:
                for key, value in doc.items():
                    if value == "serving.knative.dev/v1":
                        doc["metadata"]["name"] = "detection"+str(target_pod+1)
                        doc["spec"]["template"]["spec"]["nodeSelector"]["kubernetes.io/hostname"] = str(instance)
                        # doc["spec"]["template"]["spec"]["containers"][0]["image"] = str(detection_image)
                        doc["spec"]["template"]["metadata"]["annotations"]["autoscaling.knative.dev/window"] = str(time)+"s"
                        break
                new_deployment.insert(target_pod,doc)

        with open(path_file_output, 'w') as yaml_file:
            yaml.dump_all(new_deployment, yaml_file, default_flow_style=False)
    except yaml.YAMLError as exc:
        print(exc)

def is_all_con_ready(namespace: str = NAMESPACE):
    a = list_namespaced_pod_status(namespace)
    i:KubernetesPod
    for i in a:
        if i.number_container_ready/i.sum_pod_container != 1.0:
            return False
        else:
            print("Pod {} is ready.".format(i.pod_name))
    return True

if __name__ == "__main__":
    a = list_namespaced_pod_status()
    i:KubernetesPod
    for i in a:
        print(i.pod_name)
        print(i.pod_status)
        print(i.pod_ip)
        print("{}/{}".format(i.number_container_ready,i.sum_pod_container))
