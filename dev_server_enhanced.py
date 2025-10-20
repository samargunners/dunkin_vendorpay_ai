# Enhanced FastAPI Development Server with Document Upload
# This version includes all document upload endpoints directly

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
import hashlib

# Import our enhanced document processor
try:
    from src.ai_models.document_processor import DocumentProcessor
    PROCESSOR_AVAILABLE = True
except ImportError:
    PROCESSOR_AVAILABLE = False
    print("⚠️  Document processor not available - using fallback processing")

# Set development environment
os.environ["ENVIRONMENT"] = "development"
os.environ["SUPABASE_URL"] = "https://demo-project.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "demo_key"

app = FastAPI(
    title="VendorPay AI - Development Mode with Enhanced Document Processing",
    description="Financial document processing and vendor payment management system with AI-powered OCR",
    version="0.2.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize document processor
if PROCESSOR_AVAILABLE:
    document_processor = DocumentProcessor()
    print("✅ Enhanced document processor initialized")
else:
    document_processor = None

# Configuration
UPLOAD_BASE_DIR = Path("data/uploads")
PROCESSED_BASE_DIR = Path("data/processed")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Allowed file types
ALLOWED_EXTENSIONS = {
    '.pdf': 'application/pdf',
    '.jpg': 'image/jpeg', 
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.tiff': 'image/tiff',
    '.csv': 'text/csv',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

# Document type mapping to directories
DOC_TYPE_DIRS = {
    'bank_statement': 'bank_statements',
    'credit_card': 'credit_cards',
    'vendor_invoice': 'vendor_invoices', 
    'handwritten_note': 'handwritten_notes',
    'sales_report': 'sales_reports',
    'check_image': 'checks'
}

def generate_file_id() -> str:
    """Generate unique file ID"""
    return str(uuid.uuid4())

def get_file_hash(content: bytes) -> str:
    """Generate MD5 hash of file content"""
    return hashlib.md5(content).hexdigest()

def generate_filename(doc_type: str, source: str, original_name: str) -> str:
    """Generate standardized filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_id = generate_file_id()[:8]
    
    # Clean source name
    source_clean = ''.join(c for c in source.lower() if c.isalnum())
    
    # Get file extension
    ext = Path(original_name).suffix.lower() if original_name else ''
    
    return f"{doc_type}_{source_clean}_{timestamp}_{file_id}{ext}"

@app.get("/")
async def root():
    """Root endpoint with system status."""
    return {
        "message": "VendorPay AI API - Development Mode",
        "status": "online",
        "version": "0.1.0",
        "mode": "development",
        "note": "Document upload system ready!",
        "docs": "Visit /docs for API documentation",
        "features": {
            "document_upload": "✅ Available",
            "file_processing": "✅ Available", 
            "ocr_extraction": "⚠️ Pending Tesseract setup",
            "vendor_management": "✅ Demo mode",
            "transaction_tracking": "✅ Demo mode",
            "ai_reconciliation": "✅ Demo mode",
            "financial_reporting": "✅ Demo mode"
        },
        "upload_endpoints": {
            "upload_document": "POST /upload",
            "list_documents": "GET /documents",
            "get_document": "GET /documents/{file_id}",
            "process_document": "POST /documents/{file_id}/process",
            "system_health": "GET /upload/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mode": "development",
        "database": "not connected",
        "document_upload": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/upload", tags=["Document Upload"])
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    source: Optional[str] = Form("unknown"),
    description: Optional[str] = Form(None)
):
    """
    Upload a financial document for processing
    
    Args:
        file: The document file to upload
        doc_type: Type of document (bank_statement, credit_card, vendor_invoice, etc.)
        source: Source of the document (bank name, vendor name, etc.)
        description: Optional description
    
    Returns:
        JSON response with upload details and file information
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not allowed. Allowed types: {list(ALLOWED_EXTENSIONS.keys())}"
            )
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"
            )
        
        # Validate document type
        if doc_type not in DOC_TYPE_DIRS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document type. Allowed types: {list(DOC_TYPE_DIRS.keys())}"
            )
        
        # Generate file metadata
        file_id = generate_file_id()
        file_hash = get_file_hash(content)
        new_filename = generate_filename(doc_type, source or "unknown", file.filename)
        
        # Determine upload directory
        upload_dir = UPLOAD_BASE_DIR / DOC_TYPE_DIRS[doc_type]
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / new_filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create metadata
        metadata = {
            "file_id": file_id,
            "original_filename": file.filename,
            "new_filename": new_filename,
            "doc_type": doc_type,
            "source": source,
            "description": description,
            "file_size": len(content),
            "file_hash": file_hash,
            "content_type": file.content_type,
            "upload_timestamp": datetime.now().isoformat(),
            "file_path": str(file_path),
            "status": "uploaded",
            "processing_status": "pending"
        }
        
        # Save metadata
        metadata_dir = PROCESSED_BASE_DIR / "extracted_data"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        metadata_file = metadata_dir / f"{file_id}_metadata.json"
        
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "File uploaded successfully! 🎉",
                "data": {
                    "file_id": file_id,
                    "filename": new_filename,
                    "doc_type": doc_type,
                    "source": source,
                    "size": len(content),
                    "upload_time": metadata["upload_timestamp"],
                    "processing_status": "pending"
                },
                "next_steps": [
                    f"Process document: POST /documents/{file_id}/process",
                    f"Get status: GET /documents/{file_id}",
                    f"View all uploads: GET /documents"
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/documents", tags=["Document Management"])
async def list_documents():
    """List all uploaded documents"""
    try:
        metadata_dir = PROCESSED_BASE_DIR / "extracted_data"
        
        if not metadata_dir.exists():
            return {"documents": [], "total": 0, "message": "No documents uploaded yet"}
        
        documents = []
        for metadata_file in metadata_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    documents.append({
                        "file_id": metadata["file_id"],
                        "filename": metadata["new_filename"],
                        "original_filename": metadata["original_filename"],
                        "doc_type": metadata["doc_type"],
                        "source": metadata["source"],
                        "upload_time": metadata["upload_timestamp"],
                        "status": metadata.get("processing_status", "pending"),
                        "size": metadata["file_size"]
                    })
            except Exception as e:
                print(f"Error reading metadata file {metadata_file}: {e}")
                continue
        
        # Sort by upload time (newest first)
        documents.sort(key=lambda x: x["upload_time"], reverse=True)
        
        return {
            "documents": documents,
            "total": len(documents),
            "message": f"Found {len(documents)} uploaded documents"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@app.get("/documents/{file_id}", tags=["Document Management"])
async def get_document(file_id: str):
    """Get details for a specific document"""
    try:
        metadata_file = PROCESSED_BASE_DIR / "extracted_data" / f"{file_id}_metadata.json"
        
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        # Check if file still exists
        file_exists = Path(metadata["file_path"]).exists()
        
        return {
            "file_id": file_id,
            "metadata": metadata,
            "file_exists": file_exists,
            "actions": [
                f"Process: POST /documents/{file_id}/process",
                f"Delete: DELETE /documents/{file_id}"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@app.post("/documents/{file_id}/process", tags=["Document Processing"])
async def process_document(file_id: str):
    """
    Process an uploaded document using enhanced AI processor
    """
    try:
        metadata_file = PROCESSED_BASE_DIR / "extracted_data" / f"{file_id}_metadata.json"
        
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        # Get the original file path
        original_file = Path(metadata["file_path"])
        
        if not original_file.exists():
            raise HTTPException(status_code=404, detail="Original file not found")
        
        # Use enhanced document processor if available
        if PROCESSOR_AVAILABLE and document_processor:
            print(f"📄 Processing {original_file} with enhanced AI processor...")
            
            # Process document with enhanced processor
            result = document_processor.process_document(original_file)
            
            extracted_data = {
                "document_type": result.document_type,
                "extraction_method": result.extraction_method,
                "confidence": result.confidence_score,
                "processing_time": result.processing_time,
                "text_content": result.text_content[:500] + "..." if len(result.text_content) > 500 else result.text_content,
                "full_text_length": len(result.text_content),
                "extracted_fields": result.extracted_fields,
                "financial_data": result.financial_data,
                "processing_status": result.processing_status
            }
            
            processing_result = {
                "file_id": file_id,
                "processing_timestamp": datetime.now().isoformat(),
                "status": "processed_with_ai",
                "confidence": result.confidence_score / 100.0,  # Convert to 0-1 scale
                "extracted_data": extracted_data,
                "notes": f"Processed using enhanced AI processor with {result.extraction_method}"
            }
        else:
            # Fallback to simulated processing
            print(f"📄 Processing {original_file} with fallback processor...")
            doc_type = metadata["doc_type"]
            
            # Create different processing results based on document type
            if doc_type == "bank_statement":
                extracted_data = {
                    "transactions": [
                        {"date": "2024-10-15", "description": "DAILY SALES DEPOSIT", "amount": 1234.56, "type": "credit"},
                        {"date": "2024-10-16", "description": "SYSCO FOOD DELIVERY", "amount": -456.78, "type": "debit"},
                        {"date": "2024-10-17", "description": "RENT PAYMENT", "amount": -2800.00, "type": "debit"}
                    ],
                    "account_info": {
                        "account_number": "****1234",
                        "statement_period": "October 1-31, 2024",
                        "opening_balance": 5000.00,
                        "closing_balance": 2977.78
                    }
                }
            elif doc_type == "vendor_invoice":
                extracted_data = {
                    "vendor_info": {
                        "name": "SYSCO Corporation",
                        "address": "12345 Industrial Blvd, Houston, TX",
                        "phone": "(713) 555-0123"
                    },
                    "invoice_details": {
                        "invoice_number": "INV-2024-001567",
                        "date": "2024-10-15",
                        "due_date": "2024-11-15",
                        "total_amount": 2638.38
                    },
                    "line_items": [
                        {"description": "Ground Beef 80/20", "quantity": 25, "unit_price": 32.50, "total": 812.50},
                        {"description": "Hamburger Buns", "quantity": 10, "unit_price": 18.75, "total": 187.50}
                    ]
                }
            else:
                extracted_data = {
                    "message": f"Processing {doc_type} documents",
                    "status": "simulated_extraction"
                }
                
            processing_result = {
                "file_id": file_id,
                "processing_timestamp": datetime.now().isoformat(),
                "status": "processed_simulation",
                "confidence": 0.92,
                "extracted_data": extracted_data,
                "notes": "This is simulated processing. Enhanced AI processor not available."
            }
        
        # Update metadata
        metadata["processing_status"] = "completed"
        metadata["last_processed"] = datetime.now().isoformat()
        metadata["confidence"] = processing_result["confidence"]
        
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Save processing results
        results_file = PROCESSED_BASE_DIR / "extracted_data" / f"{file_id}_results.json"
        with open(results_file, "w") as f:
            json.dump(processing_result, f, indent=2)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Document processed successfully! 🎉",
                "data": processing_result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/upload/health", tags=["System Health"])
async def upload_system_health():
    """Check upload system health"""
    try:
        # Check if directories exist
        dirs_exist = all([
            UPLOAD_BASE_DIR.exists(),
            PROCESSED_BASE_DIR.exists()
        ])
        
        # Check available uploads
        total_uploads = len(list((PROCESSED_BASE_DIR / "extracted_data").glob("*_metadata.json"))) if (PROCESSED_BASE_DIR / "extracted_data").exists() else 0
        
        return {
            "status": "healthy",
            "directories_exist": dirs_exist,
            "total_uploads": total_uploads,
            "max_file_size_mb": MAX_FILE_SIZE // 1024 // 1024,
            "allowed_extensions": list(ALLOWED_EXTENSIONS.keys()),
            "supported_doc_types": list(DOC_TYPE_DIRS.keys()),
            "upload_directories": {
                "bank_statements": str(UPLOAD_BASE_DIR / "bank_statements"),
                "credit_cards": str(UPLOAD_BASE_DIR / "credit_cards"),
                "vendor_invoices": str(UPLOAD_BASE_DIR / "vendor_invoices"),
                "handwritten_notes": str(UPLOAD_BASE_DIR / "handwritten_notes"),
                "sales_reports": str(UPLOAD_BASE_DIR / "sales_reports"),
                "checks": str(UPLOAD_BASE_DIR / "checks")
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting VendorPay AI Development Server with Document Upload...")
    print("📝 Mode: Development (Full document upload functionality)")
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("🔗 Health Check: http://localhost:8000/health")
    print("📤 Upload Health: http://localhost:8000/upload/health")
    print("📁 Upload Endpoint: POST http://localhost:8000/upload")
    print("📋 List Documents: GET http://localhost:8000/documents")
    print()
    print("🎯 Ready to process financial documents!")
    
    uvicorn.run(
        "dev_server_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )