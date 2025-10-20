# Document Upload Guide for VendorPay AI

## 🎯 Quick Start - Upload Your Documents

### Method 1: Web Interface (Easiest) 🌐
1. **Open**: http://localhost:8000/docs
2. **Find**: `POST /upload` endpoint
3. **Click**: "Try it out"
4. **Upload**: Choose your file and click "Execute"

### Method 2: Python Script 🐍
```bash
# Upload any document (auto-detects type)
python upload_document.py path/to/your/document.pdf

# Upload with specific document type
python upload_document.py invoice.pdf vendor_invoice
python upload_document.py statement.csv bank_statement
```

### Method 3: cURL Command Line 💻
```bash
# Basic upload
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/document.pdf" \
  -F "doc_type=auto_detect"

# Upload with specific type
curl -X POST "http://localhost:8000/upload" \
  -F "file=@invoice.pdf" \
  -F "doc_type=vendor_invoice"
```

### Method 4: PowerShell (Windows) 💼
```powershell
# Upload using PowerShell
$uri = "http://localhost:8000/upload"
$filePath = "C:\path\to\your\document.pdf"
$form = @{
    file = Get-Item -Path $filePath
    doc_type = "auto_detect"
}
Invoke-RestMethod -Uri $uri -Method Post -Form $form
```

## 📁 Sample Documents Ready for Testing

We've created sample documents you can upload right now:

```bash
# Test with sample invoice
python upload_document.py data/uploads/vendor_invoices/sample_invoice_abc_coffee_20240115.txt

# Test with sample bank statement  
python upload_document.py data/uploads/bank_statements/sample_statement_202401.csv

# Test with sample check
python upload_document.py data/uploads/checks/sample_check_1234.json

# Test with sample sales report
python upload_document.py data/uploads/sales_reports/daily_sales_20240118.txt
```

## 🤖 What Happens After Upload

1. **File Validation**: System checks file type and size
2. **Storage**: Document saved in organized directory structure  
3. **AI Processing**: Automatic text extraction and analysis
4. **Classification**: Document type detection (invoice, statement, etc.)
5. **Data Extraction**: Key fields like amounts, dates, vendor info
6. **Results**: JSON response with all extracted information

## 📋 Supported Document Types

- ✅ **Vendor Invoices** (.pdf, .txt, .jpg, .png)
- ✅ **Bank Statements** (.csv, .pdf, .txt)
- ✅ **Checks** (.json, .pdf, .jpg, .png)
- ✅ **Sales Reports** (.txt, .csv, .pdf)
- ✅ **Receipts** (.jpg, .png, .pdf)
- ✅ **Handwritten Notes** (.jpg, .png, .pdf)
- ✅ **General Documents** (any text-based file)

## 🔍 Viewing Uploaded Documents

### List All Documents
- **Web**: http://localhost:8000/docs → `GET /documents`
- **cURL**: `curl http://localhost:8000/documents`

### Get Specific Document
- **Web**: http://localhost:8000/docs → `GET /documents/{file_id}`
- **cURL**: `curl http://localhost:8000/documents/YOUR_FILE_ID`

### Process Document with AI
- **Web**: http://localhost:8000/docs → `POST /documents/{file_id}/process`
- **cURL**: `curl -X POST http://localhost:8000/documents/YOUR_FILE_ID/process`

## ⚡ Quick Test Commands

```bash
# 1. Start the server
python dev_server_enhanced.py

# 2. Upload a sample document (in another terminal)
python upload_document.py data/uploads/vendor_invoices/sample_invoice_abc_coffee_20240115.txt

# 3. Run comprehensive tests
python quick_test.py
```

## 🎉 Expected Results

After uploading, you'll get:
- ✅ **File ID** for tracking
- ✅ **Document Type** (auto-detected)
- ✅ **Extracted Text** with confidence score
- ✅ **Key Fields** (vendor, amounts, dates)
- ✅ **Financial Data** (totals, account numbers)
- ✅ **Processing Status** and metadata

Ready to upload your first document! 🚀