# AKS-Latency-Detection
<sup> Dan Grecoe - A Microsoft Employee </sup>

This code is directly related to deployments of two real time Machine/Deep Learning scoring paths :

* [Machine Learning (ML)](https://github.com/microsoft/MLAKSDeployAML)
* [Deep Learning (DL)](https://github.com/microsoft/AKSDeploymentTutorialAML)


## Overview
During a project in which a DL model was deployed to a GPU cluster in Azure Kubernetes Service, it became clear that the response times, i.e. latency,  of the endpoint did not match expectations. 

Looking at the cluster through the Kubernetes Dashboard was not telling us much, but we knew that the model logged out how long it took to score a single record. 

With that knowledge, this set of scripts are used to:
1. Let the user choose which kubectl context to go after. 
2. Let the user choose the deployment from that cluster to collect and analyze logs for. 
3. Determine the number of replicas (pods) that have been allocated to the service.
4. Download the logs and parse them for useful information.

## Pre-Requisites
* You have an AKS cluster with either the DL or ML model deployed to it. You can have many, but it is required to at least have one. 
* Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) onto your machine. 
* Have collected the credentials from the AKS cluster using 
    * az aks get-credentials -g [resource_group] -n [cluster_name]
* Have minimum Python 3.6.1 installed on your machine.
* Have cloned this repository
 
## Running the script
The main script is realTimeScoringStats.py, this file will prompt you along the way when needed to collect the information it needs to parse the log files. 

When running, it will download log files from each pod to the directory in which the script runs in the form:

```
    [pod_name].txt
```

Results will be dumped to a file in the same directory from which the script runs in the form :

```
    [aks_deployment_name]_results.txt
```

For each pod/replica in the deployment in which a log was captured, an entry in the results file will be created in the form:

```
File : yourdeployname-6fc5cf8df6-sdxld.txt
Times (6452):
	 Earliest: 2019-10-17 13:00:30
	 Latest: 2019-10-17 13:08:48
	 Time in minutes: 8.3
Scoring Calls (6452):
	 Average: 70.46944048357093 ms
	 Slowest: 81.43 ms
	 Fastest: 68.63 ms
	 Throughput: 12.955823293172688 RPS
```

#### Hint: 
When prompted to pick your namespace, you will be presented with a list such as:

```
List of namespaces (deployment) found :
1 - azureml-dangaksdeploydl3 (dangdeploy3)
2 - default (azureml-ba)
3 - default (azureml-fe)
4 - kube-system (coredns)
5 - kube-system (coredns-autoscaler)
6 - kube-system (kubernetes-dashboard)
7 - kube-system (metrics-server)
8 - kube-system (tunnelfront)
Enter the integer selection for a namespace >
```

Choose the one that stars with ___azureml-___