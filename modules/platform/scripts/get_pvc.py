from kubernetes import client, config, watch
import os, subprocess

ns = "zen1003"
allPVCs=[]
volumesList=[]

config.load_incluster_config()
v1 = client.CoreV1Api()

pvcs = v1.list_namespaced_persistent_volume_claim(namespace=ns, watch=False)

for pvc in pvcs.items:
    print(pvc.metadata.name)
    allPVCs.append(pvc.metadata.name)

api_response = v1.read_namespaced_pod(name="zen-watchdog-bc5b8b9fd-qs7z5", namespace="zen1003")
podVolumes = api_response.spec.volumes
print("Pod Volumes - ", podVolumes)

for volume in podVolumes:
    isVPC = volume.persistent_volume_claim
    if isVPC != None:
        name=volume.persistent_volume_claim.claim_name
        if name in allPVCs:
            volumesList.append(name)


print("All PVCs = ",allPVCs)
print("PVC in pod = ",volumesList)

missing = list(sorted(allPVCs - volumesList))







    

