# Matrix Multiplication Service + Scheduler with Kubernetes

This repository contains a Flask-based matrix multiplication service that can be deployed as a Docker container and scaled with Kubernetes; a scheduler script will be executed every minute to scale the number of replicas according to the incoming requests.

## Overview

Test

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

Work in progress, not written for the moment

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

1. **Build the Docker Image (i.e. Matrix Multiplication)**: navigate to the `Docker/MatrixMultiplication/` directory

   ```
   docker build -t matrix-mult-app .
   ```


2. **Result Directory**

   ```
   mkdir -p results
   ```


3. **(Optional) Start the Docker Container**: 
   ```
   docker run -p 5050:5050 -v pathToResults:/app/results matrix-mult-app
   ```


4. **(Optional) Use the Docker Container**: send an HTTP POST request to `http://localhost:5050/multiply`

   ```
   curl -X POST http://localhost:5050/multiply -H "Content-Type: application/json" -d '{"matrix_a": [[1,2],[3,4]], "matrix_b": [[5,6],[7,8]], "startTime": '$(date +%s)'}'
   ```


5. **Build the Docker Image (i.e. Scheduler)**: navigate to the `Docker/Scheduler/` directory

   ```
   docker build -t scheduler-app .
   ```


## Deploying with Kubernetes

1. **Load the images on Minikube**: 
   ```
   minikube image load matrix-mult-app
   minikube image load scheduler-app
   ```
   
2. **Initialize the Kubernetes Cluster** 

   ```
   # Matrix Multiplication Manifest

   kubectl apply -f Kubernetes/MatrixMultiplication/pvc.yaml
   kubectl apply -f Kubernetes/MatrixMultiplication/deployment.yaml
   kubectl apply -f Kubernetes/MatrixMultiplication/service.yaml
   ```

   ```
   # Scheduler Manifest

   kubectl apply -f Kubernetes/Scheduler/service.yaml
   kubectl apply -f Kubernetes/Scheduler/CronJob.yaml
   ```

   Important: 
   - If you want to observe the effects of the scheduler in a clearer way, apply its manifest after some requests sent during the steps 3/4
               <br></br>
3. **Get the URL**: returns a URL in the format `http://<minikube-ip>:<port>`

   ```
   minikube service matrix-multiply-service --url
   ```
<br></br>

4. **Send the Request**

   ```
   curl -X POST http://SERVICE_URL/multiply -H "Content-Type: application/json" -d '{"matrix_a": [[1,2],[3,4]], "matrix_b": [[5,6],[7,8]], "startTime": '$(date +%s)'}'
   ```
<br></br>

5. **Access the Results**

   ```
   kubectl exec -it POD_NAME -- /bin/sh -c "ls /app/results"
   kubectl exec -it POD_NAME -- /bin/sh -c "cat /app/results/matrix_multiply_results_TIMESTAMP.json"
   kubectl exec -it POD_NAME -- /bin/sh -c "cat /app/results/podStatus.json"
   ```

   Important: 
   - The third command can be used only after the first run of the scheduler, otherwise no shuch a file would exist
<br></br>
