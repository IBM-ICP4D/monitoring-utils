**Setup Cluster role binding to monitor volumes**

To allow for cluster role access to the zen-editor-sa account, please consider running the following steps:

1. Create a cluster role that allows accounts to run the node summary API. This can be done using the following snippet.


```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-role-one
rules:
- apiGroups:
  - ""
  resources:
  - secrets
  - nodes
  - nodes/proxy
  verbs:
  - get
  - watch
  - list
  ````

2. Create a cluster role binding with the zen-editor-sa account using the following yaml.

````yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: volumes-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-role-one
subjects:
- kind: ServiceAccount
  name: zen-editor-sa
  namespace: zen1004
  ````

  Introducing the two yamls above would ensure that the service account is now able to run the node proxy APIs and fetch summary from all the node kubelets.