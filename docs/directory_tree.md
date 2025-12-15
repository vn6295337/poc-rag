# RAG Document Assistant - Directory Tree

```
.
├── app.py
├── setup.py
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── README.md
├── README_BUSINESS.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── MANIFEST.in
├── Makefile
├── pytest.ini
├── setup.cfg
├── mypy.ini
├── pyproject.toml
├── tox.ini
├── codecov.yml
├── PROJECT_STRUCTURE.md
├── scripts/
│   ├── README.md
│   ├── __init__.py
│   ├── test_ingestion.py
│   ├── ingest_documents.py
│   ├── regenerate_with_semantic.py
│   ├── search_documents.py
│   ├── check_pinecone.py
│   └── check_index_metadata.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── orchestrator.py
│   ├── llm_providers.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── load_docs.py
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── save_embeddings.py
│   │   └── data/
│   │       └── embeddings.jsonl
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── retriever.py
│   └── ui/
│       ├── __init__.py
│       └── app.py
├── docs/
│   ├── README.md
│   ├── architecture.md
│   ├── implement.md
│   ├── run.md
│   ├── test_results.md
│   ├── case_study.md
│   ├── project_summary.md
│   ├── case_study.pdf
│   ├── demo.mp4
│   ├── input_docs/
│   │   ├── eu_gdpr_data_protection_regulation.md
│   │   ├── who_digital_health_strategy_2020_2025.md
│   │   ├── un_2030_sustainable_development.md
│   │   ├── india_national_health_policy_2017.md
│   │   └── australia_international_development_policy_2023.md
│   └── source/
│       ├── conf.py
│       ├── index.rst
│       ├── installation.rst
│       ├── quickstart.rst
│       ├── architecture.rst
│       └── api/
│           ├── modules.rst
│           ├── rag_document_assistant.ingestion.rst
│           └── rag_document_assistant.retrieval.rst
├── data/
│   ├── chunks.jsonl
│   └── chunks_semantic.jsonl
├── sample_docs/
│   ├── README.md
│   └── example_document.md
├── tests/
│   ├── __init__.py
│   └── test_retrieval.py
└── docs/build/ (generated, not tracked)
    └── html/
```