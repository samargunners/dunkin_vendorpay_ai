#!/usr/bin/env python3
"""
End-to-End Testing Script for VendorPay AI Document Upload and Processing
Tests the complete workflow from upload to AI processing
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_FILES = [
    "data/uploads/vendor_invoices/sample_invoice_abc_coffee_20240115.txt",
    "data/uploads/bank_statements/sample_statement_202401.csv",
    "data/uploads/checks/sample_check_1234.json",
    "data/uploads/sales_reports/daily_sales_20240118.txt",
    "data/uploads/handwritten_notes/manager_notes_20240115.txt"
]

def test_server_health():
    """Test server health endpoints"""
    print("🏥 Testing server health...")
    
    try:
        # Test main health endpoint
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Main health check: PASSED")
        else:
            print(f"❌ Main health check: FAILED ({response.status_code})")
            return False
        
        # Test upload health endpoint
        response = requests.get(f"{BASE_URL}/upload/health")
        if response.status_code == 200:
            print("✅ Upload health check: PASSED")
            health_data = response.json()
            print(f"   📊 Upload system status: {health_data.get('status', 'unknown')}")
        else:
            print(f"❌ Upload health check: FAILED ({response.status_code})")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_document_upload(file_path):
    """Test uploading a single document"""
    print(f"\n📤 Testing upload: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file)}
            data = {'doc_type': 'auto_detect'}
            
            response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                file_id = result['data']['file_id']
                print(f"✅ Upload successful: {file_id}")
                print(f"   📄 Original name: {result['data']['original_filename']}")
                print(f"   🔍 Document type: {result['data']['doc_type']}")
                print(f"   📏 File size: {result['data']['file_size']} bytes")
                return file_id
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return None

def test_document_processing(file_id):
    """Test processing an uploaded document"""
    print(f"\n🤖 Testing AI processing for: {file_id}")
    
    try:
        response = requests.post(f"{BASE_URL}/documents/{file_id}/process")
        
        if response.status_code == 200:
            result = response.json()
            processing_data = result['data']
            
            print(f"✅ Processing successful!")
            print(f"   🎯 Status: {processing_data['status']}")
            print(f"   📊 Confidence: {processing_data['confidence']:.2f}")
            print(f"   ⏱️  Processing time: {processing_data.get('extracted_data', {}).get('processing_time', 'N/A')}s")
            
            extracted_data = processing_data.get('extracted_data', {})
            if 'document_type' in extracted_data:
                print(f"   📋 Document type: {extracted_data['document_type']}")
                print(f"   🔧 Extraction method: {extracted_data['extraction_method']}")
                
                if extracted_data.get('extracted_fields'):
                    print(f"   🔑 Extracted fields: {list(extracted_data['extracted_fields'].keys())}")
                
                if extracted_data.get('financial_data'):
                    print(f"   💰 Financial data: {list(extracted_data['financial_data'].keys())}")
            
            return processing_data
        else:
            print(f"❌ Processing failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Processing error: {str(e)}")
        return None

def test_document_retrieval(file_id):
    """Test retrieving document information"""
    print(f"\n📋 Testing document retrieval: {file_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/documents/{file_id}")
        
        if response.status_code == 200:
            result = response.json()
            document_data = result['data']
            
            print(f"✅ Document retrieved successfully!")
            print(f"   📄 Name: {document_data['original_filename']}")
            print(f"   📊 Status: {document_data['processing_status']}")
            print(f"   📅 Uploaded: {document_data['upload_timestamp']}")
            
            return document_data
        else:
            print(f"❌ Retrieval failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Retrieval error: {str(e)}")
        return None

def test_document_listing():
    """Test listing all documents"""
    print(f"\n📜 Testing document listing...")
    
    try:
        response = requests.get(f"{BASE_URL}/documents")
        
        if response.status_code == 200:
            result = response.json()
            documents = result['data']['documents']
            
            print(f"✅ Document listing successful!")
            print(f"   📊 Total documents: {len(documents)}")
            
            for doc in documents[-3:]:  # Show last 3 documents
                print(f"   📄 {doc['original_filename']} ({doc['file_id'][:8]}...)")
            
            return documents
        else:
            print(f"❌ Listing failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Listing error: {str(e)}")
        return None

def run_complete_workflow():
    """Run the complete end-to-end test workflow"""
    print("🚀 Starting VendorPay AI End-to-End Workflow Test")
    print("=" * 60)
    
    # Test 1: Server Health
    if not test_server_health():
        print("\n❌ Server health check failed. Cannot continue testing.")
        return False
    
    # Test 2: Document Upload and Processing
    uploaded_files = []
    processing_results = []
    
    for file_path in TEST_FILES:
        # Upload document
        file_id = test_document_upload(file_path)
        if file_id:
            uploaded_files.append(file_id)
            
            # Process document with AI
            processing_result = test_document_processing(file_id)
            if processing_result:
                processing_results.append(processing_result)
            
            # Retrieve document info
            document_info = test_document_retrieval(file_id)
            
            # Small delay between tests
            time.sleep(0.5)
        
        print("-" * 40)
    
    # Test 3: Document Listing
    all_documents = test_document_listing()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Documents uploaded: {len(uploaded_files)}")
    print(f"🤖 Documents processed: {len(processing_results)}")
    print(f"📋 Total documents in system: {len(all_documents) if all_documents else 0}")
    
    # Analysis of processing results
    if processing_results:
        print(f"\n🔍 AI PROCESSING ANALYSIS:")
        doc_types = {}
        extraction_methods = {}
        
        for result in processing_results:
            extracted_data = result.get('extracted_data', {})
            doc_type = extracted_data.get('document_type', 'unknown')
            extraction_method = extracted_data.get('extraction_method', 'unknown')
            
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            extraction_methods[extraction_method] = extraction_methods.get(extraction_method, 0) + 1
        
        print(f"📋 Document types detected: {doc_types}")
        print(f"🔧 Extraction methods used: {extraction_methods}")
        
        # Show extracted fields summary
        field_counts = {}
        for result in processing_results:
            extracted_data = result.get('extracted_data', {})
            fields = extracted_data.get('extracted_fields', {})
            for field in fields.keys():
                field_counts[field] = field_counts.get(field, 0) + 1
        
        if field_counts:
            print(f"🔑 Fields extracted: {field_counts}")
    
    print(f"\n🎉 End-to-end workflow test completed!")
    
    success_rate = len(processing_results) / len(TEST_FILES) * 100 if TEST_FILES else 0
    print(f"📈 Overall success rate: {success_rate:.1f}%")
    
    return success_rate > 80  # Consider 80%+ success rate as passing

if __name__ == "__main__":
    success = run_complete_workflow()
    
    if success:
        print("\n🎯 ALL TESTS PASSED! VendorPay AI is ready for document processing!")
    else:
        print("\n⚠️  Some tests failed. Please check the results above.")