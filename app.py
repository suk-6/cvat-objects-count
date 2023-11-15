import os
import requests
import json
from dotenv import load_dotenv
from tqdm import tqdm


class app:
    def __init__(self, protocol, host, port, username, password, org, taskID=None):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.org = org
        self.taskID = taskID

        self.url = f"{self.protocol}://{self.host}:{self.port}/api"

        self.login()

        if self.taskID is not None:
            if type(self.taskID) is int:
                self.tasksID = [self.taskID]
            else:
                self.tasksID = self.taskID
        else:
            self.tasks = self.tasks()
            self.tasksID = self.tasksID()
        self.labels = self.labels()

        self.counts, self.totals = self.count()
        self.result = self.taskResult()

        self.statistics = self.calcStatistics()

        self.save()

    def login(self):
        url = f"{self.url}/auth/login"
        payload = {"username": self.username, "password": self.password}
        headers = {"Content-Type": "application/json"}
        response = requests.request(
            "POST", url, headers=headers, data=json.dumps(payload)
        )

        self.cookie = response.cookies

    def get(self, url):
        return requests.request("GET", url, cookies=self.cookie)

    def tasks(self):
        url = f"{self.url}/tasks?org={self.org}&page_size=1000"
        response = self.get(url)
        return response.json()

    def tasksID(self):
        tasksID = []
        for task in self.tasks["results"]:
            tasksID.append(task["id"])
        return tasksID

    def labels(self):
        url = f"{self.url}/labels?org={self.org}&page_size=1000"
        response = self.get(url)

        labels = {}
        for label in response.json()["results"]:
            labels[label["id"]] = label["name"]

        return labels

    def annotation(self, id):
        url = f"{self.url}/tasks/{id}/annotations"
        response = self.get(url)
        return response.json()

    def sumObject(self, obj):
        total = 0

        for key in obj:
            total += obj[key]

        return total

    def initCount(self):
        counts = {}

        for label in self.labels.values():
            counts[label] = 0

        return counts

    def count(self):
        counts = {}
        totals = {}

        for id in tqdm(self.tasksID):
            count = self.initCount()
            annotations = self.annotation(id)
            try:
                for annotation in annotations["shapes"]:
                    label = self.labels[annotation["label_id"]]
                    count[label] += 1
            except:
                pass

            try:
                for track in annotations["tracks"]:
                    label = self.labels[track["label_id"]]
                    count[label] += len(track["shapes"])
            except:
                pass

            total = self.sumObject(count)

            counts[id] = count
            totals[id] = total

        return counts, totals

    def taskResult(self, id=None):
        result = {}
        if id is not None:
            result[id] = {}
            result[id]["count"] = self.counts[id]
            result[id]["total"] = self.totals[id]
        else:
            for id in self.tasksID:
                result[id] = {}
                result[id]["count"] = self.counts[id]
                result[id]["total"] = self.totals[id]
        return result

    def calcStatistics(self):
        count = self.initCount()
        total = 0

        for id in self.result:
            for label in count.keys():
                count[label] += self.result[id]["count"][label]
            total += self.result[id]["total"]

        print("Total: ", total)
        print("Count: ", count)

        return {"count": count, "total": total}

    def save(self):
        saveData = {}
        saveData["statistics"] = self.statistics
        saveData["result"] = self.result

        with open("result.json", "w") as f:
            json.dump(saveData, f, indent=4)


load_dotenv()

protocol = os.getenv("PROTOCOL")
host = os.getenv("HOST")
port = os.getenv("PORT")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
org = os.getenv("ORG")

app = app(protocol, host, port, username, password, org)
