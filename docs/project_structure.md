# RAG Document Assistant - Complete Directory Structure

This document provides a comprehensive overview of the RAG Document Assistant project directory structure, showing all files and folders organized by their functional purpose.

## Root Directory

```
.
├── app.py                          # Main Streamlit application entry point
├── setup.py                        # Package setup and distribution configuration
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies
├── Dockerfile                      # Containerization configuration
├── README.md                       # Project overview and getting started guide
├── README_BUSINESS.md              # Business-focused project overview
├── LICENSE                         # MIT license file
├── CHANGELOG.md                    # Version history and changes
├── CONTRIBUTING.md                 # Contribution guidelines
├── SECURITY.md                     # Security policies and reporting
├── MANIFEST.in                     # Package manifest for distribution
├── Makefile                        # Build automation commands
├── pytest.ini                      # Pytest configuration
├── setup.cfg                       # Setup tools configuration
├── mypy.ini                        # Type checking configuration
├── pyproject.toml                  # Modern Python project configuration
├── tox.ini                         # Testing automation configuration
└── codecov.yml                     # Code coverage reporting configuration
```

## Source Code (src/)

```
./src/
├── __init__.py                     # Package initialization
├── config.py                       # Configuration management
├── orchestrator.py                 # Query orchestration logic
├── llm_providers.py                # LLM provider integrations
├── ingestion/                      # Document ingestion pipeline
│   ├── __init__.py                 # Package initialization
│   ├── README.md                   # Ingestion module documentation
│   ├── load_docs.py                # Document loading functionality
│   ├── chunker.py                  # Document chunking algorithms
│   ├── embeddings.py               # Embedding generation
│   ├── save_embeddings.py          # Embedding persistence
│   └── data/
│       └── embeddings.jsonl        # Sample embeddings data
├── retrieval/                      # Document retrieval system
│   ├── __init__.py                 # Package initialization
│   └── retriever.py                # Vector similarity search
└── ui/                             # User interface components
    ├── __init__.py                 # Package initialization
    └── app.py                      # Streamlit UI implementation
```

## Scripts (scripts/)

```
./scripts/
├── __init__.py                     # Package initialization
├── README.md                       # Scripts directory documentation
├── test_ingestion.py               # Test ingestion pipeline
├── ingest_documents.py             # Run document ingestion
├── regenerate_with_semantic.py     # Regenerate with semantic embeddings
├── search_documents.py             # Local document search
├── check_pinecone.py               # Pinecone connectivity check
└── check_index_metadata.py         # Pinecone index metadata check
```

## Documentation (docs/)

```
./docs/
├── README.md                       # Documentation directory overview
├── architecture.md                 # System architecture documentation
├── implement.md                    # Implementation guide
├── run.md                          # Operations runbook
├── test_results.md                 # Test results and metrics
├── case_study.md                   # Technical case study
├── project_summary.md              # High-level project summary
├── case_study.pdf                  # PDF version of case study
├── demo.mp4                        # Demonstration video
├── input_docs/                     # Input documents for processing
│   ├── eu_gdpr_data_protection_regulation.md
│   ├── who_digital_health_strategy_2020_2025.md
│   ├── un_2030_sustainable_development.md
│   ├── india_national_health_policy_2017.md
│   └── australia_international_development_policy_2023.md
└── source/                         # Sphinx documentation source
    ├── conf.py                     # Sphinx configuration
    ├── index.rst                   # Documentation index
    ├── installation.rst            # Installation guide
    ├── quickstart.rst              # Quick start guide
    ├── architecture.rst            # Architecture documentation
    └── api/                        # API documentation
        ├── modules.rst             # API modules index
        ├── rag_document_assistant.ingestion.rst
        └── rag_document_assistant.retrieval.rst
```

## Data Storage (data/)

```
./data/
├── chunks.jsonl                    # Generated document chunks
└── chunks_semantic.jsonl           # Semantic embedding chunks
```

## Sample Documents (sample_docs/)

```
./sample_docs/
├── README.md                       # Sample documents overview
└── example_document.md             # Example document template
```

## Testing (tests/)

```
./tests/
├── __init__.py                     # Package initialization
└── test_retrieval.py               # Retrieval system tests
```

## Build Artifacts

```
./docs/build/                       # Generated documentation (not tracked)
└── html/                           # HTML documentation output
```

## Key Organizational Principles

### 1. Separation of Concerns
- **src/**: Core application logic
- **scripts/**: Operational utilities
- **docs/**: Documentation and input materials
- **data/**: Generated data files
- **tests/**: Automated tests

### 2. MECE Compliance
Each directory has a distinct purpose with minimal overlap:
- **Source code** is separated from **operational scripts**
- **Documentation** is distinct from **source code**
- **Test files** are isolated from **production code**
- **Data files** are separate from **code files**

### 3. Standard Conventions
- All Python packages include `__init__.py` files
- Documentation follows consistent naming patterns
- Scripts have clear, descriptive names
- Configuration files use standard formats