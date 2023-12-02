def loadConfig(path=None):
    import os
    from pprint import pprint
    from dotenv import load_dotenv

    if path is not None:
        load_dotenv(dotenv_path=path)
    else:
        load_dotenv()

    params = {
        "protocol": os.getenv("PROTOCOL"),
        "host": os.getenv("HOST"),
        "port": os.getenv("PORT"),
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD"),
        "exportFormat": os.getenv("EXPORT_FORMAT"),
        "exportPath": os.getenv("EXPORT_PATH"),
        "savePath": os.getenv("SAVE_PATH"),
        "projectList": os.getenv("PROJECT_LIST"),
        "taskList": os.getenv("TASK_LIST"),
    }

    pprint(params)
    print()
    return params
