- [Introduction and Purpose](#introduction-and-purpose)
- [Cloud Pak for Data Monitoring Framework Concepts](#cloud-pak-for-data-monitoring-framework-concepts)
- [Introduce Custom Monitors](#introduce-custom-monitors)
- [Sample Monitor](#sample-monitor)
  - [Sample - Monitor and Record PVC status](#sample---monitor-and-record-pvc-status)
  - [Building the Docker Image for the Monitor](#building-the-docker-image-for-the-monitor)
  - [Sample Extension Configmap for the Monitor](#sample-extension-configmap-for-the-monitor)
- [Service Monitor Development Guidelines](#service-monitor-development-guidelines)


## Introduction and Purpose

The intention behind this repo is to help users understand and enhance the monitoring feature by introducing sample scripts through custom monitors which would in turn help proactively address and alert of any potential issues before they turn critical.

This particular readme focuses on setting up custom monitors. It takes you through the process of creating and introducing scripts into a Cloud Pak for Data instance that can monitor and report/persist state information into an internal database. The Watchdog Alert manager then looks into these events to decide, in conjunction with associated alerting rules, to trigger alerts if needed.

## Cloud Pak for Data Monitoring Framework Concepts

Please refer to the [following doc](docs/Monitoring.md) for extensive information on monitoring essentials.

## Introduce Custom Monitors

Developers can set up custom monitors using the alerting framework.

Monitors check the state of entities periodically and generate events that are stored in the metastore database. Administrators might be interested in node resource efficiency, memory quotas, license usage, user management events, and provisioning diagnostics. You can set up custom monitors that track resource usage against your target usage for the platform.

Monitors can be registered into Cloud Pak for Data through an extension configmap. The configmap has all the details that are needed to create a cron job, including the details of the script, the image to be used, the schedule for the cron job, and any environment variables. This ensures that the alerting framework has all the necessary information to create a cron job, monitor events frequently, and trigger alerts if and when needed.

A monitor consists of:
1.  A monitor application built and packaged into a docker image.
    1.  The monitor logic can be written in any language.
    2.  The monitor creates and sends events to the zen-watchdog monitoring component using a POST http request
2.  A monitoring extension configmap that contains metadata for the monitor such as the event types for the monitor, and a definition for the monitor cronjob.
3.  An optional alert type extension configmap, if the monitor has custom alert rules other than the default rules for "platform".

## Sample Monitor

Here follows a sample monitor script which tracks PVCs and reports events based on the status. If a PVC is bound, an "info" is registered for the PVC and a "critical" event is recorded for "unbound" or "failed" PVC states.  

Our monitor will be based on Python 3.8 and we'll be using the Kubernetes Python SDK to interact with the cluster. 

The following tutorial assumes you'll be using your own image and details steps from building the script, to the docker file needed to run and finally the extension configmap needed to ensure this is included and run as part of the alerting framework. 

### Sample - Monitor and Record PVC status

The following script uses the in cluster config to authenticate to kubernetes and access the resources. By default you have access to the following volumes:
* _zen-service-broker-secret_ 

The following environment variables are made available as part of the cronjob initialization 
* _ICPD_CONTROLPLANE_NAMESPACE_  - the control plane namespace  

The python script below lists PVCs and generates events based on its state. All non-Bound PVCs are recorded with critical severity. 
The events are sent as a json array to the POST events endpoint (auth with the service broker token). Check [POST Events](docs/Monitoring.md#post-events) for more information.

**Python app**

```
pvc-monitor/ 
  pvc-monitor.py
  requirements.txt
  Dockerfile
```

* `pvc-monitor.py` is the monitor code that is called when the monitor cronjob runs
* `Dockerfile` is used for building the docker image for the monitor
* Required Python packages are listed in the `requirements.txt`


**pvc-monitor.py**

````python
import os
import requests
import json
from kubernetes import client, config, watch
def main():
    # setup the namespace
    ns = os.environ.get('ICPD_CONTROLPLANE_NAMESPACE')
    if ns is None:
        ns = ""
    monitor_type = "sample-monitor"
    event_type = "check-pvc-bound"

    # configure client
    config.load_incluster_config()
    api = client.CoreV1Api()

    # configure post request and set secret headers
    url = 'https://zen-watchdog-svc:4444/zen-watchdog/v1/monitoring/events'
    with open('/var/run/sharedsecrets/token', 'r') as file:
        secret_header = file.read().replace('\n', '')
    headers = {'Content-type': 'application/json', 'secret': secret_header}

    # Print PVC list, set status as critical for unbound or failed pvc
    pvcs = api.list_namespaced_persistent_volume_claim(namespace=ns, watch=False)
    events = []
    for pvc in pvcs.items:
        severity = "info"
        print("pvc {}: {}".format(pvc.metadata.name, pvc.status.phase))
        if pvc.status.phase != 'Bound':
            severity = "critical"
        metadata = "{}={}".format("Phase", str(pvc.status.phase))
        data = {"monitor_type":monitor_type, "event_type":event_type, "severity":severity, "metadata":metadata, "reference":pvc.metadata.name}
        events.append(data)
    json_string = json.dumps(events)

    # post call to zen-watchdog to record events
    r = requests.post(url, headers=headers, data=json_string, verify=False)
    print("status code: {}".format(r.status_code))

if __name__ == '__main__': 
    main()
````

**Docker File**

```
# set base image (host OS) 
FROM python:3.8 
RUN mkdir /pvc-monitor 

# set the working directory in the container 
WORKDIR /pvc-monitor 
ADD . /pvc-monitor 

# install dependencies 
RUN pip install -r requirements.txt 

# command to run on container start 
CMD [ "python", "./pvc_check.py" ] 
```

**requirements.txt**
```
kubernetes==11.0.0 
```

### Building the Docker Image for the Monitor

Once the above structure is in place, we can build the docker image using, 

`podman build -f Dockerfile -t pvc-monitor:latest .` 

Finally, let's tag and push the image into the openshift registry so that it can be accessed through the alerting cronjob. 

`podman login <docker-registry> -u kubeadmin -p $(oc whoami -t) --tls-verify=false`

`podman tag <docker-image-id> <docker-registry>/<namespace>/pvc-monitor:latest`

`podman push <docker-registry>/<namespace>/pvc-monitor:latest`


### Sample Extension Configmap for the Monitor

Once we have the image pushed, we can now create an extension configmap pointing to the above configuration. This will ensure that the alert manager picks it up and creates a cronjob, thereby ensuring the script is run at scheduled intervals. 

```
oc apply -f sample-monitor-extension.yaml
```

sample-monitor-extension.yaml

````yaml
apiVersion: v1 
kind: ConfigMap 
metadata: 
  name: sample-monitor-extension
  labels: 
    icpdata_addon: "true" 
    icpdata_addon_version: "1.0.0" 
data: 
  extensions: |
      [
        {
          "extension_point_id": "zen_alert_monitor",
          "extension_name": "zen_alert_monitor_sample",
          "display_name": "Sample alert monitor",
          "details": {
            "name":"sample-monitor",
            "image": "image-registry.openshift-image-registry.svc:5000/zen/pvc-monitor:latest",
            "schedule": "*/10 * * * *",
            "event_types": [
              {
                "name": "check-pvc-bound",
                "simple_name": "PVC bound check",
                "alert_type": "platform",
                "short_description": "A monitor that checks whether a PVC is bound.",
                "long_description": "PVC status phase: <Phase>"
              }
            ]
          }
        }
      ]
````

Once the extension configmap is created, the Watchdog alert manager(WAM) would then read the extensions and create a cronjob that uses the docker image to monitor and report resource status.


For additional guidelines, see [Service Monitor Development Guidelines](#service-monitor-development-guidelines)

## Service Monitor Development Guidelines

* During development, if there are changes to the monitor extension configmap, update the icpdata_addon_version so that zen-watcher detects the new changes.  For example, if the icpdata_addon_version was originally "5.0.0", increment it to some higher value like "5.1.0".
```
icpdata_addon_version: 5.1.0
```
* After the monitor extension configmap is created, check the log of the ```zen-watcher-xxx``` pod to see if the extension was successfully detected, and that there are no parsing errors.
* After the monitor extension configmap is created, monitor cronjobs are not immediately created by zen-watchdog, and may take up to 10 minutes.  For development, change schedule of the ```watchdog-alert-monitoring-cronjob``` cronjob from 10 minutes to 1 minute by editing it.  This is so the monitor cronjob can be created sooner.
* When the monitor cronjob is created, manually change the imagePullPolicy from IfNotPresent to Always for development purposes.  This ensures the monitor cronjob is running with latest image that was pushed to the image registry.
* For troubleshooing, edit the monitor cronjob and change the successfulJobsHistoryLimit and failedJobsHistoryLimit from 0 to 1.  This is so one cronjob pod is kept around, which allows you to see the cronjob pod log for debugging.  In addition, consider changing the schedule to 1 minute so the cronjob is run more often for debugging purposes.
* The OpenShift internal registry is used here as an example for development purposes.  For production, the image can be made available in any accessible image registry.
* During development, if there are changes to an event type (e.g. long_description) in the monitor extension configmap and the configmap is applied, the event type definitions are not automatically updated in the internal metastore database.  The events will still use stale information when they are displayed in the CPD Monitoring Events page.  To update event types, delete the existing rows in the event_types table, and restart the zen-watchdog pod which will re-populate the table.  For example,
```
oc rsh zen-metastore-edb-1
psql -U postgres -d zen
delete from event_types;
\q
exit

oc delete po -l component=zen-watchdog
```

