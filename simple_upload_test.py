#!/usr/bin/env python3
"""
Simple Document Upload Example
Just run this script to see how document upload works!
"""

import requests
import json

def simple_upload_test():
    """Test uploading a sample document"""
    
    # File to upload
    file_path = "data/uploads/vendor_invoices/sample_invoice_abc_coffee_20240115.txt"
    
    print("🎯 VendorPay AI - Simple Upload Test")
    print("=" * 50)
    
    try:
        # Check if server is running
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server not running. Please start with: python dev_server_enhanced.py")
            return
        
        print("✅ Server is running!")
        
        # Upload the file
        print(f"📤 Uploading: {file_path}")
        
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {'doc_type': 'auto_detect'}
            
            upload_response = requests.post(
                "http://localhost:8000/upload", 
                files=files, 
                data=data,
                timeout=30
            )
            
            if upload_response.status_code == 200:
                result = upload_response.json()
                file_id = result['data']['file_id']
                
                print("✅ Upload successful!")
                print(f"   📄 File ID: {file_id}")
                print(f"   📋 Type: {result['data']['doc_type']}")
                print(f"   📏 Size: {result['data']['file_size']} bytes")
                
                return file_id
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                print(f"   Error: {upload_response.text}")
                return None
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running:")
        print("   Run: python dev_server_enhanced.py")
        return None
    except FileNotFoundError:
        print(f"❌ Sample file not found: {file_path}")
        print("   Run: python create_sample_documents.py")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    file_id = simple_upload_test()
    
    if file_id:
        print(f"\n🎉 Success! Your document is uploaded and ready.")
        print(f"🌐 View in browser: http://localhost:8000/docs")
        print(f"🔍 Get document: http://localhost:8000/documents/{file_id}")
    else:
        print(f"\n📋 Upload didn't complete. Try the web interface instead:")
        print(f"🌐 Go to: http://localhost:8000/docs")
        print(f"   Look for 'POST /upload' and click 'Try it out'")