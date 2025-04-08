#!/bin/bash

# Delete all deployments
kubectl delete deployments --all

# Delete all services
kubectl delete services --all --namespace=default

# Delete all pods
kubectl delete pods --all

# Delete all configmaps
kubectl delete configmaps --all

# Delete all secrets
kubectl delete secrets --all

# Delete all jobs
kubectl delete jobs --all

# Delete all persistent volume claims
kubectl delete pvc --all

# Delete CronJobs
kubectl delete cronjobs --all

# Delete ServiceAccounts, Roles and RoleBindings
kubectl delete serviceaccounts autoscaler-sa
kubectl delete role deployment-modifier
kubectl delete rolebinding deployment-modifier-binding