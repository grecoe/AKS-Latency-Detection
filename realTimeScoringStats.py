
'''
    DESCRIPTION:

    This script will prompt the user to choose a namespace, then go find all the pods in that namepace and
    collect all of the logs for them into the local directory. 

    The logs will then be parsed to determine how many calls have been made to it and record times and latencies.

     
    PURPOSE:

    This script is really only viable for the DL path, though could likely be easily modified for other paths.
    
    The script will record every call to the service and track times and latencies producing statistics including
    RPS for each pod. 

    The script is locked to the DL path because the log output for a single call to the service is: 

    127.0.0.1 - - [15/Oct/2019:12:33:00 +0000] "POST /score HTTP/1.0" 200 176 "-" "-"
    Received input: <AMLRequest 'http://52.170.45.12/score' [POST]>
    Headers passed in (total 9):
                  Host: 52.170.45.12
                  X-Real-Ip: 10.244.1.5
                  X-Forwarded-For: 10.244.1.5
                  X-Forwarded-Proto: http
                  Connection: close
                  Content-Length: 27362
                  Content-Type: multipart/form-data; boundary="5cea30d8-92a2-4aeb-b75f-dca78be94f1f"
                  Authorization: Bearer g1NBvrKAUjbFoUT9fmt0nobEkK4Gtzg0
                  X-Ms-Request-Id: 5afbcc69-eec4-4661-9108-071428f0d50f
    Scoring Timer is set to 3600.0 seconds
    Scoring 1 images
    Predictions: {'file': [('n02127052', 'lynx', 0.981648325920105), ('n02128385', 'leopard', 0.007744148373603821), ('n02123159', 'tiger_cat', 0.003686134237796068)]}
    [DL] Predictions took 72.81 ms
    [ML] Prediction took 72.81 ms
    200


    PRE-REQUISITES
    - kubectl installed
    - az aks get-credential run to set the cluster with the DL path as the current context, otherwise, set the current 
      context to the cluster you want to check: 
        kubectl config get-contexts
        kubectl config use-context my-cluster-name
        https://kubernetes.io/docs/reference/kubectl/cheatsheet/
    - Run the script

    WHAT HAPPENS:
    - Script prompts user to select the deployment/namespace of the AzureML project.
    - Script gets the pods associated with the namespace
    - Script pulls down the logs for the pods it finds and stores them in the local 
      directory named [podname].txt of where the script runs. 
    - Logs are then parsed and the output is dumped out a file [deployment]_results.txt
'''

from datetime import datetime,timedelta
from utils.logUtils import *
from utils.aksUtils import * 
from utils.latencyUtils import LatencyTracker, RequestData 


# Let the user choose which kubectl context to use.
setKubectlContext()

# Have the user select a namespace/deployment
namespaceSelection = getDeploymentNamespace()
if namespaceSelection is None:
    print("An invalid selection was made....")
    quit()

print("Namespace {} selected from deployment {}".format(namespaceSelection[1], namespaceSelection[0]))

# Get the pods associated with the namespace
pods = getPodsForNamespace(namespaceSelection[1]) 
if len(pods) == 0:
    print("No pods found for namespace {}".format(namespaceSelection[1]))
    quit()

# Collect the logs from the pods and save the names to process later
fileNames = []
for pod in pods:
    fileNames.append(collectPodLogs(pod, namespaceSelection[1]))


'''
    Given the format of the request, lines that start with/contain this information are then parsed

    predictionIdentifier -> Stripped for the date time of the request
    predictionLine -> Contains the ms latency of the call. 
'''
# Line start that indicates new request
predictionIdentifier = "127.0.0.1"

# Optional header, won't hold it to it.....
optionalHeader = 'X-Ms-Request-Id'

# DL Path prediction line - "Predictions took"
# ML Path prediction line - "Prediction took"
#Default to DL path
predictionLine = "Predictions took"

# Figure out if it's ML or DL path
print("\nSelect the deployment type:")
print("1 : ML Path")
print("2 : DL Path")
pathSelector = int(input ("Enter the path number: > "))
if pathSelector == 1:
    predictionLine = "Prediction took"
else:
    predictionLine = "Predictions took"

'''
    Process whatever files were found
'''
print("Start processing logs ...")

latencyEntries = 0
callCount = 0
latencies = {}

contCount = 0
for file in fileNames:
    print("Parsing: ", file)
    with open(file=file, mode="r") as fp:
        latencies[file] = LatencyTracker()
        line = fp.readline()
        
        # First line will tell us if we have unicode or not....
        isUnicodeFile = detectUnicode(line)
 
        isRecord = False
        latency = 0.0
        timeStamp = None
        requestId = ''
        while line:
            if isUnicodeFile:
                line = converAscii(line)

            if line.__contains__(predictionIdentifier):
                callCount += 1
                # 127.0.0.1 - - [15/Oct/2019:12:33:00 +0000] "POST /score HTTP/1.0" 200 176 "-" "-"
                parts = line.split(' ')
                datePart = parts[3]
                dateString = datePart.strip('[]') 
                timeStamp = datetime.strptime(dateString, "%d/%b/%Y:%H:%M:%S")
                isRecord = True

            if line.__contains__(optionalHeader):
                #  Header : Value
                parts = line.strip().split(':')
                requestId = parts[1].strip()

            if line.__contains__(predictionLine):
                latencyEntries += 1
                # Prediction(s) took 72.81 ms
                parts = line.split(' ')
                latency = float(parts[2])

                if isRecord:
                    isRecord = False
                    rd = RequestData()
                    rd.latency = latency
                    rd.time = timeStamp
                    rd.requestId = requestId
                    latencies[file].requestInfo.append(rd)

            line = fp.readline()


'''
    Build up the results and write them out to a file {deploymentname}_results.txt
'''
resultsFile = "{}_results.txt".format(namespaceSelection[0])

results = []
results.append("Deployment: {}".format(namespaceSelection[0]))
results.append("Namespace: {}".format(namespaceSelection[1]))
results.append("Pods: ")
for pod in pods:
    results.append("\t {}".format(pod))
results.append("\n")

results.append("Total calls - {} ".format(callCount))
results.append("Total latency entries - {}".format(latencyEntries))

fullRecordCount = 0
for key in latencies.keys():
    fullRecordCount += len(latencies[key].requestInfo)
results.append("Full Requests Captured - {}\n".format(fullRecordCount))


for key in latencies.keys():
    results.extend(latencies[key].getPrintableFormat(key))

print("Writing out results.....")
with open(resultsFile,mode="w") as outputFile:
    for result in results:
        outputFile.write(result  + "\n")

print("Results in {}".format(resultsFile))

'''
    Allow a search of current records by request ID
'''
print("\nSearch for requests by ID, enter q to stop.\n")
while True:
    requestId = input("\nEnter a request ID to find> ")
    if requestId.strip() == 'q':
        break

    for key in latencies.keys():
        reqById = latencies[key].findByRequestId(requestId)
        if len(reqById) > 0:
            print("Found in file: ", key)
            for r in reqById:
                print("LATENCY: " , r.latency, " TIME: ", r.time)
