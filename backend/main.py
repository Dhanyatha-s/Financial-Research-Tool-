# # backend/main.py
# import os
# import shutil
# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.responses import FileResponse, JSONResponse
# from fastapi.middleware.cors import CORSMiddleware

# # -----------------------------
# # Excel pipeline import
# # -----------------------------
# from excel_pipeline import run_excel_pipeline  # your main.py logic wrapped as a function

# # -----------------------------
# # RAG system import
# # -----------------------------
# from rag_system import index_pdf, get_answer

# # -----------------------------
# # FastAPI app
# # -----------------------------
# app = FastAPI(title="Reag AI Backend")

# # Enable CORS for your frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # change to your frontend URL in production
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# # -----------------------------
# # Directories
# # -----------------------------
# UPLOAD_DIR = "uploads"
# OUTPUT_DIR = "outputs"
# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # -----------------------------
# # Endpoint: Upload PDF & generate Excel
# # -----------------------------
# @app.post("/upload")
# async def upload_pdf(file: UploadFile = File(...)):
#     try:
#         # Save uploaded PDF
#         pdf_path = os.path.join(UPLOAD_DIR, file.filename)
#         with open(pdf_path, "wb") as f:
#             shutil.copyfileobj(file.file, f)

#         # -----------------------------
#         # Step 1: Generate Excel
#         # -----------------------------
#         excel_file = run_excel_pipeline(pdf_path)  # must return full path to Excel

#         # -----------------------------
#         # Step 2: Index PDF for RAG
#         # -----------------------------
#         index_pdf(pdf_path)

#         # -----------------------------
#         # Step 3: Return Excel file
#         # -----------------------------
#         return FileResponse(
#             path=excel_file,
#             filename=os.path.basename(excel_file),
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

#     except Exception as e:
#         return JSONResponse(
#             content={"error": f"❌ Failed processing PDF: {str(e)}"},
#             status_code=500
#         )

# # -----------------------------
# # Endpoint: Chat with RAG
# # -----------------------------
# @app.post("/chat")
# async def chat_endpoint(user_query: str = Form(...), pdf_name: str = Form(...)):
#     try:
#         answer = get_answer(user_query, pdf_name)
#         return {"response": answer}
#     except Exception as e:
#         return {"response": f"❌ Error during RAG query: {str(e)}"}


# import os
# import shutil
# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.responses import FileResponse, JSONResponse
# from fastapi.middleware.cors import CORSMiddleware

# # Use absolute imports instead of relative (removed the '.')
# from backend.excel_pipeline import run_excel_pipeline
# from backend.rag_system import index_pdf, get_answer

# app = FastAPI(title="Offline RAG Backend")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# UPLOAD_DIR = "uploads"
# OUTPUT_DIR = "outputs"
# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# @app.post("/upload")
# async def upload_pdf(file: UploadFile = File(...)):
#     try:
#         # Secure the path
#         pdf_path = os.path.abspath(os.path.join(UPLOAD_DIR, file.filename))
        
#         with open(pdf_path, "wb") as f:
#             shutil.copyfileobj(file.file, f)

#         # Index PDF for RAG using FAISS (from the updated rag_system.py)
#         index_pdf(pdf_path)

#         # Generate Excel (assuming this uses your mainPipeline)
#         excel_file = run_excel_pipeline(pdf_path) 

#         if not os.path.exists(excel_file):
#             raise Exception("Excel file was not generated.")

#         return FileResponse(
#             path=excel_file,
#             filename=os.path.basename(excel_file),
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

#     except Exception as e:
#         return JSONResponse(
#             content={"error": f"❌ Failed processing PDF: {str(e)}"},
#             status_code=500
#         )

# @app.post("/chat")
# async def chat_endpoint(user_query: str = Form(...), pdf_name: str = Form(...)):
#     try:
#         # Use the filename (basename) as the key for your retrievers dict
#         clean_pdf_name = os.path.basename(pdf_name)
#         answer = get_answer(user_query, clean_pdf_name)
#         return {"response": answer}
#     except Exception as e:
#         return {"response": f"❌ Error during RAG query: {str(e)}"}


# import os
# import shutil
# from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
# from fastapi.responses import FileResponse, JSONResponse
# from fastapi.middleware.cors import CORSMiddleware

# from backend.excel_pipeline import run_excel_pipeline
# from backend.rag_system import index_pdf, get_answer, load_knowledge_base

# # -----------------------------
# # FastAPI App
# # -----------------------------
# app = FastAPI(title="Offline RAG Backend")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# UPLOAD_DIR = "uploads"
# OUTPUT_DIR = "outputs"
# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # Load knowledge base on startup
# load_knowledge_base()

# # -----------------------------
# # PDF Upload & Excel Generation
# # -----------------------------
# @app.post("/upload")
# async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
#     try:
#         pdf_path = os.path.abspath(os.path.join(UPLOAD_DIR, file.filename))
#         with open(pdf_path, "wb") as f:
#             shutil.copyfileobj(file.file, f)

#         # Index PDF in background
#         background_tasks.add_task(index_pdf, pdf_path)

#         # Generate Excel immediately
#         excel_file = run_excel_pipeline(pdf_path)

#         if not os.path.exists(excel_file):
#             raise Exception("Excel file was not generated.")

#         return FileResponse(
#             path=excel_file,
#             filename=os.path.basename(excel_file),
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

#     except Exception as e:
#         return JSONResponse(
#             content={"error": f"❌ Failed processing PDF: {str(e)}"},
#             status_code=500
#         )

# # -----------------------------
# # Chat / RAG Query
# # -----------------------------
# @app.post("/chat")
# async def chat_endpoint(user_query: str = Form(...), pdf_name: str = Form(...)):
#     try:
#         clean_pdf_name = os.path.basename(pdf_name)
#         answer = get_answer(user_query, clean_pdf_name)
#         return {"response": answer}
#     except Exception as e:
#         return {"response": f"❌ Error during RAG query: {str(e)}"}




# import os
# import shutil
# from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
# from fastapi.responses import FileResponse, JSONResponse
# from fastapi.middleware.cors import CORSMiddleware

# from backend.excel_pipeline import run_excel_pipeline
# from backend.rag_system import index_pdf, get_answer, load_knowledge_base

# app = FastAPI(title="Offline RAG Backend")

# # Allow all CORS for testing
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# UPLOAD_DIR = "uploads"
# OUTPUT_DIR = "outputs"
# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # Load existing knowledge base at startup
# load_knowledge_base()

# # -----------------------------
# # PDF Upload & Excel Generation
# # -----------------------------
# @app.post("/upload")
# async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
#     try:
#         pdf_path = os.path.abspath(os.path.join(UPLOAD_DIR, file.filename))
#         with open(pdf_path, "wb") as f:
#             shutil.copyfileobj(file.file, f)

#         # Index PDF in background
#         background_tasks.add_task(index_pdf, pdf_path)

#         # Generate Excel immediately
#         excel_file = run_excel_pipeline(pdf_path)
#         if not os.path.exists(excel_file):
#             raise Exception("Excel file was not generated.")

#         return FileResponse(
#             path=excel_file,
#             filename=os.path.basename(excel_file),
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

#     except Exception as e:
#         return JSONResponse(
#             content={"error": f"❌ Failed processing PDF: {str(e)}"},
#             status_code=500
#         )

# # -----------------------------
# # Chat / RAG Query
# # -----------------------------
# @app.post("/chat")
# async def chat_endpoint(user_query: str = Form(...), pdf_name: str = Form(...)):
#     try:
#         clean_pdf_name = os.path.basename(pdf_name)
#         answer = get_answer(user_query, clean_pdf_name)
#         return {"response": answer}
#     except Exception as e:
#         return {"response": f"❌ Error during RAG query: {str(e)}"}



# import os
# import shutil
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
# from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles

# from backend.excel_pipeline import run_excel_pipeline
# from backend.rag_system import index_pdf, get_answer, load_knowledge_base

# app = FastAPI(title="REAQ Financial Research Backend")

# # -----------------------------
# # CORS
# # -----------------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # -----------------------------
# # Directories
# # -----------------------------
# UPLOAD_DIR = "uploads"
# OUTPUT_DIR = "outputs"
# STATIC_DIR = "static"  # serve HTML/CSS/JS

# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(OUTPUT_DIR, exist_ok=True)
# os.makedirs(STATIC_DIR, exist_ok=True)

# # Mount static and outputs
# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

# # -----------------------------
# # Thread Executor for RAG
# # -----------------------------
# executor = ThreadPoolExecutor(max_workers=2)

# @app.on_event("startup")
# async def startup_event():
#     print("🚀 Starting REAQ Backend...")
#     try:
#         load_knowledge_base()
#         print("✅ Backend ready")
#     except Exception as e:
#         print(f"⚠️ Knowledge base init warning: {e}")
#         print("✅ Backend ready (will index PDFs on upload)")

# async def safe_index(pdf_path: str):
#     """Index PDF for RAG after a short delay"""
#     await asyncio.sleep(2)
#     loop = asyncio.get_event_loop()
#     try:
#         print(f"🔍 Starting RAG indexing: {os.path.basename(pdf_path)}")
#         await loop.run_in_executor(executor, index_pdf, pdf_path)
#         print(f"✅ RAG indexing completed: {os.path.basename(pdf_path)}")
#     except Exception as e:
#         print(f"⚠️ RAG indexing failed: {e}")

# # -----------------------------
# # Serve Landing Page
# # -----------------------------
# @app.get("/landing", response_class=HTMLResponse)
# async def landing_page():
#     with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
#         return HTMLResponse(content=f.read())

# @app.get("/chatinterface", response_class=HTMLResponse)
# async def chat_interface():
#     with open(os.path.join(STATIC_DIR, "chatinterface.html"), "r", encoding="utf-8") as f:
#         return HTMLResponse(content=f.read())

# # -----------------------------
# # PDF Upload Endpoint
# # -----------------------------
# @app.post("/upload")
# async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
#     try:
#         if not file.filename.lower().endswith('.pdf'):
#             return JSONResponse({"error": "Only PDF files are allowed"}, status_code=400)

#         safe_filename = file.filename.replace(" ", "_")
#         pdf_path = os.path.abspath(os.path.join(UPLOAD_DIR, safe_filename))
        
#         with open(pdf_path, "wb") as f:
#             shutil.copyfileobj(file.file, f)

#         # Start Excel pipeline in background
#         background_tasks.add_task(run_pipeline_and_index, pdf_path)

#         excel_filename = safe_filename.replace(".pdf", "_financial.xlsx")

#         return JSONResponse({
#             "success": True,
#             "message": f"📤 Upload received: {safe_filename}. Processing started...",
#             "pdf_name": safe_filename,
#             "filename": excel_filename
#         })
    
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return JSONResponse(content={"error": str(e)}, status_code=500)

# async def run_pipeline_and_index(pdf_path: str):
#     """Runs Excel pipeline & triggers RAG indexing in background"""
#     try:
#         # Run Excel pipeline
#         excel_file = await asyncio.to_thread(run_excel_pipeline, pdf_path)
#         print(f"✅ Excel generated: {excel_file}")
#         # RAG indexing
#         await safe_index(pdf_path)
#     except Exception as e:
#         print(f"⚠️ Pipeline failed for {pdf_path}: {e}")

# # -----------------------------
# # Download Excel
# # -----------------------------
# # @app.get("/download/{filename}")
# # async def download_file(filename: str):
# #     file_path = os.path.join(OUTPUT_DIR, filename)
# #     if not os.path.exists(file_path):
# #         return JSONResponse({"error": "File not found"}, status_code=404)
# #     return FileResponse(path=file_path, filename=filename)
# @app.get("/download/{filename}")
# async def download_file(filename: str):
#     file_path = os.path.join(OUTPUT_DIR, filename)
#     if not os.path.exists(file_path):
#         return JSONResponse({"error": "File not found"}, status_code=404)
#     return FileResponse(path=file_path, filename=filename)

# # -----------------------------
# # RAG Chat Endpoint
# # -----------------------------
# @app.post("/chat")
# async def chat_endpoint(user_query: str = Form(...), pdf_name: str = Form(...)):
#     try:
#         clean_pdf_name = os.path.basename(pdf_name).replace(" ", "_")
#         loop = asyncio.get_event_loop()
#         answer = await loop.run_in_executor(executor, get_answer, user_query, clean_pdf_name)
#         return JSONResponse(content={"response": answer})
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return JSONResponse(content={"response": f"Error: {str(e)}"}, status_code=500)

# # -----------------------------
# # Health Check
# # -----------------------------
# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "message": "REAQ Backend running",
#         "upload_dir": UPLOAD_DIR,
#         "output_dir": OUTPUT_DIR
#     }

# @app.get("/", response_class=HTMLResponse)
# async def root():
#     return await landing_page()




# import os
# import shutil
# import asyncio
# import time
# import threading
# from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
# from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from typing import Dict
# import threading

# from backend.excel_pipeline import run_excel_pipeline
# from backend.rag_system import index_pdf, get_answer, load_knowledge_base

# app = FastAPI(title="REAQ Financial Research Backend")

# # -----------------------------
# # CORS
# # -----------------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # -----------------------------
# # Directories
# # -----------------------------
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
# OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
# STATIC_DIR = os.path.join(BASE_DIR, "static")

# INDEX_HTML = os.path.join(BASE_DIR, "index.html")
# CHAT_HTML = os.path.join(BASE_DIR, "chatinterface.html")

# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # Mount outputs folder for direct download
# app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

# # -----------------------------
# # Status Tracking
# # -----------------------------
# processing_status: Dict[str, dict] = {}
# status_lock = threading.Lock()

# @app.on_event("startup")
# async def startup_event():
#     print("🚀 Starting REAQ Backend...")
#     try:
#         load_knowledge_base()
#         print("✅ Backend ready")
#     except Exception as e:
#         print(f"⚠️ Knowledge base warning: {e}")
#         print("✅ Backend ready (indexing on upload)")

# def update_status(filename: str, stage: str, message: str, progress: int,
#                   error: str = None, excel_file: str = None):
#     with status_lock:
#         processing_status[filename] = {
#             "stage": stage,
#             "message": message,
#             "progress": progress,
#             "error": error,
#             "excel_file": excel_file,
#             "download_url": f"/outputs/{excel_file}" if excel_file else None,
#             "timestamp": time.time()
#         }
#     print(f"[{filename}] {message}")

# # -----------------------------
# # Landing Pages
# # -----------------------------
# @app.get("/landing", response_class=HTMLResponse)
# async def landing_page():
#     with open(INDEX_HTML, "r", encoding="utf-8") as f:
#         return HTMLResponse(content=f.read())

# @app.get("/chatinterface", response_class=HTMLResponse)
# async def chat_interface():
#     with open(CHAT_HTML, "r", encoding="utf-8") as f:
#         return HTMLResponse(content=f.read())

# @app.get("/", response_class=HTMLResponse)
# async def root():
#     return await landing_page()

# # -----------------------------
# # Upload Endpoint
# # -----------------------------
# @app.post("/upload")
# async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
#     try:
#         if not file.filename.lower().endswith(".pdf"):
#             return JSONResponse({"error": "Only PDF files allowed"}, status_code=400)

#         safe_filename = os.path.basename(file.filename).replace(" ", "_")
#         pdf_path = os.path.join(UPLOAD_DIR, safe_filename)

#         update_status(safe_filename, "uploading", "📤 Uploading PDF...", 10)

#         with open(pdf_path, "wb") as f:
#             shutil.copyfileobj(file.file, f)

#         update_status(safe_filename, "uploaded", "✅ Upload complete", 20)

        
#         threading.Thread(
#             target=run_pipeline_and_index,
#             args=(pdf_path, safe_filename),
#             daemon=True
#         ).start()


#         return JSONResponse({
#             "success": True,
#             "pdf_name": safe_filename,
#             "message": "Upload successful. Processing started."
#         })

#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)

# # -----------------------------
# # Pipeline Runner
# # -----------------------------
# def run_pipeline_and_index(pdf_path: str, filename: str):
#     try:
#         update_status(filename, "extracting", "📊 Extracting financial tables...", 30)

#         # This MUST return full excel file path
#         excel_path = run_excel_pipeline(pdf_path, filename, update_status)

#         excel_filename = os.path.basename(excel_path)

#         update_status(
#             filename,
#             "excel_complete",
#             "✅ Excel generated successfully",
#             70,
#             excel_file=excel_filename
#         )

#         # RAG indexing
#         update_status(filename, "indexing", "🔍 Indexing for Q&A...", 80)
#         index_pdf(pdf_path)

#         update_status(
#             filename,
#             "complete",
#             "✅ All processing complete!",
#             100,
#             excel_file=excel_filename
#         )

#     except Exception as e:
#         update_status(filename, "error", f"⚠️ Pipeline failed: {str(e)}", 0, error=str(e))
#         print("Pipeline error:", e)

# # -----------------------------
# # Status Endpoint
# # -----------------------------
# @app.get("/status/{filename}")
# async def get_status(filename: str):
#     with status_lock:
#         status = processing_status.get(filename, {
#             "stage": "unknown",
#             "message": "No status available",
#             "progress": 0,
#             "error": None,
#             "excel_file": None,
#             "download_url": None
#         })
#     return JSONResponse(content=status)

# # -----------------------------
# # Optional Direct Download
# # -----------------------------
# @app.get("/download/{filename}")
# async def download_file(filename: str):
#     file_path = os.path.join(OUTPUT_DIR, filename)
#     if not os.path.exists(file_path):
#         return JSONResponse({"error": "File not found"}, status_code=404)
#     return FileResponse(path=file_path, filename=filename)

# # -----------------------------
# # Chat Endpoint
# # -----------------------------
# @app.post("/chat")
# async def chat_endpoint(user_query: str = Form(...), pdf_name: str = Form(...)):
#     try:
#         clean_pdf_name = os.path.basename(pdf_name).replace(" ", "_")
#         answer = await asyncio.to_thread(get_answer, user_query, clean_pdf_name)
#         return JSONResponse(content={"response": answer})
#     except Exception as e:
#         return JSONResponse(content={"response": f"Error: {str(e)}"}, status_code=500)

# # -----------------------------
# # Health
# # -----------------------------
# @app.get("/health")
# async def health_check():
#     return {"status": "healthy"}



import os
import shutil
import asyncio
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from celery.result import AsyncResult

from backend.worker import process_pdf_task, celery_app
from backend.rag_system import get_answer, load_knowledge_base

app = FastAPI(title="REAQ Financial Research Backend")

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Directories
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

INDEX_HTML = os.path.join(BASE_DIR, "index.html")
CHAT_HTML = os.path.join(BASE_DIR, "chatinterface.html")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


# -----------------------------
# Startup
# -----------------------------
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting REAQ Backend...")
    try:
        load_knowledge_base()
        print("✅ Backend ready")
    except Exception as e:
        print(f"⚠️ Knowledge base warning: {e}")
        print("✅ Backend ready (indexing on upload)")


# -----------------------------
# Landing Pages
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def root():
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/chatinterface", response_class=HTMLResponse)
async def chat_interface():
    with open(CHAT_HTML, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


# -----------------------------
# Upload Endpoint (CELERY)
# -----------------------------
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            return JSONResponse({"error": "Only PDF files allowed"}, status_code=400)

        safe_filename = os.path.basename(file.filename).replace(" ", "_")
        pdf_path = os.path.join(UPLOAD_DIR, safe_filename)

        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 🔥 Enqueue Celery Task
        task = process_pdf_task.delay(pdf_path)

        return JSONResponse({
            "success": True,
            "task_id": task.id,
            "pdf_name": safe_filename,
            "message": "Upload successful. Processing started."
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# -----------------------------
# Status Endpoint (CELERY)
# -----------------------------
@app.get("/status/{task_id}")
async def get_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)

    if task.state == "PENDING":
        return {"status": "PENDING", "progress": 0}

    if task.state == "PROGRESS":
        return {
            "status": "PROGRESS",
            "progress": task.info.get("progress", 0),
            "message": task.info.get("message", "")
        }

    if task.state == "SUCCESS":
        return {
            "status": "SUCCESS",
            "result": task.result
        }

    if task.state == "FAILURE":
        return {
            "status": "FAILURE",
            "error": str(task.info)
        }

    return {"status": task.state}


# -----------------------------
# Download
# -----------------------------
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(path=file_path, filename=filename)


# -----------------------------
# Chat Endpoint
# -----------------------------
@app.post("/chat")
async def chat_endpoint(user_query: str = Form(...), pdf_name: str = Form(...)):
    try:
        answer = await asyncio.to_thread(get_answer, user_query, pdf_name)
        return JSONResponse(content={"response": answer})
    except Exception as e:
        return JSONResponse(content={"response": f"Error: {str(e)}"}, status_code=500)


# -----------------------------
# Health
# -----------------------------
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
