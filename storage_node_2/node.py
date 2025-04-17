from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import hashlib

app = FastAPI()
CHUNK_DIR = "data"
os.makedirs(CHUNK_DIR, exist_ok=True)

def get_chunk_path(chunk_hash: str):
    return os.path.join(CHUNK_DIR, chunk_hash)

# 1. Upload a chunk
@app.post("/upload_chunk")
async def upload_chunk(file: UploadFile = File(...)):
    contents = await file.read()
    chunk_hash = hashlib.sha256(contents).hexdigest()
    chunk_path = get_chunk_path(chunk_hash)

    with open(chunk_path, "wb") as f:
        f.write(contents)

    return {
        "message": "Chunk uploaded",
        "chunk_hash": chunk_hash
    }

# 2. Download a chunk by hash
@app.get("/get_chunk/{chunk_hash}")
def get_chunk(chunk_hash: str):
    chunk_path = get_chunk_path(chunk_hash)
    if not os.path.exists(chunk_path):
        raise HTTPException(status_code=404, detail="Chunk not found")

    return FileResponse(chunk_path, media_type='application/octet-stream', filename=chunk_hash)
