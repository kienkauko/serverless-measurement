import time
import main
import variables
from multiprocessing import Event, Process
from k8s_API import update_deployment
import functional_methods
import merge

if __name__ == "__main__":

    target_pods_scale = [2]
    repeat_time = 1
    current_time = 1
    instance = "mec"

    # list video: highway.mp4, 4K_video_59s.webm, traffic_34s.webm, video.mp4
    # target_video = "highway.mp4"
    # detection_image = ""
    # if instance == SERVER_USER:
    #     detection_image = "29061999/knative-video-detection@sha256:477b697dae923281790d4064a2261b8a704b38baeae904a23a3b24ee0022e87d"
    # else :
    #     detection_image = "29061999/knative-video-detection-arm@sha256:47705b6d9561b0fe45fadf559802a8d500c32b069fd50ef0fc69e6859c34a9e3"

    for target_pod in target_pods_scale:
        update_deployment(target_pod, "doesntmatter") # Update number of deployment according to target_pod
        print("Deployment has been updated to {} pods".format(target_pod))
        for rep in range(current_time, repeat_time + 1, 1):
            print("Target pod: {}, Repeat time: {}/{}, Instance: {}".format(target_pod,
                  rep, repeat_time, instance))
            variables.reload()  # reset all variables
            event = Event()  # the event is unset when created
            p0 = Process(target=functional_methods.auto_delete, args=(event, ))
            p0.start()

            node = 'mec'
            image = 'x86'
            # main.collect_life_cycle(
            #     node, image, int(target_pod), int(rep), event)
            # merge.merge_csv(node,target_pod,rep)

            # node = 'jetson'
            # image = 'arm'
            # variables.INSTANCE = 'jetson'
            # variables.JETSON_IP = '192.168.1.2'
            # variables.JETSON_USERNAME = 'end'
            # variables.WRONG_IMAGE_NAME = variables.HEAVY_WRONG_IMAGE_NAME_ARM
            # variables.IMAGE_NAME = variables.HEAVY_IMAGE_NAME_ARM
            main.collect_life_cycle(
                node, image, int(target_pod), int(rep), event)
            merge.merge_csv(node,target_pod,rep)
            p0.join()
            time.sleep(30)
            # p1 = Process(target=collect_life_cycle, args=(event, int(target_pods_scale), repeat_time, ), daemon = True)
            # print("Start calculate")
            # p1.start()

            # cmd = '/usr/bin/python3 ' + DEFAULT_DIRECTORY +'/main_rebuild.py {} {} {}'.format(str(target_pod),  str(rep), str(instance))
            # process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    # event.set()
