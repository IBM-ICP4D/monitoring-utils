import os 
import requests 
import json from kubernetes 
import client, config, watch 
def main(): 
# setup the namespace 
	ns = os.environ.get('ICPD_CONTROLPLANE_NAMESPACE') 
if ns is None: 
	ns = "" 
monitor_type = "sample-monitor" 
event_type = "check-pvc-status" 
# configure client 
config.load_incluster_config() 
api = client.CoreV1Api() 

# configure post request and  set secret headers 
url = 'https://zen-watchdog-svc:4444/zen-watchdog/v1/monitoring/events' 
with open('/var/run/sharedsecrets/token', 'r') as file: 
	secret_header = file.read().replace('\n', '') 
headers = {'Content-type': 'application/json', 'secret': secret_header} 

# Print PVC list, set status as critical for unbound or failed pvc 
pvcs = api.list_namespaced_persistent_volume_claim(namespace=ns, watch=False) 
events = [] 
for pvc in pvcs.items: 
	severity = "info"  
	print(pvc.status.phase) 
	if pvc.status.phase != 'Bound': 
		severity = "critical" 
	#The metadata field needs to be in <key1:value1,key2:vaue2> format to be easily absorbed for prometheus consumption.
	#The keys(key1,key2) is also referenced as part of the property "long_description" in alert monitor extension to be available for viewing in the UI. Please refer to the 
	metadata = "Avaialble=10,Unavailable=5"  
	data = {"monitor_type":monitor_type, "event_type":event_type, "severity":severity, "metadata":metadata, "reference":pvc.metadata.name} 
	events.append(data) 
json_string = json.dumps(events) 
# post call to zen-watchdog to record events 
r = requests.post(url, headers=headers, data=json_string, verify=False) 
print(r.status_code) 
if __name__ == '__main__': 
main()