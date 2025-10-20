#!/usr/bin/env python3
"""
Quick Test for VendorPay AI Document Processing
Tests the document processor directly without HTTP server
"""

import os
import json
from pathlib import Path
from src.ai_models.document_processor import DocumentProcessor

def test_document_processor_directly():
    """Test the document processor directly on sample files"""
    print("🔍 Testing VendorPay AI Document Processor")
    print("=" * 50)
    
    # Initialize processor
    processor = DocumentProcessor()
    print("✅ Document processor initialized")
    
    # Test files
    test_files = [
        "data/uploads/vendor_invoices/sample_invoice_abc_coffee_20240115.txt",
        "data/uploads/bank_statements/sample_statement_202401.csv", 
        "data/uploads/checks/sample_check_1234.json",
        "data/uploads/sales_reports/daily_sales_20240118.txt",
        "data/uploads/handwritten_notes/manager_notes_20240115.txt"
    ]
    
    results = []
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n📄 Processing: {os.path.basename(file_path)}")
            
            try:
                result = processor.process_document(Path(file_path))
                
                print(f"   ✅ Status: {result.processing_status}")
                print(f"   📋 Type: {result.document_type}")
                print(f"   🔧 Method: {result.extraction_method}")
                print(f"   📊 Confidence: {result.confidence_score:.1f}%")
                print(f"   ⏱️  Time: {result.processing_time:.3f}s")
                print(f"   📄 Text length: {len(result.text_content)} chars")
                
                if result.extracted_fields:
                    print(f"   🔑 Fields: {list(result.extracted_fields.keys())}")
                
                if result.financial_data:
                    print(f"   💰 Financial: {list(result.financial_data.keys())}")
                
                results.append(result)
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        else:
            print(f"❌ File not found: {file_path}")
    
    # Summary
    print(f"\n📊 PROCESSING SUMMARY")
    print("=" * 50)
    print(f"📄 Files processed: {len(results)}")
    
    if results:
        # Document type analysis
        doc_types = {}
        extraction_methods = {}
        total_confidence = 0
        
        for result in results:
            doc_type = result.document_type
            method = result.extraction_method
            
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            extraction_methods[method] = extraction_methods.get(method, 0) + 1
            total_confidence += result.confidence_score
        
        avg_confidence = total_confidence / len(results)
        
        print(f"📋 Document types: {doc_types}")
        print(f"🔧 Extraction methods: {extraction_methods}")
        print(f"📊 Average confidence: {avg_confidence:.1f}%")
        
        # Show sample extracted data
        print(f"\n🔍 SAMPLE EXTRACTED DATA:")
        for i, result in enumerate(results[:2]):  # Show first 2 results
            print(f"\n   📄 File {i+1}: {result.document_type}")
            if result.extracted_fields:
                for key, value in result.extracted_fields.items():
                    print(f"      {key}: {value}")
            if result.financial_data:
                for key, value in result.financial_data.items():
                    if isinstance(value, list) and len(value) > 3:
                        print(f"      {key}: {value[:3]}... ({len(value)} total)")
                    else:
                        print(f"      {key}: {value}")
    
    success_rate = len([r for r in results if r.processing_status == 'success']) / len(results) * 100 if results else 0
    print(f"\n🎯 Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Document processing test PASSED!")
    else:
        print("⚠️  Document processing test needs improvement")
    
    return results

def test_api_availability():
    """Test if the API server is available"""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running and healthy")
            return True
        else:
            print(f"⚠️  API server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API server not available: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 VendorPay AI Quick Test Suite")
    print("=" * 60)
    
    # Test 1: Direct document processing
    print("\n1️⃣  TESTING DOCUMENT PROCESSOR")
    processor_results = test_document_processor_directly()
    
    # Test 2: API availability
    print(f"\n2️⃣  TESTING API SERVER")
    api_available = test_api_availability()
    
    # Final summary
    print(f"\n📋 OVERALL TEST SUMMARY")
    print("=" * 60)
    print(f"🤖 Document processor: {'✅ WORKING' if processor_results else '❌ FAILED'}")
    print(f"🌐 API server: {'✅ AVAILABLE' if api_available else '❌ NOT AVAILABLE'}")
    
    if processor_results and api_available:
        print(f"\n🎉 VendorPay AI is ready for document processing!")
        print(f"🌐 Visit http://localhost:8000/docs to test the full API")
    elif processor_results:
        print(f"\n🎯 Document processing is working! Start the server to test the API.")
    else:
        print(f"\n⚠️  Some components need attention. Check the results above.")