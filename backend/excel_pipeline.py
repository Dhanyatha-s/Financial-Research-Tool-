# import os
# from backend.pipeline import mainPipeline  # we will wrap your current main.py logic

# def run_excel_pipeline(pdf_path: str):
#     """
#     Run the existing Excel extraction + processing.
#     """
#     if not os.path.exists(pdf_path):
#         print(f"❌ PDF not found: {pdf_path}")
#         return

#     mainPipeline(pdf_path)  # refactor main.py to have main_process(pdf_path) function


# import os
# from backend.pipeline import mainPipeline

# def run_excel_pipeline(pdf_path: str):
#     """
#     Run the full Excel extraction and processing pipeline.
#     Returns absolute path to the generated Excel file.
#     """
#     if not os.path.exists(pdf_path):
#         print(f"❌ PDF not found: {pdf_path}")
#         return None

#     return mainPipeline(pdf_path)


# excel_pipeline.py
import os
from .pipeline import mainPipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


def run_excel_pipeline(pdf_path: str, filename: str = None, status_callback=None):
    """
    Wrapper for the main pipeline with optional status updates
    """
    try:
        if status_callback and filename:
            status_callback(filename, "processing", "⚙️ Running financial extraction pipeline...", 40)
        
        excel_path = mainPipeline(pdf_path, status_callback, filename)
        
        if status_callback and filename:
            status_callback(filename, "excel_generated", "✅ Excel file generated successfully", 65)
        
        return excel_path
    except Exception as e:
        if status_callback and filename:
            status_callback(filename, "error", f"❌ Pipeline error: {str(e)}", 0, str(e))
        raise