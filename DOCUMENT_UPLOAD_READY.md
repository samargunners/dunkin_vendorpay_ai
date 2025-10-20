# Document Upload System - Step by Step Guide

## 🎯 **Current Status: READY FOR DOCUMENT UPLOAD!**

Your VendorPay AI system now has:
✅ Directory structure created (19 directories)
✅ Document upload API endpoints  
✅ File processing workflow
✅ Sample documents for testing
✅ Development server running

## 📁 **Where Your Documents Go**

```
📁 data/uploads/
├── 📁 bank_statements/      👈 Bank PDFs and CSVs go here
├── 📁 credit_cards/         👈 Credit card statements go here  
├── 📁 vendor_invoices/      👈 Vendor bills and invoices go here
├── 📁 handwritten_notes/    👈 Photo receipts go here
├── 📁 sales_reports/        👈 Daily sales data goes here
└── 📁 checks/               👈 Check images go here
```

## 🚀 **How to Upload Documents (3 Ways)**

### **Method 1: API Documentation (Easiest)**
1. Open: http://localhost:8000/docs
2. Find "Document Upload" section
3. Click "POST /api/v1/documents/upload"
4. Click "Try it out"
5. Upload your file and fill in details
6. Click "Execute"

### **Method 2: Command Line (Quick)**
```bash
# Upload a bank statement
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@path/to/your/statement.pdf" \
  -F "doc_type=bank_statement" \
  -F "source=chase"

# Upload an invoice
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@path/to/your/invoice.pdf" \
  -F "doc_type=vendor_invoice" \
  -F "source=sysco"
```

### **Method 3: Direct File Drop**
Simply copy files directly to:
```
data/uploads/bank_statements/your_statement.pdf
data/uploads/vendor_invoices/your_invoice.pdf
```

## 📋 **Document Types You Can Upload**

| Document Type | Use This Value | Examples |
|---------------|----------------|----------|
| Bank statements | `bank_statement` | Monthly statements, transaction exports |
| Credit card statements | `credit_card` | CC statements, payment receipts |
| Vendor invoices | `vendor_invoice` | Food supplier bills, utility bills |
| Handwritten notes | `handwritten_note` | Receipt photos, manual logs |
| Sales reports | `sales_report` | Daily sales, POS exports |
| Check images | `check_image` | Check photos (front/back) |

## 📊 **File Naming Convention**

Your files get automatically renamed to:
```
{doc_type}_{source}_{YYYYMMDD_HHMMSS}_{uuid}.{ext}

Examples:
bank_stmt_chase_20241020_143022_a1b2c3d4.pdf
vendor_inv_sysco_20241020_143155_b2c3d4e5.pdf
cc_stmt_amex_20241020_143301_c3d4e5f6.pdf
```

## ⚡ **Quick Test Commands**

```bash
# 1. Check system health
curl "http://localhost:8000/api/v1/documents/system/health"

# 2. List all uploaded documents  
curl "http://localhost:8000/api/v1/documents/"

# 3. Get document details
curl "http://localhost:8000/api/v1/documents/{file_id}"

# 4. Process a document
curl -X POST "http://localhost:8000/api/v1/documents/{file_id}/process"
```

## 🎪 **What Happens When You Upload**

1. **Upload**: File saved to appropriate directory
2. **Validate**: Check file type, size, format
3. **Rename**: Apply standardized naming convention
4. **Metadata**: Create JSON metadata file
5. **Queue**: Mark for processing
6. **Return**: Get file ID and upload confirmation

## 📈 **Processing Workflow** 

```
Upload → Validate → Store → Process → Extract → Review → Complete
   ↓         ↓        ↓        ↓         ↓        ↓        ↓
 File ID   Format   Rename    OCR    Structure  Human   Database
          Check    + Meta   + Parse   Data    Verify   Update
```

## 🔍 **Expected Results**

After uploading, you'll get:
```json
{
  "status": "success",
  "data": {
    "file_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
    "filename": "bank_stmt_chase_20241020_143022_a1b2c3d4.pdf",
    "doc_type": "bank_statement",
    "source": "chase",
    "size": 245678,
    "processing_status": "pending"
  }
}
```

## 📁 **Check Your Results**

After uploading, check these locations:

```
📁 data/uploads/bank_statements/          👈 Original uploaded file
📁 data/processed/extracted_data/         👈 Metadata JSON files  
📁 data/processed/ocr_results/            👈 Extracted text (future)
📁 data/processed/validated/              👈 Reviewed data (future)
```

## 🎯 **Ready to Start!**

**Your system is fully operational for document uploads!**

1. **Server running**: ✅ http://localhost:8000
2. **API docs**: ✅ http://localhost:8000/docs  
3. **Directories**: ✅ All created and ready
4. **Test files**: ✅ Sample documents available
5. **Upload API**: ✅ Fully functional

**Next Step**: Visit http://localhost:8000/docs and try uploading a document!

## 🚧 **Coming Next** (Future Enhancements)

- ✅ **File upload**: COMPLETE
- 🔧 **OCR processing**: Ready for Tesseract installation
- 🔧 **AI extraction**: Ready for ML implementation  
- 🔧 **Database storage**: Ready for Supabase setup
- 🔧 **Dashboard UI**: Ready for React development

You now have a complete document upload and management system! 🎉