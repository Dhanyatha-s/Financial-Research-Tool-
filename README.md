# Financial-Research-Tool
-------------------------------
### PROJECT DEMO
-------------------------------

https://github.com/user-attachments/assets/9e6d7a29-b507-4cc6-ad34-7b3049ce3a4d


# 📊 Financial Documents Research Tool

**Research Platform: System Design & Execution Plan**

**Author:** Dhanyatha S  
**Date:** 06 Feb 2026  

---

# 📌 Problem Statement

Build a **research platform** that manages and extracts insights from large volumes of **unstructured financial documents**, including:

- Research papers
- Financial reports
- Corporate filings
- PDFs in mixed formats

The platform should allow users to:

- Organize and explore documents
- Extract insights from large datasets
- Generate dashboards
- Perform intelligent search
- Ask AI-based questions on documents

---

# 🏗️ Section 1: System Structure & Data Flow

## System Architecture

![System Architecture](https://github.com/user-attachments/assets/821bc68e-2256-42a4-a217-2ff6aacdf966)

**Fig 1: System Architecture**

### Ingestion Layer
Responsible for handling uploaded files.

Functions:
- Validate uploads
- Extract metadata
- Store raw files in **AWS S3**
- Queue background processing tasks

---

### Job Queue

Uses **Celery + Redis** for asynchronous execution.

Benefits:
- Prevents HTTP timeouts
- Enables parallel document processing
- Supports retries for failed jobs

---

### Processing Pipeline

A **4-stage pipeline** processes documents:

1️⃣ **Parsing**  
Extract text using `PyPDF2` / `pdfplumber`

2️⃣ **OCR**  
Extract text from scanned PDFs using  
AWS Textract or Tesseract

3️⃣ **Chunking**  
Split documents into **512 token chunks**

4️⃣ **Embedding**  
Generate embeddings for semantic search

---

### Storage Layer

| Storage | Purpose |
|------|------|
| **AWS S3** | Raw document storage |
| **PostgreSQL** | Metadata & extracted text |
| **Pinecone** | Vector embeddings |
| **Elasticsearch** | Full-text search |

---

### API & Retrieval

Backend built with **FastAPI** provides:

- Hybrid search
- AI Q&A
- Summarization
- APIs for frontend

Frontend built with **React** consumes these APIs.

---

### Data Flow
Upload
↓
S3 Storage
↓
Celery Job Queue
↓
4-Stage Processing Pipeline
↓
Multi-Database Storage
↓
Hybrid Search
↓
LLM Processing
↓
User Interface


---

# ⚙️ Section 2: Key System Design Decisions

## 1️⃣ Async Batch Processing

Documents are processed **asynchronously using Celery** instead of synchronous APIs.

Advantages:

- Avoids request timeouts
- Enables horizontal scaling
- Automatic retry support

---

## 2️⃣ Hybrid Search (Keyword + Semantic)

Combines:

- **Elasticsearch → Keyword search**
- **Pinecone → Semantic vector search**

### Why Hybrid?

| Method | Limitation |
|------|------|
Vector Search | Misses exact product names & acronyms |
Keyword Search | Misses conceptual queries |

Hybrid search provides **better recall and precision**.

---

## 3️⃣ Multi-Database Tiered Storage

Instead of a single database, each storage layer serves a purpose.

Hot storage:
- Frequently accessed embeddings

Cold storage:
- Rarely accessed documents moved to **S3 Glacier**

💡 Result: **Up to 80% storage cost reduction**

---

### Avoided Approach

❌ Pure LLM-based retrieval for every query

Reasons:

- Expensive
- High latency
- Risk of hallucinations

---

# 🧰 Section 3: Tech Stack

## Storage

- AWS S3 (Standard + Glacier)
- PostgreSQL 15 + pgvector
- Pinecone Vector DB
- Elasticsearch 8

---

## Processing

- Python 3.11
- PyPDF2 / pdfplumber
- AWS Textract / Tesseract OCR
- Celery 5.3
- Redis 7

Embeddings:

- OpenAI `text-embedding-3-small`
- HuggingFace `sentence-transformers`
- `all-MiniLM-L6-v2`

---

## Backend

- FastAPI
- Redis caching

---

## Frontend

- React + TypeScript
- TanStack Query
- Plotly.js (dashboards)

---

# 🤖 Section 4: AI Usage Strategy

## Applied AI

### Semantic Search
Query embeddings used for conceptual similarity search.

### Q&A with Citation
AI models (e.g. GPT-4) generate answers from retrieved document chunks.

### Summarization
LLMs generate:

- Executive summaries
- Document summaries

---

## Avoided AI Use

| Task | Reason |
|----|----|
Structured extraction | Regex/parsers are cheaper & deterministic |
Filtering | Databases perform faster |
UI logic | Avoid latency |

---

# 🚀 Section 5: Execution Plan

## Phase 1 — MVP (Weeks 1–4)

Goals:

- Single document upload
- Basic PDF extraction
- S3 + PostgreSQL storage
- SQL search
- Minimal UI

Purpose:
Validate ingestion pipeline.

---

## Phase 2 — AI Intelligence (Weeks 5–10)

Features:

- Batch document uploads
- Async processing with Celery
- Embedding generation
- Pinecone vector search
- Hybrid search
- AI question answering

Target:

Process **100+ company documents**

---

## Phase 3 — Production (Weeks 11–16)

Features:

- Full async architecture
- Notifications
- Analytics dashboards
- Authentication
- Role-based access control
- Saved searches
- Monitoring & logging

Target:

- **20 users**
- **1,000+ companies' documents**

---

# 📈 Section 6: Scaling & Failure Points

## Risk 1: Bulk Upload Bottleneck

Problem:
Large uploads may overwhelm Celery workers.

Mitigation:

- Horizontal scaling
- Kubernetes worker orchestration
- Intelligent job prioritization

---

## Risk 2: Vector Database Latency

Problem:
Beyond **10M vectors**, search latency increases.

Mitigation:

- Namespace sharding by company
- Metadata filtering before vector search

---

## Risk 3: Storage Cost Explosion

Problem:
Datasets exceeding **10TB** become expensive.

Mitigation:

- S3 Glacier cold storage
- Embedding compression
- Tiered storage strategy

---

# 💰 Section 7: Cost Estimation

## Infrastructure Cost

| Scenario | Dataset Size | Estimated Cost |
|------|------|------|
1,000 Companies | 2.97 TB | $1,002 / month |
3,000 Companies | 8.91 TB | $2,337 / month |
5,000 Companies | 14.85 TB | $3,797 / month |

---

# 💡 $400 Budget Constraint Architecture

Low-cost alternative setup:

| Component | Replacement |
|------|------|
AWS servers | Hetzner AX102 ($200/month) |
S3 storage | Backblaze B2 ($12/month) |
Pinecone | Self-hosted pgvector |
Elasticsearch | Typesense |

Additional strategies:

- Open-source embeddings
- GPT-4 only for paid users
- Daily batch processing
- No redundancy (daily backups)

---

## Revised Cost

Estimated monthly cost:
~ $343 / month


---

# ⚖️ Tradeoffs

| Category | Impact |
|------|------|
Performance | 2.5s latency vs <1s |
Concurrency | 20-30 users vs 100+ |
Reliability | Single point of failure |
Features | Limited AI for free tier |
Scalability | Maximum ~5K companies |

---

# 📊 Monetization Strategy

| Plan | Features |
|------|------|
Free | Keyword search |
Standard ($20/month) | Semantic search + 5 queries/day |
Premium ($50/month) | 50 AI queries/day |

Additional strategies:

- Aggressive caching
- Database indexing
- Docker portability
- S3-compatible APIs

---

# 📉 Startup Strategy

Treat this system as a **6–12 month bootstrap phase**.

Goals:

- Validate product-market fit
- Scale infrastructure after reaching **$1K MRR**
- Keep early experimentation costs low

---

# 📄 Full Report

For the **comprehensive structured research report**,  
see the detailed documentation linked in the repository.
