#!/bin/bash

# Print colored status messages
print_status() {
  echo -e "\e[1;34m>> $1\e[0m"
}

print_success() {
  echo -e "\e[1;32m✓ $1\e[0m"
}

print_error() {
  echo -e "\e[1;31m✗ $1\e[0m"
  exit 1
}

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
  print_error "Minikube is not installed. Please install it first."
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
  print_error "Docker is not installed. Please install it first."
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
  print_error "kubectl is not installed. Please install it first."
fi

# 1. Start minikube if it's not already running
print_status "Starting Minikube..."
if ! minikube status | grep -q "Running"; then
  minikube start
  if [ $? -ne 0 ]; then
    print_error "Failed to start Minikube."
  fi
  print_success "Minikube started successfully."
else
  print_success "Minikube is already running."
fi

# 2. Build Docker images
print_status "Building Docker images..."

# Building Matrix Multiplication image
print_status "Building Matrix Multiplication image..."
cd Cluster/MatrixMultiplication
docker build -t matrix-mult-app .
if [ $? -ne 0 ]; then
  print_error "Failed to build matrix-mult-app image."
fi
print_success "Matrix Multiplication image built successfully."

# Building Scheduler image
print_status "Building Scheduler image..."
cd ../Scheduler
docker build -t scheduler-app .
if [ $? -ne 0 ]; then
  print_error "Failed to build scheduler-app image."
fi
print_success "Scheduler image built successfully."

# Building JMeter image
print_status "Building JMeter image..."
cd ../Jmeter
docker build -t jmeter:latest .
if [ $? -ne 0 ]; then
  print_error "Failed to build JMeter image."
fi
print_success "JMeter image built successfully."

# Go back to root directory
cd ../..

# 3. Load images into Minikube
print_status "Loading images into Minikube..."
minikube image load matrix-mult-app
minikube image load scheduler-app
minikube image load jmeter:latest
print_success "Images loaded into Minikube successfully."

# 4. Apply Kubernetes manifests
print_status "Applying Kubernetes manifests..."

# Matrix Multiplication manifests
print_status "Applying Matrix Multiplication manifests..."
kubectl apply -f Cluster/MatrixMultiplication/manifests/pvc.yaml
kubectl apply -f Cluster/MatrixMultiplication/manifests/deployment.yaml
kubectl apply -f Cluster/MatrixMultiplication/manifests/service.yaml
print_success "Matrix Multiplication manifests applied."

# Scheduler manifests
print_status "Applying Scheduler manifests..."
kubectl apply -f Cluster/Scheduler/manifests/service.yaml
kubectl apply -f Cluster/Scheduler/manifests/CronJob.yaml
print_success "Scheduler manifests applied."

# JMeter manifests
print_status "Applying JMeter manifests..."
kubectl apply -f Cluster/Jmeter/manifests/jmeter-pvc.yaml
kubectl apply -f Cluster/Jmeter/manifests/jmeter-configmap.yaml
kubectl apply -f Cluster/Jmeter/manifests/jmeter-job.yaml
print_success "JMeter manifests applied."

