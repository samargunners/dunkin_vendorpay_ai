# 📄 Document Processing Step-by-Step Guide

## 🎯 **Goal: Start Processing Real Financial Documents**

This guide will walk you through setting up and using the VendorPay AI document processing system to scan bank statements, credit card statements, invoices, and other financial documents.

## 📋 **Step 1: Install OCR Dependencies (15 minutes)**

### **Install Tesseract OCR**

#### **Windows Installation:**
```bash
# Method 1: Using Chocolatey (Recommended)
# First install Chocolatey if you don't have it:
# Visit: https://chocolatey.org/install

# Then install Tesseract:
choco install tesseract

# Method 2: Manual Download
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Choose: tesseract-ocr-w64-setup-5.3.3.20231005.exe
# Install to default location: C:\Program Files\Tesseract-OCR\
```

#### **Verify Installation:**
```bash
# Test Tesseract is working
tesseract --version

# Should show something like:
# tesseract 5.3.3
```

### **Install Additional Python Dependencies**
```bash
# Activate your virtual environment
.\venv\Scripts\activate

# Install OCR and image processing packages
pip install pytesseract pillow opencv-python-headless pdf2image

# For PDF processing
pip install PyPDF2 pdfplumber

# For Excel/CSV files
pip install pandas openpyxl
```

## 📋 **Step 2: Set Up Document Storage (10 minutes)**

### **Create Document Directories**
```bash
# Create folders for document processing
mkdir uploads
mkdir uploads\bank_statements
mkdir uploads\credit_cards
mkdir uploads\invoices
mkdir uploads\receipts
mkdir uploads\processed
mkdir uploads\temp
```

### **Update Environment Settings**
```bash
# Add to your .env file:
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png,tiff,csv,xlsx,xls
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## 📋 **Step 3: Test Document Upload Endpoint (20 minutes)**

### **Start the Development Server**
```bash
# Make sure you're in the project directory
cd C:\Projects\Dunkin_vendorpay_ai

# Activate virtual environment
.\venv\Scripts\activate

# Start the server
python dev_server.py
```

### **Create Document Upload Test Script**
Let me create a test script for you to try document uploads.

## 📋 **Step 4: Process Your First Document (30 minutes)**

### **Sample Documents to Try:**
1. **Bank Statement PDF** - Download from your bank's website
2. **Credit Card Statement PDF** - From your credit card company
3. **Invoice Image** - Take a photo of a paper invoice
4. **Receipt Image** - Photo of a grocery/restaurant receipt

### **Processing Workflow:**
1. Upload document via API
2. System detects document type
3. Extracts text using OCR (for images) or PDF parsing
4. Identifies key data (amounts, dates, vendors)
5. Stores structured data in database
6. Returns processing results with confidence scores

## 📋 **Step 5: Verify Results (15 minutes)**

### **Check Processing Results:**
- View extracted transactions
- Verify vendor names are correct
- Check amount accuracy
- Review date extraction
- Validate confidence scores

## 🛠️ **Practical Implementation**

Let me create the actual tools you need to start processing documents right now.

---

## 📊 **Document Types We Support**

### **Bank Statements**
- **Formats**: PDF, CSV download
- **Extracts**: Transaction date, description, amount, balance
- **Vendors**: Merchant names, check numbers
- **Categories**: Auto-categorization by merchant

### **Credit Card Statements**
- **Formats**: PDF, CSV download  
- **Extracts**: Transaction date, merchant, amount, category
- **Features**: Credit vs debit identification
- **Analysis**: Spending patterns, merchant frequency

### **Vendor Invoices**
- **Formats**: PDF, JPG, PNG images
- **Extracts**: Invoice number, date, vendor info, line items
- **Validation**: Tax calculations, payment terms
- **Matching**: Auto-match to existing vendors

### **Receipts**
- **Formats**: JPG, PNG photos
- **Extracts**: Store name, date, items, total amount
- **OCR**: Handles handwritten receipts
- **Categorization**: Expense category assignment

### **Checks**
- **Formats**: JPG, PNG photos
- **Extracts**: Check number, date, payee, amount
- **Validation**: MICR line reading
- **Tracking**: Check clearing status

## 🚀 **Quick Start Commands**

Once we set everything up, you'll be able to process documents with simple commands:

```bash
# Upload and process a bank statement
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@bank_statement.pdf" \
  -F "document_type=bank_statement"

# Process a scanned invoice
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@invoice.jpg" \
  -F "document_type=vendor_invoice"

# Get processing results
curl "http://localhost:8000/api/v1/documents/{document_id}/results"
```

## ⚡ **Expected Processing Times**

- **PDF Bank Statement (5 pages)**: 10-15 seconds
- **Scanned Invoice Image**: 15-25 seconds  
- **Receipt Photo**: 5-10 seconds
- **CSV File**: 2-5 seconds
- **Complex Multi-page PDF**: 30-60 seconds

## 🎯 **Success Criteria**

After completing this guide, you should be able to:
- [x] Upload financial documents via API
- [x] See extracted transaction data
- [x] Verify vendor information is captured
- [x] Review confidence scores for accuracy
- [x] Process multiple document types
- [x] Get structured JSON output from any document

Ready to start? Let's begin with installing the dependencies!