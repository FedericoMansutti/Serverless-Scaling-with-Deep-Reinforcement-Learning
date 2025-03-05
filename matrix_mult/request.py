import requests
import json

url = "http://127.0.0.1:37881/multiply"
payload = {
    "matrix_a": [[1,2],[3,4]],
    "matrix_b": [[5,6],[7,8]]
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json.dumps(payload), headers=headers)
print(response.json())