# applications used in the measurement
## Abnomal detection app
### Data streaming
data streaming are docker images that constantly broadcast a flow of sensor data.  
Images:
+ for x86: `mc0137/source_data:v1.4 sha256:277a9795e355933ced7097d6be29ef8fc83bbe330eee495bff4729dc70c7e658`
+ for ARM: `mc0137/source_data:arm1.1 sha256:5e76454ad9926fc1864770433b75cd8a4745a47028ecb2a1c9255892623a1215`  

Example of running cmds:
```
docker run -p 12345:12345 mc0137/source_data:v1.4 ( log)
docker run -d -p 12345:12345 mc0137/source_data:v1.4 (no log)
```
### Abnomal detection
this app uses ML to detect abnormal from the fetched sensor data, output is 1 or 0
Image:
+ for x86: mc0137/detect_abnormal:v1.4 sha256:3ba0c98c26a48d6afe4df6945551f4ac956f8c1fcb9f1837b3e9a8187f09d2d8
+ for ARM: mc0137/detect_abnormal:arm1.1 sha256:ea4866fffee1c5536c59e0850b4d8acbbdb655a4a575f6fbbe904a0e38e23a27
  
Example of running cmds:
```
docker run -p 8080:8080 mc0137/detect_abnormal:v1.4
```
  
APIs:
```
Detection:
http://<ip>:<port>/api/stream/<ip>:<port>/time_detect/time_sleep
examples:
http://<ip>:<port>/api/stream/<ip>:<port>/1/1
Termination:
http://<ip>:<port>/api/terminate
```

## Object detection app
