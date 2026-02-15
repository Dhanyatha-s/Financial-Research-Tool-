# # app.py
# import streamlit as st
# import tempfile
# import threading
# import time
# import os
# from backend.excel_pipeline import run_excel_pipeline

# st.set_page_config(page_title="Financial PDF AI", layout="wide")
# st.title("📊 Financial Statement Extractor AI")
# st.caption("Upload a financial PDF → Get structured Excel output")

# # -----------------------------
# # Initialize session state
# # -----------------------------
# for key, default in {
#     "messages": [],
#     "processing": False,
#     "progress": 0,
#     "status_text": "",
#     "excel_file": None,
#     "thread_result": None
# }.items():
#     if key not in st.session_state:
#         st.session_state[key] = default

# # -----------------------------
# # Display previous messages
# # -----------------------------
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # -----------------------------
# # Upload PDF
# # -----------------------------
# uploaded_file = st.file_uploader("Upload Financial PDF", type=["pdf"])

# if uploaded_file and not st.session_state.processing:
#     st.session_state.messages.append({
#         "role": "user",
#         "content": f"📄 Uploaded: {uploaded_file.name}"
#     })
#     st.session_state.processing = True
#     st.session_state.progress = 10
#     st.session_state.status_text = "📥 Saving uploaded file..."

#     # Save uploaded file
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#         tmp_file.write(uploaded_file.read())
#         temp_pdf_path = tmp_file.name

#     # Thread-safe result container
#     st.session_state.thread_result = {
#         "finished": False,
#         "excel_path": None,
#         "messages": []
#     }

#     # -----------------------------
#     # Status callback
#     # -----------------------------
#     def status_callback(filename, stage, message, percent, error=None):
#         st.session_state.thread_result["messages"].append(message)
#         st.session_state.thread_result["progress"] = percent
#         st.session_state.thread_result["status_text"] = message

#     # -----------------------------
#     # Background thread
#     # -----------------------------
#     def process_pdf():
#         try:
#             excel_path = run_excel_pipeline(temp_pdf_path, uploaded_file.name, status_callback)
#             st.session_state.thread_result["excel_path"] = excel_path
#             st.session_state.thread_result["messages"].append("✅ Processing complete!")
#         except Exception as e:
#             st.session_state.thread_result["messages"].append(f"❌ Error: {str(e)}")
#         finally:
#             st.session_state.thread_result["finished"] = True

#     threading.Thread(target=process_pdf, daemon=True).start()

# # -----------------------------
# # Real-time updates
# # -----------------------------
# if st.session_state.processing:
#     progress_bar = st.progress(0)
#     status_placeholder = st.empty()

#     displayed_messages = set()
#     while not st.session_state.thread_result.get("finished", False):
#         # Update progress bar
#         progress = st.session_state.thread_result.get("progress", st.session_state.progress)
#         progress_bar.progress(progress)

#         # Update status text
#         status_text = st.session_state.thread_result.get("status_text", "")
#         status_placeholder.markdown(status_text)

#         # Display new messages
#         for msg in st.session_state.thread_result.get("messages", []):
#             if msg not in displayed_messages:
#                 displayed_messages.add(msg)
#                 st.session_state.messages.append({"role": "assistant", "content": msg})
#                 with st.chat_message("assistant"):
#                     st.markdown(msg)

#         time.sleep(0.3)  # small delay to avoid hogging CPU

#     # Final update
#     st.session_state.processing = False
#     progress_bar.progress(100)
#     status_placeholder.markdown("✅ Finished processing.")

# # -----------------------------
# # Downloadable Excel
# # -----------------------------
# excel_file = st.session_state.thread_result.get("excel_path") if st.session_state.thread_result else None
# if excel_file and os.path.exists(excel_file):
#     with open(excel_file, "rb") as f:
#         st.download_button(
#             "⬇ Download Excel File",
#             f,
#             file_name=os.path.basename(excel_file),
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )


import os
import streamlit as st
from backend.excel_pipeline import run_excel_pipeline

st.set_page_config(page_title="PDF to Excel", layout="wide")

st.title("📄 PDF Financial Extractor")

uploaded_file = st.file_uploader("Upload a financial PDF", type=["pdf"])

if uploaded_file:
    st.info("Processing your PDF, please wait...")
    
    # Save uploaded file to a temporary location
    temp_pdf_path = os.path.join("temp", uploaded_file.name)
    os.makedirs("temp", exist_ok=True)
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # Run the pipeline synchronously
        excel_path = run_excel_pipeline(temp_pdf_path, uploaded_file.name)

        st.success("✅ Excel generated successfully!")

        # Provide download button
        with open(excel_path, "rb") as f:
            st.download_button(
                label="⬇ Download Excel",
                data=f,
                file_name=os.path.basename(excel_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
