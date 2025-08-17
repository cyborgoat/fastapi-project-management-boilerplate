from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Initializing database...")
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    print("Database initialization complete.")
    
    yield
    
    # Shutdown
    print("Application shutdown complete.")


app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix=settings.API_V1_STR)
