# Deploy to Hugging Face Spaces

**Best option: Completely free, designed for ML/AI apps, native Streamlit support**

## Quick Deploy (5 minutes)

### 1. Create a Hugging Face Account
Go to: https://huggingface.co/join

### 2. Create a New Space
- Go to: https://huggingface.co/new-space
- **Space name:** `rag-poc` (or any name you want)
- **License:** MIT
- **Space SDK:** Select **"Streamlit"**
- **Space hardware:** CPU basic (free)
- Click **"Create Space"**

### 3. Configure Space Files

Hugging Face Spaces needs these files in the repository root:

**app.py** (main file - already created as ui/app.py)
**requirements.txt** (already created)
**README.md** (optional but recommended)

### 4. Upload Your Code

**Option A: Use Git (Recommended)**

```bash
# Clone your new Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/rag-poc
cd rag-poc

# Copy files from poc-rag
cp /home/vn6295337/poc-rag/ui/app.py ./app.py
cp /home/vn6295337/poc-rag/requirements.txt ./requirements.txt
cp -r /home/vn6295337/poc-rag/src ./src
cp -r /home/vn6295337/poc-rag/retrieval ./retrieval
cp -r /home/vn6295337/poc-rag/ingestion ./ingestion

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

**Option B: Use Web UI**
- Click "Files" tab in your Space
- Upload files manually

### 5. Add Secrets (Environment Variables)

In your Space page:
1. Click **"Settings"** tab
2. Scroll to **"Repository secrets"**
3. Add these secrets:

```
PINECONE_API_KEY = your_pinecone_key_from_~/secrets/pinecone.key
PINECONE_INDEX_NAME = rag-semantic-384
GEMINI_API_KEY = your_gemini_key_from_~/secrets/gemini.key
GEMINI_MODEL = gemini-2.5-flash
GROQ_API_KEY = your_groq_key_from_~/secrets/groq.key
GROQ_MODEL = llama-3.1-8b-instant
OPENROUTER_API_KEY = your_openrouter_key_from_~/secrets/openrouter.key
OPENROUTER_MODEL = mistralai/mistral-7b-instruct:free
```

**Get your actual keys from:**
```bash
cat ~/secrets/pinecone.key
cat ~/secrets/gemini.key
cat ~/secrets/groq.key
cat ~/secrets/openrouter.key
```

### 6. Wait for Build

Hugging Face will automatically:
- Install dependencies from requirements.txt
- Start the Streamlit app
- Make it available at: `https://huggingface.co/spaces/YOUR_USERNAME/rag-poc`

## Why Hugging Face Spaces?

✅ **Completely free** - No credit card, no time limits
✅ **Built for ML/AI** - Perfect for RAG applications
✅ **Native Streamlit** - No configuration needed
✅ **Easy sharing** - Great for portfolio/demos
✅ **GPU available** - Can upgrade to GPU if needed (paid)
✅ **Community** - Good for showcasing ML projects

## Alternative: Render.com

If you prefer Render:
1. Go to: https://render.com
2. Sign up (free, no credit card)
3. Click "New +" → "Web Service"
4. Connect GitHub repo: `vn6295337/poc-rag`
5. Configure:
   - **Name:** rag-poc
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run ui/app.py --server.port=$PORT --server.address=0.0.0.0`
6. Add environment variables (same as above)
7. Deploy!

Free tier: 750 hours/month, sleeps after 15 min inactivity

## Which One to Choose?

**Hugging Face Spaces** - Best for:
- ML/AI projects
- Portfolio showcase
- Community visibility
- Permanent free hosting

**Render** - Best for:
- General web apps
- More control over deployment
- Custom domains (paid tier)
