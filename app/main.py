import logging
from fastapi import FastAPI
from app.api.v1 import ingestion, insights

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Competitive Intelligence AI Agent - Core",
    description="Backend API for managing competitor state and computing deltas.",
    version="1.0.0",
)

app.include_router(ingestion.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Competitor Radar Core API is running."}
