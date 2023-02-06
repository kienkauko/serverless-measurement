# serverless-measurement
Measurement code for Serverless-based container life-cycle 

## Purpose:
Built specifically to deploy and measure `Knative` serverless function's lifecycle in terms of energy, resource consumption and latency.
However, it can be used for any K8S-related platform to conduct the same purpose.

## Before running:
You can see the required library in the `main.py` files, other from that, there are some prerequisites as follows:
⋅⋅* File `curl.yaml` must be deployed and stay in the system forever, it serves as the container for curl cmd to run over
⋅⋅* Prometheus must be installed and its address must be given in the `variable` file
⋅⋅* Tinkerforge devices and its relevant libs must be implemented in order to be used the `power.py` file

## Basic cmds:
File `auto_generate.py` contains a loop, which repetitively runs the `main.py` file. Why repetition? because it's basic measurement requirement.
File `main.py` control which part of lifecycle needs to be measured, it can be run independently for testing purpose. 

## Advanced cmds:
There is a separated process called **freeze mem**, which measures the freeze memory state of the serverless function. To measure this process, the following order must be complied:
1. Remove every deployment that are currently running
2. Apply files and change config following this [link](https://github.com/knative-sandbox/container-freezer)
3. Use the `main_mem_freeze.py` file instead of the `main.py`*
4. After finishing **freeze mem** measurement, the steps 1 and 2 above must be reversed.

> * *currently **freeze mem** can only measure its state, its actions are measured by **curl** tool *