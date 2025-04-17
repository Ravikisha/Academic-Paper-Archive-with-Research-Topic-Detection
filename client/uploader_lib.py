# client/uploader_lib.py

import os
import requests
import hashlib

MASTER_NODE_URL = "http://localhost:8000/upload"  # Adjust if needed


def calculate_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def upload_file(file_path):
    file_hash = calculate_hash(file_path)
    with open(file_path, "rb") as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {'hash': file_hash}
        response = requests.post(MASTER_NODE_URL, files=files, data=data)

    if response.status_code == 200:
        return response.json().get("file_id")
    else:
        raise Exception(f"Upload failed: {response.text}")
