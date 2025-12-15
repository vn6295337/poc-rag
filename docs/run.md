# RAG PoC Operations Runbook

> **Version**: 1.0
> **Last Updated**: December 7, 2025
> **Project**: RAG-document-assistant
> **Focus**: Setup, configuration, and deployment instructions

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Setup](#local-setup)
3. [Configuration](#configuration)
4. [Running Ingestion](#running-ingestion)
5. [Running the Application](#running-the-application)
6. [Running Tests](#running-tests)
7. [Deployment](#deployment)
8. [Monitoring & Logging](#monitoring--logging)
9. [Troubleshooting](#troubleshooting)
10. [Common Operations](#common-operations)
11. [Performance Tuning](#performance-tuning)
12. [Backup & Recovery](#backup--recovery)

---

## Prerequisites

### Document Purpose

This document provides operational guidance for setting up, configuring, deploying, and maintaining the RAG system. It is intended for DevOps engineers, system administrators, and operators who need to deploy and maintain the system.

For architectural details, see [Architecture](architecture.md). For implementation details, see [Implementation Guide](implement.md).

### System Requirements

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| **RAM** | 2GB | 4GB | sentence-transformers needs ~800MB |
| **CPU** | 2 cores | 4 cores | PyTorch CPU-only inference |
| **Disk** | 500MB | 1GB | Models + data + dependencies |
| **Python** | 3.11+ | 3.11.x | 3.13 has dependency issues |
| **Internet** | Required | Broadband | Pinecone + LLM APIs |

### Required Accounts & API Keys

1. **Pinecone** (Required)
   - Sign up: https://www.pinecone.io/
   - Create serverless index: `rag-semantic-384`
   - Dimension: 384, Metric: cosine
   - Get API key from dashboard

2. **At least ONE LLM Provider** (Required)

   **Option A: Gemini** (Recommended)
   - Sign up: https://ai.google.dev/
   - Free tier: 15 RPM
   - Best quality-to-speed ratio

   **Option B: Groq**
   - Sign up: https://console.groq.com/
   - Free tier: 30 RPM
   - Fastest inference (~1s)

   **Option C: OpenRouter**
   - Sign up: https://openrouter.ai/
   - Free models available
   - Fallback option

3. **GitHub** (Optional - for deployment)
   - Required for HF Spaces deployment
   - Required for version control

4. **Hugging Face** (Optional - for deployment)
   - Sign up: https://huggingface.co/
   - Free tier: 16GB RAM
   - Best for ML app hosting

### Development Tools

```bash
# Required
python3.11 or higher
pip (latest version)
git

# Recommended
virtualenv or venv
curl (for API testing)
jq (for JSON parsing)
```

---

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/vn6295337/RAG-document-assistant.git
cd RAG-document-assistant
```

### 2. Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify Python version
python --version
# Expected: Python 3.11.x
```

### 3. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "pinecone|streamlit|sentence|torch"

# Expected output:
# pinecone         5.0.1
# streamlit        1.40.0
# sentence-transformers  2.2.2
# torch            2.1.0
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or vim, code, etc.
```

**`.env` template**:
```bash
# Pinecone (Required)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=rag-semantic-384

# LLM Providers (at least one required)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free
```

### 5. Verify Setup

```bash
# Test Pinecone connection
python -c "
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
indexes = pc.list_indexes()
print(f' Pinecone connected: {len(indexes)} indexes found')
"

# Test sentence-transformers
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
emb = model.encode('test')
print(f' sentence-transformers loaded: {len(emb)}-dim embeddings')
"

# Expected output:
#  Pinecone connected: X indexes found
#  sentence-transformers loaded: 384-dim embeddings
```

---

## Configuration

### Environment Variables Reference

#### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `PINECONE_API_KEY` | Pinecone API authentication | `a1b2c3...` |

#### Required (at least one)

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | - |
| `GROQ_API_KEY` | Groq API key | - |
| `OPENROUTER_API_KEY` | OpenRouter API key | - |

#### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `PINECONE_INDEX_NAME` | Pinecone index name | `rag-semantic-384` |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.5-flash` |
| `GROQ_MODEL` | Groq model name | `llama-3.1-8b-instant` |
| `OPENROUTER_MODEL` | OpenRouter model | `mistralai/mistral-7b-instruct:free` |

### Configuration by Platform

#### Local Development

**Method**: `.env` file
```bash
# 1. Create .env from template
cp .env.example .env

# 2. Edit .env
nano .env

# 3. Load automatically via python-dotenv
# (handled by src/config.py)
```

#### Streamlit Cloud

**Method**: `st.secrets` TOML file

1. Go to Streamlit Cloud dashboard
2. Settings ' Secrets
3. Add TOML format:
   ```toml
   PINECONE_API_KEY = "your_key"
   GEMINI_API_KEY = "your_key"
   PINECONE_INDEX_NAME = "rag-semantic-384"
   ```

#### Hugging Face Spaces

**Method**: Environment variables via UI

1. Go to HF Space settings
2. Repository Secrets ' New Secret
3. Add each variable:
   - Name: `PINECONE_API_KEY`
   - Value: `your_key`

#### Docker / Cloud Run

**Method**: Environment variables

```bash
# Cloud Run deployment
gcloud run deploy rag-poc \
  --set-env-vars "PINECONE_API_KEY=your_key" \
  --set-env-vars "GEMINI_API_KEY=your_key" \
  --region us-central1
```

**Docker run**:
```bash
docker run -e PINECONE_API_KEY=your_key \
           -e GEMINI_API_KEY=your_key \
           rag-document-assistant:latest
```

---

## Running Ingestion

### Step 1: Prepare Documents

```bash
# Place markdown files in sample_docs/
ls sample_docs/
# Example output:
# EU_GDPR_Data_Protection_Regulation.md
# HIPAA_Privacy_Rule.md
# ...
```

### Step 2: Test Document Loading

```bash
# Test document loader
python src/ingestion/load_docs.py sample_docs/

# Expected output:
# FILENAME                                 STATUS         CHARS    WORDS
# 
# EU_GDPR_Data_Protection_Regulation.md   OK             15234     2154
# ...
# Total files: 5  OK: 5  Skipped: 0
```

### Step 3: Run Full Ingestion Pipeline

```bash
# Run complete ingestion
python src/scripts/run_ingestion.py

# Expected output:
# Loading documents from sample_docs/...
#  Loaded 5 documents
#  Generated 44 chunks
#  Embedded 44 chunks (384-dim)
#  Upserted to Pinecone index: rag-semantic-384
#  Saved to data/chunks_semantic.jsonl
# Ingestion complete!
```

### Step 4: Verify Pinecone Index

```bash
# Check index stats
python -c "
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index_name = os.getenv('PINECONE_INDEX_NAME', 'rag-semantic-384')
idx_meta = pc.describe_index(index_name)
host = getattr(idx_meta, 'host', None) or idx_meta.get('host')
index = pc.Index(host=host)
stats = index.describe_index_stats()
print(f'Index: {index_name}')
print(f'Vectors: {stats.get(\"total_vector_count\", \"N/A\")}')
print(f'Dimension: {stats.get(\"dimension\", \"N/A\")}')
"

# Expected output:
# Index: rag-semantic-384
# Vectors: 44
# Dimension: 384
```

### Step 5: Test Retrieval

```bash
# Test semantic search
python tests/test_retrieval.py "what is GDPR"

# Expected output:
# Query: "what is GDPR"
# 
# Top 3 Results:
# 1. EU_GDPR_Data_Protection_Regulation.md::0 (Score: 0.5403)
# 2. EU_GDPR_Data_Protection_Regulation.md::7 (Score: 0.4082)
# 3. EU_GDPR_Data_Protection_Regulation.md::6 (Score: 0.3768)
```

---

## Running the Application

### Local Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run Streamlit app (local UI)
streamlit run src/ui/app.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
# Network URL: http://192.168.1.x:8501
```

**Using the UI**:
1. Open http://localhost:8501
2. Enter query: "what is GDPR"
3. Click "Run Query"
4. View:
   - Answer (with citations)
   - Citations (ID + score)
   - Debug view (JSON response)

### Production (HF Spaces)

**Already deployed**: https://huggingface.co/spaces/vn6295337/rag-poc

**To redeploy**:
```bash
# 1. Clone HF Space
git clone https://huggingface.co/spaces/vn6295337/rag-poc hf-rag-poc
cd hf-rag-poc

# 2. Copy updated files
cp ../RAG-document-assistant/app.py .
cp ../RAG-document-assistant/src/*.py src/
cp ../RAG-document-assistant/retrieval/*.py retrieval/
cp ../RAG-document-assistant/ingestion/*.py ingestion/

# 3. Commit and push
git add .
git commit -m "Update: [describe changes]"
git push

# 4. HF Spaces auto-rebuilds (takes ~2-5 minutes)
```

### Background Service

```bash
# Run as background service with nohup
nohup streamlit run src/ui/app.py \
  --server.port=8501 \
  --server.headless=true \
  > streamlit.log 2>&1 &

# Check logs
tail -f streamlit.log

# Stop service
pkill -f "streamlit run"
```

---

## Running Tests

### 1. End-to-End Pipeline Test

```bash
# Run full RAG pipeline test
python test_rag_pipeline.py

# Expected output:
# ============================================================
# Testing RAG Pipeline: what is GDPR
# ============================================================
#
#  ANSWER:
# The General Data Protection Regulation (GDPR) is...
#
# = CITATIONS:
# 1. EU_GDPR_Data_Protection_Regulation.md::0 (Score: 0.5403)
# 2. EU_GDPR_Data_Protection_Regulation.md::7 (Score: 0.4082)
# ...
#  Pipeline test successful
```

### 2. Retrieval-Only Test

```bash
# Test retrieval with custom query
python retrieval/test_retrieval.py "how does data protection work"

# Output: Top-K chunks with similarity scores
```

### 3. Ingestion Test

```bash
# Test document loading only
python src/ingestion/load_docs.py sample_docs/

# Test chunking only
python -c "
from ingestion.chunker import chunk_text
text = 'Sample text ' * 100
chunks = chunk_text(text, max_tokens=50, overlap=10)
print(f'Generated {len(chunks)} chunks')
"

# Test embedding only
python -c "
from ingestion.embeddings import get_embedding
emb = get_embedding('test', provider='sentence-transformers')
print(f'Embedding dimension: {len(emb)}')
"
```

### 4. Manual API Testing

```bash
# Test Gemini API directly
curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "contents": [{"parts": [{"text": "What is GDPR in one sentence?"}]}],
    "generationConfig": {"temperature": 0.0, "maxOutputTokens": 100}
  }' | jq '.candidates[0].content.parts[0].text'

# Expected: Brief GDPR description
```

---

## Deployment

### Deployment Options Comparison

| Platform | RAM | Cost | Setup Time | Best For |
|----------|-----|------|------------|----------|
| **Hugging Face Spaces** | 16GB | $0 | 15 min |  Recommended (ML apps) |
| **Cloud Run** | 2-8GB | Pay-per-use | 30 min | Production scale |
| **Streamlit Cloud** | 1GB | $0 | 20 min | Simple Streamlit apps |
| **Render** | 512MB | $7/mo | 15 min | Not recommended (OOM) |
| **Railway** | 512MB | Pay-per-use | 15 min | Not recommended (OOM) |

### Hugging Face Spaces Deployment (Recommended)

**Prerequisites**:
- Hugging Face account
- Git installed
- Hugging Face CLI (optional)

**Steps**:

1. **Create New Space**
   - Go to https://huggingface.co/new-space
   - Name: `rag-poc`
   - SDK: Docker
   - License: MIT
   - Visibility: Public

2. **Clone Space Repository**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/rag-poc hf-rag-poc
   cd hf-rag-poc
   ```

3. **Copy Project Files**
   ```bash
   # From your local RAG-document-assistant directory
   cp /path/to/RAG-document-assistant/app.py .
   cp /path/to/RAG-document-assistant/Dockerfile .
   cp /path/to/RAG-document-assistant/start-app.sh .
   cp /path/to/RAG-document-assistant/requirements.txt .
   cp -r /path/to/RAG-document-assistant/src .
   cp -r /path/to/RAG-document-assistant/retrieval .
   cp -r /path/to/RAG-document-assistant/ingestion .
   cp -r /path/to/RAG-document-assistant/data .
   ```

4. **Configure Secrets**
   - Go to Space Settings ' Repository Secrets
   - Add secrets:
     - `PINECONE_API_KEY`
     - `GEMINI_API_KEY` (or other LLM provider)
     - `PINECONE_INDEX_NAME` (optional: defaults to rag-semantic-384)

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "Initial deployment: RAG PoC with Streamlit"
   git push
   ```

6. **Wait for Build** (~2-5 minutes)
   - HF Spaces automatically builds Docker image
   - Check logs in "Logs" tab
   - Status changes to "Running" when ready

7. **Validate Deployment**
   - Open Space URL: `https://huggingface.co/spaces/YOUR_USERNAME/rag-poc`
   - Test query: "what is GDPR"
   - Verify answer and citations appear

**Troubleshooting**:
- Check logs for build errors
- Verify secrets are set correctly
- Ensure `start-app.sh` is executable: `chmod +x start-app.sh`

### Cloud Run Deployment

**Prerequisites**:
- GCP account with billing enabled
- `gcloud` CLI installed and authenticated
- Docker installed (optional - Cloud Build can build for you)

**Steps**:

1. **Enable APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

2. **Build Container**
   ```bash
   # Using Cloud Build (recommended)
   gcloud builds submit --tag gcr.io/PROJECT_ID/rag-poc

   # Or build locally and push
   docker build -t gcr.io/PROJECT_ID/rag-poc .
   docker push gcr.io/PROJECT_ID/rag-poc
   ```

3. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy rag-poc \
     --image gcr.io/PROJECT_ID/rag-poc \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "PINECONE_API_KEY=$PINECONE_API_KEY" \
     --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY" \
     --set-env-vars "PINECONE_INDEX_NAME=rag-semantic-384" \
     --memory 2Gi \
     --cpu 2 \
     --timeout 300
   ```

4. **Get Service URL**
   ```bash
   gcloud run services describe rag-poc \
     --region us-central1 \
     --format='value(status.url)'

   # Output: https://rag-poc-xxxxx-uc.a.run.app
   ```

5. **Test Deployment**
   ```bash
   curl https://rag-poc-xxxxx-uc.a.run.app
   ```

**Cost Estimation**:
- First 2 million requests/month: Free
- $0.40 per million requests after
- $0.00002400 per vCPU-second
- $0.00000250 per GiB-second

### Streamlit Cloud Deployment

**Prerequisites**:
- Streamlit Cloud account
- GitHub repository

**Steps**:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select repository: `your-username/RAG-document-assistant`
   - Main file path: `ui/app.py`
   - Click "Deploy"

3. **Configure Secrets**
   - App settings ' Secrets
   - Add TOML format:
     ```toml
     PINECONE_API_KEY = "your_key"
     GEMINI_API_KEY = "your_key"
     ```

4. **Wait for Deployment** (~2-3 minutes)

**Limitations**:
- 1GB RAM (may OOM with sentence-transformers)
- Limited CPU resources
- Not recommended for this project (use HF Spaces instead)

---

## Monitoring & Logging

### Application Logs

#### Local Development
```bash
# Streamlit logs to console
streamlit run src/ui/app.py

# View logs in terminal
# Errors appear with traceback
```

#### Hugging Face Spaces
```bash
# View logs in HF Spaces UI
# Go to Space ' Logs tab

# Example log entries:
# 2025-12-07 10:15:32 - INFO - Loading sentence-transformers model
# 2025-12-07 10:15:35 - INFO - Model loaded (384-dim)
# 2025-12-07 10:15:40 - INFO - Query: "what is GDPR"
# 2025-12-07 10:15:43 - INFO - Retrieved 3 chunks (top score: 0.5403)
# 2025-12-07 10:15:45 - INFO - LLM response received (provider: gemini)
```

#### Cloud Run
```bash
# View logs via gcloud
gcloud run services logs read rag-poc \
  --region us-central1 \
  --limit 50

# Stream logs in real-time
gcloud run services logs tail rag-poc \
  --region us-central1

# Filter by severity
gcloud run services logs read rag-poc \
  --region us-central1 \
  --log-filter="severity>=ERROR"
```

### Performance Metrics

#### Cold Start Monitoring

```bash
# Test cold start time
time curl -s https://your-deployment-url > /dev/null

# Expected:
# real    0m35.412s  (first request)
# real    0m3.821s   (subsequent requests)
```

#### Query Latency Breakdown

Add timing to `src/orchestrator.py`:
```python
import time

def orchestrate_query(query, top_k=3):
    t0 = time.time()

    # Retrieval
    chunks = query_pinecone(query, top_k)
    t1 = time.time()
    print(f"Retrieval: {t1-t0:.2f}s")

    # LLM
    llm_response = call_llm(prompt, context)
    t2 = time.time()
    print(f"LLM: {t2-t1:.2f}s")

    # Total
    print(f"Total: {t2-t0:.2f}s")
```

### Error Tracking

#### Add Custom Logging

```python
# src/orchestrator.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def orchestrate_query(query, top_k=3):
    logger.info(f"Query received: {query}")
    try:
        chunks = query_pinecone(query, top_k)
        logger.info(f"Retrieved {len(chunks)} chunks")
        # ...
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Symptom**:
```
ModuleNotFoundError: No module named 'src'
```

**Solution**:
```python
# Add to app.py (if not already present)
import sys
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
```

#### 2. Pinecone Connection Errors

**Symptom**:
```
PineconeException: API key is invalid
```

**Solution**:
```bash
# Verify API key
echo $PINECONE_API_KEY

# Test connection
python -c "
from pinecone import Pinecone
pc = Pinecone(api_key='YOUR_KEY')
print(pc.list_indexes())
"
```

#### 3. Out of Memory (OOM)

**Symptom**:
```
Killed
# or
MemoryError
```

**Solution**:
- Use platform with >2GB RAM (Hugging Face Spaces: 16GB)
- Reduce batch size in embeddings
- Clear model cache between runs

#### 4. Slow Cold Start

**Symptom**: First query takes >60s

**Root Cause**: sentence-transformers model loading (~300MB download)

**Solution**:
```python
# Pre-load model during startup
# src/orchestrator.py
from retrieval.retriever import _get_sentence_transformer_model

# Load model at import time
_get_sentence_transformer_model("all-MiniLM-L6-v2")
```

#### 5. LLM API Failures

**Symptom**:
```
gemini: 429 Too Many Requests
```

**Solution**:
- Multi-provider cascade handles this automatically
- Verify other providers are configured:
  ```bash
  echo $GROQ_API_KEY
  echo $OPENROUTER_API_KEY
  ```

### Debug Mode

#### Enable Detailed Logging

```bash
# Set environment variable
export DEBUG=1

# Or in .env
echo "DEBUG=1" >> .env
```

```python
# src/orchestrator.py
import os

DEBUG = os.getenv("DEBUG") == "1"

def orchestrate_query(query, top_k=3):
    if DEBUG:
        print(f"[DEBUG] Query: {query}")
        print(f"[DEBUG] Top-K: {top_k}")

    chunks = query_pinecone(query, top_k)

    if DEBUG:
        print(f"[DEBUG] Retrieved chunks:")
        for c in chunks:
            print(f"  - {c['id']} (score: {c['score']:.4f})")
```

---

## Common Operations

### 1. Add New Documents

```bash
# 1. Add markdown files to sample_docs/
cp new_document.md sample_docs/

# 2. Re-run ingestion
python src/scripts/run_ingestion.py

# 3. Verify new chunks
python -c "
import json
with open('data/chunks_semantic.jsonl') as f:
    chunks = [json.loads(line) for line in f]
print(f'Total chunks: {len(chunks)}')
"
```

### 2. Update LLM Provider

```bash
# Update .env with new API key
echo "GEMINI_API_KEY=new_key_here" >> .env

# Restart application
pkill -f streamlit
streamlit run src/ui/app.py
```

### 3. Switch Pinecone Index

```bash
# Create new index via Pinecone dashboard
# Update .env
echo "PINECONE_INDEX_NAME=new-index-name" >> .env

# Re-run ingestion to populate new index
python src/scripts/run_ingestion.py
```

### 4. Clear Model Cache

```bash
# Remove cached sentence-transformers model
rm -rf ~/.cache/torch/sentence_transformers/

# Next run will re-download model
python retrieval/test_retrieval.py "test query"
```

### 5. Export Query Results

```python
# Export to JSON file
import json
from src.orchestrator import orchestrate_query

result = orchestrate_query("what is GDPR")

with open("query_result.json", "w") as f:
    json.dump(result, f, indent=2)

print(" Saved to query_result.json")
```

---

## Performance Tuning

### 1. Optimize Embedding Generation

```python
# ingestion/embeddings.py
# Use batch encoding for better throughput

def batch_embed_chunks(chunks, batch_size=32):
    model = _get_sentence_transformer_model()

    # Process in batches
    embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        texts = [c["text"] for c in batch]
        batch_embs = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        embeddings.extend(batch_embs)

    return embeddings
```

### 2. Add Response Caching

```python
# src/orchestrator.py
from functools import lru_cache

@lru_cache(maxsize=100)
def orchestrate_query_cached(query, top_k=3):
    return orchestrate_query(query, top_k)
```

### 3. Reduce LLM Latency

```python
# src/llm_providers.py
# Use faster models or increase timeout

def _call_gemini(prompt, temperature, max_tokens, context):
    payload = {
        "generationConfig": {
            "temperature": 0.0,  # Faster generation
            "maxOutputTokens": 256,  # Reduce from 512
            "topP": 0.95,
            "topK": 40
        }
    }
```

### 4. Optimize Chunking

```python
# ingestion/chunker.py
# Increase chunk size to reduce total chunks

def chunk_text(text, max_tokens=500, overlap=100):
    # Larger chunks = fewer embeddings = faster retrieval
    # But may reduce answer precision
    ...
```

---

## Backup & Recovery

### 1. Backup Pinecone Index

```python
# Export all vectors from Pinecone
import json
from pinecone import Pinecone
import os

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "rag-semantic-384"
idx_meta = pc.describe_index(index_name)
host = idx_meta.host if hasattr(idx_meta, 'host') else idx_meta.get('host')
index = pc.Index(host=host)

# Fetch all vectors (use pagination for large indexes)
results = index.query(
    vector=[0] * 384,  # Dummy vector
    top_k=10000,  # Max
    include_metadata=True,
    include_values=True
)

# Save to file
with open("pinecone_backup.jsonl", "w") as f:
    for match in results.matches:
        f.write(json.dumps({
            "id": match.id,
            "values": match.values,
            "metadata": match.metadata
        }) + "\n")

print(f" Backed up {len(results.matches)} vectors")
```

### 2. Restore Pinecone Index

```python
# Restore from backup
import json
from pinecone import Pinecone

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(host="your-index-host")

with open("pinecone_backup.jsonl") as f:
    vectors = []
    for line in f:
        obj = json.loads(line)
        vectors.append({
            "id": obj["id"],
            "values": obj["values"],
            "metadata": obj["metadata"]
        })

    # Upsert in batches of 100
    for i in range(0, len(vectors), 100):
        batch = vectors[i:i+100]
        index.upsert(vectors=batch)

print(f" Restored {len(vectors)} vectors")
```

### 3. Backup Configuration

```bash
# Backup all environment variables
env | grep -E "PINECONE|GEMINI|GROQ|OPENROUTER" > .env.backup

# Restore
cat .env.backup >> .env
```

### 4. Backup Application State

```bash
# Create full backup
tar -czf rag-poc-backup-$(date +%Y%m%d).tar.gz \
  --exclude=venv \
  --exclude=.git \
  --exclude=__pycache__ \
  .

# Restore
tar -xzf rag-poc-backup-20251207.tar.gz
```

---

## Production Checklist

Before deploying to production:

- [ ] All API keys configured and tested
- [ ] Pinecone index created and populated
- [ ] sentence-transformers model downloaded
- [ ] At least 2 LLM providers configured
- [ ] Environment variables set correctly
- [ ] All tests passing (`test_rag_pipeline.py`)
- [ ] Deployment platform meets RAM requirements (>2GB)
- [ ] Secrets stored securely (not in code)
- [ ] Error handling tested (API failures, rate limits)
- [ ] Cold start time acceptable (<60s)
- [ ] Warm query time acceptable (<10s)
- [ ] Logs and monitoring enabled
- [ ] Backup strategy in place

---

## References

- **Architecture**: [docs/architecture.md](architecture.md)
- **Implementation**: [docs/implement.md](implement.md)
- **Test Results**: [docs/test_results.md](test_results.md)
- **Repository**: https://github.com/vn6295337/RAG-document-assistant
- **Live Demo**: https://huggingface.co/spaces/vn6295337/rag-poc

---

**Document Version**: 1.0
**Last Updated**: December 7, 2025
**Authors**: Built with Claude Code
**License**: MIT