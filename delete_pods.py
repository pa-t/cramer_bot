from time import sleep
from tkinter import E
import kubernetes as k8s
k8s.config.load_kube_config()
v1 = k8s.client.CoreV1Api()
while True:
  try:
    kubeflow_pods = v1.list_namespaced_pod(namespace='kubeflow')
    names = [
      pod.metadata.name 
      for pod in kubeflow_pods.items 
      if pod.metadata.name.startswith('tweet-pipeline')
      and pod.status.phase in ['Running', 'Succeeded', 'ContainerCreating']
    ]
    for name in names:
      v1.delete_namespaced_pod(namespace='kubeflow', name=name)
      print(f'deleted pod: {name}')
  except Exception as e:
    print(f'error deleting pods: {e}')
  sleep(0.1)