allPVCs =  ['data-dsx-influxdb-0', 'datadir-zen-metastoredb-0', 'datadir-zen-metastoredb-1', 'datadir-zen-metastoredb-2', 'user-home-pvc']
volumes =  ['config']
set1 = set(allPVCs)
set2 = set(volumes)
missing = list(sorted(set1 - set2))
print(missing)