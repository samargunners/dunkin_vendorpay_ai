# Simple FastAPI Development Server Test
# Run this to test the server without full Supabase setup

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.document_upload import upload_router
import os

# Set development environment
os.environ["ENVIRONMENT"] = "development"
os.environ["SUPABASE_URL"] = "https://demo-project.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "demo_key"

app = FastAPI(
    title="VendorPay AI - Development Mode",
    description="Financial document processing and vendor payment management system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include document upload router
app.include_router(upload_router)

@app.get("/")
async def root():
    """Root endpoint with system status."""
    return {
        "message": "VendorPay AI API - Development Mode",
        "status": "online",
        "version": "0.1.0",
        "mode": "development",
        "note": "Supabase not configured - using demo mode",
        "docs": "Visit /docs for API documentation",
        "features": {
            "document_processing": "Available",
            "vendor_management": "Demo mode",
            "transaction_tracking": "Demo mode",
            "ai_reconciliation": "Demo mode",
            "financial_reporting": "Demo mode"
        },
        "next_steps": [
            "Set up Supabase project",
            "Update .env with real credentials",
            "Run database migrations",
            "Start full API server"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mode": "development",
        "database": "not connected",
        "timestamp": "2024-10-18T15:30:00Z"
    }

@app.get("/docs-redirect")
async def docs_redirect():
    """Redirect to API documentation."""
    return {"redirect": "/docs"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting VendorPay AI Development Server...")
    print("📝 Mode: Development (Supabase not required)")
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("🔗 Health Check: http://localhost:8000/health")
    print("⚠️  Note: This is a demo mode. Set up Supabase for full functionality.")
    
    uvicorn.run(
        "dev_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )