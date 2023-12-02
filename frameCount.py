import json
from tqdm import tqdm
from utils.cvat import api


class app:
    def __init__(self, params, taskID=None):
        self.API = api(params)
        self.taskID = taskID
        self.projectList = params["projectList"]

        self.project = self.getProjects()
        self.tasks = self.getTasks()

        print(f"Projects: {self.projectList}")
        print(f"Total frames in the project: {self.sumFrames()}")

    def getProjects(self):
        projects = self.API.getProjects()
        if self.projectList is not None:
            with open(self.projectList, "r") as f:
                self.projectList = [name for name in f.read().split("\n") if name != ""]
            projects["results"] = [
                project
                for project in projects["results"]
                if project["name"] in self.projectList
            ]
        return projects

    def getTasks(self):
        tasks = []
        for project in self.project["results"]:
            tasks += self.API.getTasks(project["id"])["results"]
        return tasks

    def sumFrames(self):
        sumFrames = 0
        for task in self.tasks:
            sumFrames += task["segment_size"]
        return sumFrames


if __name__ == "__main__":
    from utils.config import loadConfig

    params = loadConfig()

    app = app(params)
