import os
import shutil

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult

from backend.worker import process_pdf_task, celery_app
from backend.rag_system import get_answer

app = FastAPI(title="REAQ Celery Version")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Upload + Trigger Celery Task
# -----------------------------
@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    operation: str = Form(...)
):
    try:
        filename = os.path.basename(file.filename).replace(" ", "_")
        pdf_path = os.path.join(UPLOAD_DIR, filename)

        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        task = process_pdf_task.delay(pdf_path, operation)

        return {"task_id": task.id}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# -----------------------------
# Check Task Status
# -----------------------------
@app.get("/status/{task_id}")
async def get_status(task_id: str):

    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task_result.status,
        "progress": 0,
        "message": ""
    }

    if task_result.status == "PROGRESS":
        response["progress"] = task_result.info.get("progress", 0)
        response["message"] = task_result.info.get("message", "")

    if task_result.status == "SUCCESS":
        response.update(task_result.result)

    if task_result.status == "FAILURE":
        response["error"] = str(task_result.info)

    return response


# -----------------------------
# Download
# -----------------------------
@app.get("/download/{filename}")
async def download_file(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(path, filename=filename)


# -----------------------------
# Chat Endpoint
# -----------------------------
@app.post("/chat")
async def chat(user_query: str = Form(...), pdf_name: str = Form(...)):
    answer = get_answer(user_query, pdf_name)
    return {"response": answer}
