# 🔬 CI/CD Failure Analyzer

A production-ready full-stack application for intelligent CI/CD failure analysis using **LLM + RAG (Retrieval-Augmented Generation)**. Automatically classifies failures, identifies root causes, suggests fixes, and learns from feedback.

---

## 🏗 Architecture

```
cicd-analyzer/
├── backend/                    # FastAPI Python backend
│   ├── main.py                 # App entry point, CORS, lifespan
│   ├── config.py               # Settings (env vars)
│   ├── routers/
│   │   ├── logs.py             # Upload, analyze, history endpoints
│   │   ├── analyses.py         # Fetch analysis by ID
│   │   ├── feedback.py         # Submit feedback
│   │   └── metrics.py          # Dashboard metrics
│   ├── services/
│   │   ├── analysis_service.py # Orchestration pipeline
│   │   ├── llm_service.py      # OpenAI / mock LLM
│   │   └── vector_store.py     # ChromaDB RAG store
│   ├── models/
│   │   ├── db_models.py        # SQLAlchemy ORM models
│   │   └── schemas.py          # Pydantic request/response schemas
│   └── utils/
│       ├── database.py         # Async DB engine + session
│       └── log_processor.py    # Preprocessing, chunking, classification
│
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── AnalyzePage.jsx # Upload + analyze + result view
│   │   │   ├── HistoryPage.jsx # Past analyses table + detail modal
│   │   │   └── MetricsPage.jsx # Charts dashboard (Recharts)
│   │   ├── utils/
│   │   │   ├── api.js          # Axios API client
│   │   │   └── sampleLogs.js   # Demo log samples
│   │   ├── App.jsx             # Layout + sidebar navigation
│   │   └── index.css           # Dark industrial design system
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

### Data Flow

```
User uploads log
      │
      ▼
  Log Processor
  ├─ Remove noise (downloads, progress bars)
  ├─ Extract error sections + context
  ├─ Chunk into segments
  └─ Classify: build / test / infrastructure
      │
      ▼
  RAG Retrieval (ChromaDB)
  └─ Embed preprocessed log → query similar past issues
      │
      ▼
  LLM Analysis (OpenAI GPT / Mock)
  ├─ System prompt: expert DevOps engineer
  ├─ User prompt: preprocessed log + similar issues context
  └─ Structured JSON response: summary, root_cause, fixes
      │
      ▼
  Store in DB (SQLite/PostgreSQL) + ChromaDB
      │
      ▼
  Return to frontend → display + collect feedback
      │
      ▼
  Feedback → update ChromaDB ranking scores
```

---

## 🚀 Quick Start (Local, No Docker)

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) OpenAI API key

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — at minimum leave OPENAI_API_KEY blank for mock mode

# Start server
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000  
API docs (Swagger): http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API URL
cp .env.example .env
# VITE_API_URL=http://localhost:8000  (default, usually no change needed)

# Start dev server
npm run dev
```

Frontend runs at: http://localhost:5173

---

## 🐳 Docker Compose (Recommended)

```bash
# From project root
cp backend/.env.example backend/.env
# Optionally add OPENAI_API_KEY to backend/.env

docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

---

## 🔑 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(empty)* | OpenAI key. Leave blank to use built-in mock analysis |
| `DATABASE_URL` | `sqlite+aiosqlite:///./cicd_analyzer.db` | DB connection string |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage directory |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `LLM_MODEL` | `gpt-3.5-turbo` | OpenAI model name |
| `MAX_CHUNK_SIZE` | `2000` | Max chars per log chunk |
| `TOP_K_SIMILAR` | `3` | Number of similar issues to retrieve |

> **No OpenAI key?** The system uses intelligent mock analysis that classifies failures and returns realistic suggestions based on the failure category. All RAG, feedback, and metrics features still work fully.

---

## 📡 API Reference

### Upload + Analyze (single call)
```
POST /logs/upload-and-analyze
Content-Type: multipart/form-data

Fields:
  file        (optional) .txt/.log file
  raw_log     (optional) plain text log
```

### Two-step flow
```
POST /logs/upload           → { log_entry_id, failure_category }
POST /logs/{id}/analyze     → AnalysisResponse
```

### Fetch analysis
```
GET /analyses/{analysis_id}
```

### History
```
GET /logs/history?skip=0&limit=20
```

### Submit feedback
```
POST /feedback/
Body: { "analysis_id": 1, "is_correct": true, "comment": "..." }
```

### Metrics
```
GET /metrics/
```

---

## 🎯 Features

### Log Processing
- **Noise removal**: strips Maven download progress, blank lines, irrelevant INFO
- **Error extraction**: finds error lines + 3 lines of surrounding context
- **Smart chunking**: splits on stage/step boundaries before falling back to size
- **Auto-classification**: regex scoring across 3 categories (build / test / infrastructure)

### RAG System
- Embeddings via `sentence-transformers/all-MiniLM-L6-v2` (runs locally, no API needed)
- ChromaDB persistent vector store with cosine similarity
- Each stored document includes: summary, root cause, fix preview, feedback score
- Similar issues boost LLM prompt quality over time

### Feedback Learning
- 👍/👎 per analysis stored in SQLite
- Positive feedback: +0.1 to ChromaDB document score
- Negative feedback: -0.1 to ChromaDB document score
- Higher-scored documents surface first in RAG retrieval

### Dashboard Metrics
- Total analyses count
- Accuracy rate (from feedback)
- 7-day trend line chart
- Failure breakdown pie chart
- Top root cause terms bar chart
- System health progress bars

---

## 🧪 Testing with Sample Logs

The frontend includes 3 built-in sample logs:
- **Build failure** — Maven compilation error (missing symbol, type mismatch)
- **Test failure** — pytest with assertion errors and TypeError
- **Infrastructure failure** — Docker registry connection refused + K8s RBAC

Click the `build`, `test`, or `infrastructure` buttons on the Analyze page to load them instantly.

---

## 🔧 Extending the Project

### Add PostgreSQL
```bash
pip install asyncpg
# In .env:
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cicd_db
```

### Use a local LLM (Ollama)
Edit `backend/services/llm_service.py` — replace the OpenAI client with:
```python
from openai import AsyncOpenAI
client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
```

### Add authentication
Add `python-jose[cryptography]` and `passlib[bcrypt]`, create an `/auth/token` endpoint, and add `Depends(get_current_user)` to protected routes.

### CI/CD webhook trigger
```bash
# Auto-trigger analysis from Jenkins post-build step:
curl -X POST http://your-server:8000/logs/upload-and-analyze \
  -F "raw_log=$(cat build.log)"
```

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 (async) |
| Database | SQLite (swap to PostgreSQL easily) |
| Vector store | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | OpenAI GPT-3.5 / mock fallback |
| Frontend | React 18 + Vite |
| Charts | Recharts |
| File upload | react-dropzone |
| Notifications | react-hot-toast |
| Containerization | Docker + Docker Compose |
