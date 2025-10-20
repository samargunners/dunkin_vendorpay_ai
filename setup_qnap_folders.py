#!/usr/bin/env python3
"""
Setup VendorPay AI Folder System for QNAP Integration
Creates the folder structure and configuration for automatic processing
"""

import os
import json
from pathlib import Path

def create_folder_structure(base_path: str = "./vendorpay_qnap"):
    """Create the complete folder structure for VendorPay AI"""
    
    base = Path(base_path)
    
    # Define folder structure
    folders = {
        # Input folders (where you drop files)
        "input": {
            "invoices": base / "input" / "invoices",
            "bank_statements": base / "input" / "bank_statements", 
            "checks": base / "input" / "checks",
            "receipts": base / "input" / "receipts",
            "sales_reports": base / "input" / "sales_reports",
            "general": base / "input" / "general"
        },
        
        # Output folders (where processed files go)
        "processed": {
            "invoices": base / "processed" / "invoices",
            "bank_statements": base / "processed" / "bank_statements",
            "checks": base / "processed" / "checks", 
            "receipts": base / "processed" / "receipts",
            "sales_reports": base / "processed" / "sales_reports",
            "general": base / "processed" / "general"
        },
        
        # System folders
        "results": base / "results",        # JSON results from AI processing
        "failed": base / "failed",          # Files that couldn't be processed
        "archive": base / "archive",        # Backup of original files
        "logs": base / "logs"               # Processing logs
    }
    
    print("🎯 Creating VendorPay AI Folder Structure")
    print("=" * 50)
    print(f"📁 Base path: {base_path}")
    print()
    
    # Create all folders
    created_folders = []
    for category, folder_dict in folders.items():
        if isinstance(folder_dict, dict):
            for name, path in folder_dict.items():
                path.mkdir(parents=True, exist_ok=True)
                created_folders.append(str(path))
                print(f"✅ Created: {path}")
        else:
            folder_dict.mkdir(parents=True, exist_ok=True)
            created_folders.append(str(folder_dict))
            print(f"✅ Created: {folder_dict}")
    
    # Create configuration file
    config = {
        "base_path": str(base),
        "watch_folders": [str(path) for path in folders["input"].values()],
        "processed_folder": str(base / "processed"),
        "results_folder": str(base / "results"),
        "failed_folder": str(base / "failed"),
        "archive_folder": str(base / "archive"),
        "logs_folder": str(base / "logs"),
        "auto_process": True,
        "move_originals": True,
        "create_backups": True,
        "log_level": "INFO"
    }
    
    config_file = base / "vendorpay_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created config: {config_file}")
    print()
    
    # Create README files
    create_readme_files(base, folders)
    
    print("🎉 Folder structure created successfully!")
    print()
    print("📋 QUICK START:")
    print("1. Copy this folder structure to your QNAP")
    print("2. Drop documents into the 'input' folders")
    print("3. Run: python folder_processor.py")
    print("4. Processed files appear in 'processed' folders")
    print("5. AI results saved in 'results' folder")
    print()
    
    return config

def create_readme_files(base: Path, folders: dict):
    """Create helpful README files in each folder"""
    
    # Main README
    main_readme = base / "README.md"
    with open(main_readme, 'w') as f:
        f.write("""# VendorPay AI - Folder-Based Processing

## How to Use

### 1. Drop Files Here (Input Folders):
- `input/invoices/` - Vendor invoices (PDF, images, text)
- `input/bank_statements/` - Bank statements (CSV, PDF)
- `input/checks/` - Check images and records
- `input/receipts/` - Receipt images
- `input/sales_reports/` - Daily sales reports
- `input/general/` - Any other business documents

### 2. Processed Files Go Here:
- `processed/[type]/` - Organized by document type
- `results/` - JSON files with extracted data
- `failed/` - Documents that couldn't be processed
- `archive/` - Backup copies of originals

### 3. Start Processing:
```bash
python folder_processor.py
```

### 4. View Results:
- Check the `results/` folder for JSON files with extracted data
- Each file contains vendor info, amounts, dates, etc.

## Supported File Types:
- PDF documents
- Images (JPG, PNG, TIFF, BMP)
- Text files (TXT, CSV, JSON)

## AI Processing Features:
- ✅ Automatic document type detection
- ✅ Text extraction and OCR
- ✅ Vendor and financial data extraction
- ✅ Smart folder organization
- ✅ Detailed processing logs
""")
    
    # Input folder README
    input_readme = base / "input" / "README.md"
    with open(input_readme, 'w') as f:
        f.write("""# Input Folders - Drop Your Documents Here

## 📁 Folder Guide:

### `invoices/`
Drop vendor invoices here:
- Supplier bills
- Service invoices  
- Purchase orders
- Any vendor payment documents

### `bank_statements/`
Drop bank statements here:
- Monthly statements (PDF, CSV)
- Transaction exports
- Account summaries

### `checks/`
Drop check-related documents:
- Check images
- Check registers
- Payment records

### `receipts/`
Drop receipts here:
- Purchase receipts
- Expense receipts
- Customer transaction receipts

### `sales_reports/`
Drop sales documents:
- Daily sales reports
- POS summaries
- Revenue reports

### `general/`
Drop any other business documents:
- Contracts
- Notes
- Mixed document types

## 🤖 What Happens:
1. Files are automatically detected when dropped
2. AI processes and extracts key information
3. Files are moved to appropriate processed folders
4. Results are saved as JSON in the results folder

## ⚡ Processing Speed:
- Text files: Instant
- PDF files: 1-3 seconds  
- Images: 2-5 seconds (with OCR)
""")
    
    # Results folder README  
    results_readme = base / "results" / "README.md"
    with open(results_readme, 'w') as f:
        f.write("""# Results Folder - AI Processing Output

## 📊 What You'll Find Here:

Each processed document creates a JSON file with:

### Document Information:
- Original filename and path
- Processing timestamp
- Document type (invoice, statement, etc.)
- Confidence score

### Extracted Data:
- **Text Content**: Full extracted text
- **Key Fields**: Vendor names, amounts, dates
- **Financial Data**: Totals, account numbers, balances
- **Structured Fields**: Organized by document type

### Example Invoice Result:
```json
{
  "file_id": "20241020_143052_1234",
  "document_type": "invoice", 
  "confidence": 95.5,
  "extracted_fields": {
    "vendor_name": "ABC Supply Co",
    "invoice_number": "INV-2024-001",
    "total_amount": "1,234.56",
    "due_date": "2024-11-15"
  },
  "financial_data": {
    "amounts_found": ["$1,234.56", "$1,100.00"],
    "main_total": "$1,234.56"
  }
}
```

## 📋 File Naming:
`YYYYMMDD_HHMMSS_XXXX_results.json`
- Date and time processed
- Unique identifier
- Easy to sort chronologically

## 💡 Tips:
- Results are updated in real-time as files are processed
- Use these JSON files for accounting software integration
- All monetary amounts and dates are extracted automatically
""")

def main():
    """Main setup function"""
    print("🎯 VendorPay AI - QNAP Folder Setup")
    print("=" * 40)
    print()
    print("This will create a folder structure for automatic document processing.")
    print("Perfect for QNAP integration - no web interface needed!")
    print()
    
    # Get base path from user
    default_path = "./vendorpay_qnap"
    user_path = input(f"Enter folder path (default: {default_path}): ").strip()
    
    if not user_path:
        user_path = default_path
    
    # Create the structure
    config = create_folder_structure(user_path)
    
    print("🎉 Setup complete!")
    print()
    print("📋 Next Steps:")
    print("1. Copy this entire folder to your QNAP")
    print("2. Update paths in vendorpay_config.json if needed")
    print("3. Run: python folder_processor.py")
    print("4. Start dropping documents into the input folders!")
    print()
    print("💡 The system will automatically:")
    print("   • Detect new files")
    print("   • Process them with AI") 
    print("   • Extract key information")
    print("   • Organize files by type")
    print("   • Generate detailed JSON results")

if __name__ == "__main__":
    main()