"""
Supabase Database Configuration and Connection Management

This module handles all Supabase database operations for the VendorPay AI system.
"""

import os
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
from datetime import datetime, date
import asyncio
import asyncpg
import json
from decimal import Decimal

class SupabaseManager:
    """Manages Supabase database connections and operations"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        # Development mode: Allow demo/placeholder values
        if not self.url or not self.key or self.url.startswith("https://demo-"):
            if os.getenv("ENVIRONMENT") == "development":
                print("⚠️  WARNING: Running in development mode with demo Supabase credentials")
                print("📝 To connect to real Supabase:")
                print("   1. Create a project at https://supabase.com")
                print("   2. Update .env file with your project URL and keys")
                print("   3. Run database migrations from docs/database_schema.sql")
                self.url = "https://demo-project.supabase.co"
                self.key = "demo_key"
                self.client = None
                self.admin_client = None
                return
            else:
                raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        try:
            self.client: Client = create_client(self.url, self.key)
        except Exception as e:
            print(f"⚠️  Failed to connect to Supabase: {e}")
            if os.getenv("ENVIRONMENT") == "development":
                print("📝 Running in offline development mode")
                self.client = None
                self.admin_client = None
                return
            else:
                raise
        self.admin_client: Optional[Client] = None
        
        if self.service_key:
            self.admin_client = create_client(self.url, self.service_key)
    
    def get_client(self, admin: bool = False) -> Client:
        """Get Supabase client (admin or regular)"""
        if admin and self.admin_client:
            return self.admin_client
        return self.client

class VendorManager:
    """Handles vendor-related database operations"""
    
    def __init__(self, supabase_manager: SupabaseManager):
        self.supabase = supabase_manager
    
    async def create_vendor(self, vendor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new vendor"""
        try:
            result = self.supabase.get_client().table('vendors').insert(vendor_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error creating vendor: {str(e)}")
    
    async def get_vendor(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """Get vendor by ID"""
        try:
            result = self.supabase.get_client().table('vendors').select('*').eq('id', vendor_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error fetching vendor: {str(e)}")
    
    async def search_vendors(self, query: str) -> List[Dict[str, Any]]:
        """Search vendors by name or other fields"""
        try:
            result = self.supabase.get_client().table('vendors').select('*').ilike('name', f'%{query}%').execute()
            return result.data or []
        except Exception as e:
            raise Exception(f"Error searching vendors: {str(e)}")
    
    async def update_vendor(self, vendor_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update vendor information"""
        try:
            update_data['updated_at'] = datetime.now().isoformat()
            result = self.supabase.get_client().table('vendors').update(update_data).eq('id', vendor_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error updating vendor: {str(e)}")

class DocumentManager:
    """Handles document storage and processing operations"""
    
    def __init__(self, supabase_manager: SupabaseManager):
        self.supabase = supabase_manager
    
    async def upload_document(self, file_path: str, file_data: bytes, document_type: str, 
                            uploaded_by: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Upload document to Supabase storage and create database record"""
        try:
            # Upload to Supabase storage
            storage_path = f"documents/{document_type}/{datetime.now().strftime('%Y/%m')}/{file_path}"
            
            storage_result = self.supabase.get_client().storage.from_('documents').upload(
                storage_path, file_data
            )
            
            if storage_result.status_code != 200:
                raise Exception(f"Storage upload failed: {storage_result.json()}")
            
            # Create document record
            doc_data = {
                'filename': file_path,
                'original_filename': file_path,
                'file_path': storage_path,
                'file_size': len(file_data),
                'document_type': document_type,
                'processing_status': 'pending',
                'uploaded_by': uploaded_by,
                'extracted_data': metadata or {}
            }
            
            result = self.supabase.get_client().table('documents').insert(doc_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            raise Exception(f"Error uploading document: {str(e)}")
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        try:
            result = self.supabase.get_client().table('documents').select('*').eq('id', document_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error fetching document: {str(e)}")
    
    async def update_processing_status(self, document_id: str, status: str, 
                                     extracted_data: Optional[Dict] = None, 
                                     confidence: Optional[float] = None) -> Dict[str, Any]:
        """Update document processing status and extracted data"""
        try:
            update_data = {
                'processing_status': status,
                'processed_at': datetime.now().isoformat()
            }
            
            if extracted_data:
                update_data['extracted_data'] = extracted_data
            if confidence:
                update_data['extraction_confidence'] = confidence
            
            result = self.supabase.get_client().table('documents').update(update_data).eq('id', document_id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            raise Exception(f"Error updating document status: {str(e)}")
    
    async def get_pending_documents(self, document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get documents pending processing"""
        try:
            query = self.supabase.get_client().table('documents').select('*').eq('processing_status', 'pending')
            
            if document_type:
                query = query.eq('document_type', document_type)
            
            result = query.execute()
            return result.data or []
            
        except Exception as e:
            raise Exception(f"Error fetching pending documents: {str(e)}")

class TransactionManager:
    """Handles financial transaction operations"""
    
    def __init__(self, supabase_manager: SupabaseManager):
        self.supabase = supabase_manager
    
    async def create_outgoing_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new outgoing transaction (expense/payment)"""
        try:
            # Ensure proper data types
            if isinstance(transaction_data.get('transaction_date'), date):
                transaction_data['transaction_date'] = transaction_data['transaction_date'].isoformat()
            
            result = self.supabase.get_client().table('outgoing_transactions').insert(transaction_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error creating outgoing transaction: {str(e)}")
    
    async def create_incoming_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new incoming transaction (revenue/sales)"""
        try:
            # Ensure proper data types
            if isinstance(transaction_data.get('transaction_date'), date):
                transaction_data['transaction_date'] = transaction_data['transaction_date'].isoformat()
            
            result = self.supabase.get_client().table('incoming_transactions').insert(transaction_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error creating incoming transaction: {str(e)}")
    
    async def create_statement_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a statement transaction from bank/credit card data"""
        try:
            # Ensure proper data types
            for date_field in ['transaction_date', 'posted_date']:
                if isinstance(transaction_data.get(date_field), date):
                    transaction_data[date_field] = transaction_data[date_field].isoformat()
            
            result = self.supabase.get_client().table('statement_transactions').insert(transaction_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error creating statement transaction: {str(e)}")
    
    async def get_unreconciled_transactions(self, account_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get all unreconciled transactions"""
        try:
            # Get unreconciled outgoing transactions
            outgoing_query = self.supabase.get_client().table('outgoing_transactions').select('*').eq('reconciliation_status', 'unreconciled')
            if account_id:
                outgoing_query = outgoing_query.eq('payment_account_id', account_id)
            outgoing_result = outgoing_query.execute()
            
            # Get unreconciled incoming transactions
            incoming_query = self.supabase.get_client().table('incoming_transactions').select('*').eq('reconciliation_status', 'unreconciled')
            if account_id:
                incoming_query = incoming_query.eq('payment_account_id', account_id)
            incoming_result = incoming_query.execute()
            
            # Get unmatched statement transactions
            statement_query = self.supabase.get_client().table('statement_transactions').select('*').eq('is_matched', False)
            if account_id:
                statement_query = statement_query.eq('payment_account_id', account_id)
            statement_result = statement_query.execute()
            
            return {
                'outgoing': outgoing_result.data or [],
                'incoming': incoming_result.data or [],
                'statements': statement_result.data or []
            }
            
        except Exception as e:
            raise Exception(f"Error fetching unreconciled transactions: {str(e)}")
    
    async def create_reconciliation(self, reconciliation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a reconciliation record linking statement and business transactions"""
        try:
            result = self.supabase.get_client().table('reconciliation_records').insert(reconciliation_data).execute()
            
            # Update the linked transactions as reconciled
            if reconciliation_data.get('business_transaction_type') == 'outgoing':
                await self.update_transaction_reconciliation_status(
                    'outgoing_transactions', 
                    reconciliation_data['business_transaction_id'], 
                    'matched'
                )
            elif reconciliation_data.get('business_transaction_type') == 'incoming':
                await self.update_transaction_reconciliation_status(
                    'incoming_transactions', 
                    reconciliation_data['business_transaction_id'], 
                    'matched'
                )
            
            # Update statement transaction as matched
            await self.update_statement_transaction_match(
                reconciliation_data['statement_transaction_id'], 
                True
            )
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            raise Exception(f"Error creating reconciliation: {str(e)}")
    
    async def update_transaction_reconciliation_status(self, table: str, transaction_id: str, status: str):
        """Update reconciliation status of a transaction"""
        try:
            self.supabase.get_client().table(table).update({
                'reconciliation_status': status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', transaction_id).execute()
        except Exception as e:
            raise Exception(f"Error updating transaction reconciliation status: {str(e)}")
    
    async def update_statement_transaction_match(self, transaction_id: str, is_matched: bool):
        """Update statement transaction match status"""
        try:
            self.supabase.get_client().table('statement_transactions').update({
                'is_matched': is_matched
            }).eq('id', transaction_id).execute()
        except Exception as e:
            raise Exception(f"Error updating statement transaction match: {str(e)}")

class PaymentAccountManager:
    """Handles payment account operations"""
    
    def __init__(self, supabase_manager: SupabaseManager):
        self.supabase = supabase_manager
    
    async def create_payment_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new payment account"""
        try:
            result = self.supabase.get_client().table('payment_accounts').insert(account_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error creating payment account: {str(e)}")
    
    async def get_all_accounts(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all payment accounts"""
        try:
            query = self.supabase.get_client().table('payment_accounts').select('*')
            if active_only:
                query = query.eq('is_active', True)
            
            result = query.execute()
            return result.data or []
        except Exception as e:
            raise Exception(f"Error fetching payment accounts: {str(e)}")
    
    async def update_account_balance(self, account_id: str, new_balance: float) -> Dict[str, Any]:
        """Update account balance"""
        try:
            result = self.supabase.get_client().table('payment_accounts').update({
                'balance': new_balance,
                'updated_at': datetime.now().isoformat()
            }).eq('id', account_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error updating account balance: {str(e)}")

# Utility functions for data type conversion
def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def prepare_for_supabase(data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare data for Supabase insertion by converting types"""
    prepared = {}
    for key, value in data.items():
        if isinstance(value, Decimal):
            prepared[key] = float(value)
        elif isinstance(value, (date, datetime)):
            prepared[key] = value.isoformat()
        else:
            prepared[key] = value
    return prepared