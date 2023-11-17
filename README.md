# CVAT Tools

## Setting up

Write a environment variable file named `.env` with the following content:

```bash
PROTOCOL=https
HOST=app.cvat.ai
PORT=443
USERNAME=username
PASSWORD=password
ORG=orgnization
EXPORT_FORMAT='YOLO 1.1'
EXPORT_PATH='./export'
SAVE_PATH='./data'
PROJECT_LIST='./project_list.txt'
```

## Count Objects

    ```bash
    python count.py
    ```

## Download Dataset

    ```bash
    python download.py
    ```
