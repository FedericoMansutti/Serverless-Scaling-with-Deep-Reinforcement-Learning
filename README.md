# Kubernetes Matrix Multiplication Load Testing Architecture

This project demonstrates a complete Kubernetes infrastructure for testing, scaling, and monitoring a matrix multiplication service under load. The system consists of three main components that work together:

1. **Matrix Multiplication Service**: A scalable Python service that performs matrix multiplication
2. **Autoscaler**: A scheduler that monitors performance and scales the service based on response times
3. **JMeter Load Tester**: A performance testing tool that generates load against the service

### Components and Their Interactions

#### Matrix Multiplication Service
- Python Flask API that performs matrix multiplication using NumPy
- Exposes a `/multiply` endpoint that accepts JSON payloads with two matrices
- Records performance metrics (service time and response time) for each request
- Scales automatically based on the scheduler's decisions
- Stores results in a shared persistent volume

#### Autoscaler (Scheduler)
- Runs as a CronJob every minute
- Analyzes response time data from the shared volume
- Scales the Matrix Multiplication service based on performance:
  - \> 200ms response time: Scale to 5 replicas
  - \< 100ms response time: Scale to 2 replicas
  - Otherwise: 1 replica
- Tracks pod lifecycle events (started/shutdown) in a history file
- Uses Kubernetes API (via a service account with appropriate RBAC permissions)

#### JMeter Load Tester
- Executes performance tests against the Matrix Multiplication service
- Configured to simulate concurrent users with a defined test plan
- Results are stored in a separate persistent volume
- Runs as a Kubernetes Job

## Directory Structure

```
Cluster/
├── MatrixMultiplication/  # Matrix multiplication service
│   ├── Dockerfile
│   ├── matrixMultiplication.py
│   ├── requirements.txt
│   └── manifests/
│       ├── deployment.yaml
│       ├── pvc.yaml
│       └── service.yaml
├── Scheduler/             # Autoscaling component
│   ├── Dockerfile
│   ├── scheduler.py
│   ├── requirements.txt
│   └── manifests/
│       ├── CronJob.yaml
│       └── service.yaml
└── Jmeter/                # Load testing component
    ├── Dockerfile
    ├── jmeter.properties
    ├── scripts/
    │   └── jmeter.jmx
    └── manifests/
        ├── jmeter-configmap.yaml
        ├── jmeter-job.yaml
        └── jmeter-pvc.yaml
scripts/
├── setup.sh               # Setup and deployment script
├── clean.sh               # Cleanup script
└── get_results.sh         # Script to retrieve test results
```

## Data Flow

1. JMeter sends matrix multiplication requests to the service
2. Matrix service processes requests and stores performance data in PVC
3. Scheduler analyzes the performance data periodically
4. Scheduler adjusts the number of matrix service replicas based on load
5. The cycle continues as JMeter generates more load

## Getting Started

### Prerequisites

- Docker
- Minikube (or any Kubernetes cluster)
- kubectl

### Setup Instructions

1. Clone this repository:
   ```bash
   git clone https://github.com/FedericoMansutti/Serverless-Scaling-with-Deep-Reinforcement-Learning.git
   cd Serverless-Scaling-with-Deep-Reinforcement-Learning
   ```

2. Make the scripts executable:
   ```bash
   chmod +x scripts/*.sh
   ```

3. Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```
   
   This script will:
   - Start Minikube if not already running
   - Build all Docker images
   - Load the images into Minikube
   - Apply all Kubernetes manifests

### Retrieving Results

To retrieve the JMeter test results:

```bash
./scripts/get_results.sh
```

This will copy the results from the JMeter PVC to a local directory named `jmeter-results`.

### Cleanup

To clean up all resources:

```bash
./scripts/clean.sh
```

## How Load Testing Works

1. The JMeter test plan (`jmeter.jmx`) defines:
   - 100 concurrent threads (users)
   - Each thread performs 100 iterations
   - Each request contains two matrices to multiply

2. The request format is:
   ```json
   {
     "matrix_a": [[1,2],[3,4]],
     "matrix_b": [[5,6],[7,8]],
     "startTime": ${__time()}
   }
   ```

3. The Matrix Multiplication service processes these requests and stores timing information.

4. The Scheduler analyzes these results and scales the service accordingly.

## How Autoscaling Works

1. The Scheduler runs every minute (defined in the CronJob spec)
2. It calculates the average response time from the result files
3. Based on the average response time, it decides how many replicas are needed:
   - If response time > 200ms: Scale to 5 replicas
   - If response time < 100ms: Scale to 2 replicas
   - Otherwise: 1 replica
4. It tracks which pods are active, started, or shut down in each check
5. All processed files are moved to an "AnalyzedPods" directory

## Persistent Storage

The system uses two Persistent Volume Claims (PVCs):

1. `matrix-results-pvc`: Shared between the Matrix service and Scheduler
   - Matrix service writes performance data
   - Scheduler reads this data for scaling decisions

2. `jmeter-results-pvc`: Used by JMeter to store test results
   - Contains detailed metrics about the load test
   - Can be extracted using the `get_results.sh` script

## Troubleshooting
### Viewing Logs

To view logs from any component:

```bash
# Matrix service logs
kubectl logs -l app=matrix-multiply

# Scheduler logs
kubectl logs -l job-name=autoscaler

# JMeter logs
kubectl logs -l job-name=jmeter-test
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
