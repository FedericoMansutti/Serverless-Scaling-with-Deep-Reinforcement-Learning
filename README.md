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


6. **Build the Docker Image (i.e. RL Agent)**: navigate to the directory containing the `DockerFile` (e.g. if using this repo structure, the `Docker/RLAgent` directory) and run the following command:  

   ```shell
   eval $(minikube docker-env)            # Switch Docker CLI to use Minikube's daemon
   docker build -f src/production_agents/DQN/Dockerfile -t production_agent:latest .
   eval $(minikube docker-env -u)         # Exit from minikube daemon
   ```

   Note: This process builds the Docker image directly within Minikube’s Docker daemon, which allows the image to be used immediately without needing to push or load it separately; indeed, due to the large size of the image, this approach is much faster and more efficient than building it locally and then loading it into Minikube 

   <br>
   The agent will use the following evaluation metrics: <br><br>

   | Metric                        | Formula                                                                                     | Description                                                                                                     | Interpretation                                                                                                                                   |
   |------------------------------|---------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
   | `n_instances`                | —                                                                                           | Number of active instances of a specific computational resource                                                           | /                                                                                                             |
   | `pressure` (p)               | $\Large\frac{R}{\bar{R}}$                                                                      | Indicates how close the system is to violating its response time constraints <br> $R$ = observed response time, $\bar{R}$ = response time threshold.             | - $p < 1$: Within accettable ranges  <br> - $p \geq 1$: Risk of violation                                                                                       |
   | `queue_length_dominant` (qld) | $\Large \frac{R_d - D_d}{D_d}$                                                                | Measures queue buildup on the dominant component (the one with the highest pressure) <br> $R_d$ = response time, $D_d$ = demand (service time).            | Higher `qld` implies longer waiting times and potential bottlenecks.                                                                            |
   | `utilization` (u)            | $\Large \frac{\sum_{i \in \mathcal{I}} \lambda_i \cdot D_i}{n}$ <br><br> s.c.: $\Large \frac{\lambda \cdot D}{n}$ | Represents the fraction of time each instance is busy processing requests <br> $\lambda_i$ = arrival rate, $D_i$ = demand, $n$ = instances.         | - $u < 1$: Instances are not fully utilized <br> - $u = 1$: Fully utilized <br> - $u > 1$: Overload Condition                                                              |
   | `workload`                   | —                                                                                           | Number of requests received per unit of time (e.g. requests per second).                                        | As workload increases, more resources are required to maintain acceptable performance. 

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
   kubectl apply -f Kubernetes/MatrixMultiplication/ingress.yaml
   ```

   ```
   # RL Agent Manifest

   kubectl apply -f Kubernetes/RLAgent/agentDeployment.yaml
   kubectl apply -f Kubernetes/RLAgent/agentService.yaml
   ```

   ```
   # Scheduler Manifest

   kubectl apply -f Kubernetes/Scheduler/schedulerService.yaml
   kubectl apply -f Kubernetes/Scheduler/CronJob.yaml
   ```

   Important: 
   - Ensure you execute these commands in the given sequence to maintain proper resource dependencies
   - If you want to observe the effects of the scheduler in a clearer way, apply its manifest after some requests sent during the following steps
   - The scheduler can work if and only if the container associated to the RL Agent is actually running!
<br><br>


3. **Enable the Ingress Controller**

   ```shell
   minikube addons enable ingress
   
   # You can also check the ingress status (ingress-nginx-controller should be in Running)
   kubectl get pods -n ingress-nginx
   ```

4. **Configure the NGINX Ingress to Allow Custom Headers**: by default, the NGINX Ingress controller blocks custom snippets 

   ```shell
   # Edit the ConfigMap (This opens the configuration in a text editor, typically VIM)
   kubectl patch configmap ingress-nginx-controller -n ingress-nginx --type merge -p '{"data":{"allow-snippet-annotations":"true"}}'
   ```

5. **Start Minikube Tunnel**

   ```shell
   minikube tunnel 
   ```

6. **Send the Request**: perform a request to the server to check whether it is working or not

   ```shell
   curl -X POST http://127.0.0.1/multiply -H "Content-Type: application/json" -d '{"matrix_a": [[1,2],[3,4]], "matrix_b": [[5,6],[7,8]]}'
   ```
<br>

7. **Access the Results**

   ```
   kubectl exec -it POD_NAME -- /bin/sh -c "ls /app/results"
   kubectl exec -it POD_NAME -- /bin/sh -c "cat /app/results/matrix_multiply_results_TIMESTAMP.json"
   kubectl exec -it POD_NAME -- /bin/sh -c "cat /app/results/podStatus.json"
   ```

   Important: 
   - The third command can be used only after the first run of the scheduler, otherwise no shuch a file would exist
<br></br>

## Testing the Scaler with JMeter

1. **Configure the JMeter Test Plan**: open the notebook `WorkloadAndConfigGenerator.ipynb`. This will allow you to generate the desired workload (currently, only a sinusoidal pattern is supported) and, once the workload is generated, configure the following parameters:

   ```text
   # Workload
   It defines the path to the generated workload file

   # Concurrency Values
   TargetLevel = Number of concurrent users. Set this high enough to support the throughput defined in the Throughput Shaping Timer (there is a mathematical formula to compute it but in general we can use this naive approach)
   RampUp = Time (in minutes) to gradually add users until the TargetLevel is reached
   Steps = Number of incremental steps to reach the TargetLevel
   Hold = Duration (in minutes) to maintain the peak user load. This should match the observation time

   # HTTP Request
   HTTPSampler.domain = Domain to send the requests to
   HTTPSampler.port = Port to use (must remain set to 80 for tests to work)
   HTTPSampler.path = Endpoint path
   HTTPSampler.method = HTTP method (e.g., POST, GET, etc...)
   jsonBody = Payload for the POST request

   # CSV File Upload (about the Matrices to send in the requests)
   delimiter = Delimiter used used in the Matrices.csv file
   fileEncoding = Encoding of the CSV file
   filename = Path to the Matrices.csv file
   variableNames = Column headers in the CSV file
   shareMode = Scope of file sharing among threads
   ignoreFirstLine = it specify whether we have to consider the first row of the Matrices.csv file or not (spoiler: we have to do it)
   recycle = Set to true to reuse rows when requests exceed the file length
   stopThread = Set to false to prevent threads from stopping if the file ends
   ```

    Important Plugins Required:

     - JMeter Plugin Manager
     - Custom Thread Group Plugin
     - Throughput Shaping Timer Plugin
                  

    Manual Edits: If you modify the configuration manually, preserve proper indentation to avoid test failures.

2. **Launch JMeter and Load the Test Plan**

   ```shell
   sh JMeterAppFolder/bin/jmeter.sh
   ```

   Important: Ensure the port number remains set to 80, changing it will cause the requests to fail.
   <br></br>

3. **Run the Test** <br><br>

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