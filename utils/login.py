import requests
import json


def login(url, username, password):
    url = f"{url}/auth/login"
    payload = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

    return response.cookies
