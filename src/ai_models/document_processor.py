"""
Document Processing AI Model

Handles OCR, text extraction, and document classification for invoices,
receipts, contracts, and other vendor-related documents.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import tempfile
import re
from datetime import datetime
from dataclasses import dataclass

# Optional imports for enhanced functionality
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """Enhanced metadata extracted from processed documents."""
    document_type: str
    confidence_score: float
    extracted_fields: Dict[str, str]
    processing_time: float
    file_size: int
    extraction_method: str
    text_content: str
    financial_data: Dict[str, str]
    processing_status: str


class DocumentProcessor:
    """AI-powered document processing with OCR capabilities."""
    
    def __init__(self, model_config: Optional[Dict] = None, tesseract_path: Optional[str] = None):
        """
        Initialize the document processor.
        
        Args:
            model_config: Configuration for AI models
            tesseract_path: Path to tesseract executable (auto-detect if None)
        """
        self.logger = logging.getLogger(__name__)
        self.config = model_config or {}
        self.tesseract_path = tesseract_path
        self._initialize_models()
        
        # Supported file types
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        self.pdf_extensions = {'.pdf'}
        self.text_extensions = {'.txt', '.csv', '.json'}
    
    def _initialize_models(self) -> None:
        """Initialize AI models and OCR engine."""
        self.logger.info("Initializing document processing models...")
        
        # Setup tesseract OCR
        if PYTESSERACT_AVAILABLE:
            self._setup_tesseract()
        else:
            self.logger.warning("Tesseract OCR not available")
    
    def _setup_tesseract(self):
        """Setup tesseract OCR engine"""
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        else:
            # Try common Windows paths
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    self.logger.info(f"Found Tesseract at: {path}")
                    break
            else:
                self.logger.warning("Tesseract not found. OCR will use fallback processing.")
    
    def process_document(self, file_path: Path) -> DocumentMetadata:
        """
        Process a document and extract relevant information.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            DocumentMetadata: Extracted information and metadata
        """
        start_time = datetime.now()
        file_path = Path(file_path)
        
        try:
            # Extract text based on file type
            extraction_result = self._extract_text_advanced(file_path)
            
            # Classify document type
            doc_type = self._classify_document_advanced(extraction_result['text'])
            
            # Extract structured fields
            fields = self._extract_structured_fields(extraction_result['text'], doc_type)
            
            # Analyze financial data
            financial_data = self._extract_financial_data(extraction_result['text'])
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return DocumentMetadata(
                document_type=doc_type,
                confidence_score=extraction_result['confidence'],
                extracted_fields=fields,
                processing_time=processing_time,
                file_size=file_path.stat().st_size if file_path.exists() else 0,
                extraction_method=extraction_result['method'],
                text_content=extraction_result['text'],
                financial_data=financial_data,
                processing_status='success'
            )
            
        except Exception as e:
            self.logger.error(f"Document processing failed: {e}")
            return DocumentMetadata(
                document_type='unknown',
                confidence_score=0.0,
                extracted_fields={},
                processing_time=(datetime.now() - start_time).total_seconds(),
                file_size=0,
                extraction_method='error',
                text_content=f'[Processing Error: {str(e)}]',
                financial_data={},
                processing_status='failed'
            )
    
    def _extract_text_advanced(self, file_path: Path) -> Dict[str, Union[str, float]]:
        """Enhanced text extraction with multiple methods"""
        extension = file_path.suffix.lower()
        
        if extension in self.image_extensions:
            return self._extract_image_text_ocr(file_path)
        elif extension in self.pdf_extensions:
            return self._extract_pdf_text_advanced(file_path)
        elif extension in self.text_extensions:
            return self._extract_text_file_content(file_path)
        else:
            return {
                'text': f"[Unsupported file type: {extension}]",
                'confidence': 0.0,
                'method': 'unsupported'
            }
    
    def _extract_image_text_ocr(self, file_path: Path) -> Dict[str, Union[str, float]]:
        """Extract text from images using OCR"""
        if not PYTESSERACT_AVAILABLE or not PIL_AVAILABLE:
            return {
                'text': '[OCR libraries not available]',
                'confidence': 0.0,
                'method': 'error'
            }
        
        try:
            # Load and preprocess image
            image = Image.open(file_path)
            processed_image = self._preprocess_image(image)
            
            # Extract text with confidence
            if PYTESSERACT_AVAILABLE:
                text_data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
                
                # Calculate average confidence
                confidences = [int(conf) for conf in text_data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                # Extract text
                extracted_text = pytesseract.image_to_string(processed_image)
                
                return {
                    'text': extracted_text.strip(),
                    'confidence': avg_confidence,
                    'method': 'tesseract_ocr'
                }
            else:
                return {
                    'text': '[Tesseract OCR not available]',
                    'confidence': 0.0,
                    'method': 'error'
                }
                
        except Exception as e:
            self.logger.error(f"OCR extraction failed for {file_path}: {str(e)}")
            return {
                'text': f"[OCR Error: {str(e)}]",
                'confidence': 0.0,
                'method': 'error'
            }
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results"""
        if not PIL_AVAILABLE:
            return image
            
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        # Apply slight gaussian blur to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return image
    
    def _extract_pdf_text_advanced(self, file_path: Path) -> Dict[str, Union[str, float]]:
        """Extract text from PDF using multiple methods"""
        # Try direct text extraction first
        if PYPDF2_AVAILABLE:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    
                    if text.strip():  # If we got meaningful text
                        return {
                            'text': text,
                            'confidence': 95.0,
                            'method': 'pdf_direct_extraction'
                        }
            except Exception as e:
                self.logger.warning(f"Direct PDF extraction failed: {e}")
        
        # Fall back to OCR if direct extraction failed or no text
        if PDF2IMAGE_AVAILABLE and PYTESSERACT_AVAILABLE:
            try:
                # Convert PDF to images
                pages = pdf2image.convert_from_path(file_path)
                
                extracted_texts = []
                confidences = []
                
                for i, page in enumerate(pages):
                    # Save page as temporary image
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        page.save(temp_file.name, 'PNG')
                        
                        # Extract text from page
                        result = self._extract_image_text_ocr(Path(temp_file.name))
                        extracted_texts.append(f"--- Page {i+1} ---\n{result['text']}")
                        confidences.append(result['confidence'])
                        
                        # Clean up temp file
                        os.unlink(temp_file.name)
                
                # Combine all pages
                full_text = '\n\n'.join(extracted_texts)
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                return {
                    'text': full_text,
                    'confidence': avg_confidence,
                    'method': 'pdf_to_image_ocr',
                    'pages': len(pages)
                }
                
            except Exception as e:
                self.logger.error(f"PDF OCR extraction failed for {file_path}: {str(e)}")
        
        return {
            'text': f"[PDF Processing Error: Required libraries not available]",
            'confidence': 0.0,
            'method': 'error'
        }
    
    def _extract_text_file_content(self, file_path: Path) -> Dict[str, Union[str, float]]:
        """Extract content from text-based files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'text': content,
                'confidence': 100.0,
                'method': 'direct_text_read'
            }
            
        except Exception as e:
            self.logger.error(f"Text extraction failed for {file_path}: {str(e)}")
            return {
                'text': f"[Text Read Error: {str(e)}]",
                'confidence': 0.0,
                'method': 'error'
            }
    
    def _classify_document_advanced(self, text: str) -> str:
        """Advanced document classification based on content"""
        if not text or text.startswith('['):
            return 'unknown'
        
        text_lower = text.lower()
        
        # Check for invoice indicators
        invoice_keywords = ['invoice', 'bill to', 'due date', 'subtotal', 'tax', 'total amount']
        if sum(1 for keyword in invoice_keywords if keyword in text_lower) >= 2:
            return 'invoice'
        
        # Check for bank statement indicators  
        bank_keywords = ['bank statement', 'balance', 'deposit', 'debit', 'credit', 'account']
        if sum(1 for keyword in bank_keywords if keyword in text_lower) >= 2:
            return 'bank_statement'
        
        # Check for check indicators
        check_keywords = ['check', 'pay to', 'dollars', 'routing number']
        if sum(1 for keyword in check_keywords if keyword in text_lower) >= 2:
            return 'check'
        
        # Check for sales report indicators
        sales_keywords = ['sales report', 'daily sales', 'units', 'payment methods']
        if sum(1 for keyword in sales_keywords if keyword in text_lower) >= 2:
            return 'sales_report'
        
        # Check for receipt indicators
        receipt_keywords = ['receipt', 'total', 'cash', 'credit card', 'thank you']
        if sum(1 for keyword in receipt_keywords if keyword in text_lower) >= 2:
            return 'receipt'
        
        return 'general_document'
    
    def _extract_financial_data(self, text: str) -> Dict[str, str]:
        """Extract financial information from text"""
        financial_data = {}
        
        if not text or text.startswith('['):
            return financial_data
        
        # Extract monetary amounts
        amounts = re.findall(r'\$[\d,]+\.?\d*', text)
        if amounts:
            financial_data['amounts_found'] = amounts
            financial_data['total_amounts'] = str(len(amounts))
            
            # Try to identify the main total
            for amount in reversed(amounts):  # Often the total is at the end
                if 'total' in text.lower()[text.lower().find(amount.lower())-20:text.lower().find(amount.lower())+20]:
                    financial_data['main_total'] = amount
                    break
        
        # Extract dates
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\w+ \d{1,2}, \d{4}\b', text)
        if dates:
            financial_data['dates_found'] = dates
            
        # Extract account numbers (partial)
        account_numbers = re.findall(r'\*+[-]?\d{4}', text)
        if account_numbers:
            financial_data['account_numbers'] = account_numbers
        
        return financial_data
    
    def _extract_structured_fields(self, text: str, doc_type: str) -> Dict[str, str]:
        """Extract structured fields based on document type"""
        fields = {}
        
        if doc_type == "invoice":
            fields.update(self._extract_invoice_fields(text))
        elif doc_type == "bank_statement":
            fields.update(self._extract_bank_statement_fields(text))
        elif doc_type == "check":
            fields.update(self._extract_check_fields(text))
        elif doc_type == "sales_report":
            fields.update(self._extract_sales_report_fields(text))
        elif doc_type == "receipt":
            fields.update(self._extract_receipt_fields(text))
        
        return fields
    
    def _extract_invoice_fields(self, text: str) -> Dict[str, str]:
        """Extract fields specific to invoices."""
        fields = {}
        
        # Invoice number
        invoice_match = re.search(r'invoice\s*#?:?\s*([A-Z0-9-]+)', text, re.IGNORECASE)
        if invoice_match:
            fields['invoice_number'] = invoice_match.group(1)
        
        # Vendor name (look for "From:" or similar)
        vendor_match = re.search(r'from:?\s*\n?([^\n]+)', text, re.IGNORECASE)
        if vendor_match:
            fields['vendor_name'] = vendor_match.group(1).strip()
        
        # Due date
        due_match = re.search(r'due\s+date:?\s*([^\n]+)', text, re.IGNORECASE)
        if due_match:
            fields['due_date'] = due_match.group(1).strip()
        
        # Total amount
        total_match = re.search(r'total:?\s*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if total_match:
            fields['total_amount'] = total_match.group(1)
        
        return fields
    
    def _extract_bank_statement_fields(self, text: str) -> Dict[str, str]:
        """Extract fields specific to bank statements."""
        fields = {}
        
        # Balance
        balance_match = re.search(r'balance:?\s*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if balance_match:
            fields['balance'] = balance_match.group(1)
        
        # Account info
        account_match = re.search(r'account\s*#?:?\s*([X*\d-]+)', text, re.IGNORECASE)
        if account_match:
            fields['account_number'] = account_match.group(1)
        
        return fields
    
    def _extract_check_fields(self, text: str) -> Dict[str, str]:
        """Extract fields specific to checks."""
        fields = {}
        
        # Check number
        check_match = re.search(r'check\s*#?:?\s*(\d+)', text, re.IGNORECASE)
        if check_match:
            fields['check_number'] = check_match.group(1)
        
        # Pay to
        payto_match = re.search(r'pay\s+to:?\s*([^\n]+)', text, re.IGNORECASE)
        if payto_match:
            fields['pay_to'] = payto_match.group(1).strip()
        
        # Amount
        amount_match = re.search(r'amount:?\s*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if amount_match:
            fields['amount'] = amount_match.group(1)
        
        return fields
    
    def _extract_sales_report_fields(self, text: str) -> Dict[str, str]:
        """Extract fields specific to sales reports."""
        fields = {}
        
        # Location
        location_match = re.search(r'location:?\s*([^\n]+)', text, re.IGNORECASE)
        if location_match:
            fields['location'] = location_match.group(1).strip()
        
        # Total sales
        total_match = re.search(r'total:?\s*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if total_match:
            fields['total_sales'] = total_match.group(1)
        
        return fields
    
    def _extract_receipt_fields(self, text: str) -> Dict[str, str]:
        """Extract fields specific to receipts."""
        fields = {}
        
        # Merchant name (usually at the top)
        lines = text.split('\n')
        if lines:
            fields['merchant_name'] = lines[0].strip()
        
        # Total amount
        total_match = re.search(r'total:?\s*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if total_match:
            fields['total_amount'] = total_match.group(1)
        
        # Payment method
        if 'cash' in text.lower():
            fields['payment_method'] = 'Cash'
        elif 'credit' in text.lower():
            fields['payment_method'] = 'Credit Card'
        elif 'debit' in text.lower():
            fields['payment_method'] = 'Debit Card'
        
        return fields


def test_document_processor():
    """Test the document processor with sample files"""
    processor = DocumentProcessor()
    
    # Test with sample documents
    sample_docs = [
        "data/uploads/vendor_invoices/sample_invoice_abc_coffee_20240115.txt",
        "data/uploads/bank_statements/sample_statement_202401.csv",
        "data/uploads/checks/sample_check_1234.json",
        "data/uploads/sales_reports/daily_sales_20240118.txt",
        "data/uploads/handwritten_notes/manager_notes_20240115.txt"
    ]
    
    print("🔍 Testing Enhanced Document Processor...")
    
    results = []
    for doc_path in sample_docs:
        if os.path.exists(doc_path):
            print(f"\n📄 Processing: {doc_path}")
            result = processor.process_document(Path(doc_path))
            
            print(f"   Type: {result.document_type}")
            print(f"   Status: {result.processing_status}")
            print(f"   Method: {result.extraction_method}")
            print(f"   Text length: {len(result.text_content)} characters")
            print(f"   Confidence: {result.confidence_score:.1f}%")
            print(f"   Processing time: {result.processing_time:.2f}s")
            
            if result.extracted_fields:
                print(f"   Key fields: {list(result.extracted_fields.keys())}")
            
            if result.financial_data:
                print(f"   Financial data: {list(result.financial_data.keys())}")
            
            results.append(result)
        else:
            print(f"❌ File not found: {doc_path}")
    
    print(f"\n✅ Enhanced document processor testing complete!")
    print(f"📊 Processed {len(results)} documents successfully")
    
    return results


if __name__ == "__main__":
    test_document_processor()