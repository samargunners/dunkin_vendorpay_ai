#!/usr/bin/env python3
"""
Simple Document Upload Script for VendorPay AI
Upload any document and get AI processing results
"""

import requests
import json
import sys
import os
from pathlib import Path

def upload_document(file_path, doc_type="auto_detect"):
    """
    Upload a document to VendorPay AI
    
    Args:
        file_path: Path to the document file
        doc_type: Type of document (auto_detect, invoice, bank_statement, etc.)
    """
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    # Prepare the upload
    url = "http://localhost:8000/upload"
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file)}
            data = {'doc_type': doc_type}
            
            print(f"📤 Uploading: {file_path}")
            print(f"🔍 Document type: {doc_type}")
            
            # Upload the file
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                file_id = result['data']['file_id']
                
                print(f"✅ Upload successful!")
                print(f"   📄 File ID: {file_id}")
                print(f"   📋 Document type: {result['data']['doc_type']}")
                print(f"   📏 File size: {result['data']['file_size']} bytes")
                print(f"   📅 Uploaded: {result['data']['upload_timestamp']}")
                
                # Now process the document with AI
                print(f"\n🤖 Processing document with AI...")
                process_url = f"http://localhost:8000/documents/{file_id}/process"
                process_response = requests.post(process_url)
                
                if process_response.status_code == 200:
                    process_result = process_response.json()
                    extracted_data = process_result['data']['extracted_data']
                    
                    print(f"✅ AI Processing complete!")
                    print(f"   🎯 Status: {process_result['data']['status']}")
                    print(f"   📊 Confidence: {process_result['data']['confidence']:.2f}")
                    
                    if 'document_type' in extracted_data:
                        print(f"   📋 Detected type: {extracted_data['document_type']}")
                        print(f"   🔧 Method: {extracted_data['extraction_method']}")
                        
                        if extracted_data.get('extracted_fields'):
                            print(f"   🔑 Key fields found: {list(extracted_data['extracted_fields'].keys())}")
                            
                            # Show some extracted data
                            for field, value in list(extracted_data['extracted_fields'].items())[:3]:
                                print(f"      • {field}: {value}")
                        
                        if extracted_data.get('financial_data'):
                            print(f"   💰 Financial data: {list(extracted_data['financial_data'].keys())}")
                
                return file_id
                
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return None

def main():
    """Main function to handle command line usage"""
    
    if len(sys.argv) < 2:
        print("🎯 VendorPay AI Document Upload Tool")
        print("=" * 50)
        print("Usage: python upload_document.py <file_path> [doc_type]")
        print()
        print("Examples:")
        print("  python upload_document.py invoice.pdf")
        print("  python upload_document.py statement.csv bank_statement")
        print("  python upload_document.py receipt.jpg auto_detect")
        print()
        print("Available document types:")
        print("  • auto_detect (default)")
        print("  • vendor_invoice")
        print("  • bank_statement") 
        print("  • check")
        print("  • sales_report")
        print("  • receipt")
        print("  • handwritten_note")
        print()
        
        # Show sample documents available for testing
        sample_files = [
            "data/uploads/vendor_invoices/sample_invoice_abc_coffee_20240115.txt",
            "data/uploads/bank_statements/sample_statement_202401.csv",
            "data/uploads/checks/sample_check_1234.json",
            "data/uploads/sales_reports/daily_sales_20240118.txt",
            "data/uploads/handwritten_notes/manager_notes_20240115.txt"
        ]
        
        print("📁 Sample documents available for testing:")
        for file_path in sample_files:
            if os.path.exists(file_path):
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path} (not found)")
        
        return
    
    file_path = sys.argv[1]
    doc_type = sys.argv[2] if len(sys.argv) > 2 else "auto_detect"
    
    # Upload the document
    file_id = upload_document(file_path, doc_type)
    
    if file_id:
        print(f"\n🎉 Success! Document uploaded and processed.")
        print(f"📋 You can view all documents at: http://localhost:8000/docs")
        print(f"🔍 Or get this document: http://localhost:8000/documents/{file_id}")

if __name__ == "__main__":
    main()