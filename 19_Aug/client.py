import requests

url = "http://127.0.0.1:5000/run"

data = {
    "a": 1,
    "b": 1
}

response = requests.post(url, json=data)

print(response.json())