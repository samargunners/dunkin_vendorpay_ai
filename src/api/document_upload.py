"""
Document Upload API

Handles file uploads and basic document processing for VendorPay AI
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional, List
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
import hashlib

# Create router
upload_router = APIRouter(prefix="/api/v1/documents", tags=["Document Upload"])

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

@upload_router.post("/upload")
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
                "message": "File uploaded successfully",
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
                    f"Process document: POST /api/v1/documents/{file_id}/process",
                    f"Get status: GET /api/v1/documents/{file_id}",
                    f"View all uploads: GET /api/v1/documents"
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@upload_router.get("/")
async def list_documents():
    """List all uploaded documents"""
    try:
        metadata_dir = PROCESSED_BASE_DIR / "extracted_data"
        
        if not metadata_dir.exists():
            return {"documents": [], "total": 0}
        
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
            "summary": {
                "by_type": {},
                "by_status": {}
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@upload_router.get("/{file_id}")
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
                f"Process: POST /api/v1/documents/{file_id}/process",
                f"Download: GET /api/v1/documents/{file_id}/download",
                f"Delete: DELETE /api/v1/documents/{file_id}"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@upload_router.post("/{file_id}/process")
async def process_document(file_id: str):
    """
    Process an uploaded document (placeholder for now)
    This will be enhanced with actual OCR and AI processing
    """
    try:
        metadata_file = PROCESSED_BASE_DIR / "extracted_data" / f"{file_id}_metadata.json"
        
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        # Simulate processing (replace with actual processing later)
        processing_result = {
            "file_id": file_id,
            "processing_timestamp": datetime.now().isoformat(),
            "status": "processed",
            "extracted_data": {
                "doc_type": metadata["doc_type"],
                "confidence": 0.85,
                "extracted_text": "Sample extracted text (OCR would go here)",
                "structured_data": {
                    "transactions": [],
                    "vendor_info": {},
                    "amounts": [],
                    "dates": []
                }
            },
            "notes": "This is a placeholder. Real processing will extract actual data."
        }
        
        # Update metadata
        metadata["processing_status"] = "completed"
        metadata["last_processed"] = datetime.now().isoformat()
        
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
                "message": "Document processed successfully",
                "data": processing_result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@upload_router.delete("/{file_id}")
async def delete_document(file_id: str):
    """Delete an uploaded document and its metadata"""
    try:
        metadata_file = PROCESSED_BASE_DIR / "extracted_data" / f"{file_id}_metadata.json"
        
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Read metadata to get file path
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        # Delete actual file
        file_path = Path(metadata["file_path"])
        if file_path.exists():
            file_path.unlink()
        
        # Delete metadata file
        metadata_file.unlink()
        
        # Delete results file if exists
        results_file = PROCESSED_BASE_DIR / "extracted_data" / f"{file_id}_results.json"
        if results_file.exists():
            results_file.unlink()
        
        return {
            "status": "success", 
            "message": f"Document {file_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

# Health check for upload system
@upload_router.get("/system/health")
async def upload_system_health():
    """Check upload system health"""
    try:
        # Check if directories exist
        dirs_exist = all([
            UPLOAD_BASE_DIR.exists(),
            PROCESSED_BASE_DIR.exists()
        ])
        
        # Check available space (simplified)
        total_uploads = len(list((PROCESSED_BASE_DIR / "extracted_data").glob("*_metadata.json"))) if (PROCESSED_BASE_DIR / "extracted_data").exists() else 0
        
        return {
            "status": "healthy",
            "directories_exist": dirs_exist,
            "total_uploads": total_uploads,
            "max_file_size_mb": MAX_FILE_SIZE // 1024 // 1024,
            "allowed_extensions": list(ALLOWED_EXTENSIONS.keys()),
            "supported_doc_types": list(DOC_TYPE_DIRS.keys())
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }