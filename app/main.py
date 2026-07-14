import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1 import ingestion, insights, clients, competitors, orchestration, webhooks, billing, dashboard, auth
from app.core.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield

app = FastAPI(
    title="Competitive Intelligence AI Agent - Core",
    description="Backend API for managing competitor state and computing deltas.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(ingestion.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")
app.include_router(clients.router, prefix="/api/v1")
app.include_router(competitors.router, prefix="/api/v1")
app.include_router(orchestration.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Competitor Radar Core API is running."}
