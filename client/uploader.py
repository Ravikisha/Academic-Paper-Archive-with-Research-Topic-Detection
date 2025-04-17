import os
import requests
import hashlib
import random
from typing import List
from pathlib import Path

MASTER_NODE = "http://localhost:8000"
STORAGE_NODES = [
    "http://localhost:8001",
    "http://localhost:8002"
]
CHUNK_SIZE = 4 * 1024 * 1024  # 4MB
REPLICATION_FACTOR = 2

def split_file(file_path: str) -> List[bytes]:
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk

def upload_file(file_path: str):
    filename = os.path.basename(file_path)
    chunks_meta = []

    for index, chunk in enumerate(split_file(file_path)):
        chunk_hash = hashlib.sha256(chunk).hexdigest()
        nodes = random.sample(STORAGE_NODES, REPLICATION_FACTOR)

        for storage_node in nodes:
            # Upload chunk to the node
            print(f"[+] Uploading chunk {index} to {storage_node}")
            files = {"file": (chunk_hash, chunk)}
            res = requests.post(f"{storage_node}/upload_chunk", files=files)

            if res.status_code != 200:
                raise Exception(f"Failed to upload chunk {index} to {storage_node}: {res.text}")

            # Store metadata for this replica
            chunks_meta.append({
                "chunk_index": index,
                "chunk_hash": chunk_hash,
                "storage_node": storage_node
            })

    # Register file metadata to master node
    metadata = {
        "filename": filename,
        "chunks": chunks_meta
    }
    print(f"[✓] Registering file metadata to master node...")
    res = requests.post(f"{MASTER_NODE}/register_file", json=metadata)

    if res.status_code == 200:
        file_id = res.json()["file_id"]
        print(f"[🎉] File uploaded successfully! File ID: {file_id}")
        return file_id
    else:
        raise Exception(f"Failed to register metadata: {res.text}")
    

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python uploader.py <file_path>")
        exit(1)
    
    file_path = sys.argv[1]
    if not Path(file_path).is_file():
        print(f"❌ File not found: {file_path}")
        exit(1)
    
    upload_file(file_path)
