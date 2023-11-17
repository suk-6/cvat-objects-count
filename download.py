import os
import re
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
        self.exportFormat = params["exportFormat"]
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
        if self.exportFormat == None and self.exportPath == None:
            raise Exception("Export format and path not specified")
        elif os.path.exists(self.exportPath) == False:
            os.mkdir(self.exportPath)
        elif os.path.isdir(self.exportPath) == False:
            raise Exception("Export path is not a directory")

        exported = []

        for task in tqdm(self.tasks, desc="Exporting"):
            id = task["id"]
            path = os.path.join(self.exportPath, f"{id}.zip")
            if os.path.exists(path):
                pass
            else:
                content = self.API.getDataset(id)
                with open(path, "wb") as f:
                    f.write(content)
            exported.append(id)

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

            files = sorted(
                os.listdir(f"{extractedPath}/obj_train_data"),
                key=lambda x: int(re.findall("\d+", x)[0]),
            )

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
