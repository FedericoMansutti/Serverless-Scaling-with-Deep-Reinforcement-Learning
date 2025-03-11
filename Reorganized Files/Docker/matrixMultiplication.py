import numpy as np
import time
import datetime
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Get the pod's name and, in the case in which it is not present, it returns a 
# default value (e.g. when we run the bare docker image out of kubernetes)
podName = os.getenv("pod_name", "[ERROR] Unknown Pod")

def matrix_multiply(A, B):
    
    # Multiply two matrices A and B using NumPy
    
    return np.matmul(A, B)

@app.route('/multiply', methods = ['POST'])
def multiply_matrices():
    
    # As soon as the request arrives, we register the timestamp
    timestamp = datetime.datetime.now().strftime("%Y.%m.%d_%H:%M:%S")

    # Get JSON data from request
    data = request.get_json()
    
    # Extract matrices from request
    try:

        A = np.array(data['matrix_a'], dtype = float)
        B = np.array(data['matrix_b'], dtype = float)
        
        # Validate matrices can be multiplied
        if A.shape[1] != B.shape[0]:

            return jsonify({'error': f"Matrix dimensions don't match for multiplication. A: {A.shape}, B: {B.shape}"}), 400
        
        # Create results directory if it doesn't exist
        os.makedirs("results", exist_ok = True)
        
        # Measure execution time
        start_time = time.time()
        
        # Perform matrix multiplication
        C = matrix_multiply(A, B)
        
        # Calculate execution time
        execution_time = time.time() - start_time

        # Generate a unique filename based on timestamp
        filename = f"{podName}_{timestamp}.txt"
        filepath = os.path.join("results", filename)
        
        # Write results to file
        with open(filepath, "w") as f:
            
            # For our purposes, we are only interested in the execution time

            # f.write(f"Matrix multiplication of {A.shape}x{B.shape} matrices completed.\n")
            
            f.write(f"Execution time: {execution_time:.4f} seconds\n\n")
            
            # Write a sample of the result matrix (top-left 5x5)
            # f.write("Sample of result matrix (top-left 5x5):\n")
            # for i in range(C.shape[0]):
            #    row_str = " ".join([f"{val:.6f}" for val in C[i, :]])
            #    f.write(row_str + "\n")
        
        # Return results
        return jsonify({
            'message': f"Matrix multiplication completed. Results saved to {filepath}",
            'execution_time': execution_time,
            'result_shape': C.shape,
            'result_sample': C[:5, :5].tolist() if min(C.shape) >= 5 else C.tolist()
        })
    
    except KeyError:

        return jsonify({'error': 'Missing matrix_a or matrix_b in request'}), 400
    
    except Exception as e:
        
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":

    app.run(host = '0.0.0.0', port = 5050)
