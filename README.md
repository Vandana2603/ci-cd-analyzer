CI/CD Failure Analyzer (LLM + RAG)

AI-powered full-stack tool for intelligent CI/CD failure analysis. Automatically classifies failures, identifies root causes, suggests fixes, and learns from feedback.

🚀 Features
Automatic failure classification: build, test, or infrastructure errors
Root cause detection and fix suggestions using LLM + RAG (ChromaDB + sentence-transformers)
Feedback learning: improves analysis over time
Interactive frontend dashboard: React 18 + Vite with Recharts visualizations
Containerized for easy deployment: Docker + Docker Compose
💻 Tech Stack

FastAPI, Uvicorn, SQLAlchemy 2.0 (async), SQLite/PostgreSQL, ChromaDB, sentence-transformers, GPT-3.5, React 18, Vite, Recharts, react-dropzone, react-hot-toast, Docker

⚡ Quick Start (Local)
# Backend
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

Frontend: http://localhost:5173
 | Backend API: http://localhost:8000

🐳 Docker (Recommended)
cp backend/.env.example backend/.env
docker-compose up --build

Frontend: http://localhost:3000
 | Backend API: http://localhost:8000
 | Swagger docs: http://localhost:8000/docs
