.PHONY: install test clean format lint type-check docker-build docker-run

# Install dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements.txt
	pip install pytest black flake8 mypy

# Run tests
test:
	python -m pytest tests/ -v

# Format code with black
format:
	black src/ tests/

# Lint code with flake8
lint:
	flake8 src/ tests/

# Type check with mypy
type-check:
	mypy src/

# Clean Python cache files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

# Build Docker image
docker-build:
	docker build -t rag-document-assistant .

# Run Docker container
docker-run:
	docker run -p 7860:7860 --env-file .env rag-document-assistant

# Run local ingestion
ingest:
	python src/ingestion/cli_ingest.py sample_docs/

# Run local search
search:
	python src/ingestion/search_local.py src/ingestion/data/embeddings.jsonl

# Help
help:
	@echo "Available targets:"
	@echo "  install        - Install dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo "  test           - Run tests"
	@echo "  format         - Format code with black"
	@echo "  lint           - Lint code with flake8"
	@echo "  type-check     - Type check with mypy"
	@echo "  clean          - Clean Python cache files"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"
	@echo "  ingest         - Run local ingestion"
	@echo "  search         - Run local search"
	@echo "  help           - Show this help"