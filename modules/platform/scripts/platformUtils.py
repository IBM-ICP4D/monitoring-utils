import os
import json, requests
from requests.structures import CaseInsensitiveDict
from kubernetes import client, config, watch
import configparser



WATCHDOG_SVC='zen-watchdog-svc'
WATCHDOG_PORT='4444'
SECRET_PATH='/var/run/sharedsecrets/token'

# Point to the internal API server hostname
APISERVER='https://kubernetes.default.svc.cluster.local'

# Path to ServiceAccount token
SERVICEACCOUNT='/var/run/secrets/kubernetes.io/serviceaccount'

## Get kube client
config.load_incluster_config()
v1 = client.CoreV1Api()

def getMonitorName():
    return 'platform'

def getVolumeMonitoringEventName():
    return 'check-volume-status'

def getNamespace():
    # Check if file is present
    if os.path.isfile(SERVICEACCOUNT+"/namespace"):
        namespace_file=open(SERVICEACCOUNT+"/namespace", "r")
        namespaceData=namespace_file.read()
        namespace_file.close()
        NAMESPACE=namespaceData
        return NAMESPACE

def getToken():
    # Check if file is present
    if os.path.isfile(SERVICEACCOUNT+"/token"):
        namespace_file=open(SERVICEACCOUNT+"/token", "r")
        tokenData=namespace_file.read()
        namespace_file.close()
        TOKEN=tokenData
        return TOKEN

NAMESPACE = getNamespace()
TOKEN = getToken()

## Return list of PVCs
def list_all_pvcs(namespace):
    allPVCs=[]
    pvcResponse = v1.list_namespaced_persistent_volume_claim(namespace=namespace, watch=False)
    for pvc in pvcResponse.items:
        allPVCs.append(pvc.metadata.name)
    return allPVCs

## Return list of nodes
def list_all_nodes():
    allNodes=[]
    nodeResponse = v1.list_node()
    for node in nodeResponse.items:
        allNodes.append(node.metadata.name)
    return allNodes

def construct_node_response():
    ## Get node stats summary
    ## Get node summary from all nodes
    responses = list()
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer "+ TOKEN
    for nodeName in list_all_nodes():
        print("----------------------- Getting data from node ", nodeName)
        resp=requests.get(APISERVER+"/api/v1/nodes/"+nodeName+"/proxy/stats/summary", headers=headers, verify=SERVICEACCOUNT+"/ca.crt")
        jsonData=json.loads(resp.text)
        responses.append(jsonData)
        statusCode=resp.status_code
        if statusCode==200:
            print("Received data from node ", nodeName)
        else:
            print("Error with receiving node data ", resp.text)
    return responses

## Get pod details
def get_pvc_claim_name(volumeName, podName, volumesList):
    api_response = v1.read_namespaced_pod(name=podName, namespace=NAMESPACE)
    podVolumes = api_response.spec.volumes
    for podVolume in podVolumes:
        isVPC = podVolume.persistent_volume_claim
        volumeMountName = podVolume.name
        if isVPC != None:
            if volumeMountName==volumeName:
                if podVolume.persistent_volume_claim.claim_name not in volumesList:
                    podVolumeClaimName=podVolume.persistent_volume_claim.claim_name
                    return podVolumeClaimName
                else:
                    return None

## Record volume monitoring events into Influx DB through the watchdog post events API
def record_events(events):
    url = 'https://'+WATCHDOG_SVC+':'+WATCHDOG_PORT+'/zen-watchdog/v1/monitoring/events'
    with open(SECRET_PATH, 'r') as file:
        secret_header = file.read().replace('\n', '')
    headers = {'Content-type': 'application/json', 'secret': secret_header}
    json_string=json.dumps(events)
    print("Data to be input into influx - ", events)
    # post call to zen-watchdog to record events
    r = requests.post(url, headers=headers, data=json_string, verify=False)
    print("Response code for events POST api",r.status_code)
    return r.status_code

## Difference between two lists
def diff_between_two_lists(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    missing = list(sorted(set1 - set2))
    return missing

## Get usage pct
def get_usage_pct(usage, total):
    usagePct=(usage/total)*100

## Get user defined warning and critical percentages
def get_percentages():
    config = configparser.ConfigParser()   
    config.read("platform.config")

    critical_pct = config.getint('volumes_percentages', 'critical_pct')
    warning_pct = config.getint('volumes_percentages', 'warning_pct')

    return critical_pct, warning_pct