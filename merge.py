from variables import *
import csv
import glob
import copy


def merge_csv(instance, target_pod, rep):
    status = ['null_state', 'null_to_cold_process', 'warm_disk_state', 'warm_disk_to_warm_cpu_process', 'warm_cpu_state',
              'active_state', 'warm_cpu_to_warm_disk_process', 'warm_disk_to_cold_process', 'cold_state', 'cold_to_warm_disk_process', 'cold_to_null_process', 'warm_mem_to_warm_disk_process']
    path = DEFAULT_DIRECTORY + "/data/resource/"
    writeFileName = DEFAULT_DIRECTORY + '/data/' + \
        "target_pod_"+str(target_pod)+"_repeat_"+str(rep)+"_" + \
        instance+"_" + generate_file_time + '.csv'
    for x in status:
        readFileName = path + instance + '/*' + x + '*.csv'
        for filename in glob.glob(readFileName):
            with open(filename, 'r') as f:
                writer = csv.writer(open(writeFileName, 'a'))
                csvreader = csv.reader(f)
                for row in csvreader:
                    r = copy.deepcopy(row[:])
                    # r.append(str(x))
                    writer.writerow(r)


# if __name__ == "__main__":
#     merge_csv('mec', 1, 1)
    # merge_csv('jetson', 1, 1)
