import os
import shutil
from tqdm import tqdm
from utils.cvat import api
from datetime import datetime


class app:
    def __init__(self, params):
        self.API = api(params)

        self.projectList = params[
            "projectList"
        ]  # A file containing the name of the project to download
        self.exportPath = params["exportPath"]
        self.savePath = params["savePath"]

        self.projects = self.getProjects()
        self.tasks = self.getTasks()

        self.exported = self.export()

        self.save()

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
        for project in self.projects["results"]:
            tasks += self.API.getTasks(project["id"])["results"]
        return tasks

    def export(self):
        exported = []
        for task in tqdm(self.tasks, desc="Exporting"):
            exported.append(self.API.taskDataset(task["id"]))
        return exported

    def save(self):
        if os.path.exists(self.savePath):
            self.savePath = f'{self.savePath}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        os.mkdir(self.savePath)
        os.mkdir(f"{self.savePath}/images")
        os.mkdir(f"{self.savePath}/labels")

        for id in tqdm(self.exported, desc="Extracting"):
            id = str(id)
            zipFile = os.path.join(self.exportPath, f"{id}.zip")
            extractedPath = os.path.join(self.exportPath, id)
            os.mkdir(extractedPath)
            os.system(f"unzip {zipFile} -d {extractedPath} > /dev/null")

            files = os.listdir(f"{extractedPath}/obj_train_data")
            imageFiles = [
                file
                for file in files
                if file.endswith(".jpg")
                or file.endswith(".png")
                or file.endswith(".jpeg")
            ]

            for idx, image in enumerate(imageFiles):
                imageExt = image.split(".")[-1]
                label = image.replace(f".{imageExt}", ".txt")
                shutil.move(
                    f"{extractedPath}/obj_train_data/{image}",
                    f"{self.savePath}/images/{id}_{idx}.{imageExt}",
                )

                shutil.move(
                    f"{extractedPath}/obj_train_data/{label}",
                    f"{self.savePath}/labels/{id}_{idx}.txt",
                )

            shutil.rmtree(extractedPath)


if __name__ == "__main__":
    from utils.config import loadConfig

    params = loadConfig()

    app = app(params)
