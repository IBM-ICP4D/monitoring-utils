# Prometheus

Prometheus is an open-source monitoring and alerting framework that is available with Openshift 4.x. You can access Prometheus, the Alerting UI and the Graphana UIs using a Web browser through the Openshift Container Platform web console.

## Procedure to access Openshift Prometheus

1.	Navigate to the OpenShift Container Platform Web console and authenticate.
2.	To access Prometheus, navigate to "Monitoring" → "Metrics".
To access the Alerting UI, navigate to "Monitoring" → "Alerts" 

## Prometheus metrics syntax 

`<metric_name> {<label1>:<value>,<label2>:<value>…} <value_of_metric>`

All metrics include the following labels

### Event Type 
Type of resource being monitored eg: check-quota-status

### Monitor Type
Name of the monitor eg: diagnostics

### Reference
Resource name eg: Watson Analytics

There are two types of metrics that are reported.

1. **Health** - Reports the health(severity) of the resource being monitored. It could be either 0(critical), 1(warning) or 2(info). Such metrics start with `watchdog_<name_of_the_monitor>_<event_type>`

Sample:

`watchdog_diagnostics_check_replica_status{event_type="check-replica-status", monitor_type="diagnostics",reference="ibm-nginx"} 2`

 The above line reports that the _ibm-nginx_ replica is currently reporting an info(2) state, concluding that it's working as expected.

2. **Metric value** - Value of the resource properties being monitored. For eg: memory_limits for a service.

`cpu_limits{event_type="check-quota-status",monitor_type="diagnostics",reference="platform"} 7.4`

The above references the CPU limit value for the entire platform.

## Setup to enable Prometheus scraping

1. **Metrics endpoint**

CPD watchdog would expose a metrics endpoint which would list out all metrics in prometheus compatible format. It includes latest metrics from out of the box diagnostics monitor and any custom monitors that have been onboarded. Once the servicemonitor is configured against this service, Prometheus would be able to scrape the metrics available through the endpoint.

2.	**Enable custom Metrics endpoint monitoring**

[Enable application monitoring](https://github.com/redhat-scholars/openshift-admins-devops/blob/v4.6blog/documentation/modules/ROOT/pages/metrics-alerting.adoc#enable-end-user-application-monitoring)

3.	**Configure a servicemonitor on the CPD controlplane namespace** 

[Setup a service monitor](https://github.com/redhat-scholars/openshift-admins-devops/blob/v4.6blog/documentation/modules/ROOT/pages/metrics-alerting.adoc#creating-a-service-monitor)

## Watchdog Diagnostics monitor

There's a default diagnostics monitor that is shipped out of the box with zen. The metrics endpoint is `<CP4D Route>/zen/metrics`

The following event types are monitored as part of the diagnostics monitor.

### 1. PVC

Event type - _check_pvc_status_

What it does: Checks if a PVC is bound. A persistent volume claim (PVC) is a request for storage by a user from a PV. Claims can request specific size and access modes (e.g: they can be mounted once read/write or many times read-only).

Health metric name - _watchdog_diagnostics_check_pvc_status_

`watchdog_diagnostics_check_pvc_status{event_type="check-pvc-status",monitor_type="diagnostics",reference="cpd-install-operator-pvc"} 2`




### 2. Replica

**Event type** - _check_replica_status_

**What it does** - Check status of deployment and statefulset replicas. A critical state indicates that the desired replicas state is not being maintained.

**Health metric name** - _watchdog_diagnostics_check_replica_status_

`watchdog_diagnostics_check_replica_status{event_type="check-replica-status",monitor_type="diagnostics",reference="cpd-install-operator"} 2`


**Metric values**

For statefulsets

a. _replicas_ - Total Replicas

`replicas{event_type="check-replica-status",monitor_type="diagnostics",reference="dsx-influxdb"} 1`


b. _current_ - Current replicas

`current{event_type="check-replica-status",monitor_type="diagnostics",reference="dsx-influxdb"} 1`

c. _ready_ - Ready replicas 

`ready{event_type="check-replica-status",monitor_type="diagnostics",reference="dsx-influxdb"} 1`

For deployments

a. _available_ - Total Available replicas

`available{event_type="check-replica-status",monitor_type="diagnostics",reference="ibm-nginx"} 2`


b. _unavailable_ - Total Unavailable replicas

`unavailable{event_type="check-replica-status",monitor_type="diagnostics",reference="cpd-install-operator"} 0`


c. _ready_ - Number of Ready replicas

`ready{event_type="check-replica-status",monitor_type="diagnostics",reference="cpd-install-operator"} 1`



### 3. Quota

Event type - _check_quota_status_

What it does: Check quota status of installed services. A critical state indicates one or more of its pods belonging to the service has run into quota issues.

**Health metric name** - _watchdog_diagnostics_check_quota_status_

`watchdog_diagnostics_check_quota_status{event_type="check-quota-status",monitor_type="diagnostics",reference="platform"} 2`

**Metric values** - 

a. _cpu_limits_ - Total CPU Limits for the monitored service

`cpu_limits{event_type="check-quota-status",monitor_type="diagnostics",reference="IBM Cloud Pak for Data Control Plane"} 7.4`

b. _cpu_requests_ - Total CPU Requests for the monitored service

`cpu_requests{event_type="check-quota-status",monitor_type="diagnostics",reference="IBM Cloud Pak for Data Control Plane"} 2.79`

c. _cpu_utilization_ - Total CPU Utilization for the monitored service

`cpu_utilization{event_type="check-quota-status",monitor_type="diagnostics",reference="IBM Cloud Pak for Data Control Plane"} 0.14`

d. _memory_limits_ - Total Memory Limits for the monitored service

`memory_limits{event_type="check-quota-status",monitor_type="diagnostics",reference="IBM Cloud Pak for Data Control Plane"} 15.6`

e. _memory_requests_ - Total Memory Requests for the monitored service

`memory_requests{event_type="check-quota-status",monitor_type="diagnostics",reference="IBM Cloud Pak for Data Control Plane"} 5.59`

f. _memory_utilization_ - Total Memory Utilization for the monitored service

`memory_utilization{event_type="check-quota-status",monitor_type="diagnostics",reference="IBM Cloud Pak for Data Control Plane"} 3.7`


### 4. Instance

Event type - _check_instance_status_

What it does: CPD services can have one or more instances which in turn contain one or more pods. An instance is said to be in running state when all pods are in Running state. 

**Health metric name** - _watchdog_diagnostics_check_instance_status_

`watchdog_diagnostics_check_instance_status{event_type="check-instance-status",monitor_type="diagnostics",reference="Instance 1"} 2`

**Metric values** -

a. _pods_ - Number of pods associated with the service instance

`pods{event_type="check-instance-status",monitor_type="diagnostics",reference="Instance 1"} 10`


### 5. Service

Event type - _check_service_status_

What it does: Check status of installed services. A critical state indicates one or more of its pods or service instances are not running as expected.

**Health metric name** - _watchdog_diagnostics_check_service_status_

`watchdog_diagnostics_check_service_status{event_type="check-service-status",monitor_type="diagnostics",reference="IBM Cloud Pak for Data Control Plane"} 2`


**Metric Values** - 

a. _instances_ - Total number of instances provisioned for the service

`instances{event_type="check-service-status",monitor_type="diagnostics",reference="IBM Cloud Pak for Data Control Plane"} 0`

b. _pods_ - Total number of pods associated with the service 

`pods{event_type="check-service-status",monitor_type="diagnostics",reference="IBM Cloud Pak for Data Control Plane"} 34`



