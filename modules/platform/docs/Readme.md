**Platform Monitoring**

Platform monitoring cronjob monitors the following resources and ensures there are warnings and alerts to go along with it.

1. Volumes usage tracking

PVs are resources in the cluster. PVCs are requests for those resources and also act as claim checks to the resource. It is essential that we track volume usage across the cloud pak instance to help warn if we're running out of disk space.

The Volume monitor works in different ways depending on requirement.

**Complete**

**NFS** - If your primary storage class is NFS, ensure the type value under Volumes is set to `nfs`. 

**All** - If the option to monitor using the node API is available, ensure the type value under volumes is set to `all`. Make sure the pre-requisites(cluster role and cluster role binding) is taken care of.

**In Progress**

**Portworx** - Set the type value to "pwx"