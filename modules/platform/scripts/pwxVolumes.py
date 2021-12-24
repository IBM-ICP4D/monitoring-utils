import json

jsonStr = {"pods": [
  {
   "podRef": {
    "name": "sdn-h5f2n",
    "namespace": "openshift-sdn",
    "uid": "72533be3-d91f-43e7-b85a-13b4654da0e7"
   },
   "startTime": "2021-06-23T01:10:21Z",
   "containers": [
    {
     "name": "sdn",
     "startTime": "2021-12-23T23:19:47Z",
     "cpu": {
      "time": "2021-12-23T23:32:33Z",
      "usageNanoCores": 4650432,
      "usageCoreNanoSeconds": 28198476319
     },
     "memory": {
      "time": "2021-12-23T23:32:33Z",
      "usageBytes": 129355776,
      "workingSetBytes": 78622720,
      "rssBytes": 62676992,
      "pageFaults": 2196711,
      "majorPageFaults": 297
     },
     "rootfs": {
      "time": "2021-12-23T23:32:33Z",
      "availableBytes": 81190658048,
      "capacityBytes": 106808979456,
      "usedBytes": 0,
      "inodesFree": 52040039,
      "inodes": 52157888,
      "inodesUsed": 17
     },
     "logs": {
      "time": "2021-12-23T23:32:33Z",
      "availableBytes": 81190658048,
      "capacityBytes": 106808979456,
      "usedBytes": 49958912,
      "inodesFree": 52040039,
      "inodes": 52157888,
      "inodesUsed": 117849
     }
    },
    {
     "name": "kube-rbac-proxy",
     "startTime": "2021-12-23T23:19:47Z",
     "cpu": {
      "time": "2021-12-23T23:32:21Z",
      "usageNanoCores": 34518,
      "usageCoreNanoSeconds": 175640786
     },
     "memory": {
      "time": "2021-12-23T23:32:21Z",
      "usageBytes": 36876288,
      "workingSetBytes": 14295040,
      "rssBytes": 14225408,
      "pageFaults": 2277,
      "majorPageFaults": 66
     },
     "rootfs": {
      "time": "2021-12-23T23:32:21Z",
      "availableBytes": 81190658048,
      "capacityBytes": 106808979456,
      "usedBytes": 0,
      "inodesFree": 52040039,
      "inodes": 52157888,
      "inodesUsed": 5
     },
     "logs": {
      "time": "2021-12-23T23:32:21Z",
      "availableBytes": 81190658048,
      "capacityBytes": 106808979456,
      "usedBytes": 24576,
      "inodesFree": 52040039,
      "inodes": 52157888,
      "inodesUsed": 117849
     }
    }
   ],
   "cpu": {
    "time": "2021-12-23T23:32:29Z",
    "usageNanoCores": 5108670,
    "usageCoreNanoSeconds": 28643820045
   },
   "memory": {
    "time": "2021-12-23T23:32:29Z",
    "usageBytes": 179077120,
    "workingSetBytes": 105521152,
    "rssBytes": 83087360,
    "pageFaults": 0,
    "majorPageFaults": 0
   },
   "network": {
    "time": "2021-12-23T23:32:26Z",
    "name": "",
    "interfaces": [
     {
      "name": "vxlan_sys_4789",
      "rxBytes": 4921523,
      "rxErrors": 0,
      "txBytes": 8340250,
      "txErrors": 0
     },
     {
      "name": "br0",
      "rxBytes": 0,
      "rxErrors": 0,
      "txBytes": 0,
      "txErrors": 0
     },
     {
      "name": "ovs-system",
      "rxBytes": 0,
      "rxErrors": 0,
      "txBytes": 0,
      "txErrors": 0
     },
     {
      "name": "tun0",
      "rxBytes": 10206797,
      "rxErrors": 0,
      "txBytes": 40839281,
      "txErrors": 0
     },
     {
      "name": "ens3",
      "rxBytes": 846595940,
      "rxErrors": 0,
      "txBytes": 778805169,
      "txErrors": 0
     }
    ]
   },
   "volume": [
    {
     "time": "2021-12-23T23:20:44Z",
     "availableBytes": 81036546048,
     "capacityBytes": 106808979456,
     "usedBytes": 4096,
     "inodesFree": 52040038,
     "inodes": 52157888,
     "inodesUsed": 5,
     "name": "config"
    },
    {
     "time": "2021-12-23T23:20:44Z",
     "availableBytes": 81036546048,
     "capacityBytes": 106808979456,
     "usedBytes": 0,
     "inodesFree": 52040038,
     "inodes": 52157888,
     "inodesUsed": 3,
     "name": "env-overrides"
    },
    {
     "time": "2021-12-23T23:20:44Z",
     "availableBytes": 8207945728,
     "capacityBytes": 8207974400,
     "usedBytes": 28672,
     "inodesFree": 2003889,
     "inodes": 2003900,
     "inodesUsed": 11,
     "name": "sdn-token-w4tsz"
    },
    {
     "time": "2021-12-23T23:20:44Z",
     "availableBytes": 8207966208,
     "capacityBytes": 8207974400,
     "usedBytes": 8192,
     "inodesFree": 2003893,
     "inodes": 2003900,
     "inodesUsed": 7,
     "name": "sdn-metrics-certs"
    }
   ],
   "ephemeral-storage": {
    "time": "2021-12-23T23:32:33Z",
    "availableBytes": 81190658048,
    "capacityBytes": 106808979456,
    "usedBytes": 49987584,
    "inodesFree": 52040039,
    "inodes": 52157888,
    "inodesUsed": 30
   },
   "process_stats": {
    "process_count": 0
   }
  }]}

data = json.dumps(jsonStr)

jsonData = json.loads(data)

for pod in jsonData["pods"]:
    podRef=pod["podRef"]
    namespace=podRef["namespace"]
    name=podRef["name"]
    print("%s%s"%(name,namespace))

    if pod["volume"]:
        for volume in pod["volume"]:
            name=volume["name"]
            print(name)
