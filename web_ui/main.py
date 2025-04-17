from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import shutil
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from client.uploader import upload_file
from client.downloader import download_file


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MASTER_NODE = "http://localhost:8000"
CLIENT_UPLOAD = "http://localhost:5000/client/uploader.py"  # Reference only if using CLI uploader

uploaded_files = {}  # In-memory for demo; use DB in production


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    # Call the upload_file function directly
    file_id = upload_file(file_path)
    if file_id:
        uploaded_files[file.filename] = file_id
        return RedirectResponse(url="/downloads", status_code=303)
    else:
        return {"error": "Upload failed"}
    


@app.get("/downloads")
def downloads(request: Request):
    return templates.TemplateResponse("downloads.html", {
        "request": request,
        "files": uploaded_files
    })


@app.get("/download/{file_id}")
def download_file_web(file_id: str):
    # import subprocess
    # subprocess.run(["python", "../client/downloader.py", file_id])
    # return {"message": "Download triggered in backend (check downloads folder)"}
    
    # Call the download_file function directly
    download_file(file_id)
    filepath = os.path.join(UPLOAD_DIR, file_id)
    if os.path.exists(filepath):
        return {
            "message": f"File downloaded successfully: {filepath}",
            "file_path": filepath
        }
    else:
        return {"error": "File not found"}
