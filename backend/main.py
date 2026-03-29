from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from utils.database import init_db
from routers import logs, analyses, feedback, metrics
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Warm up vector store
    from services.vector_store import get_vector_store
    get_vector_store()
    print(f"[startup] {settings.APP_NAME} ready.")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="CI/CD Failure Analysis with LLM + RAG",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs.router)
app.include_router(analyses.router)
app.include_router(feedback.router)
app.include_router(metrics.router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
