from fastapi import FastAPI
from sqlalchemy import text

from backend.core.config import settings
from backend.core.database import engine


app = FastAPI(
    title=settings.app_name,
    description=(
        "Production-oriented document processing service for "
        "extracting structured examination questions from PDF "
        "and image documents."
    ),
    version="1.0.0",
)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/health/database", tags=["System"])
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "PostgreSQL",
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "PostgreSQL",
        }