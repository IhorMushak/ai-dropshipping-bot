"""
FastAPI application entry point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import engine

# Import all models to register them with Base
from app.database.models import (
    Product, Supplier, ProductSupplier, Order, Customer,
    Campaign, AdMetric, Decision, RewardLog, Event,
    Trend, Config, PriceHistory
)
from app.database.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    
    # Create database tables
    logger.info("Creating database tables...")
    logger.info(f"Registered tables: {list(Base.metadata.tables.keys())}")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

# Import API router
from app.api.v1.api import api_router

# Include API router
app.include_router(api_router, prefix="/api/v1")
from fastapi.staticfiles import StaticFiles
import os

# Додаємо статичні файли
static_dir = "/tmp/landings"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static/landings", StaticFiles(directory=static_dir), name="landings")
