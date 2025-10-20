"""
Financial Management API Endpoints

This module provides FastAPI endpoints for document processing, transaction management,
and financial reconciliation for the VendorPay AI system.
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uuid

from ..core.supabase_manager import (
    SupabaseManager, VendorManager, DocumentManager, 
    TransactionManager, PaymentAccountManager
)
from ..ai_models.document_processing_pipeline import DocumentProcessor
from ..ai_models.reconciliation_engine import ReconciliationEngine, CashFlowAnalyzer

# Initialize managers
supabase_manager = SupabaseManager()
vendor_manager = VendorManager(supabase_manager)
document_manager = DocumentManager(supabase_manager)
transaction_manager = TransactionManager(supabase_manager)
account_manager = PaymentAccountManager(supabase_manager)

# Initialize processors
document_processor = DocumentProcessor(supabase_manager)
reconciliation_engine = ReconciliationEngine(supabase_manager)
cash_flow_analyzer = CashFlowAnalyzer(supabase_manager)

# Create router
financial_router = APIRouter(prefix="/api/financial", tags=["Financial Management"])

# =============================================
# PYDANTIC MODELS
# =============================================

class VendorCreate(BaseModel):
    name: str
    vendor_type: str = Field(..., description="supplier, utility, service, royalty")
    tax_id: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    payment_terms: Optional[str] = None
    preferred_payment_method: Optional[str] = None

class VendorResponse(BaseModel):
    id: str
    name: str
    vendor_type: str
    status: str
    created_at: datetime

class PaymentAccountCreate(BaseModel):
    account_name: str
    account_type: str = Field(..., description="bank_account, credit_card, cash")
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    routing_number: Optional[str] = None
    balance: Optional[float] = 0.0

class TransactionCreate(BaseModel):
    payment_account_id: Optional[str] = None
    vendor_id: Optional[str] = None
    amount: float
    transaction_date: date
    payment_method: str
    category: Optional[str] = None
    description: Optional[str] = None
    is_manual_entry: bool = False

class ReconciliationRequest(BaseModel):
    account_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    auto_confirm_exact_matches: bool = True

class CashFlowRequest(BaseModel):
    start_date: date
    end_date: date
    include_projections: bool = False

# =============================================
# VENDOR MANAGEMENT ENDPOINTS
# =============================================

@financial_router.post("/vendors", response_model=VendorResponse)
async def create_vendor(vendor: VendorCreate):
    """Create a new vendor"""
    try:
        vendor_data = vendor.dict()
        result = await vendor_manager.create_vendor(vendor_data)
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create vendor")
        
        return VendorResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.get("/vendors", response_model=List[VendorResponse])
async def get_vendors(search: Optional[str] = Query(None, description="Search vendors by name")):
    """Get all vendors or search vendors"""
    try:
        if search:
            vendors = await vendor_manager.search_vendors(search)
        else:
            # This would need to be implemented in VendorManager
            vendors = []  # Placeholder
        
        return [VendorResponse(**vendor) for vendor in vendors]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.get("/vendors/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: str):
    """Get vendor by ID"""
    try:
        vendor = await vendor_manager.get_vendor(vendor_id)
        
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        return VendorResponse(**vendor)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.put("/vendors/{vendor_id}", response_model=VendorResponse)
async def update_vendor(vendor_id: str, vendor_update: VendorCreate):
    """Update vendor information"""
    try:
        update_data = vendor_update.dict(exclude_unset=True)
        result = await vendor_manager.update_vendor(vendor_id, update_data)
        
        if not result:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        return VendorResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================
# PAYMENT ACCOUNT MANAGEMENT
# =============================================

@financial_router.post("/accounts")
async def create_payment_account(account: PaymentAccountCreate):
    """Create a new payment account"""
    try:
        account_data = account.dict()
        result = await account_manager.create_payment_account(account_data)
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create payment account")
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.get("/accounts")
async def get_payment_accounts(active_only: bool = Query(True)):
    """Get all payment accounts"""
    try:
        accounts = await account_manager.get_all_accounts(active_only)
        return accounts
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.put("/accounts/{account_id}/balance")
async def update_account_balance(account_id: str, new_balance: float):
    """Update account balance"""
    try:
        result = await account_manager.update_account_balance(account_id, new_balance)
        
        if not result:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================
# DOCUMENT PROCESSING ENDPOINTS
# =============================================

@financial_router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(..., description="bank_statement, credit_card_statement, vendor_bill, handwritten_note, sales_report, check"),
    uploaded_by: str = Form(..., description="User ID who uploaded the document")
):
    """Upload and process a financial document"""
    try:
        # Validate document type
        valid_types = ['bank_statement', 'credit_card_statement', 'vendor_bill', 
                      'handwritten_note', 'sales_report', 'check']
        if document_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid document type. Must be one of: {valid_types}")
        
        # Read file data
        file_data = await file.read()
        
        # Upload to Supabase
        document = await document_manager.upload_document(
            file.filename, file_data, document_type, uploaded_by
        )
        
        if not document:
            raise HTTPException(status_code=400, detail="Failed to upload document")
        
        # Start processing asynchronously
        asyncio.create_task(
            document_processor.process_document(
                document['id'], 
                document['file_path'], 
                document_type
            )
        )
        
        return {
            "message": "Document uploaded successfully and processing started",
            "document_id": document['id'],
            "status": "processing"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Get document information and processing status"""
    try:
        document = await document_manager.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.get("/documents/pending")
async def get_pending_documents(document_type: Optional[str] = Query(None)):
    """Get documents that are pending processing"""
    try:
        documents = await document_manager.get_pending_documents(document_type)
        return documents
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.post("/documents/{document_id}/reprocess")
async def reprocess_document(document_id: str):
    """Reprocess a failed or manually reviewed document"""
    try:
        document = await document_manager.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Reset status to pending
        await document_manager.update_processing_status(document_id, 'pending')
        
        # Start processing
        asyncio.create_task(
            document_processor.process_document(
                document['id'], 
                document['file_path'], 
                document['document_type']
            )
        )
        
        return {"message": "Document reprocessing started"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================
# TRANSACTION MANAGEMENT ENDPOINTS
# =============================================

@financial_router.post("/transactions/outgoing")
async def create_outgoing_transaction(transaction: TransactionCreate):
    """Create a new outgoing transaction (expense/payment)"""
    try:
        transaction_data = transaction.dict()
        result = await transaction_manager.create_outgoing_transaction(transaction_data)
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create transaction")
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.post("/transactions/incoming")
async def create_incoming_transaction(transaction: TransactionCreate):
    """Create a new incoming transaction (revenue/sales)"""
    try:
        transaction_data = transaction.dict()
        result = await transaction_manager.create_incoming_transaction(transaction_data)
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create transaction")
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.get("/transactions/unreconciled")
async def get_unreconciled_transactions(account_id: Optional[str] = Query(None)):
    """Get all unreconciled transactions"""
    try:
        transactions = await transaction_manager.get_unreconciled_transactions(account_id)
        return transactions
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================
# RECONCILIATION ENDPOINTS
# =============================================

@financial_router.post("/reconciliation/run")
async def run_reconciliation(request: ReconciliationRequest):
    """Run the reconciliation process"""
    try:
        date_range = None
        if request.start_date and request.end_date:
            date_range = (request.start_date, request.end_date)
        
        results = await reconciliation_engine.run_reconciliation(
            account_id=request.account_id,
            date_range=date_range
        )
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.post("/reconciliation/manual-match")
async def create_manual_reconciliation(
    statement_transaction_id: str = Form(...),
    business_transaction_id: str = Form(...),
    business_transaction_type: str = Form(..., description="outgoing or incoming"),
    notes: Optional[str] = Form(None)
):
    """Manually create a reconciliation match"""
    try:
        reconciliation_data = {
            'statement_transaction_id': statement_transaction_id,
            'business_transaction_id': business_transaction_id,
            'business_transaction_type': business_transaction_type,
            'match_type': 'manual',
            'confidence_score': 1.0,
            'reconciled_by': 'manual_user',  # Would be actual user ID
            'notes': notes
        }
        
        result = await transaction_manager.create_reconciliation(reconciliation_data)
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create reconciliation")
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================
# CASH FLOW AND REPORTING ENDPOINTS
# =============================================

@financial_router.post("/reports/cash-flow")
async def get_cash_flow_report(request: CashFlowRequest):
    """Generate cash flow report for specified period"""
    try:
        report = await cash_flow_analyzer.generate_cash_flow_report(
            request.start_date, 
            request.end_date
        )
        
        return report
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.get("/dashboard/summary")
async def get_dashboard_summary():
    """Get dashboard summary with key financial metrics"""
    try:
        # This would aggregate data for dashboard display
        summary = {
            'total_unreconciled_transactions': 0,
            'pending_vendor_payments': 0,
            'monthly_revenue': 0.0,
            'monthly_expenses': 0.0,
            'reconciliation_rate': 0.0,
            'recent_activity': [],
            'alerts': []
        }
        
        # Implementation would fetch real data
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.get("/dashboard/money-flow")
async def get_money_flow_visualization(
    period: str = Query("month", description="day, week, month, quarter, year"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    """Get money flow data for visualization"""
    try:
        # This would return data formatted for charts/graphs
        money_flow = {
            'period': period,
            'income_data': {
                'dates': [],
                'amounts': [],
                'categories': {}
            },
            'expense_data': {
                'dates': [],
                'amounts': [],
                'categories': {}
            },
            'net_flow': {
                'dates': [],
                'amounts': []
            }
        }
        
        # Implementation would fetch and format real data
        return money_flow
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================
# MANUAL ENTRY ENDPOINTS
# =============================================

@financial_router.post("/manual-entry/handwritten-note")
async def create_manual_handwritten_entry(
    vendor_name: str = Form(...),
    amount: float = Form(...),
    transaction_date: date = Form(...),
    description: str = Form(...),
    category: str = Form("manual_entry"),
    payment_method: str = Form("cash")
):
    """Manually enter data from a handwritten note"""
    try:
        transaction_data = {
            'amount': amount,
            'transaction_date': transaction_date,
            'payment_method': payment_method,
            'category': category,
            'description': f"Manual entry: {description} (Vendor: {vendor_name})",
            'is_manual_entry': True,
            'reconciliation_status': 'unreconciled'
        }
        
        result = await transaction_manager.create_outgoing_transaction(transaction_data)
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create manual entry")
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.post("/manual-entry/check")
async def create_manual_check_entry(
    payee: str = Form(...),
    amount: float = Form(...),
    check_number: str = Form(...),
    check_date: date = Form(...),
    memo: Optional[str] = Form(None),
    category: str = Form("check_payment")
):
    """Manually enter check information"""
    try:
        transaction_data = {
            'amount': amount,
            'transaction_date': check_date,
            'payment_method': 'check',
            'check_number': check_number,
            'category': category,
            'description': f"Check #{check_number} to {payee}" + (f" - {memo}" if memo else ""),
            'is_manual_entry': True,
            'reconciliation_status': 'unreconciled'
        }
        
        result = await transaction_manager.create_outgoing_transaction(transaction_data)
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create check entry")
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================
# HEALTH CHECK ENDPOINT
# =============================================

@financial_router.get("/health")
async def health_check():
    """Health check for financial management system"""
    try:
        # Test Supabase connection
        client = supabase_manager.get_client()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "supabase": "connected",
                "document_processing": "ready",
                "reconciliation_engine": "ready"
            }
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }