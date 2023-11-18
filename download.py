import os
import re
import shutil
from tqdm import tqdm
from utils.cvat import api
from datetime import datetime


class app:
    def __init__(self, params):
        self.API = api(params)
        self.now = datetime.now()

        self.projectList = params[
            "projectList"
        ]  # A file containing the name of the project to download
        self.taskList = params[
            "taskList"
        ]  # A file containing the name of the task to download
        self.exportFormat = params["exportFormat"]
        self.exportPath = params["exportPath"]
        self.savePath = params["savePath"]

        if os.path.exists(self.savePath):
            if input("Are you creating a bounding box? (y/n): ") == "y":
                self.drawBoundingBox()
                exit()

        self.projects = self.getProjects()
        self.tasks, self.taskOptions = self.getTasks()

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
        taskOptions = {}
        if self.projectList is not None:
            for project in self.projects["results"]:
                tasks += self.API.getTasks(project["id"])["results"]
        elif self.taskList is not None:
            with open(self.taskList, "r") as f:
                self.taskList = []
                for data in f.read().split("\n"):
                    if data != "":
                        if " | " in data:
                            task, option = data.split(" | ")
                            self.taskList.append(task)
                            option = option.split("(")[1].split(")")[0].split(", ")
                            taskOptions[task] = list(
                                map(int, option)
                            )  # (start, end, step)
                        else:
                            task = data
                            self.taskList.append(task)
            for task in self.API.getTasks()["results"]:
                if task["name"] in self.taskList:
                    tasks.append(task)
                    self.taskList.remove(task["name"])
                    try:
                        taskOptions[str(task["id"])] = taskOptions.pop(task["name"])
                    except:
                        pass
            if len(self.taskList) > 0:
                print(f"Task(s) not found: {self.taskList}")
        else:
            tasks = self.API.getTasks()["results"]
        return tasks, taskOptions

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
        confirm = ""
        if os.path.exists(self.savePath):
            confirm = input("Are you sure merge all the dataset? (y/n): ")
            if confirm != "y":
                self.savePath = f'{self.savePath}_{self.now.strftime("%Y%m%d%H%M%S")}'

        if confirm != "y" or os.path.exists(self.savePath) == False:
            os.mkdir(self.savePath)
            os.mkdir(os.path.join(self.savePath, "images"))
            os.mkdir(os.path.join(self.savePath, "labels"))

        for id in tqdm(self.exported, desc="Extracting"):
            id = str(id)
            zipFile = os.path.join(self.exportPath, f"{id}.zip")
            extractedPath = os.path.join(self.exportPath, id)
            if os.path.exists(extractedPath):
                shutil.rmtree(extractedPath)
            os.mkdir(extractedPath)
            os.system(f"unzip {zipFile} -d {extractedPath} > /dev/null")

            files = sorted(
                os.listdir(f"{extractedPath}/obj_train_data"),
                key=lambda x: int(re.findall("\d+", x)[0]),
            )

            imageFiles = [
                file
                for file in files
                if file.lower().endswith(".jpg")
                or file.lower().endswith(".png")
                or file.lower().endswith(".jpeg")
            ]

            if len(imageFiles) == 0:
                print(f"Task {id} has no image files")

            if self.taskOptions.get(id) is not None:
                try:
                    start, end, step = self.taskOptions[id]
                except:
                    start, end = self.taskOptions[id]
                    step = 1

                if end == -1:
                    end = len(imageFiles)
                else:
                    end += 1

                imageFiles = imageFiles[start:end:step]

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

    def drawBoundingBox(self):
        import cv2
        from PIL import Image

        if not os.path.exists(f"{self.savePath}/verifyImage"):
            os.mkdir(f"{self.savePath}/verifyImage")

        for _, _, files in os.walk(f"{self.savePath}/images"):
            for fname in tqdm(files):
                if (
                    fname.lower().endswith(".jpg")
                    or fname.lower().endswith(".png")
                    or fname.lower().endswith(".jpeg")
                ):
                    img = cv2.imread(f"{self.savePath}/images/{fname}")
                    f = open(f"{self.savePath}/labels/{fname.split('.')[0]}.txt", "r")
                    lines = f.readlines()
                    for line in lines:
                        line = line.split(" ")
                        x = float(line[1])
                        y = float(line[2])
                        w = float(line[3])
                        h = float(line[4])
                        x1 = int((x - w / 2) * img.shape[1])
                        y1 = int((y - h / 2) * img.shape[0])
                        x2 = int((x + w / 2) * img.shape[1])
                        y2 = int((y + h / 2) * img.shape[0])
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(
                        img, (int(img.shape[1] / 2), int(img.shape[0] / 2))
                    )
                    img = Image.fromarray(img)
                    img.save(
                        f"{self.savePath}/verifyImage/{fname}",
                    )


if __name__ == "__main__":
    from utils.config import loadConfig

    # params = loadConfig()
    params = loadConfig("cvat.ai.env")

    app = app(params)
