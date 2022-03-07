import platformUtils as pUtils
import nfsVolumes as nfsUtils
import allVolumes as allVolumeUtils
import pwxVolumes as pwxUtils
import configparser

print("Checking type of volume monitoring needed")
config = configparser.ConfigParser()   
config.read("platform.config")

volumesType = config.get('volumes', 'type')

print("Volumes = ", volumesType)
if volumesType == "nfs":
    print("Choosing NFS...")
    nfsUtils.run()
elif volumesType == "pwx":
    print("Choosing portworx...")
    pwxUtils.run()
elif volumesType == "all":
    print("Choosing all volumes with cluster privilege option...")
    allVolumeUtils.run()
