
import os, subprocess
import requests
import json
import platformUtils as pUtils
from kubernetes import client, config, watch
from kubernetes.stream import stream

def getNFSUsage():
    # Initialize variables
    NAMESPACE=pUtils.getNamespace()
    monitor_type=pUtils.getMonitorName()
    event_type=pUtils.getVolumeMonitoringEventName()


    # Initialize kube client
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    #Get nginx pod for execing and fetching free and usage values for user-home volume for NFS 
    result = v1.list_namespaced_pod( NAMESPACE, label_selector="component=ibm-nginx",watch=False)

    # Find total usage for user-home
    pod = result.items[0].metadata.name
    duCMD = [
        '/bin/sh',
        '-c',
        'du -s /user-home']
    resp = stream(v1.connect_get_namespaced_pod_exec, pod, NAMESPACE,
                command=duCMD,
                stderr=True, stdin=False,
                stdout=True, tty=False)
    usageString=resp.split()


    # Find the free space for user-home
    dfCMD = [
        '/bin/sh',
        '-c',
        'df /user-home']
    resp = stream(v1.connect_get_namespaced_pod_exec, pod, NAMESPACE,
                command=dfCMD,
                stderr=True, stdin=False,
                stdout=True, tty=False)
    freeString=resp.split()

    # configure post request and set secret headers
    url = 'https://zen-watchdog-svc:4444/zen-watchdog/v1/monitoring/events'
    with open('/var/run/sharedsecrets/token', 'r') as file:
        secret_header = file.read().replace('\n', '')
    headers = {'Content-type': 'application/json', 'secret': secret_header}

    severity = "info"
    usageInt=int(usageString[0])
    freeInt=int(freeString[8])
    usagePct=(usageInt/freeInt)*100

    critical_pct, warning_pct=pUtils.get_percentages()

    if usagePct>critical_pct:
        severity='critical'
    elif usagePct>warning_pct:
        severity='warning'
    events=[]
    metadata="Usage=%s,Free=%s" % (usageString[0], freeString[8])
    data = {"monitor_type":monitor_type, "event_type":event_type, "severity":severity, "metadata":metadata, "reference":"user-home"}
    print("Data to be input into a database - ", data)
    events.append(data)
    json_string=json.dumps(events)
    statusCode=pUtils.record_events(events)
    if statusCode==200:
        print("Events added successfully!!")
    else:
        print("Issue with recording NFS events. Please try again later.")

def run():
    getNFSUsage()