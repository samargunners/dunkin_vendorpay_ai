"""
VendorPay AI FastAPI Application

Main FastAPI application for the VendorPay AI financial management system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import the financial management router
from .financial_endpoints import financial_router

# Create FastAPI application
app = FastAPI(
    title="VendorPay AI",
    description="AI-powered vendor payment processing and financial management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include financial management router
app.include_router(financial_router)

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "VendorPay AI Financial Management System",
        "version": "1.0.0",
        "status": "active",
        "features": [
            "Document Processing (OCR, PDF parsing)",
            "Financial Reconciliation",
            "Vendor Management", 
            "Transaction Tracking",
            "Cash Flow Analysis",
            "Manual Entry Support"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "financial_api": "/api/financial",
            "health": "/api/financial/health"
        }
    }

@app.get("/health")
async def health_check():
    """Application health check"""
    return {
        "status": "healthy",
        "service": "VendorPay AI",
        "version": "1.0.0"
    }

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )