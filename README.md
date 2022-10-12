# Kubeflow Testing

# Setup
*PS:* Short alias for kubectl `alias k=kubectl`


## Install kubeflow python sdk:
```
pip3 install https://storage.googleapis.com/ml-pipeline/release/0.1.29/kfp.tar.gz --upgrade --user
```

## Install kind
```
brew install kind
```

### Create cluster
```
kind create cluster --config=yamls/kind.yaml
```

### Set up registry
```
docker run -d --restart=always -p "127.0.0.1:5001:5000" --name "kind-registry" registry:2
docker network connect "kind" "kind-registry"
```

## Install kubeflow
```
export PIPELINE_VERSION=1.8.4
k apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
k wait --for condition=established --timeout=60s crd/applications.app.k8s.io
k apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic-pns?ref=$PIPELINE_VERSION"
```

This will take some time, can check progress with `k get pods -n kubeflow`

### Make log directory
```
mkdir logs
```

### Set up port forwarding
```
k port-forward -n kubeflow svc/ml-pipeline-ui 3000:80 >> ./logs/ml-pipeline-ui.logs 2>&1 & \
  k port-forward -n kubeflow svc/minio-service 9000:9000 >> ./logs/minio-service.logs 2>&1 &
```

Can now go to [dashboard](http://localhost:3000)




# Run Tweet Pipeline
Install components
```
python setup.py install --user
```

Run pipeline
```
python3 code/tweet_pipeline.py
```


If you make changes to components:
```
pip3 uninstall components && python setup.py install --user
```


## Build base docker image
```
docker build . -t 'component_reqs'
```

Then push to local repository
```
docker tag <ID> 127.0.0.1:5001/component_reqs:latest
docker push 127.0.0.1:5001/component_reqs:latest
```



# Clean up cluster
```
kubectl delete pods --field-selector status.phase=Succeeded --all-namespaces
kubectl delete pods --field-selector status.phase=Failed --all-namespaces
kubectl delete pods --field-selector status.phase=Error --all-namespaces
```


# Uninstall kubeflow
Delete everything
```
export PIPELINE_VERSION=1.8.4
k delete -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic-pns?ref=$PIPELINE_VERSION"
k delete -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
```
and
```
k config delete-cluster kind-ness
```

Switch back to context
```
k config use-context docker-desktop
```

Unistall kind
```
brew uninstall kind
```