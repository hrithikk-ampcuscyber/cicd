from fastapi import FastAPI

from app.config import settings
from app.routers import items

app = FastAPI(title="CI/CD Practice API", version=settings.app_version)
app.include_router(items.router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.environment,
        "version": settings.app_version,
    }
