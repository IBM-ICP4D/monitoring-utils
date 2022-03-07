**Platform Monitoring**

Platform monitoring cronjob monitors the following resources and ensures there are warnings and alerts to go along with it.

**Volumes usage tracking**

A PersistentVolume (PV) is a piece of storage in the cluster that has been provisioned by an administrator or dynamically provisioned using Storage Classes. It is a resource in the cluster just like a node is a cluster resource. PVs are volume plugins like Volumes, but have a lifecycle independent of any individual Pod that uses the PV. This API object captures the details of the implementation of the storage, be that NFS, iSCSI, or a cloud-provider-specific storage system.

A PersistentVolumeClaim (PVC) is a request for storage by a user. It is similar to a Pod. Pods consume node resources and PVCs consume PV resources. Pods can request specific levels of resources (CPU and Memory). Claims can request specific size and access modes (e.g., they can be mounted ReadWriteOnce, ReadOnlyMany or ReadWriteMany).

PVs are resources in the cluster. PVCs are requests for those resources and also act as claim checks to the resource. It is essential that we track volume usage across the cloud pak instance to help warn if we're running out of disk space.

***User defined properties***

1. Type - This defines the type of storage class in use. By default the type is set to `all` which works for monitoring volumes belonging to any storage provider and requires the user to configure certain rules that permits the CPD editor Service Account access to cluster APIs. The user also has the option to specify certain types like `nfs` which would eliminate the need for cluster privileges by leveraging the storage provider APIs directly. Support for additional storage providers like Openshift container storage(OCS) and Portworx are in progress and would be included shortly. Reminder that the `all` option would continue to support persistent volumes provisioned by any storage provider including OCS and Portworx.

**nfs** - If your primary storage class is NFS, ensure the type value under Volumes is set to `nfs`. 

**all** - This option works for all scenarios irrespective of the storage class. However, this option requires the need for cluster role access. 
Please follow the steps in [here](pre-requisites.md) to address the pre-requisites.

2. Percentages - The user also has the option to set threshold and critical percentages for alerting purposes. This is done as part of the platform.config file. By default, we have critical percentage set to 85% and threshold to 75%. This can be modified as per the user's liking.


**Alerting**

Monitoring and Alerting specifically is documented in detail [here](https://github.com/IBM-ICP4D/monitoring-utils/blob/main/docs/Monitoring.md#alert). Please refer to this section to setup alerting rules and forwarding connections including SMTP, SNMP traps and Slack alerts.

Besides Alerting, all monitored resources are also available to view as part of the Cloud Pak for Data Montioring UI. This page will also show you the critical and warning events currently being tracked and alerted on. 