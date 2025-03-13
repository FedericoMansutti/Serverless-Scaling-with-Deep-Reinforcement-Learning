# Matrix Multiplication Service with Kubernetes

This repository contains a Flask-based matrix multiplication service that can be deployed as a Docker container and scaled with Kubernetes.

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Getting Started](#getting-started)
4. [Running with Docker](#running-with-docker)
5. [Deploying with Kubernetes](#deploying-with-kubernetes)
6. [Using the API](#using-the-api)
7. [Accessing Results](#accessing-results)
8. [Troubleshooting](#troubleshooting)

## Overview

This project provides a RESTful web service for multiplying matrices. When you send two matrices in JSON format, the service:
- **Multiplies them** using **NumPy**
- **Saves the results** to a file
- **Returns calculation details**

**Technologies Used:**
- **Flask**: Lightweight web framework for Python.
- **NumPy**: Fast matrix operations.
- **Docker**: Containerization for consistent environments.
- **Kubernetes**: Orchestration and scaling of containerized applications.

---

## Project Structure

```plaintext
matrix-multiplication-service/
├── matrix_multiply.py         # Flask application for matrix multiplication
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker build instructions
├── deployment/                # Kubernetes configuration files
│   ├── matrix-app-deployment.yaml  # Deployment configuration
│   ├── matrix-app-service.yaml     # Service configuration
│   └── matrix-app-pvc.yaml         # Persistent Volume Claim
└── README.md                  # This file
```
## Getting Started

### Prerequisites

- Python 3.8+
- Docker
- Kubernetes cluster (Minikube for local testing)

### Installation

1. Clone this repository:
bash
git clone https://github.com/FedericoMansutti/Serverless-Scaling-with-Deep-Reinforcement-Learning.git
cd matrix-multiplication-service

2. Install Python dependencies:
bash
pip install -r requirements.txt

## Running with Docker

### Building the Docker Image
```sh
docker build -t matrix-mult-app .
```

### Running the Docker Container
Create a directory for the results:
```sh
mkdir -p results
```

Run the container with volume mounting:
```sh
docker run -p 5000:5000 -v $(pwd)/results:/app/results matrix-mult-app
```

### Testing the Docker Container
```sh
curl -X POST http://localhost:5000/multiply \
-H "Content-Type: application/json" \
-d '{"matrix_a": [[1,2],[3,4]], "matrix_b": [[5,6],[7,8]]}'
```

## Deploying with Kubernetes

### Step 1: Load the Docker Image into Minikube
For Minikube (remember to start minikube with minikube start):
```sh
minikube image load matrix-mult-app
```

### Step 2: Create the Kubernetes Resources
```sh
kubectl apply -f deployment/matrix-app-pvc.yaml

kubectl apply -f deployment/matrix-app-deployment.yaml

kubectl apply -f deployment/matrix-app-service.yaml
```

### Step 3: Verify the Deployment
```sh
kubectl get pods

kubectl get service matrix-multiply-service
```

### Getting the Service URL (Minikube)
```sh
minikube service matrix-multiply-service --url
```
Tip: since this cannot be started in detatched mode, you can use tmux to start it
### Sending a Matrix Multiplication Request
```sh
curl -X POST http://SERVICE_URL/multiply \
-H "Content-Type: application/json" \
-d '{"matrix_a": [[1,2],[3,4]], "matrix_b": [[5,6],[7,8]]}'
```

### List files in the results directory
```sh
kubectl exec -it POD_NAME -- /bin/sh -c "ls -la /app/results"
```

### View a specific file
```sh
kubectl exec -it POD_NAME -- /bin/sh -c "cat /app/results/matrix_multiply_results_TIMESTAMP.txt"

