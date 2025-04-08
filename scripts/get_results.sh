#download jmeter results ---------can probably be improved
# Create a temporary pod with the PVC mounted
kubectl run copy-pod --image=busybox --restart=Never \
  --overrides='{"spec": {"volumes": [{"name": "results-volume", "persistentVolumeClaim": {"claimName": "jmeter-results-pvc"}}], "containers": [{"name": "copy-pod", "image": "busybox", "command": ["sleep", "3600"], "volumeMounts": [{"name": "results-volume", "mountPath": "/results"}]}]}}'

# Wait for the pod to be ready
kubectl wait --for=condition=Ready pod/copy-pod

# Copy files from the pod to your local machine
kubectl cp copy-pod:/results ./jmeter-results

# Delete the temporary pod when done
kubectl delete pod copy-pod