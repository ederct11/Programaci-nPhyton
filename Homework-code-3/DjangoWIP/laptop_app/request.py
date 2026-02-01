import requests

url = "http://localhost:8000/dynamic-pages/materials/"

payload = {}
headers = {
  'Accept': 'application/json'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
