#!/bin/bash
# Deploy RAG PoC to Google Cloud Run

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-ai-portfolio-v2}"
SERVICE_NAME="${SERVICE_NAME:-rag-poc}"
REGION="${REGION:-us-central1}"

echo "================================================"
echo "Deploying RAG PoC to Cloud Run"
echo "================================================"
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Check if required environment variables are set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "WARNING: GEMINI_API_KEY not set"
fi

if [ -z "$PINECONE_API_KEY" ]; then
    echo "ERROR: PINECONE_API_KEY must be set"
    exit 1
fi

echo "Building and deploying with Cloud Run Buildpacks..."

gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --set-env-vars "PINECONE_API_KEY=$PINECONE_API_KEY" \
    --set-env-vars "PINECONE_INDEX_NAME=${PINECONE_INDEX_NAME:-rag-semantic-384}" \
    --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY:-}" \
    --set-env-vars "GEMINI_MODEL=${GEMINI_MODEL:-gemini-2.5-flash}" \
    --set-env-vars "GROQ_API_KEY=${GROQ_API_KEY:-}" \
    --set-env-vars "GROQ_MODEL=${GROQ_MODEL:-llama-3.1-8b-instant}" \
    --set-env-vars "OPENROUTER_API_KEY=${OPENROUTER_API_KEY:-}" \
    --set-env-vars "OPENROUTER_MODEL=${OPENROUTER_MODEL:-mistralai/mistral-7b-instruct:free}"

echo ""
echo "================================================"
echo "Deployment complete!"
echo "================================================"
echo "Service URL will be displayed above"
echo ""
echo "To view logs:"
echo "  gcloud run services logs read $SERVICE_NAME --region $REGION"
echo ""
