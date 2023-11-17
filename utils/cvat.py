import os
import time
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
        self.exportFormat = params["exportFormat"]
        self.exportPath = params["exportPath"]

        self.url = f"{self.protocol}://{self.host}:{self.port}/api"

        self.cookie = login(self.url, self.username, self.password)

    def get(self, url):
        return requests.request("GET", url, cookies=self.cookie)

    def getProjects(self):
        url = f"{self.url}/projects?org={self.org}&page_size=1000"
        response = self.get(url)
        return response.json()

    def getTasks(self, projectID=None):
        if projectID is not None:
            url = (
                f"{self.url}/tasks?org={self.org}&page_size=1000&project_id={projectID}"
            )
        else:
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

    def getDataset(self, id):
        url = f"{self.url}/tasks/{id}/dataset?org={self.org}&format={self.exportFormat}&action=download"
        response = self.get(url)

        if response.status_code == 200:
            return response.content
        elif response.status_code == 201:
            return self.getDataset(id)
        elif response.status_code == 202:
            time.sleep(5)
            return self.getDataset(id)
        elif response.status_code == 400:
            raise Exception("Exporting without data is not allowed")
        elif response.status_code == 405:
            raise Exception("Dataset not found")
        else:
            raise Exception("Unknown error")
