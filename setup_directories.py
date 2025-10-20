"""
VendorPay AI - Directory Setup Script

This script creates all necessary directories for document processing
and file organization in the VendorPay AI system.
"""

import os
from pathlib import Path
import json
from datetime import datetime

def create_directory_structure():
    """Create all required directories for document processing"""
    
    print("🚀 Setting up VendorPay AI directory structure...")
    
    # Define all required directories
    directories = {
        "uploads": [
            "data/uploads/bank_statements",
            "data/uploads/credit_cards", 
            "data/uploads/vendor_invoices",
            "data/uploads/handwritten_notes",
            "data/uploads/sales_reports",
            "data/uploads/checks",
            "data/uploads/temp"  # Temporary processing folder
        ],
        "processed": [
            "data/processed/extracted_data",
            "data/processed/ocr_results", 
            "data/processed/validated",
            "data/processed/failed"  # Failed processing attempts
        ],
        "archive": [
            "data/archive/completed",
            "data/archive/monthly",
            "data/archive/yearly"
        ],
        "logs": [
            "logs/processing",
            "logs/errors",
            "logs/api"
        ],
        "static": [
            "static/sample_documents",
            "static/templates"
        ]
    }
    
    created_count = 0
    
    # Create all directories
    for category, dir_list in directories.items():
        print(f"\n📁 Creating {category} directories:")
        for dir_path in dir_list:
            try:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                print(f"   ✅ {dir_path}")
                created_count += 1
                
                # Create .gitkeep file to preserve empty directories in git
                gitkeep_path = Path(dir_path) / ".gitkeep"
                if not gitkeep_path.exists():
                    gitkeep_path.write_text("# This file keeps the directory in git")
                    
            except Exception as e:
                print(f"   ❌ Failed to create {dir_path}: {e}")
    
    return created_count

def create_sample_documents():
    """Create sample documents for testing"""
    
    print("\n📝 Creating sample documents...")
    
    # Sample bank statement data
    sample_bank_data = {
        "account_number": "****1234",
        "statement_period": "2024-09-01 to 2024-09-30",
        "opening_balance": 5234.56,
        "closing_balance": 4876.23,
        "transactions": [
            {
                "date": "2024-09-02",
                "description": "SYSCO FOOD DELIVERY",
                "amount": -423.67,
                "type": "debit"
            },
            {
                "date": "2024-09-03", 
                "description": "DAILY SALES DEPOSIT",
                "amount": 1256.78,
                "type": "credit"
            },
            {
                "date": "2024-09-05",
                "description": "PEPSI COLA DELIVERY",
                "amount": -189.45,
                "type": "debit"
            }
        ]
    }
    
    # Sample invoice data
    sample_invoice_data = {
        "vendor": "SYSCO Corporation",
        "invoice_number": "INV-2024-001234",
        "date": "2024-09-15",
        "due_date": "2024-10-15",
        "total_amount": 1234.56,
        "line_items": [
            {"description": "Ground Beef 80/20", "quantity": 50, "unit_price": 6.99, "total": 349.50},
            {"description": "Hamburger Buns", "quantity": 100, "unit_price": 0.35, "total": 35.00},
            {"description": "French Fries Frozen", "quantity": 20, "unit_price": 12.45, "total": 249.00}
        ]
    }
    
    # Save sample data files
    sample_files = [
        ("static/sample_documents/sample_bank_statement.json", sample_bank_data),
        ("static/sample_documents/sample_invoice.json", sample_invoice_data)
    ]
    
    for file_path, data in sample_files:
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"   ✅ Created {file_path}")
        except Exception as e:
            print(f"   ❌ Failed to create {file_path}: {e}")

def create_processing_config():
    """Create configuration file for document processing"""
    
    print("\n⚙️ Creating processing configuration...")
    
    config = {
        "document_processing": {
            "max_file_size_mb": 50,
            "allowed_extensions": [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".csv", ".xlsx"],
            "ocr_settings": {
                "tesseract_config": "--oem 3 --psm 6",
                "confidence_threshold": 0.7,
                "preprocessing": {
                    "resize": True,
                    "denoise": True,
                    "contrast_enhancement": True
                }
            },
            "pdf_settings": {
                "extract_text_first": True,
                "fallback_to_ocr": True,
                "split_pages": True
            }
        },
        "file_naming": {
            "pattern": "{doc_type}_{source}_{date}_{uuid}",
            "date_format": "%Y%m%d_%H%M%S",
            "uuid_length": 8
        },
        "processing_rules": {
            "bank_statements": {
                "required_fields": ["date", "description", "amount"],
                "date_formats": ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"],
                "amount_patterns": [r"\$?[\d,]+\.\d{2}", r"[\d,]+\.\d{2}"]
            },
            "invoices": {
                "required_fields": ["vendor", "invoice_number", "date", "total"],
                "vendor_extraction_patterns": [
                    r"Bill To:\s*(.+)",
                    r"Vendor:\s*(.+)", 
                    r"From:\s*(.+)"
                ]
            }
        }
    }
    
    config_path = "config/processing_config.json"
    try:
        Path("config").mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"   ✅ Created {config_path}")
    except Exception as e:
        print(f"   ❌ Failed to create {config_path}: {e}")

def create_readme_files():
    """Create README files explaining directory purposes"""
    
    print("\n📖 Creating README files...")
    
    readme_content = {
        "data/uploads/README.md": """# Document Uploads Directory

This directory contains all uploaded documents organized by type:

- `bank_statements/` - Bank statement PDFs and CSV files
- `credit_cards/` - Credit card statement PDFs  
- `vendor_invoices/` - Vendor bills and invoices
- `handwritten_notes/` - Scanned handwritten notes and receipts
- `sales_reports/` - Daily/weekly sales reports
- `checks/` - Check images (front and back)
- `temp/` - Temporary files during processing

## File Naming Convention
Files are automatically renamed to: `{type}_{source}_{date}_{uuid}.{ext}`

Example: `bank_stmt_chase_20241020_143022_a1b2c3d4.pdf`
""",
        
        "data/processed/README.md": """# Processed Documents Directory

This directory contains the results of document processing:

- `extracted_data/` - Structured JSON data extracted from documents
- `ocr_results/` - Raw OCR text output from image processing
- `validated/` - Manually reviewed and validated extractions  
- `failed/` - Documents that failed processing (for review)

## Processing Pipeline
1. Upload → OCR/Parse → Extract → Validate → Store
2. Each stage creates files in the corresponding subdirectory
3. Failed processing attempts are saved for manual review
""",

        "data/archive/README.md": """# Document Archive Directory

Long-term storage for processed documents:

- `completed/` - Successfully processed and reconciled documents
- `monthly/` - Monthly archive organized by year/month
- `yearly/` - Yearly summaries and reports

## Retention Policy
- Active documents: Keep in processed/ for 90 days
- Archived documents: Keep for 7 years for tax purposes
- Failed processing: Review monthly, archive or reprocess
"""
    }
    
    for file_path, content in readme_content.items():
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"   ✅ Created {file_path}")
        except Exception as e:
            print(f"   ❌ Failed to create {file_path}: {e}")

def generate_setup_report():
    """Generate a setup completion report"""
    
    print("\n📊 Generating setup report...")
    
    report = {
        "setup_timestamp": datetime.now().isoformat(),
        "directories_created": True,
        "sample_documents": True,
        "configuration": True,
        "readme_files": True,
        "next_steps": [
            "Install OCR dependencies (Tesseract)",
            "Start FastAPI server",
            "Test document upload via API",
            "Upload sample documents for testing"
        ],
        "api_endpoints": [
            "POST /api/v1/documents/upload - Upload documents",
            "GET /api/v1/documents - List uploaded documents", 
            "GET /api/v1/documents/{id} - Get document details",
            "POST /api/v1/documents/{id}/process - Process document"
        ]
    }
    
    with open("setup_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"   ✅ Setup report saved to setup_report.json")

def main():
    """Main setup function"""
    
    print("🎯 VendorPay AI - Document Processing Setup")
    print("=" * 50)
    
    # Create directory structure
    created_count = create_directory_structure()
    
    # Create sample documents
    create_sample_documents()
    
    # Create processing configuration
    create_processing_config()
    
    # Create README files
    create_readme_files()
    
    # Generate setup report
    generate_setup_report()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print(f"📁 Created {created_count} directories")
    print("📝 Created sample documents and configuration")
    print("📖 Created documentation files")
    
    print("\n🚀 Next Steps:")
    print("1. Install Tesseract OCR for image processing")
    print("2. Start your FastAPI server: uvicorn src.api.main:app --reload")
    print("3. Visit http://localhost:8000/docs to test document upload")
    print("4. Upload test documents to verify processing pipeline")
    
    print("\n💡 Quick Test:")
    print("curl -X POST 'http://localhost:8000/api/v1/documents/upload' \\")
    print("  -F 'file=@sample_document.pdf' \\")
    print("  -F 'doc_type=bank_statement'")

if __name__ == "__main__":
    main()