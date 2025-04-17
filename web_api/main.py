from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import shutil
import os
import sys
import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from client.uploader import upload_file
from client.downloader import download_file
from metadata.db import add_paper, list_papers, get_paper
from ml_engine.vector_store import search_similar_papers, add_paper_vector
from ml_engine.summarizer import generate_summary, extract_text_from_pdf
from ml_engine.topic_model import extract_topics


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.mount("/files", StaticFiles(directory="client/downloads"), name="files")

UPLOAD_DIR = "uploads"
MERGE_FILE_PATH = "client/downloads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MASTER_NODE = "http://localhost:8000"
CLIENT_UPLOAD = "http://localhost:5000/client/uploader.py" 


@app.get("/")
def index(request: Request):
    papers = list_papers()
    return templates.TemplateResponse("index.html", {"request": request, "papers": papers})

@app.post("/")
async def search_query(request: Request):
    form = await request.form()
    query = form.get("query")

    if not query:
        return templates.TemplateResponse("search.html", {
            "request": request,
            "error": "Please enter a query."
        })

    similar_ids = search_similar_papers(query)
    results = [get_paper(pid) for pid in similar_ids]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "query": query,
        "results": results
    })
    
@app.get("/upload")
def upload(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload")
async def handle_upload(request: Request, file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    # Call the upload_file function directly
    file_id = upload_file(file_path)
    if file_id:
        # Get Text
        raw_text = extract_text_from_pdf(file_path)    
        # Get the summary
        summary = generate_summary(raw_text)
        # Get the topics
        topics = extract_topics(raw_text)
        add_paper_vector(file_id, raw_text)
        # Add paper metadata to the database
        add_paper(file_id, file.filename, summary, topics, file.filename)
        # Clean up the uploaded file
        os.remove(file_path)
        
        return RedirectResponse(url="/", status_code=303)
    else:
        return {"error": "Upload failed"}
    
@app.get("/download/{file_id}")
def download_file_web(file_id: str):
    # Call the download_file function directly
    download_file(file_id)
    result = get_paper(file_id)
    file = os.path.join(MERGE_FILE_PATH, result.title)
    if os.path.exists(file):
        return RedirectResponse(url=f"/files/{result.title}", status_code=303)
    else:
        raise HTTPException(status_code=404, detail="File not found")
