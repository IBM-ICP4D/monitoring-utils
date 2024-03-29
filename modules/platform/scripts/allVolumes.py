# This program prints Hello, world!
import os
import requests
import math
import json
import platformUtils as pUtils
from requests.structures import CaseInsensitiveDict
from kubernetes import client, config, watch

def getAllVolumes():

    NAMESPACE=pUtils.getNamespace()
    monitor_type=pUtils.getMonitorName()
    event_type=pUtils.getVolumeMonitoringEventName()
    all_events_recorded=False
    volumesList=[]
    allPVCs=[]
    events=[]
    missing=[]
    responses = list()

    ## Get list of PVCs
    allPVCs=pUtils.list_all_pvcs(NAMESPACE)
    print("All PVCs = ", allPVCs)
    missing = pUtils.diff_between_two_lists(allPVCs, volumesList)
    print("Missing - ", missing)

    ## Get node summary from all nodes
    responses=pUtils.construct_node_response()

    ## Browse through node summary responses
    ## Browse through pods in the namesapce and filter out the volumes that have not been measured yet
    ## Construct the event objects for those volumes
    ## Record the events in a database
    for response in responses:
        print("Reading response ..... ")
        if not pUtils.diff_between_two_lists(allPVCs, volumesList):
            print("All pvcs covered...")
            break
        print("Reading node response .......................................... ")
        if 'pods' in response:
            for pod in response["pods"]:
                
                if not pUtils.diff_between_two_lists(allPVCs, volumesList):
                    print("All pvcs covered...")
                    break
                
                ## Pod metadata
                podRef=pod["podRef"]
                namespace=podRef["namespace"]
                podName=podRef["name"]
                

                ## If pod from different namespace, ignore. If not, find the associated volumes.
                ## find the claim name from the mount name(this is not available through the nodes API and hence the need to use the pods API)
                ## If claim already added to the volumesList(list of PVCs whose usage has been calculated, continue to the next volume)
                if namespace != NAMESPACE:
                    continue
                print("Pod being considered - ", podName)
                if 'volume' in pod:
                    for volume in pod["volume"]:
                        volumeName=volume["name"]
                        podVolumeClaimName=''

                        ## Find out the pvc claim name from the mount name using the pods object
                        podVolumeClaimName=pUtils.get_pvc_claim_name(volumeName, podName, volumesList)
                        print('Pod Volume claim = ', podVolumeClaimName)
                        if podVolumeClaimName==None:
                            print("Moving on from data for volume ", volumeName)
                            continue
                        volumesList.append(podVolumeClaimName)

                        ## Construct the event object
                        usedBytes=volume["usedBytes"]
                        totalBytes=volume["capacityBytes"]
                        usagePct=(usedBytes/totalBytes)*100
                        severity='info'
                        
                        critical_pct, warning_pct=pUtils.get_percentages()

                        if usagePct>critical_pct:
                            severity='critical'
                        elif usagePct>warning_pct:
                            severity='warning'
                        metadata="Usage=%s,Total=%s,UsagePct=%s" % (convert_size(usedBytes), convert_size(totalBytes), usagePct)
                        print("Adding data for volume ", volumeName)
                        data = {"monitor_type":monitor_type, "event_type":event_type, "severity":severity, "metadata":metadata, "reference":podVolumeClaimName}

                        events.append(data)
                        if pUtils.diff_between_two_lists(allPVCs, volumesList):
                            continue
                        else:
                            print("All PVCs covered...")
                            ## Record all events into a database using the watchdog service
                            status_code=pUtils.record_events(events)
                            if status_code==200:
                                print("Successfully recorded the Volume monitoring events into a database.")
                                all_events_recorded=True
                            break

    if not all_events_recorded:
        pUtils.record_events(events)

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def run():
    getAllVolumes()