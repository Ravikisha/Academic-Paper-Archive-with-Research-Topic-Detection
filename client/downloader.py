import os
import requests
from pathlib import Path

MASTER_NODE = "http://localhost:8000"
OUTPUT_DIR = "client/downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_file(file_id: str):
    # Step 1: Fetch metadata from master
    res = requests.get(f"{MASTER_NODE}/get_chunks/{file_id}")
    if res.status_code != 200:
        raise Exception(f"❌ Failed to fetch metadata: {res.text}")

    data = res.json()
    filename = data["filename"]
    chunks = data["chunks"]

    # Group by chunk_index
    chunk_map = {}
    for chunk in chunks:
        i = chunk["chunk_index"]
        if i not in chunk_map:
            chunk_map[i] = []
        chunk_map[i].append(chunk)

    output_path = os.path.join(OUTPUT_DIR, filename)
    with open(output_path, "wb") as f:
        for i in sorted(chunk_map.keys()):
            replicas = chunk_map[i]
            success = False
            for replica in replicas:
                url = f"{replica['storage_node']}/get_chunk/{replica['chunk_hash']}"
                try:
                    print(f"[+] Trying to download chunk {i} from {url}")
                    chunk_res = requests.get(url, timeout=5)
                    if chunk_res.status_code == 200:
                        f.write(chunk_res.content)
                        success = True
                        break
                except Exception as e:
                    print(f"[!] Failed replica: {e}")
            if not success:
                raise Exception(f"❌ All replicas failed for chunk {i}")

    print(f"[🎉] File reconstructed successfully at {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python downloader.py <file_id>")
        exit(1)
    
    file_id = sys.argv[1]
    download_file(file_id)
