Architecture
============

Overview
--------

The RAG Document Assistant follows a modular architecture with clear separation of concerns:

.. code-block:: text

    ┌─────────────────────┐
    │   User Interface    │
    │  (Streamlit/Web)    │
    └─────────┬───────────┘
              │
    ┌─────────▼───────────┐
    │   Orchestrator      │
    │  (Query Pipeline)   │
    └─────────┬───────────┘
              │
    ┌─────────▼───────────┐
    │   Retrieval Layer   │
    │  (Pinecone Search)  │
    └─────────┬───────────┘
              │
    ┌─────────▼───────────┐
    │  Embedding Layer    │
    │ (Sentence Transformers) │
    └─────────┬───────────┘
              │
    ┌─────────▼───────────┐
    │   LLM Providers     │
    │ (Gemini/Groq/etc.)  │
    └─────────────────────┘

Core Components
---------------

1. **Ingestion Pipeline**
   - Document loading and parsing
   - Text chunking
   - Embedding generation
   - Vector storage

2. **Retrieval Pipeline**
   - Semantic search
   - Similarity ranking
   - Context assembly

3. **Generation Pipeline**
   - Prompt construction
   - LLM interaction
   - Response formatting

4. **User Interface**
   - Web-based query interface
   - Result visualization
   - Citation tracking

Data Flow
---------

1. **Document Ingestion**
   - Documents are loaded from source
   - Text is chunked into manageable pieces
   - Each chunk is embedded using sentence-transformers
   - Embeddings are stored in Pinecone vector database

2. **Query Processing**
   - User query is embedded using the same model
   - Semantic search is performed against Pinecone
   - Top-k relevant chunks are retrieved
   - Context is assembled for LLM

3. **Response Generation**
   - Prompt is constructed with context
   - LLM generates response
   - Citations are tracked and formatted
   - Final response is returned to user

Technology Stack
----------------

- **Language**: Python 3.11
- **Framework**: Streamlit
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB**: Pinecone Serverless
- **LLMs**: Multi-provider cascade (Gemini → Groq → OpenRouter)
- **Deployment**: Docker, Hugging Face Spaces