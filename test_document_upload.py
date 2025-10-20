"""
Test script for VendorPay AI document upload functionality

This script tests the document upload API with sample documents
"""

import requests
import json
from pathlib import Path

# API base URL
API_BASE = "http://localhost:8000/api/v1/documents"

def test_upload_system_health():
    """Test the upload system health check"""
    print("🏥 Testing upload system health...")
    
    try:
        response = requests.get(f"{API_BASE}/system/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Upload system is healthy")
            print(f"   📁 Directories exist: {health_data['directories_exist']}")
            print(f"   📄 Total uploads: {health_data['total_uploads']}")
            print(f"   📏 Max file size: {health_data['max_file_size_mb']}MB")
            print(f"   📋 Allowed extensions: {health_data['allowed_extensions']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def upload_document(file_path: str, doc_type: str, source: str, description: str = None):
    """Upload a document to the API"""
    print(f"\n📤 Uploading {file_path}...")
    
    try:
        # Prepare the file
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'text/plain')}
            data = {
                'doc_type': doc_type,
                'source': source
            }
            if description:
                data['description'] = description
            
            response = requests.post(f"{API_BASE}/upload", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"   📄 File ID: {result['data']['file_id']}")
            print(f"   📝 Filename: {result['data']['filename']}")
            print(f"   📊 Size: {result['data']['size']} bytes")
            print(f"   ⏰ Upload time: {result['data']['upload_time']}")
            return result['data']['file_id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def process_document(file_id: str):
    """Process an uploaded document"""
    print(f"\n⚙️ Processing document {file_id}...")
    
    try:
        response = requests.post(f"{API_BASE}/{file_id}/process")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Processing successful!")
            print(f"   🎯 Status: {result['data']['status']}")
            print(f"   📊 Confidence: {result['data']['extracted_data']['confidence']}")
            print(f"   📝 Notes: {result['data']['notes']}")
            return True
        else:
            print(f"❌ Processing failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return False

def get_document_details(file_id: str):
    """Get details for a specific document"""
    print(f"\n📋 Getting details for document {file_id}...")
    
    try:
        response = requests.get(f"{API_BASE}/{file_id}")
        
        if response.status_code == 200:
            result = response.json()
            metadata = result['metadata']
            print("✅ Document details retrieved!")
            print(f"   📄 Original filename: {metadata['original_filename']}")
            print(f"   📝 Document type: {metadata['doc_type']}")
            print(f"   🏢 Source: {metadata['source']}")
            print(f"   📊 Status: {metadata['processing_status']}")
            print(f"   📁 File exists: {result['file_exists']}")
            return True
        else:
            print(f"❌ Failed to get details: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Get details error: {e}")
        return False

def list_all_documents():
    """List all uploaded documents"""
    print(f"\n📋 Listing all documents...")
    
    try:
        response = requests.get(f"{API_BASE}/")
        
        if response.status_code == 200:
            result = response.json()
            documents = result['documents']
            total = result['total']
            
            print(f"✅ Found {total} documents:")
            
            for doc in documents:
                print(f"   📄 {doc['filename']}")
                print(f"      🆔 ID: {doc['file_id']}")
                print(f"      📝 Type: {doc['doc_type']}")
                print(f"      🏢 Source: {doc['source']}")
                print(f"      📊 Status: {doc['status']}")
                print(f"      ⏰ Uploaded: {doc['upload_time']}")
                print()
            
            return True
        else:
            print(f"❌ Failed to list documents: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ List documents error: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 VendorPay AI Document Upload Test")
    print("=" * 50)
    
    # Test system health
    if not test_upload_system_health():
        print("❌ System health check failed. Cannot proceed.")
        return
    
    # Test document uploads
    test_files = [
        {
            'path': 'static/sample_documents/sample_bank_statement.txt',
            'doc_type': 'bank_statement',
            'source': 'chase_bank',
            'description': 'September 2024 business checking statement'
        },
        {
            'path': 'static/sample_documents/sample_vendor_invoice.txt',
            'doc_type': 'vendor_invoice',
            'source': 'sysco',
            'description': 'Food supply invoice from SYSCO'
        }
    ]
    
    uploaded_file_ids = []
    
    # Upload test files
    for test_file in test_files:
        if Path(test_file['path']).exists():
            file_id = upload_document(
                test_file['path'],
                test_file['doc_type'],
                test_file['source'],
                test_file['description']
            )
            if file_id:
                uploaded_file_ids.append(file_id)
        else:
            print(f"⚠️ Test file not found: {test_file['path']}")
    
    # Process uploaded documents
    for file_id in uploaded_file_ids:
        process_document(file_id)
        get_document_details(file_id)
    
    # List all documents
    list_all_documents()
    
    print("\n" + "=" * 50)
    print("🎉 Document upload test completed!")
    print(f"✅ Successfully uploaded {len(uploaded_file_ids)} documents")
    
    if uploaded_file_ids:
        print("\n🔗 Next steps:")
        print("1. Visit http://localhost:8000/docs to see the API documentation")
        print("2. Try uploading your own documents via the API")
        print("3. Check the data/uploads/ directories for your files")
        print("4. Review processing results in data/processed/")

if __name__ == "__main__":
    main()