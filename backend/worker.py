# from celery import Celery
# import os

# from backend.excel_pipeline import run_excel_pipeline
# from backend.rag_system import index_pdf

# # Redis broker + backend
# celery_app = Celery(
#     "tasks",
#     broker="redis://localhost:6379/0",
#     backend="redis://localhost:6379/0"
# )

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# OUTPUT_DIR = os.path.join(os.path.dirname(BASE_DIR), "outputs")


# @celery_app.task(bind=True)
# def process_pdf_task(self, pdf_path: str, operation: str):

#     try:
#         if operation == "extract":

#             self.update_state(
#                 state="PROGRESS",
#                 meta={"message": "Extracting tables...", "progress": 20}
#             )

#             excel_path = run_excel_pipeline(
#                 pdf_path,
#                 os.path.basename(pdf_path),
#                 lambda f, s, m, p, **k:
#                     self.update_state(
#                         state="PROGRESS",
#                         meta={"message": m, "progress": p}
#                     )
#             )

#             return {
#                 "status": "completed",
#                 "excel_file": os.path.basename(excel_path)
#             }

#         elif operation == "chat":

#             self.update_state(
#                 state="PROGRESS",
#                 meta={"message": "Indexing document...", "progress": 40}
#             )

#             index_pdf(pdf_path)

#             return {
#                 "status": "completed",
#                 "rag_ready": True
#             }

#     except Exception as e:
#         self.update_state(
#             state="FAILURE",
#             meta={"error": str(e)}
#         )
#         raise e




from celery import Celery
import os

from backend.excel_pipeline import run_excel_pipeline
from backend.rag_system import index_pdf

# Redis broker + backend
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(bind=True)
def process_pdf_task(self, pdf_path: str):
    try:
        filename = os.path.basename(pdf_path)

        # -----------------------------
        # Step 1: Excel Extraction
        # -----------------------------
        self.update_state(
            state="PROGRESS",
            meta={"message": "📊 Extracting financial tables...", "progress": 20}
        )

        excel_path = run_excel_pipeline(
            pdf_path,
            filename,
            lambda f, s, m, p, **k:
                self.update_state(
                    state="PROGRESS",
                    meta={"message": m, "progress": p}
                )
        )

        excel_filename = os.path.basename(excel_path)

        # -----------------------------
        # Step 2: RAG Indexing
        # -----------------------------
        self.update_state(
            state="PROGRESS",
            meta={"message": "🔍 Indexing for Q&A...", "progress": 80}
        )

        index_pdf(pdf_path)

        # -----------------------------
        # Done
        # -----------------------------
        return {
            "excel_file": excel_filename,
            "download_url": f"/outputs/{excel_filename}",
            "message": "✅ All processing complete!"
        }

    except Exception as e:
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise e
