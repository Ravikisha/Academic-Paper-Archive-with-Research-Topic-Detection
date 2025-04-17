from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict
import uuid
import sqlite3
import os

app = FastAPI()
DB_FILE = "file_metadata.db"

# ---------------------- DB INIT ----------------------

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS files (
            file_id TEXT,
            filename TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            file_id TEXT,
            chunk_index INTEGER,
            chunk_hash TEXT,
            storage_node TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------------- Schemas ----------------------

class ChunkMetadata(BaseModel):
    chunk_index: int
    chunk_hash: str
    storage_node: str

class FileRegistration(BaseModel):
    filename: str
    chunks: List[ChunkMetadata]

# ---------------------- Routes ----------------------

@app.post("/register_file")
def register_file(metadata: FileRegistration):
    file_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    cur.execute("INSERT INTO files (file_id, filename) VALUES (?, ?)", (file_id, metadata.filename))

    for chunk in metadata.chunks:
        cur.execute(
            "INSERT INTO chunks (file_id, chunk_index, chunk_hash, storage_node) VALUES (?, ?, ?, ?)",
            (file_id, chunk.chunk_index, chunk.chunk_hash, chunk.storage_node)
        )

    conn.commit()
    conn.close()
    return {"file_id": file_id, "message": "File registered successfully"}

@app.get("/get_chunks/{file_id}")
def get_chunks(file_id: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT filename FROM files WHERE file_id = ?", (file_id,))
    file_row = cur.fetchone()
    if not file_row:
        raise HTTPException(status_code=404, detail="File not found")

    cur.execute("SELECT chunk_index, chunk_hash, storage_node FROM chunks WHERE file_id = ? ORDER BY chunk_index", (file_id,))
    chunks = cur.fetchall()
    conn.close()

    return {
        "file_id": file_id,
        "filename": file_row[0],
        "chunks": [
            {
                "chunk_index": index,
                "chunk_hash": chunk_hash,
                "storage_node": node
            } for index, chunk_hash, node in chunks
        ]
    }

@app.get("/list_files")
def list_files():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT file_id, filename FROM files")
    files = cur.fetchall()
    conn.close()
    return {"files": [{"file_id": fid, "filename": name} for fid, name in files]}
