#!/usr/bin/env python3
"""
VendorPay AI - Simple Folder Monitor
Drop files in folders, get automatic AI processing - no web interface needed!
"""

import os
import time
import json
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Import our document processor
try:
    from src.ai_models.document_processor import DocumentProcessor
    PROCESSOR_AVAILABLE = True
except ImportError:
    PROCESSOR_AVAILABLE = False

def setup_folder_structure():
    """Create simple folder structure for testing"""
    folders = {
        'input': Path('./file_input'),
        'processed': Path('./file_processed'),
        'results': Path('./file_results'),
        'failed': Path('./file_failed')
    }
    
    print("📁 Creating folder structure...")
    for name, path in folders.items():
        path.mkdir(exist_ok=True)
        print(f"✅ {name}: {path}")
    
    # Create subfolders in processed
    for doc_type in ['invoices', 'bank_statements', 'checks', 'receipts', 'general']:
        (folders['processed'] / doc_type).mkdir(exist_ok=True)
    
    return folders

def process_file(file_path: Path, folders: dict, processor) -> bool:
    """Process a single file"""
    try:
        print(f"\n📄 Processing: {file_path.name}")
        
        # Generate unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = f"{timestamp}_{hash(str(file_path)) % 10000:04d}"
        
        # Process with AI
        if processor:
            result = processor.process_document(file_path)
            
            processing_data = {
                'file_id': file_id,
                'original_name': file_path.name,
                'processed_at': datetime.now().isoformat(),
                'document_type': result.document_type,
                'confidence': result.confidence_score,
                'extracted_fields': result.extracted_fields,
                'financial_data': result.financial_data,
                'text_preview': result.text_content[:300] + "..." if len(result.text_content) > 300 else result.text_content,
                'processing_status': result.processing_status
            }
            
            success = result.processing_status == 'success'
        else:
            # Basic processing without AI
            processing_data = {
                'file_id': file_id,
                'original_name': file_path.name,
                'processed_at': datetime.now().isoformat(),
                'document_type': 'unknown',
                'confidence': 0.0,
                'processing_status': 'basic_processing'
            }
            success = True
        
        # Determine destination folder
        if success:
            doc_type = processing_data['document_type']
            if doc_type in ['invoice']:
                subfolder = 'invoices'
            elif doc_type in ['bank_statement']:
                subfolder = 'bank_statements'
            elif doc_type in ['check']:
                subfolder = 'checks'
            elif doc_type in ['receipt']:
                subfolder = 'receipts'
            else:
                subfolder = 'general'
            
            dest_folder = folders['processed'] / subfolder
        else:
            dest_folder = folders['failed']
        
        # Move file
        new_filename = f"{file_id}_{file_path.name}"
        dest_path = dest_folder / new_filename
        shutil.move(str(file_path), str(dest_path))
        
        # Save results
        results_file = folders['results'] / f"{file_id}_results.json"
        processing_data['processed_path'] = str(dest_path)
        
        with open(results_file, 'w') as f:
            json.dump(processing_data, f, indent=2)
        
        # Print results
        print(f"✅ Success!")
        print(f"   📋 Type: {processing_data['document_type']}")
        print(f"   📊 Confidence: {processing_data['confidence']:.1f}%")
        print(f"   📁 Moved to: {dest_path}")
        print(f"   📄 Results: {results_file}")
        
        if processing_data.get('extracted_fields'):
            print(f"   🔑 Key fields: {list(processing_data['extracted_fields'].keys())}")
        
        if processing_data.get('financial_data'):
            financial = processing_data['financial_data']
            if 'main_total' in financial:
                print(f"   💰 Main total: {financial['main_total']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def monitor_folder(input_folder: Path, folders: dict, processor):
    """Monitor folder for new files"""
    processed_files = set()
    
    print(f"👀 Monitoring: {input_folder}")
    print("💡 Drop files here and they'll be processed automatically!")
    print("📋 Supported: PDF, JPG, PNG, TXT, CSV, JSON files")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        while True:
            # Check for new files
            current_files = set()
            if input_folder.exists():
                for file_path in input_folder.iterdir():
                    if file_path.is_file():
                        current_files.add(file_path)
            
            # Process new files
            new_files = current_files - processed_files
            for file_path in new_files:
                # Skip hidden/temp files
                if file_path.name.startswith('.') or file_path.name.startswith('~'):
                    continue
                
                # Check if supported file type
                supported_ext = {'.pdf', '.jpg', '.jpeg', '.png', '.txt', '.csv', '.json', '.tiff', '.bmp'}
                if file_path.suffix.lower() in supported_ext:
                    # Wait a moment for file to be fully written
                    time.sleep(0.5)
                    
                    if process_file(file_path, folders, processor):
                        processed_files.add(file_path)
                else:
                    print(f"⚠️  Skipped unsupported file: {file_path.name}")
                    processed_files.add(file_path)  # Don't keep trying
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopping monitor...")

def main():
    """Main function"""
    print("🎯 VendorPay AI - Simple Folder Monitor")
    print("=" * 50)
    print("Drop files in a folder, get automatic AI processing!")
    print()
    
    # Setup folders
    folders = setup_folder_structure()
    
    # Initialize AI processor
    if PROCESSOR_AVAILABLE:
        print("🤖 Initializing AI processor...")
        processor = DocumentProcessor()
        print("✅ AI processor ready!")
    else:
        processor = None
        print("⚠️  AI processor not available - using basic processing")
    
    print()
    print("📋 How to use:")
    print(f"1. Drop documents into: {folders['input']}")
    print(f"2. Processed files go to: {folders['processed']}/[type]/")
    print(f"3. AI results saved in: {folders['results']}/")
    print(f"4. Failed files go to: {folders['failed']}/")
    print()
    
    # Start monitoring
    monitor_folder(folders['input'], folders, processor)
    
    print("✅ Monitor stopped")

if __name__ == "__main__":
    main()