# # rag_system.py
# import os
# from langchain.document_loaders.pdf import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import Chroma
# from langchain.chains import RetrievalQA

# # -----------------------------
# # Your Groq LLM
# # -----------------------------
# try:
#     from groq_sdk import ChatGroq  # Make sure your SDK path is correct
# except ImportError:
#     raise ImportError("ChatGroq SDK not found. Ensure Groq SDK is downloaded and available.")

# # -----------------------------
# # Embeddings (using Sentence Transformers)
# # -----------------------------
# from langchain.embeddings import HuggingFaceEmbeddings

# # Example: MiniLM model for fast, local embeddings
# embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# # -----------------------------
# # Global Constants
# # -----------------------------
# CHROMA_DIR = "chroma_db"
# os.makedirs(CHROMA_DIR, exist_ok=True)

# # In-memory mapping: pdf_name -> retriever
# retrievers = {}

# # Groq LLM instance
# api_key = os.getenv("GROQ_API_KEY")
# if not api_key:
#     raise ValueError("GROQ_API_KEY not found")

# llm = ChatGroq(
#     model="llama-3.1-8b-instant",
#     groq_api_key=api_key,
#     temperature=0
# )

# # -----------------------------
# # Step 1: Index PDF for RAG
# # -----------------------------
# def index_pdf(pdf_path: str):
#     """
#     Load a PDF, split into chunks, create a Chroma vector store,
#     and store a retriever in memory for RAG queries.
#     """
#     if not os.path.exists(pdf_path):
#         raise FileNotFoundError(f"PDF not found: {pdf_path}")

#     # Load PDF
#     loader = PyPDFLoader(pdf_path)
#     documents = loader.load()

#     # Split into manageable chunks
#     splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#     chunks = splitter.split_documents(documents)

#     # Create Chroma vector store using SentenceTransformer embeddings
#     db = Chroma.from_documents(
#         chunks,
#         embedding=embedding_model,
#         persist_directory=CHROMA_DIR
#     )
#     db.persist()

#     # Create retriever for similarity search
#     retrievers[os.path.basename(pdf_path)] = db.as_retriever(
#         search_type="similarity",
#         search_kwargs={"k": 3}
#     )

# # -----------------------------
# # Step 2: Query PDF using RAG
# # -----------------------------
# def get_answer(user_query: str, pdf_name: str):
#     """
#     Retrieve an answer from indexed PDF using RAG + Groq LLM
#     """
#     if not pdf_name or pdf_name not in retrievers:
#         return "❌ PDF not indexed yet. Please upload first."

#     retriever = retrievers[pdf_name]

#     # Use RetrievalQA with Groq LLM
#     qa = RetrievalQA.from_chain_type(
#         llm=llm,
#         retriever=retriever,
#         chain_type="stuff"  # simple chain; can switch to "map_reduce" later
#     )

#     try:
#         answer = qa.run(user_query)
#     except Exception as e:
#         answer = f"❌ Error during RAG query: {str(e)}"

#     return answer


# rag_system.py
# import os
# from langchain.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import Chroma
# from langchain.chains import RetrievalQA

# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.llms import HuggingFacePipeline
# from transformers import pipeline
# embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# # -----------------------------
# # Offline LLM (HuggingFace)
# # -----------------------------
# from langchain.llms import HuggingFacePipeline
# from transformers import pipeline

# # Small FLAN-T5 model for local inference
# flan_pipeline = pipeline(
#     "text2text-generation",
#     model="google/flan-t5-small",
#     max_length=512
# )
# llm = HuggingFacePipeline(pipeline=flan_pipeline)

# # -----------------------------
# # Global Constants
# # -----------------------------
# CHROMA_DIR = "chroma_db"
# os.makedirs(CHROMA_DIR, exist_ok=True)

# # In-memory mapping: pdf_name -> retriever
# retrievers = {}

# # -----------------------------
# # Step 1: Index PDF for RAG
# # -----------------------------
# def index_pdf(pdf_path: str):
#     if not os.path.exists(pdf_path):
#         raise FileNotFoundError(f"PDF not found: {pdf_path}")

#     # Load PDF
#     loader = PyPDFLoader(pdf_path)
#     documents = loader.load()

#     # Split into chunks
#     splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#     chunks = splitter.split_documents(documents)

#     # Create Chroma vector store with local embeddings
#     db = Chroma.from_documents(
#         chunks,
#         embedding=embedding_model,
#         persist_directory=CHROMA_DIR
#     )
#     db.persist()

#     # Store retriever
#     retrievers[os.path.basename(pdf_path)] = db.as_retriever(
#         search_type="similarity",
#         search_kwargs={"k": 3}
#     )

# # -----------------------------
# # Step 2: Query PDF using RAG
# # -----------------------------
# def get_answer(user_query: str, pdf_name: str):
#     if not pdf_name or pdf_name not in retrievers:
#         return "❌ PDF not indexed yet. Please upload first."

#     retriever = retrievers[pdf_name]

#     # Use RetrievalQA with local HuggingFace LLM
#     qa = RetrievalQA.from_chain_type(
#         llm=llm,
#         retriever=retriever,
#         chain_type="stuff"
#     )

#     try:
#         answer = qa.run(user_query)
#     except Exception as e:
#         answer = f"❌ Error during RAG query: {str(e)}"

#     return answer


import os
import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import torch
import pickle

# OCR imports
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from tqdm import tqdm

# -----------------------------
# 0. Device setup
# -----------------------------
device_name = "cuda" if torch.cuda.is_available() else "cpu"
device_id = 0 if device_name == "cuda" else -1
print(f"Using device: {device_name}")
if device_name == "cuda":
    print(torch.cuda.get_device_name(0))

# -----------------------------
# 1. Load Models
# -----------------------------
embedder = SentenceTransformer('all-MiniLM-L6-v2', device=device_name)

llm_pipeline = pipeline(
    "text2text-generation",
    model="google/flan-t5-small",
    max_new_tokens=128,  # shorter = faster
    temperature=0.1,
    top_p=0.9,
    do_sample=True,
    device=device_id
)

# -----------------------------
# 2. Knowledge Base
# -----------------------------
knowledge_base = {}  # { pdf_name: {"index": faiss_index, "chunks": [str]} }

# -----------------------------
# 3. Text Splitter
# -----------------------------
def split_text(text: str, chunk_size=500, overlap=50):
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks

# -----------------------------
# 4. OCR for scanned PDF
# -----------------------------
def extract_text_from_scanned_pdf(pdf_path):
    """Convert PDF pages to images and run OCR."""
    pages = convert_from_path(pdf_path)
    full_text = ""
    for page in tqdm(pages, desc="OCR pages"):
        text = pytesseract.image_to_string(page)
        full_text += text + "\n"
    return full_text

# -----------------------------
# 5. Index PDF
# -----------------------------
def index_pdf(pdf_path: str, save_pickle=True):
    if not os.path.exists(pdf_path):
        return "❌ PDF not found."

    pdf_name = os.path.basename(pdf_path)

    if pdf_name in knowledge_base:
        print(f"⚡ Already indexed: {pdf_name}")
        return pdf_name

    full_text = ""

    # Try extracting normal text first
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        # If no text found, use OCR
        if not full_text.strip():
            print("⚡ PDF is scanned. Using OCR...")
            full_text = extract_text_from_scanned_pdf(pdf_path)

    except Exception as e:
        return f"❌ Error reading PDF: {str(e)}"

    if not full_text.strip():
        return "❌ No text found in PDF after OCR."

    # Split text into chunks
    chunks = split_text(full_text, chunk_size=500, overlap=50)

    # Embed chunks in batches
    embeddings = embedder.encode(
        chunks,
        convert_to_numpy=True,
        show_progress_bar=True,
        batch_size=64
    )

    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Store in knowledge base
    knowledge_base[pdf_name] = {"index": index, "chunks": chunks}
    print(f"✅ Indexed {pdf_name} ({len(chunks)} chunks).")

    # Optionally save pickle
    if save_pickle:
        with open("knowledge_base.pkl", "wb") as f:
            pickle.dump(knowledge_base, f)

    return pdf_name

# -----------------------------
# 6. Load knowledge base
# -----------------------------
def load_knowledge_base(pickle_path="knowledge_base.pkl"):
    global knowledge_base
    if os.path.exists(pickle_path):
        with open(pickle_path, "rb") as f:
            knowledge_base = pickle.load(f)
        print(f"📦 Knowledge base loaded: {len(knowledge_base)} PDFs")
    else:
        print("⚠️ No pre-saved knowledge base found.")

# -----------------------------
# 7. Query PDF
# -----------------------------
def get_answer(user_query: str, pdf_name: str, top_k=3):
    if pdf_name not in knowledge_base:
        return "❌ PDF not indexed yet."

    data = knowledge_base[pdf_name]
    index = data["index"]
    chunks = data["chunks"]

    # Embed query
    query_embedding = embedder.encode([user_query], convert_to_numpy=True)

    # Retrieve top_k chunks
    distances, indices = index.search(query_embedding, k=top_k)
    retrieved_chunks = [chunks[i] for i in indices[0] if i < len(chunks)]
    context_str = "\n\n".join(retrieved_chunks)

    # Build prompt
    prompt = (
        f"Use the following context to answer the question.\n\n"
        f"Context:\n{context_str}\n\n"
        f"Question: {user_query}\nAnswer:"
    )

    # Generate answer
    response = llm_pipeline(prompt)
    answer = response[0].get("generated_text", "❌ LLM failed to generate an answer.")
    return answer
