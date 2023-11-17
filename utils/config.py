def loadConfig():
    import os
    from dotenv import load_dotenv

    load_dotenv()

    params = {
        "protocol": os.getenv("PROTOCOL"),
        "host": os.getenv("HOST"),
        "port": os.getenv("PORT"),
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD"),
        "org": os.getenv("ORG"),
        "exportFormat": os.getenv("EXPORT_FORMAT"),
        "exportPath": os.getenv("EXPORT_PATH"),
        "savePath": os.getenv("SAVE_PATH"),
        "projectList": os.getenv("PROJECT_LIST"),
    }

    print(params)
    return params
