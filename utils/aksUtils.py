
__version__ = 0.1

import os

'''
    kubectl commands that will be required

    kubectl config get-contexts
    kubectl config use-context [name]
'''
# Params : namespaceName
podsCommand = "kubectl get pods --namespace {}"
# Params : podName, namespaceName, podName
logsCommand = "kubectl logs {} --namespace {} > {}"
# Get the deployments on the cluster
deploymentCommand = "kubectl get deployments --all-namespaces"
# Get the contexts
getContextCommand = "kubectl config get-contexts"
# Set the context, param context name
setContextCommand = "kubectl config use-context {}"

'''
    Show the contexts and let them select between the two

    OUTPUT:

        CURRENT   NAME                      CLUSTER                   AUTHINFO                                                           NAMESPACE    
        *         dangdeploy3aksa7f577165   dangdeploy3aksa7f577165   clusterUser_dangaksdeploydl3_dangdeploy3aksa7f577165
                  ai-ml28e05045c68bc        ai-ml28e05045c68bc        clusterUser_Trident-ai-ml-northcentralus-test_ai-ml28e05045c68bc
'''
def setKubectlContext():
    print("\nSelect the kubectl context to use, if you don't see the one you want")
    print("you may need to set it up with the following command:")
    print("az aks get-credentials -g [resource_group] -n [aks_service_name]")
    print("(HINT: You need to be logged into that account, i.e. az account set -s [subid])\n")
    print("\nNOTE: A star following the context name means it is the current context\n")

    contextSelections = {}
    contexts = os.popen(getContextCommand).read()

    # Break down each entry to get {deploymnetName, namespaceName}
    entries = contexts.split("\n")

    # Get each line
    for entry in entries:
        entryParts = entry.split('\n')

        # Break down the lines
        for ctx in entryParts:
            ctxParts = ctx.split(' ')
            isCurrent = ctxParts[0] == '*'

            ctxParts = [x for x in ctxParts if x != '']
            if len(ctxParts) > 2:
                if ctxParts[0] == "CURRENT":
                    continue
                
                if isCurrent:
                    contextSelections[ctxParts[1]] = ctxParts[0]
                else:
                    contextSelections[ctxParts[0]] = ''
    
    selectedKey = None
    selectionIndex = 1
    contextChoices = {}
    for ctxKey in contextSelections.keys():
        choice = "{} {}".format(ctxKey, contextSelections[ctxKey])
        contextChoices[selectionIndex] = ctxKey
        print("{} - {}".format(selectionIndex, choice))
        selectionIndex += 1

    userchoice = int(input("\nEnter the integer selection for a context > ")) 

    if userchoice in contextChoices.keys():
        print("You chose to use ", contextChoices[userchoice])
        
        if contextSelections[contextChoices[userchoice]] == '*':
            print("Context is already selected.....")
        else:
            print("Changing context to ", contextChoices[userchoice])
            issueChangeContext = setContextCommand.format(contextChoices[userchoice])
            res = os.popen(issueChangeContext).read()
            print(res)
    else:
        print("I have no idea what you picked")

'''
    Get the deployments on the cluster so the user can choose one and 
    we can get the namespace name
    
    Call returns a tuple of [0] = deployment and [1] = namespace

    Command:
        kubectl get deployments --all-namespaces
    Results returned by AKS:

    NAMESPACE                  NAME                   DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
    azureml-dangaksdeploydl3   dangdeploy3            3         3         3            3           5d
    default                    azureml-ba             1         1         1            1           5d
    default                    azureml-fe             3         3         3            3           5d
    kube-system                coredns                2         2         2            2           5d
    kube-system                coredns-autoscaler     1         1         1            1           5d
    kube-system                kubernetes-dashboard   1         1         1            1           5d
    kube-system                metrics-server         1         1         1            1           5d
    kube-system                tunnelfront            1         1         1            1           5d
'''
def getDeploymentNamespace():
    print("Collecting AKS deployments....")

    deploymentSelections = {}
    deploymentsCollection = os.popen(deploymentCommand).read()

    # Break down each entry to get {deploymnetName, namespaceName}
    entries = deploymentsCollection.split("\n")

    # Get each line
    for entry in entries:
        entryParts = entry.split('\n')

        # Break down the lines
        for deployment in entryParts:
            deployParts = deployment.split(' ')
            deployParts = [x for x in deployParts if x != '']
            if len(deployParts) > 2:
                if deployParts[0] == "NAMESPACE":
                    continue

                deploymentSelections[deployParts[1]] = deployParts[0]

    # Now offer the items as a selection
    selectionIndex = 1
    namespaceSelections = {}
    print("List of namespaces (deployment) found :")
    for deployKey in deploymentSelections.keys():
        choice = "{} ({})".format(deploymentSelections[deployKey], deployKey)
        namespaceSelections[selectionIndex] = choice
        print("{} - {}".format(selectionIndex, choice))
        selectionIndex += 1

    userchoice = int(input("Enter the integer selection for a namespace > ")) 

    returnValue = None
    if userchoice in namespaceSelections.keys():
        selection = namespaceSelections[userchoice]
        breakdown = selection.split(' ')
        selectedNamespace = breakdown[0]
        selectedDeployment = breakdown[1].strip("()")
        returnValue = (selectedDeployment, selectedNamespace)
    
    return returnValue

'''
    Get the pods associated with a namespace

    Returns a list of pod names

    Command:

        Params : namespace name
        kubectl get pods --namespace {}

    Results returned by AKS:

    NAME                           READY     STATUS    RESTARTS   AGE
    dangdeploy3-6fc5cf8df6-sdxld   1/1       Running   0          5d
    dangdeploy3-6fc5cf8df6-vx58m   1/1       Running   2          5d
    dangdeploy3-6fc5cf8df6-zk9jm   1/1       Running   0          5d
'''
def getPodsForNamespace(namespaceName):
    print("Collecting pods for namespace {} ....".format(namespaceName))

    podNames = []
    podCollection = os.popen(podsCommand.format(namespaceName)).read()

    # Break down each entry to get {deploymnetName, namespaceName}
    entries = podCollection.split("\n")

    # Go through each line
    for entry in entries:
        entryParts = entry.split('\n')

        # Break down the lines
        for pod in entryParts:
            podParts = pod.split(' ')
            podParts = [x for x in podParts if x != '']
            if len(podParts) > 2:
                if podParts[0] == "NAME":
                    continue

                podNames.append(podParts[0])

    return podNames

'''
    Collect the logs for a specific pod

    Command: 
        Params : podName, namespaceName, fileName
        kubectl logs  {} --namespace {} > {}
'''
def collectPodLogs(podName, namespaceName):
    fileName = podName + ".txt"
    podLogCommand = logsCommand.format(podName, namespaceName, fileName) 

    print("Downloading logs for pod {}".format(podName))
    print("Issuing : " + podLogCommand)

    if os.path.exists(fileName):
        os.remove(fileName)
    os.system(podLogCommand)

    return fileName

