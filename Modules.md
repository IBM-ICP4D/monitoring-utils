**Modules**

Modules are a convenient way to collate scripts that monitor related resources. Ideally, we would like to have it grouped by services where each service is responsible to creating and maintaining the monitor and build scripts. Each module is represented as a separate folder and contains the following structure

**Structure of a Module**

_docs_ - Docs contains readme and other related documentation for the responsible module.

_scripts_ - Contains the monitoring scripts

_extensions_ - Extensions that help define the monitor settings like image name, tag, associatd service account, volumes etc. This extension is installed on the CPD instance namespace and provisions a cronjob which runs the monitoring scripts that is associated with the module.

**Instructions to install the module**

1. Pre-requisites
Each module may involve certain pre-requisites that must be followed before the module is installed. 

2. Build docker image
This step constructs the docker image for the module. It contains any install steps, the scripts to monitor the resources and startup commands, if any. 

3. Push the docker image to the cluster

4. Edit the extensions file under the module/extensions folder
The extensions file would need to be updated to include certain custom details like image, schedule etc. This would translated into the cronjob settings that would be created to run the monitor.

5. Oc login to the cluster 

6. Install the edited extensions yaml located under the module/extensions folder

`oc apply -f <extension_file>.yaml` 

**What happens once the module is installed**

Once the module has been installed, a cronjob would be created based on the extensions file. This cronjob would be responsible for monitoring the resources that are part of the module. 

