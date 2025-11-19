import requests
import json

try:
    response = requests.get("http://localhost:8000/properties")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print("Response Text:", response.text)
except Exception as e:
    print(f"Error: {e}")
