import json

with open("result.json", "r") as f:
    data = json.load(f)

label = "unknown"
tasks = [
    taskID
    for taskID in data["result"].keys()
    if data["result"][taskID]["count"][label] > 0
]

print(tasks)
