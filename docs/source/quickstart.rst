Quick Start
===========

This guide will help you get started with the RAG Document Assistant quickly.

Prerequisites
-------------

Before you begin, ensure you have:

1. Python 3.8 or higher installed
2. A Pinecone account and API key
3. At least one LLM provider API key (Gemini, Groq, or OpenRouter)

Installation
------------

.. code-block:: bash

    pip install rag-document-assistant

Configuration
-------------

Create a ``.env`` file with your API keys:

.. code-block:: bash

    # Pinecone (Required)
    PINECONE_API_KEY=your_pinecone_api_key
    PINECONE_INDEX_NAME=rag-semantic-384

    # LLM Providers (at least one required)
    GEMINI_API_KEY=your_gemini_api_key
    GROQ_API_KEY=your_groq_api_key
    OPENROUTER_API_KEY=your_openrouter_api_key

Basic Usage
-----------

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~

Ingest documents:

.. code-block:: bash

    rag-ingest /path/to/your/documents

Search documents:

.. code-block:: bash

    rag-search "your query here"

Python API
~~~~~~~~~~

.. code-block:: python

    from rag_document_assistant import orchestrate_query

    result = orchestrate_query("What is GDPR?")
    print(result["answer"])

Web Interface
~~~~~~~~~~~~~

Run the Streamlit web interface:

.. code-block:: bash

    streamlit run src/ui/app.py