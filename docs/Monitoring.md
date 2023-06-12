- [Monitoring and Alerting in Cloud Pak for Data](#monitoring-and-alerting-in-cloud-pak-for-data)
  - [Glossary](#glossary)
    - [Event](#event)
    - [Event type](#event-type)
    - [Severity](#severity)
    - [Alert](#alert)
    - [Alert Monitor](#alert-monitor)
    - [Alert Type](#alert-type)
    - [Alert Profile](#alert-profile)
    - [Watchdog Alert manager](#watchdog-alert-manager)
  - [Diagnostics monitor](#diagnostics-monitor)
  - [Monitoring Extensions Overview](#monitoring-extensions-overview)
  - [Alert Monitor Extension](#alert-monitor-extension)
    - [Overview](#overview)
    - [Monitor Cronjob Metadata](#monitor-cronjob-metadata)
    - [Event Types](#event-types)
      - [Standarized Variables Names in long\_description](#standarized-variables-names-in-long_description)
  - [Alert Type Extension](#alert-type-extension)
  - [Alert Profile Extension](#alert-profile-extension)
    - [SMTP](#smtp)
    - [SNMP](#snmp)
    - [Slack](#slack)
  - [Custom Monitor Implementation Notes](#custom-monitor-implementation-notes)
    - [POST Events](#post-events)
    - [POST Events Sample](#post-events-sample)
    - [Zen service broker secret](#zen-service-broker-secret)
    - [Events Body](#events-body)
# Monitoring and Alerting in Cloud Pak for Data

IBM Cloud Pak for Data provides a monitoring and alerting framework that you can use to monitor the state of the platform and set up events to alert based on thresholds.

## Glossary

### Event
An event is the state of an entity such as a pod, persistent volume claim (PVC), or other resource at a certain point in time. 

### Event type
An event type is the type of resource being monitored. It can be a pod, persistent volume claim (PVC) etc. Each event type is associated with an alert type which allows for separate rules to be set for different resources. For example, a PVC critical state would need to be alerted immediately while a pod could have a relaxed rule.

### Severity
Each event is associated with a severity which could be one of "critical", "warning" or "info" based on state of the monitored entity. For example, a pod in Running status could emit an Informational Event, while one in Pending status a warning event and critical event for pod which is in failing state.

### Alert
Alerts can be configured to be sent based on the above events. For example, an alert can be set to trigger when a pod indicates 3 consecutive critical events. 
Alerts could also be based on thresholds ( say resource consumption > 75% ). We support SMTP, SNMP(v2) and Slack alert forwarding at this time.

### Alert Monitor
A script that is scheduled to run as part of a cronjob which monitors resources and emits events. These events are persisted in an internal database which is then monitored by the Watchdog Alert Manager(WAM).

### Alert Type
Rules for alerting. Can be set to trigger in case of warning or critical events.

### Alert Profile
Enable alert forwarding and associated properties. For example, users can set SMTP to true to receive e-mail alerts and also provide intended recipients to receive the alerts.

### Watchdog Alert manager
A cronjob that serves 2 purposes -- 
 1. Sets up cronjobs based on *custom monitor extensions*
 2. Monitors events in an internal database to identify any potential alerts(based on Alert Type) and forwards the alerts based on associated profiles.

## Diagnostics monitor

Cloud Pak for data installs a *diagnostics* monitor that monitors a few critical resources every 10 mins. These *event types*(resources) being tracked out of the box are as follows:

 1. **Services** - Cumulative status of *Service instances* as well as pods belonging to *services* installed as part of Cloud Pad for data.
 2. **Service Instances** - Tracks status of pods associated with the *service instance*.
 3. **Replicas** - Checks the availability of *replicas* for *deployments* and *statefulsets*.
 4. **Persistent Volume Claim** - Looks for issues surrounding PVCs in instance namespaces.
 5. **Service quota** - Tracks *quota* status of installed *services*.

**WAM**(running every 10 mins) then looks at all the events that have been pushed into an internal database to look specifically for *Critical/Warning* events. It then cross checks those events with associated alerting rules for those *event types* and triggers alerts if needed. 
For example, if the *alert type* for PVC is set to immediate and one of the PVCs were found to be in *critical* state, the **WAM** would trigger alerts as soon as it finds one in *critical* state in the database.


## Monitoring Extensions Overview

Custom monitor and profiles can be introduced into the CP4D ecosystem using extensions. Extensions are configmaps containing metadata information that can be leveraged by CP4D microservices. We use this concept to introduce information about Custom monitors, alert types and profiles and then use it as basis for monitoring and alerting purposes. For eg: The type of alert, whether _immediate_ or _custom_, can be set as part of the _alert type_ extension configmap and it dictates how alerts are sent.

The monitoring extensions together provide a monitoring and alerting framework.

## Alert Monitor Extension
**Extension ID** - *zen_alert_monitor*

### Overview
Developers can set up custom monitors using the alerting framework.

Monitors check the state of event types(resources) periodically and generate events that are stored in an internal database. Administrators might be interested in node resource efficiency, memory quotas, license usage, user management events, and provisioning diagnostics. You can set up custom monitors that track resource usage against your target usage for the platform.

Monitors can be registered into Cloud Pak for Data through an extension configmap. The configmap has all the details that are needed to create a cron job, including the details of the script, the image to be used, the schedule for the cron job, and any environment variables. This ensures that the alerting framework has all the necessary information to create a cron job, monitor events frequently, and trigger alerts if and when needed.

### Monitor Cronjob Metadata
The monitor part of the configmap provides metadata for the cronjob. The extension id for registering the monitors  is "zen_alert_monitor". The alert manager looks for all extensions defiened under the above id and creates cronjobs for each of them. The details for the monitor is provided under the "details" section in the configmap. 

```
{ 
  "image"           - Image to be used. Format "<docker-registry>/<image_name>:<tag>.
  "name"            - Name of the monitor.  Underscores are not allowed.  The name of the monitor cronjob will be name + "-cronjob"
  "schedule"        - Schedule for the cronjob, in cron expression format
  "command"         - Command to be run when cronjob gets scheduled
  "args"            - Arguments for the above command
  "service_account" - Service account for the monitor cronjob
  "env_vars"        - Environment variables
  "working_dir"     - Working directory
  "event_types"     - Types of events that are being monitored. (see below)
  "volumes"         - Volumes
  "volume_mounts"   - Volume mounts
  "resources"       - Resource requirements for the monitor cronjob.  Avaialble starting in CPD 4.7.
} 
```

By default, the zen-service-broker-secret volumes are mounted to the cronjob (no need to mount them again as part of the above config setup). They're available as follows: 

````yaml
volumeMounts: 
  mountPath: /var/run/sharedsecrets 
  name: zen-service-broker-secret 
````

Extenion Configmap Example:
```
kind: ConfigMap
apiVersion: v1
metadata:
  name: my-sample-extension
  labels:
    icpdata_addon: 'true'
    icpdata_addon_version: 4.3.0
data:
  extensions: |
    [
      {
        "extension_point_id": "zen_alert_monitor",
        "extension_name": "my_sample_service_monitor",
        "display_name": "My Sample Service Monitor",
        "details": {
          "name": "mysampleservicemonitor",
          "image": "icr.io/cpopen/cpd/my-sample-monitor:latest",
          "schedule": "*/10 * * * *",
          "command": ["sh"],
          "args": ["/opt/ansible/bin/cp4d-monitors/run_scripts.sh"],
          "resources": {
            "limits": {
              "cpu": "86m",
              "ephemeral-storage": "151Mi",
              "memory": "186Mi"
            },
            "requests": {
              "cpu": "21m",
              "ephemeral-storage": "31Mi",
              "memory": "121Mi"
            }
          },
          "event_types": [
            {
              "name": "global_connections_count",
              "simple_name": "Number of CP4D Platform connections",
              "alert_type": "platform",
              "short_description": "Number of CP4D Platform connections",
              "long_description": "Number of CP4D Platform connections: <global_connections_count>",
            }
          ]
        }
      }
    ]
```

### Event Types
Each monitor can be associated with one or more event types. These event types need to be explicitly stated in the above monitor configuration. For example, 

```
"event_types": [
    {
      "name"               - Name of the event type (string)
      "simple_name"        - Display name of the event type (string)
      "alert_type"         - Name of the alert type (string)
      "short_description"  - Short description of the event type (string)
      "long_description"   - Long description of the event type.  Can contain variable names encapsulated with < and >, with are resolved by metadata when the event object is created. (string)
      "url"                - Optional url link to a page with additional information for the event (string)
      "url_title"          - Optional link name for the url link (string)
      "reason_code_prefix" - Reason code prefix for the event (string)
     }
  ]
```

#### Standarized Variables Names in long_description
By convention, the following variables should be used in the long_description when applicable.  This allows events to be correlated by common fields.
* \<addon_id\> - addon id for the event
* \<namespace\> - namespace for the event


[Sample for alert monitor](./extensions/alert_monitor.yaml)

## Alert Type Extension
**Extension ID** - *zen_alert_type*

Alerting rules can be defined through zen_alert_type extensions. Each alert type consists of rules for events belonging to type "critical" and "warning". Alerts can be enabled for critical and warning events and their rules define on when to forward a certain alert to the user as well as the throttle time so users are not spammed with alerts when a certain situation persists.

Rules can be defined based on severity types -- critical or warning.  You can't configure the alert rules for informational alerts.

The alerting rules are defined under "details" section in the extension configmap 

The conditions for alerts are then defined under critical or warning. 

```
{ 
  "trigger_type"                 - Can be "immediate" or "custom". Immediate states that the alert needs to be sent as soon as an event of the severity is encountered. Best used with critical severity.  The custom option is associated with *alert_count* and *alert_over_count*. |
  "alert_count"                  - Count of events with the severity type for the current resource.
  "alert_over_count"             - Count of total past events for the current resource to be referenced.
  "snooze_time"                  - The number of hours to wait before an alert is sent for the current resource.
  "notify_when_condition_clears" - Determines whether to send an alert when the *critical/warning* condition clears, if a previous alert for the critical/warning condition had been sent earlier.
} 
```

When a "critical" or "warning" event is encountered, the alert manager looks at the alert type associated with the event type for the event. Based on the trigger type, an alert will be sent either immediately or based on the custom parameters provided via alert_count and alert_over_count.  
An alert_count of 5 and alert_over_count of 20 essentially means that an alert will be sent if 5 of the last 20 events recorded for that reference were of that severity ("warning" or "critical") 
The "notify_when_condition_clears" flag is used in tandem with "critical" severity and determines whether an alert needs to be sent if the object is no longer in "critical" state. 

The default alerting rules for "platform" are set as follows:
-   For critical events, a condition persists for 30 minutes when 3 consecutive critical events are recorded during monitor runs. When the condition is alerted, it is snoozed for 12 hours.
-   For warning events, 5 warning events are recorded during the last 20 monitor runs with a snooze period of 24 hours.


[Sample for alert type](extensions/alert_rules.yaml)

## Alert Profile Extension
**Extension ID** - *zen_alert_profile*

Settings to enable/disable SMTP, SNMP and Slack alerts. They're brought in via extensions ( extension_point_id : zen_alert_profile ) and a default profile is installed during cpd install. The default profile has all settings enabled and based on the configuration availability, the alerts are forwarded.

Currently, you cannot set up custom alert profiles.

```
{
  "extension_point_id": "zen_alert_profile",
  "extension_name": "Default",
  "details": {
    "name": "default",
    "description": "Default alert profile which enables all possible alerts, as long as the respective configuration details are provided.",
    "alerts": {
      "smtp":true,
      "snmp":true,
      "slack":true,
    },
    "smtp":{
      "registered_emails":[]
    }
  }
}
```

[Sample for alert profile](extensions/alert_profile.yaml)

### SMTP

Alerts can be sent as email by using SMTP. You can configure a connection to your SMTP server in Administration > Platform configuration.

### SNMP

 Alerts can be sent as traps by using SNMP (simple network management protocol). SNMP is a standard protocol for collecting and organizing information about managed devices or services. It exposes management data in the form of variables that are defined in managed information base (MIB) files.

### Slack 

To enable Slack alerts, an administrator must provide a webhook URL, which can be set up to receive notifications on a channel. When the webhook URL is available, the following information can be provided:

Reason codes are associated with SNMP to allow for easy recognition. Reason codes are made up of a prefix and a suffix based on the following.

**Prefix** - This is specified for each event type and is identified as part of the alert monitor extension (check [sample](extensions/alert_monitor.yaml))

**Suffix** - This identifies the state of the resource. 

00-information 

01-warning

02-critical

Thus a trap with reason code 102 would mean that a replica (w/prefix=1) is in critical (suffix=02) state.

## Custom Monitor Implementation Notes

### POST Events

The monitor script posts events with the /v1/monitoring/events endpoint. The endpoint is served by the zen-watchdog service. 

### POST Events Sample

````curl
curl -X POST -k https://zen-watchdog-svc:4444/v1/monitoring/events \
-H 'secret: <zen-service-broker-secret-token>' 
-d '<event_body>' 
````

### Zen service broker secret

The post calls are authenticated in zen-watchdog using the zen service broker token. The alert manager mounts the secret volume to all the monitor cronjobs, hence no additional work is needed as part of the monitor setup. The secret token is available under "/var/run/sharedsecrets/token" The value of this token is to be retrieved and passed as the value for the secret header in the above POST call. 

### Events Body

The body of the json included in the POST is as follows -  

```
[
  {
    "monitor_type" -  Name of the monitor (string)
    "event_type"   -  Event type (string)
    "severity"     -  One of { "critical", "warning" or "info" }  (string)
    "reference"    -  Object reference  (string)
    "metadata"     -  Comma-separated, key-value pair where the key is a variable denoted by <...> in the long description.  The value replaces the variable in the event.  (string)
  }
]
```

Notes:

metadata

This is a comma-separated, key-value pair that specifies how variables in your ```long_description``` are be resolved.  For example, if your long description is:
```
Test result CP4D Platform connection: <global_connection_valid>
```
And your metadata is:
```
global_connection_valid=1
```
Your long description for the event will be resolved to:
```
Test result CP4D Platform connection: 1
```

*Example of post events body*
```
[
  {
    "monitor_type" : "diagnostics",
    "event_type" : "check-replica-status",
    "severity" : "critical",
    "reference" : "metastore-db",
    "metadata" : "Unavailable=2"
  },
  {
    "monitor_type" : "diagnostics",
    "event_type" : "check-replica-status",
    "severity" : "info",
    "reference" : "zen-core",
    "metadata" : "Unavailable=0"
  }
]
```

The event for `metastore-db` reports critical severity since there are unavailable replicas being reported by the kube api.
Event posts with severity type "info" when the monitored entity works as expected.
