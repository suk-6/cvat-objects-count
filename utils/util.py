import requests
from utils.login import login


class api:
    def __init__(self, params):
        self.protocol = params["protocol"]
        self.host = params["host"]
        self.port = params["port"]
        self.username = params["username"]
        self.password = params["password"]
        self.org = params["org"]

        self.url = f"{self.protocol}://{self.host}:{self.port}/api"

        self.cookie = login(self.url, self.username, self.password)

    def get(self, url):
        return requests.request("GET", url, cookies=self.cookie)

    def getTasks(self):
        url = f"{self.url}/tasks?org={self.org}&page_size=1000"
        response = self.get(url)
        return response.json()

    def getJobs(self):
        url = f"{self.url}/jobs?org={self.org}&page_size=1000"
        response = self.get(url)
        return response.json()

    def getLabels(self):
        url = f"{self.url}/labels?org={self.org}&page_size=1000"
        response = self.get(url)

        labels = {}
        for label in response.json()["results"]:
            labels[label["id"]] = label["name"]

        return labels

    def getAnnotation(self, id):
        url = f"{self.url}/jobs/{id}/annotations"
        response = self.get(url)
        return response.json()
