@echo off
REM start master
start "Master" cmd /k "call venv/Scripts/activate && cd master && uvicorn main:app --reload --port 8000"

REM start storage_node
start "Storage Node 1" cmd /k "call venv/Scripts/activate && cd storage_node && uvicorn node:app --reload --port 8001"

REM start storage_node_2
start "Storage Node 2" cmd /k "call venv/Scripts/activate && cd storage_node_2 && uvicorn node:app --reload --port 8002"

REM start Web App
start "Web App" cmd /k "call venv/Scripts/activate && cd web_api && uvicorn main:app --reload --port 9000"