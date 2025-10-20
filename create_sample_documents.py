#!/usr/bin/env python3
"""
Create sample documents for testing VendorPay AI upload functionality
"""

import os
import json
from datetime import datetime, timedelta
import csv
import random

def create_sample_invoice():
    """Create a sample vendor invoice as a text file"""
    invoice_content = """
VENDOR INVOICE

Invoice #: INV-2024-001
Date: January 15, 2024
Due Date: February 14, 2024

Bill To:
Dunkin' Donuts Franchise
123 Main Street
Boston, MA 02101

From:
ABC Coffee Supplies Inc.
456 Supply Avenue
Cambridge, MA 02139
Phone: (617) 555-0123
Email: billing@abccoffee.com

Description                    Qty    Unit Price    Total
Coffee Beans - Colombian       50 lbs    $8.50     $425.00
Coffee Beans - French Roast    30 lbs    $9.00     $270.00
Paper Cups - 12oz            1000 pcs    $0.15     $150.00
Paper Cups - 16oz             500 pcs    $0.20     $100.00
Coffee Filters - Size 4       200 pcs    $0.05      $10.00

                               Subtotal:           $955.00
                               Tax (6.25%):         $59.69
                               Total:            $1,014.69

Payment Terms: Net 30
Payment Method: Check or ACH Transfer

Thank you for your business!
"""
    
    invoice_path = "data/uploads/vendor_invoices/sample_invoice_abc_coffee_20240115.txt"
    os.makedirs(os.path.dirname(invoice_path), exist_ok=True)
    
    with open(invoice_path, 'w') as f:
        f.write(invoice_content)
    
    return invoice_path

def create_sample_bank_statement():
    """Create a sample bank statement as CSV"""
    statement_data = [
        ["Date", "Description", "Debit", "Credit", "Balance"],
        ["2024-01-15", "DEPOSIT - DAILY SALES", "", "2,345.67", "15,234.56"],
        ["2024-01-15", "ABC COFFEE SUPPLIES", "425.00", "", "14,809.56"],
        ["2024-01-16", "PAYROLL - WEEKLY", "3,200.00", "", "11,609.56"],
        ["2024-01-16", "DEPOSIT - DAILY SALES", "", "1,987.43", "13,596.99"],
        ["2024-01-17", "UTILITY BILL - ELECTRIC", "234.56", "", "13,362.43"],
        ["2024-01-17", "DEPOSIT - DAILY SALES", "", "2,100.00", "15,462.43"],
        ["2024-01-18", "FOOD DISTRIBUTOR INC", "1,234.78", "", "14,227.65"],
        ["2024-01-18", "DEPOSIT - DAILY SALES", "", "1,876.54", "16,104.19"]
    ]
    
    statement_path = "data/uploads/bank_statements/sample_statement_202401.csv"
    os.makedirs(os.path.dirname(statement_path), exist_ok=True)
    
    with open(statement_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(statement_data)
    
    return statement_path

def create_sample_check():
    """Create a sample check record as JSON"""
    check_data = {
        "check_number": "1234",
        "date": "2024-01-15",
        "pay_to": "ABC Coffee Supplies Inc.",
        "amount": 1014.69,
        "amount_text": "One thousand fourteen and 69/100 dollars",
        "memo": "Invoice INV-2024-001",
        "account_number": "****-1234",
        "routing_number": "011000015"
    }
    
    check_path = "data/uploads/checks/sample_check_1234.json"
    os.makedirs(os.path.dirname(check_path), exist_ok=True)
    
    with open(check_path, 'w') as f:
        json.dump(check_data, f, indent=2)
    
    return check_path

def create_sample_sales_report():
    """Create a sample daily sales report"""
    sales_content = """
DAILY SALES REPORT
Location: Dunkin' Donuts - Main Street
Date: January 18, 2024

ITEM SALES:
Coffee (Hot) - Medium        89 units    @$2.49    $221.61
Coffee (Hot) - Large         67 units    @$2.79    $186.93
Coffee (Iced) - Medium       45 units    @$2.69    $121.05
Donuts - Glazed              156 units   @$1.29    $201.24
Donuts - Boston Cream        34 units    @$1.49     $50.66
Muffins - Blueberry          23 units    @$2.99     $68.77
Bagels - Everything          78 units    @$1.99    $155.22
Breakfast Sandwiches         92 units    @$4.99    $459.08

PAYMENT METHODS:
Cash:                        $387.45
Credit Card:                 $1,156.23
Debit Card:                  $332.88
Total:                       $1,876.56

STAFF:
Manager: Sarah Johnson
Cashiers: Mike Chen, Lisa Rodriguez
Kitchen: David Kim

Daily Deposits: $1,876.56
Cash Register Balance: $387.45
Credit Card Processing: $1,489.11
"""
    
    sales_path = "data/uploads/sales_reports/daily_sales_20240118.txt"
    os.makedirs(os.path.dirname(sales_path), exist_ok=True)
    
    with open(sales_path, 'w') as f:
        f.write(sales_content)
    
    return sales_path

def create_handwritten_note():
    """Create a sample handwritten note simulation"""
    note_content = """
HANDWRITTEN NOTE (Simulated for testing)

Date: Jan 15, 2024

Remember to:
- Call ABC Coffee about delivery schedule
- Check inventory on Friday
- Update vendor payment terms
- Schedule equipment maintenance

Vendor phone: (617) 555-0123
Next delivery: January 22nd
Payment due: February 14th

Notes: ABC Coffee increased prices by 5%
Need to update menu pricing accordingly

Signed: Store Manager
"""
    
    note_path = "data/uploads/handwritten_notes/manager_notes_20240115.txt"
    os.makedirs(os.path.dirname(note_path), exist_ok=True)
    
    with open(note_path, 'w') as f:
        f.write(note_content)
    
    return note_path

def main():
    """Create all sample documents"""
    print("🎯 Creating sample documents for VendorPay AI testing...")
    
    created_files = []
    
    # Create each type of sample document
    files = [
        ("Invoice", create_sample_invoice()),
        ("Bank Statement", create_sample_bank_statement()),
        ("Check Record", create_sample_check()),
        ("Sales Report", create_sample_sales_report()),
        ("Handwritten Note", create_handwritten_note())
    ]
    
    for doc_type, file_path in files:
        created_files.append(file_path)
        print(f"✅ Created {doc_type}: {file_path}")
    
    # Create a summary file
    summary = {
        "created_at": datetime.now().isoformat(),
        "total_files": len(created_files),
        "files": created_files,
        "note": "Sample documents for testing VendorPay AI upload and processing functionality"
    }
    
    with open("sample_documents_created.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n🎉 Successfully created {len(created_files)} sample documents!")
    print("📋 Summary saved to: sample_documents_created.json")
    print("\n📂 Sample documents ready for upload testing:")
    for file_path in created_files:
        print(f"   • {file_path}")
    
    print("\n🚀 You can now test document uploads at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()