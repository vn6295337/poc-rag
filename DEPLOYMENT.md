# RAG PoC - Cloud Run Deployment Guide

## Prerequisites

1. **Google Cloud CLI installed and configured**
   ```bash
   gcloud --version
   gcloud auth list
   gcloud config get-value project
   ```

2. **Environment variables configured**
   - Copy `.env.example` to `.env`
   - Fill in API keys for Pinecone and LLM providers
   - Source the environment: `source ~/aienv/bin/activate`

3. **Enable required GCP APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

## Deployment Steps

### 1. Quick Deployment (Automated)

```bash
# Source your API keys
source ~/aienv/bin/activate

# Deploy to Cloud Run
./deploy-cloudrun.sh
```

### 2. Manual Deployment

```bash
# Set environment variables
export GOOGLE_CLOUD_PROJECT="ai-portfolio-v2"
export SERVICE_NAME="rag-poc"
export REGION="us-central1"

# Deploy with gcloud
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --set-env-vars "PINECONE_API_KEY=$PINECONE_API_KEY" \
    --set-env-vars "PINECONE_INDEX_NAME=rag-semantic-384" \
    --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY" \
    --set-env-vars "GEMINI_MODEL=gemini-2.5-flash"
```

## Configuration Files

- **requirements.txt**: Python dependencies
- **Procfile**: Specifies how to run the Streamlit app
- **runtime.txt**: Python version (3.11.2)
- **.streamlit/config.toml**: Streamlit server configuration
- **.env.example**: Template for environment variables

## Environment Variables

Required:
- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_INDEX_NAME`: Index name (default: rag-semantic-384)

Optional (LLM providers - at least one recommended):
- `GEMINI_API_KEY`, `GEMINI_MODEL`
- `GROQ_API_KEY`, `GROQ_MODEL`
- `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`

## Post-Deployment

### View Service URL
```bash
gcloud run services describe rag-poc --region us-central1 --format="value(status.url)"
```

### View Logs
```bash
gcloud run services logs read rag-poc --region us-central1 --limit=50
```

### Test Cold Start
```bash
# Access the URL after service has been idle for 5+ minutes
curl -I https://YOUR-SERVICE-URL.run.app
```

## Troubleshooting

### Build Failures
- Check `requirements.txt` for incompatible versions
- Verify Python runtime is supported
- Check build logs: `gcloud builds list --limit=5`

### Runtime Errors
- Check environment variables are set correctly
- View logs: `gcloud run services logs read rag-poc --region us-central1`
- Verify Pinecone index exists and is accessible

### Performance Issues
- Cold start: ~15-30 seconds (PyTorch model loading)
- Consider increasing memory/CPU if responses are slow
- Monitor with: `gcloud run services describe rag-poc --region us-central1`

## Architecture

```
User Request → Cloud Run (Streamlit UI)
              ↓
         orchestrator.py
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
retriever.py      llm_providers.py
(sentence-transformers)  (Gemini/Groq/OpenRouter)
    ↓                   ↓
 Pinecone            LLM APIs
(semantic search)   (answer generation)
```

## Cost Considerations

- Cloud Run: Pay-per-use (free tier: 2M requests/month)
- Pinecone: Free tier (1 index, serverless)
- LLM APIs:
  - Gemini: Free tier available
  - Groq: Free tier available
  - OpenRouter: Some free models available

## Security Notes

- API keys stored as environment variables (not in code)
- Service allows unauthenticated access (public demo)
- For production: Use Cloud Run IAM for authentication
