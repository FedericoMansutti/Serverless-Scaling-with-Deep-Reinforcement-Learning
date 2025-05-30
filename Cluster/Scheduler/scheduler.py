import os
import glob
import json
import shutil
from datetime import datetime
from kubernetes import client, config

# Configuration
RESULTS_DIR = "/app/results"
ANALYZED_DIR = os.path.join(RESULTS_DIR, "AnalyzedPods")
POD_STATUS_FILE = os.path.join(RESULTS_DIR, "podStatus.json")


def getAverageResponseTime():

    # List all the JSON files in the results folder (ignoring the podStatus.json)
    filePattern = os.path.join(RESULTS_DIR, "*.json")
    files = glob.glob(filePattern)
    responseTimes = []
    
    for file in files:

        if os.path.basename(file) == "podStatus.json":
            continue

        try:

            with open(file, "r") as f:

                data = json.load(f)
                responseTimes.append(data["Response Time"])

        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    if responseTimes:
        return sum(responseTimes) / len(responseTimes)
    
    return None


def updateReplicasNumber(deploymentName, namespace, replicas):

    # Take the configuration loaded within the Kubernetes cluster
    config.load_incluster_config()
    api = client.AppsV1Api()

    # Define the dictionary that represents what we want to update
    patch = {"spec": {"replicas": replicas}}

    # Call the K8s API to update apply the patch
    api.patch_namespaced_deployment(deploymentName, namespace, patch)
    print(f"Deployment {deploymentName} scaled to {replicas} replicas!")


def moveAnalyzedFiles():

    os.makedirs(ANALYZED_DIR, exist_ok = True)
    filePattern = os.path.join(RESULTS_DIR, "*.json")
    files = glob.glob(filePattern)

    for file in files:

        if os.path.basename(file) == "podStatus.json":
            continue
        
        dest = os.path.join(ANALYZED_DIR, os.path.basename(file))
        shutil.move(file, dest)


def getCurrentPodNames(namespace, labelSelector = "app=matrix-multiply"):

    config.load_incluster_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace, label_selector=labelSelector)

    return {pod.metadata.name for pod in pods.items}


def updatePodStatus(namespace, avgResponseTime):

    # Get current active pods
    currentPods = getCurrentPodNames(namespace)
    
    # Load previous pod status history if exists, otherwise create it
    history = {}
    if os.path.exists(POD_STATUS_FILE):

        try:
            
            with open(POD_STATUS_FILE, "r") as f:
                history = json.load(f)
        
        except Exception as e:
            print(f"Error reading pod status file: {e}")
    
    # Determine the new check number (the json will have the field 'checkNumber': 'data of that check')
    if history:

        checkNumbers = [int(key.split('_')[1]) for key in history.keys() if key.startswith("check_")]
        lastCheck = max(checkNumbers) if checkNumbers else 0

    else:

        lastCheck = 0

    newCheckNumber = lastCheck + 1
    checkKey = f"check_{newCheckNumber}"
    
    if lastCheck > 0:

        previousActive = set(history[f"check_{lastCheck}"].get("active", []))
        started = list(currentPods - previousActive)
        shutdown = list(previousActive - currentPods)

    else:

        previousActive = set()
        started = list(currentPods)             # All pods are new in check_1
        shutdown = []
    
    newStatus = {

        "timestamp": datetime.now().strftime("%d.%m.%Y_%H:%M:%S"),
        "averageResponseTime": avgResponseTime,
        "active": list(currentPods),
        "started": started,
        "shutdown": shutdown
    }
    
    # Record the new check into history
    history[checkKey] = newStatus
    
    with open(POD_STATUS_FILE, "w") as f:

        json.dump(history, f, indent = 4)


def main():

    # Values provided via environment variables in the CronJob spec
    namespace = os.environ.get("NAMESPACE", "default")
    deploymentName = os.environ.get("DEPLOYMENT_NAME", "matrix-multiply")
    
    # Process all the result files and compute the average response time
    avgResponseTime = getAverageResponseTime()

    if avgResponseTime is not None:

        # Determine desired replicas based on the scaling logic
        if avgResponseTime > 200:
            replicas = 5

        elif avgResponseTime < 100:
            replicas = 2
        
        else:
            replicas = 1

        updateReplicasNumber(deploymentName, namespace, replicas)
    
    else:
        print("No response time data found.")
    
    #Move processed files to the AnalyzedPods folder
    moveAnalyzedFiles()
    
    # Update the pod status file with active, started and shutdown pods
    updatePodStatus(namespace, avgResponseTime)


if __name__ == "__main__":
    main()