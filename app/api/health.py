from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    """Application health check"""
    print(request.headers)
    return {"status": "healthy", "message": "API is running"}


@router.get("/health/db")
async def database_health_check(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        # Try to execute a simple query
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        return {"status": "healthy", "message": "Database connection is working"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}") 