# Matrix Multiplication Service + Scheduler with Kubernetes

This repository contains a Flask-based matrix multiplication service that can be deployed as a Docker container and scaled with Kubernetes; a scheduler script will be executed every minute to scale the number of replicas according to the incoming requests.

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

## Test the scaler with JMeter

1. **Start JMeter and open the `JMeter/jmeter.jmx` file**

   ```
   sh JMeterAppFolder/bin/jmeter.sh
   ```

   Important: Change the port number in the file, the port used by Minikube will change at every run!
   <br></br>

2. **Run the test**: try to run it after the first check to observe how the replicas number changes

<div align="center">
  
  <div style="display: flex; justify-content: center; gap: 10px;">
    <img src="Images/Check%201.png" alt = "First Check" width = "30%">
    <img src="Images/Check%202.png" alt = "Second Check" width = "30%">
    <img src="Images/Check%203.png" alt = "Third Check" width = "30%">
  </div>

  
  <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
    <img src="Images/Check%204.png" alt = "Fourth Check" width = "30%">
    <img src="Images/Check%205.png" alt = "Fifth Check" width = "30%">
    <img src="Images/Check%206.png" alt = "Sixth Check" width = "30%">
  </div>
</div>


## Monitoring the system

Before proceeding, install the required libraries:
   
   ```
   brew install kubernetes-helm
   ```

We will use:
   -  NodeExporter: collects system-level metrics, such as CPU, memory, disk I/O, network usage, etc., from the underlying host 
   - cAdvisor: it automatically collects container-level metrics so as to provide detailed insights into the resource usage for each pod
   - Blackbox Exporter: it analyzes endpoints (e.g. the service’s HTTP endpoint) to measures metric such as response time and availability

1. **Add helm repos and update**

   ```
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo add grafana https://grafana.github.io/helm-charts
   helm repo update
   ```

2. **Deploy the kube-prometheus-stack**: through this installation, we are automatically setting up NodeExporter, cAdvisor and a fully functional Grafana instance with pre-built dashboards for kubernetes metrics.

   ```
   helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
   ```

   Important: The Kubernetes Cluster must be active in this phase, otherwise the process would not work!

3. **Deploy the Blackbox Exporter**

   ```
   helm install blackbox-exporter prometheus-community/prometheus-blackbox-exporter --namespace monitoring
   ```

4. **Create a Prob Job**

   ```
   kubectl apply -f Kubernetes/Prometheus/blackbox-probe.yaml
   ```

   Important: This would not work with our actual app since it performs a get request to the endpoint to observe the performance.
   But it should be useful for the real application we will use at the end!

5. **Expose the Prometheus and Grafana Services**

   ```
   # Prometheus
   kubectl port-forward svc/monitoring-kube-prometheus-prometheus -n monitoring 9090

   # Grafana
   # Username: admin
   # Password: kubectl get secret monitoring-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

   kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
   ```
6. **Access the Services**

   ```
   Prometheus: http://localhost:9090

   Grafana: http://localhost:3000
   ```

7. **Add the Prometheus Service on Grafana**:

   Connections -> Data sources -> Add new data source -> Time series databases -> Connection: http://monitoring-kube-prometheus-prometheus.monitoring:9090 -> Save & Test
   

8. **Import the custom dashboard on Grafana**: Dashboards -> New -> Import -> `Grafana/dashboard.json`

   <p align = "center">
   <img src = "Images/Grafana Performance.png" alt = "Grafaba" width = "80%">
   </p>