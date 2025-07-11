from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.api import health, auth, carriers, loads, offers
from app.database import engine, Base
from app.models import load, call_log  # Import models to register them

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT != "production" else None,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    Base.metadata.create_all(bind=engine)

# Add security middleware for production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure this properly for production
    )

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["api-key-validation"])
app.include_router(carriers.router, prefix=f"{settings.API_V1_STR}/carriers", tags=["carriers"])
app.include_router(loads.router, prefix=f"{settings.API_V1_STR}/loads", tags=["loads"])
app.include_router(offers.router, prefix=f"{settings.API_V1_STR}/offers", tags=["offers"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to HappyRobot Carrier Engagement API",
        "docs_url": "/docs" if settings.ENVIRONMENT != "production" else "Documentation disabled in production",
        "version": "1.0.0",
        "description": "API for AI-powered inbound carrier engagement and load matching"
    } 