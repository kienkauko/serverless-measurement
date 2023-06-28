import time
import main
import variables
from multiprocessing import Event, Process
from k8s_API import update_deployment
import functional_methods
import merge
import sys

if __name__ == "__main__":
    
    target_pods_scale = [1, 2, 3, 4, 5]
    repeat_time = 1
    current_time = 1
    node = 'mec'
    image = 'x86'
    list_quality = ["360P", "480P", "HD", "2K", "4K"]

    # list video: highway.mp4, 4K_video_59s.webm, traffic_34s.webm, video.mp4
    # target_video = "highway.mp4"
    # detection_image = ""
    # if instance == SERVER_USER:
    #     detection_image = "29061999/knative-video-detection@sha256:477b697dae923281790d4064a2261b8a704b38baeae904a23a3b24ee0022e87d"
    # else :
    #     detection_image = "29061999/knative-video-detection-arm@sha256:47705b6d9561b0fe45fadf559802a8d500c32b069fd50ef0fc69e6859c34a9e3"

    for target_pod in target_pods_scale:
        update_deployment(target_pod, "null") # Update number of deployment according to target_pod
        print("Deployment has been updated to {} pods".format(target_pod))
        for rep in range(current_time, repeat_time + 1, 1):
            print("Target pod: {}, Repeat time: {}/{}, Instance: {}".format(target_pod,
                  rep, repeat_time, node))
            variables.reload()  # reset all variables
            event = Event()  # the event is unset when created
            p0 = Process(target=functional_methods.auto_delete, args=(target_pod, event, ))
            p0.start()
            # main.curl_latency(node, image, list_quality, int(target_pod), int(rep), event)
            main.collect_life_cycle(node, image, int(target_pod), int(rep), event)
            p0.join()
            time.sleep(10)
            # p1 = Process(target=collect_life_cycle, args=(event, int(target_pods_scale), repeat_time, ), daemon = True)
            # print("Start calculate")
            # p1.start()

            # cmd = '/usr/bin/python3 ' + DEFAULT_DIRECTORY +'/main_rebuild.py {} {} {}'.format(str(target_pod),  str(rep), str(instance))
            # process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    # event.set()
