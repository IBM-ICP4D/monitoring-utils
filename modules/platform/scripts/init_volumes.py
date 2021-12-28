import platformUtils as pUtils
import nfsVolumes as nfsUtils
import allVolumes as allVolumeUtils
import pwxVolumes as pwxUtils
import configparser

print("Checking type of volume monitoring needed")
configParser = configparser.RawConfigParser()   
configFilePath = r'platform.config'
configParser.read(configFilePath)

volumesType = configParser.get('volumes', 'type')

print("Volumes = ", volumesType)
if volumesType == "nfs":
    print("Choosing NFS...")
    nfsUtils.run()
elif volumesType == "pwx":
    print("Choosing portworx...")
    pwxUtils.run()
else:
    print("Choosing all volumes with cluster privilege option...")
    allVolumeUtils.run()
