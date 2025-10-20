"""
Document Processing Pipeline

This module handles the processing of various financial documents including:
- Bank statements (PDF, CSV)
- Credit card statements (PDF, CSV) 
- Vendor bills and invoices (PDF, images)
- Handwritten notes (images)
- Sales reports (CSV, Excel)
- Check images

The pipeline extracts relevant financial data and stores it in Supabase.
"""

import os
import re
import cv2
import pytesseract
import pandas as pd
import PyPDF2
from PIL import Image
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date
from decimal import Decimal
import json
import asyncio
from pathlib import Path

from ..core.supabase_manager import SupabaseManager, DocumentManager, TransactionManager

class DocumentProcessor:
    """Main document processing coordinator"""
    
    def __init__(self, supabase_manager: SupabaseManager):
        self.supabase_manager = supabase_manager
        self.document_manager = DocumentManager(supabase_manager)
        self.transaction_manager = TransactionManager(supabase_manager)
        
        # Initialize specialized processors
        self.bank_processor = BankStatementProcessor()
        self.credit_card_processor = CreditCardProcessor()
        self.vendor_bill_processor = VendorBillProcessor()
        self.sales_report_processor = SalesReportProcessor()
        self.handwritten_processor = HandwrittenNoteProcessor()
        self.check_processor = CheckProcessor()
    
    async def process_document(self, document_id: str, file_path: str, document_type: str) -> Dict[str, Any]:
        """Main entry point for document processing"""
        try:
            # Get document info
            document = await self.document_manager.get_document(document_id)
            if not document:
                raise Exception(f"Document {document_id} not found")
            
            # Update status to processing
            await self.document_manager.update_processing_status(document_id, 'processing')
            
            # Route to appropriate processor based on document type
            if document_type == 'bank_statement':
                result = await self.bank_processor.process(file_path)
            elif document_type == 'credit_card_statement':
                result = await self.credit_card_processor.process(file_path)
            elif document_type == 'vendor_bill':
                result = await self.vendor_bill_processor.process(file_path)
            elif document_type == 'sales_report':
                result = await self.sales_report_processor.process(file_path)
            elif document_type == 'handwritten_note':
                result = await self.handwritten_processor.process(file_path)
            elif document_type == 'check':
                result = await self.check_processor.process(file_path)
            else:
                raise Exception(f"Unsupported document type: {document_type}")
            
            # Store extracted data
            await self.document_manager.update_processing_status(
                document_id, 
                'completed', 
                result['extracted_data'], 
                result.get('confidence', 0.8)
            )
            
            # Create transactions from extracted data
            await self._create_transactions_from_data(result['extracted_data'], document_id, document_type)
            
            return result
            
        except Exception as e:
            # Update status to failed
            await self.document_manager.update_processing_status(document_id, 'failed')
            raise Exception(f"Error processing document {document_id}: {str(e)}")
    
    async def _create_transactions_from_data(self, extracted_data: Dict[str, Any], 
                                           document_id: str, document_type: str):
        """Create transaction records from extracted data"""
        try:
            if document_type in ['bank_statement', 'credit_card_statement']:
                # Create statement transactions
                for transaction in extracted_data.get('transactions', []):
                    transaction['document_id'] = document_id
                    await self.transaction_manager.create_statement_transaction(transaction)
            
            elif document_type == 'vendor_bill':
                # Create outgoing transaction
                transaction_data = {
                    'document_id': document_id,
                    'vendor_id': extracted_data.get('vendor_id'),
                    'amount': extracted_data.get('amount'),
                    'transaction_date': extracted_data.get('due_date') or extracted_data.get('invoice_date'),
                    'payment_method': 'pending',
                    'category': extracted_data.get('category', 'vendor_payment'),
                    'description': extracted_data.get('description'),
                    'reconciliation_status': 'unreconciled',
                    'is_manual_entry': False
                }
                await self.transaction_manager.create_outgoing_transaction(transaction_data)
            
            elif document_type == 'sales_report':
                # Create incoming transactions
                for transaction in extracted_data.get('transactions', []):
                    transaction['document_id'] = document_id
                    await self.transaction_manager.create_incoming_transaction(transaction)
            
        except Exception as e:
            print(f"Warning: Could not create transactions from extracted data: {str(e)}")

class BankStatementProcessor:
    """Processes bank statements (PDF/CSV)"""
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """Process bank statement file"""
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                return await self._process_pdf_statement(file_path)
            elif file_extension == '.csv':
                return await self._process_csv_statement(file_path)
            else:
                raise Exception(f"Unsupported bank statement format: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Error processing bank statement: {str(e)}")
    
    async def _process_pdf_statement(self, file_path: str) -> Dict[str, Any]:
        """Process PDF bank statement using OCR and text extraction"""
        extracted_data = {
            'account_info': {},
            'transactions': [],
            'statement_period': {},
            'balances': {}
        }
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                for page in pdf_reader.pages:
                    full_text += page.extract_text() + "\n"
            
            # Extract account information
            account_match = re.search(r'Account\s+(?:Number|#)?\s*:?\s*(\w+)', full_text, re.IGNORECASE)
            if account_match:
                extracted_data['account_info']['account_number'] = account_match.group(1)
            
            # Extract statement period
            date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            period_match = re.search(r'(?:Statement\s+Period|From|Beginning)\s*:?\s*' + date_pattern + r'\s*(?:to|through|-)\s*' + date_pattern, full_text, re.IGNORECASE)
            if period_match:
                extracted_data['statement_period'] = {
                    'start_date': self._parse_date(period_match.group(1)),
                    'end_date': self._parse_date(period_match.group(2))
                }
            
            # Extract transactions using regex patterns
            # This is a simplified pattern - you'll need to adjust for your specific bank formats
            transaction_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(.*?)\s+(-?\$?[\d,]+\.?\d*)'
            transactions = re.findall(transaction_pattern, full_text)
            
            for trans in transactions:
                try:
                    transaction = {
                        'transaction_date': self._parse_date(trans[0]),
                        'description': trans[1].strip(),
                        'amount': self._parse_amount(trans[2]),
                        'transaction_type': 'debit' if '-' in trans[2] or float(self._parse_amount(trans[2])) < 0 else 'credit'
                    }
                    extracted_data['transactions'].append(transaction)
                except:
                    continue  # Skip malformed transactions
            
            return {
                'extracted_data': extracted_data,
                'confidence': 0.7,  # PDF text extraction is fairly reliable
                'processing_method': 'pdf_text_extraction'
            }
            
        except Exception as e:
            raise Exception(f"Error processing PDF bank statement: {str(e)}")
    
    async def _process_csv_statement(self, file_path: str) -> Dict[str, Any]:
        """Process CSV bank statement"""
        try:
            df = pd.read_csv(file_path)
            
            # Common CSV column mappings (adjust based on your bank's format)
            column_mappings = {
                'Date': ['date', 'transaction_date', 'posting_date'],
                'Description': ['description', 'memo', 'payee'],
                'Amount': ['amount', 'transaction_amount'],
                'Balance': ['balance', 'running_balance'],
                'Type': ['type', 'transaction_type', 'debit_credit']
            }
            
            # Map columns to standard names
            mapped_columns = {}
            for std_name, possible_names in column_mappings.items():
                for col in df.columns:
                    if col.lower().strip() in [name.lower() for name in possible_names]:
                        mapped_columns[std_name] = col
                        break
            
            transactions = []
            for _, row in df.iterrows():
                try:
                    transaction = {
                        'transaction_date': self._parse_date(str(row[mapped_columns.get('Date', df.columns[0])])),
                        'description': str(row[mapped_columns.get('Description', df.columns[1])]),
                        'amount': float(str(row[mapped_columns.get('Amount', df.columns[2])]).replace('$', '').replace(',', '')),
                    }
                    
                    # Determine transaction type
                    if 'Type' in mapped_columns:
                        transaction['transaction_type'] = str(row[mapped_columns['Type']]).lower()
                    else:
                        transaction['transaction_type'] = 'debit' if transaction['amount'] < 0 else 'credit'
                    
                    transactions.append(transaction)
                except:
                    continue  # Skip malformed rows
            
            return {
                'extracted_data': {
                    'transactions': transactions,
                    'total_transactions': len(transactions)
                },
                'confidence': 0.9,  # CSV parsing is very reliable
                'processing_method': 'csv_parsing'
            }
            
        except Exception as e:
            raise Exception(f"Error processing CSV bank statement: {str(e)}")
    
    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats to ISO format"""
        try:
            # Try different date formats
            date_formats = ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y', '%m-%d-%y']
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str.strip(), fmt).date()
                    return parsed_date.isoformat()
                except ValueError:
                    continue
            
            return date_str  # Return original if can't parse
        except:
            return date_str
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.-]', '', amount_str)
            return float(cleaned)
        except:
            return 0.0

class CreditCardProcessor:
    """Processes credit card statements"""
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """Process credit card statement - similar to bank statement but with credit card specific fields"""
        # Implementation similar to BankStatementProcessor but adapted for credit card statements
        # Focus on: merchant names, categories, rewards, payments, balances
        
        extracted_data = {
            'account_info': {},
            'transactions': [],
            'payment_info': {},
            'balances': {}
        }
        
        # For now, use similar logic to bank statements
        bank_processor = BankStatementProcessor()
        result = await bank_processor.process(file_path)
        
        # Add credit card specific processing here
        return result

class VendorBillProcessor:
    """Processes vendor bills and invoices"""
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """Process vendor bill/invoice"""
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                return await self._process_pdf_invoice(file_path)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff']:
                return await self._process_image_invoice(file_path)
            else:
                raise Exception(f"Unsupported vendor bill format: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Error processing vendor bill: {str(e)}")
    
    async def _process_pdf_invoice(self, file_path: str) -> Dict[str, Any]:
        """Process PDF invoice"""
        extracted_data = {
            'vendor_name': '',
            'vendor_address': '',
            'invoice_number': '',
            'invoice_date': '',
            'due_date': '',
            'amount': 0.0,
            'line_items': [],
            'category': 'vendor_payment'
        }
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                for page in pdf_reader.pages:
                    full_text += page.extract_text() + "\n"
            
            # Extract vendor name (usually at the top)
            vendor_match = re.search(r'^([A-Z][A-Za-z\s&,.]+)(?:\n|\r)', full_text)
            if vendor_match:
                extracted_data['vendor_name'] = vendor_match.group(1).strip()
            
            # Extract invoice number
            invoice_match = re.search(r'(?:Invoice|Bill)\s*#?\s*:?\s*(\w+)', full_text, re.IGNORECASE)
            if invoice_match:
                extracted_data['invoice_number'] = invoice_match.group(1)
            
            # Extract dates
            date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            invoice_date_match = re.search(r'(?:Invoice\s+Date|Date)\s*:?\s*' + date_pattern, full_text, re.IGNORECASE)
            if invoice_date_match:
                extracted_data['invoice_date'] = self._parse_date(invoice_date_match.group(1))
            
            due_date_match = re.search(r'(?:Due\s+Date|Payment\s+Due)\s*:?\s*' + date_pattern, full_text, re.IGNORECASE)
            if due_date_match:
                extracted_data['due_date'] = self._parse_date(due_date_match.group(1))
            
            # Extract total amount
            amount_match = re.search(r'(?:Total|Amount\s+Due|Balance\s+Due)\s*:?\s*\$?([\d,]+\.?\d*)', full_text, re.IGNORECASE)
            if amount_match:
                extracted_data['amount'] = float(amount_match.group(1).replace(',', ''))
            
            return {
                'extracted_data': extracted_data,
                'confidence': 0.75,
                'processing_method': 'pdf_text_extraction'
            }
            
        except Exception as e:
            raise Exception(f"Error processing PDF invoice: {str(e)}")
    
    async def _process_image_invoice(self, file_path: str) -> Dict[str, Any]:
        """Process invoice image using OCR"""
        try:
            # Load and preprocess image
            image = cv2.imread(file_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply image preprocessing for better OCR
            gray = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Use pytesseract for OCR
            text = pytesseract.image_to_string(gray)
            
            # Process extracted text similar to PDF processing
            extracted_data = {
                'vendor_name': '',
                'invoice_number': '',
                'invoice_date': '',
                'due_date': '',
                'amount': 0.0,
                'raw_text': text,
                'category': 'vendor_payment'
            }
            
            # Apply same regex patterns as PDF processing
            # ... (similar extraction logic)
            
            return {
                'extracted_data': extracted_data,
                'confidence': 0.6,  # OCR is less reliable than PDF text
                'processing_method': 'ocr_extraction'
            }
            
        except Exception as e:
            raise Exception(f"Error processing invoice image: {str(e)}")
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        # Same implementation as BankStatementProcessor
        try:
            date_formats = ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y', '%m-%d-%y']
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str.strip(), fmt).date()
                    return parsed_date.isoformat()
                except ValueError:
                    continue
            
            return date_str
        except:
            return date_str

class SalesReportProcessor:
    """Processes sales reports (CSV/Excel)"""
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """Process sales report file"""
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise Exception(f"Unsupported sales report format: {file_extension}")
            
            transactions = []
            
            # Common sales report column mappings
            column_mappings = {
                'Date': ['date', 'sale_date', 'transaction_date'],
                'Amount': ['amount', 'total', 'sale_amount'],
                'Payment_Method': ['payment_method', 'payment_type', 'tender_type'],
                'Terminal': ['terminal', 'register', 'pos'],
                'Transaction_ID': ['transaction_id', 'ticket_number', 'receipt_number']
            }
            
            # Map columns
            mapped_columns = {}
            for std_name, possible_names in column_mappings.items():
                for col in df.columns:
                    if col.lower().strip() in [name.lower() for name in possible_names]:
                        mapped_columns[std_name] = col
                        break
            
            for _, row in df.iterrows():
                try:
                    transaction = {
                        'transaction_date': self._parse_date(str(row[mapped_columns.get('Date', df.columns[0])])),
                        'amount': float(str(row[mapped_columns.get('Amount', df.columns[1])]).replace('$', '').replace(',', '')),
                        'payment_method': str(row[mapped_columns.get('Payment_Method', 'card')]).lower(),
                        'revenue_type': 'sales',
                        'reconciliation_status': 'unreconciled'
                    }
                    
                    # Add optional fields
                    if 'Terminal' in mapped_columns:
                        transaction['terminal_id'] = str(row[mapped_columns['Terminal']])
                    if 'Transaction_ID' in mapped_columns:
                        transaction['transaction_id'] = str(row[mapped_columns['Transaction_ID']])
                    
                    transactions.append(transaction)
                except:
                    continue
            
            return {
                'extracted_data': {
                    'transactions': transactions,
                    'total_sales': sum(t['amount'] for t in transactions),
                    'transaction_count': len(transactions)
                },
                'confidence': 0.95,
                'processing_method': 'structured_data_parsing'
            }
            
        except Exception as e:
            raise Exception(f"Error processing sales report: {str(e)}")
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        try:
            date_formats = ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y', '%m-%d-%y']
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str.strip(), fmt).date()
                    return parsed_date.isoformat()
                except ValueError:
                    continue
            
            return date_str
        except:
            return date_str

class HandwrittenNoteProcessor:
    """Processes handwritten notes using OCR"""
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """Process handwritten note image"""
        try:
            # Load image
            image = cv2.imread(file_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhanced preprocessing for handwriting
            gray = cv2.medianBlur(gray, 3)
            gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
            
            # Use pytesseract with handwriting-optimized config
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(gray, config=custom_config)
            
            extracted_data = {
                'raw_text': text,
                'vendor_name': '',
                'amount': 0.0,
                'description': text,
                'requires_manual_review': True,
                'category': 'manual_entry'
            }
            
            # Try to extract amount from text
            amount_match = re.search(r'\$?([\d,]+\.?\d*)', text)
            if amount_match:
                try:
                    extracted_data['amount'] = float(amount_match.group(1).replace(',', ''))
                except:
                    pass
            
            return {
                'extracted_data': extracted_data,
                'confidence': 0.4,  # Handwriting OCR is less reliable
                'processing_method': 'handwriting_ocr'
            }
            
        except Exception as e:
            raise Exception(f"Error processing handwritten note: {str(e)}")

class CheckProcessor:
    """Processes check images"""
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """Process check image"""
        try:
            # Load image
            image = cv2.imread(file_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Preprocess for check OCR
            gray = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Use pytesseract
            text = pytesseract.image_to_string(gray)
            
            extracted_data = {
                'raw_text': text,
                'payee': '',
                'amount': 0.0,
                'check_number': '',
                'date': '',
                'memo': '',
                'category': 'check_payment'
            }
            
            # Extract check-specific information
            # Check number (usually in top right)
            check_num_match = re.search(r'(?:Check|#)\s*(\d+)', text, re.IGNORECASE)
            if check_num_match:
                extracted_data['check_number'] = check_num_match.group(1)
            
            # Amount (look for dollar amount)
            amount_match = re.search(r'\$?([\d,]+\.?\d*)', text)
            if amount_match:
                try:
                    extracted_data['amount'] = float(amount_match.group(1).replace(',', ''))
                except:
                    pass
            
            # Date
            date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
            if date_match:
                extracted_data['date'] = self._parse_date(date_match.group(1))
            
            return {
                'extracted_data': extracted_data,
                'confidence': 0.7,
                'processing_method': 'check_ocr'
            }
            
        except Exception as e:
            raise Exception(f"Error processing check: {str(e)}")
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        try:
            date_formats = ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y', '%m-%d-%y']
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str.strip(), fmt).date()
                    return parsed_date.isoformat()
                except ValueError:
                    continue
            
            return date_str
        except:
            return date_str