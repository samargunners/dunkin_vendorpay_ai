#!/usr/bin/env python3
"""
Simple Folder Monitor for VendorPay AI
Monitors folders and automatically processes documents - perfect for QNAP!
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

def setup_logging(log_folder: str):
    """Setup logging to file and console"""
    log_path = Path(log_folder)
    log_path.mkdir(parents=True, exist_ok=True)
    
    log_file = log_path / f"vendorpay_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def process_file(file_path: Path, config: dict, logger, processor) -> bool:
    """Process a single file"""
    try:
        logger.info(f"📄 Processing: {file_path.name}")
        
        # Generate unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = f"{timestamp}_{hash(str(file_path)) % 10000:04d}"
        
        # Process with AI
        if processor:
            result = processor.process_document(file_path)
            
            processing_data = {
                'file_id': file_id,
                'original_name': file_path.name,
                'original_path': str(file_path),
                'processed_at': datetime.now().isoformat(),
                'document_type': result.document_type,
                'confidence': result.confidence_score,
                'extraction_method': result.extraction_method,
                'extracted_fields': result.extracted_fields,
                'financial_data': result.financial_data,
                'text_preview': result.text_content[:200] + "..." if len(result.text_content) > 200 else result.text_content,
                'processing_status': result.processing_status
            }
            
            success = result.processing_status == 'success'
        else:
            # Fallback processing
            processing_data = {
                'file_id': file_id,
                'original_name': file_path.name,
                'original_path': str(file_path),
                'processed_at': datetime.now().isoformat(),
                'document_type': 'unknown',
                'confidence': 0.0,
                'processing_status': 'processed_without_ai'
            }
            success = True
        
        # Determine destination folder
        if success:
            doc_type = processing_data['document_type']
            type_folder = get_type_folder(doc_type)
            dest_folder = Path(config['processed_folder']) / type_folder
        else:
            dest_folder = Path(config['failed_folder'])
        
        # Create destination folder
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        # Move file
        new_filename = f"{file_id}_{file_path.name}"
        dest_path = dest_folder / new_filename
        shutil.move(str(file_path), str(dest_path))
        
        # Update processing data
        processing_data['processed_path'] = str(dest_path)
        processing_data['processed_filename'] = new_filename
        
        # Save results
        results_file = Path(config['results_folder']) / f"{file_id}_results.json"
        with open(results_file, 'w') as f:
            json.dump(processing_data, f, indent=2)
        
        # Log results
        if success:
            logger.info(f"✅ Success: {file_path.name}")
            logger.info(f"   📋 Type: {processing_data['document_type']}")
            logger.info(f"   📊 Confidence: {processing_data['confidence']:.1f}%")
            logger.info(f"   📁 Moved to: {dest_path}")
            
            if processing_data.get('extracted_fields'):
                fields = list(processing_data['extracted_fields'].keys())
                logger.info(f"   🔑 Extracted: {fields[:3]}{'...' if len(fields) > 3 else ''}")
        else:
            logger.error(f"❌ Failed: {file_path.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error processing {file_path.name}: {str(e)}")
        return False

def get_type_folder(doc_type: str) -> str:
    """Get folder name for document type"""
    type_map = {
        'invoice': 'invoices',
        'bank_statement': 'bank_statements', 
        'check': 'checks',
        'sales_report': 'sales_reports',
        'receipt': 'receipts',
        'general_document': 'general',
        'unknown': 'general'
    }
    return type_map.get(doc_type, 'general')

def is_processable_file(file_path: Path) -> bool:
    """Check if file can be processed"""
    # Skip hidden/temp files
    if file_path.name.startswith('.') or file_path.name.startswith('~'):
        return False
    
    # Check extensions
    supported = {'.pdf', '.jpg', '.jpeg', '.png', '.txt', '.csv', '.json', '.tiff', '.tif', '.bmp'}
    return file_path.suffix.lower() in supported

def scan_and_process_folders(config: dict, logger, processor) -> int:
    """Scan folders and process any new files"""
    total_processed = 0
    
    for watch_folder in config['watch_folders']:
        folder_path = Path(watch_folder)
        if not folder_path.exists():
            continue
        
        # Find all processable files
        for file_path in folder_path.rglob("*"):
            if file_path.is_file() and is_processable_file(file_path):
                if process_file(file_path, config, logger, processor):
                    total_processed += 1
                
                # Small delay between files
                time.sleep(0.1)
    
    return total_processed

def main():
    """Main monitoring function"""
    print("🎯 VendorPay AI - Simple Folder Monitor")
    print("=" * 50)
    
    # Load config
    config_file = "vendorpay_qnap/vendorpay_config.json"
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        print("Run 'python setup_qnap_folders.py' first to create folder structure")
        return
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Setup logging
    logger = setup_logging(config['logs_folder'])
    logger.info("🎯 VendorPay AI Folder Monitor Starting")
    
    # Initialize processor
    if PROCESSOR_AVAILABLE:
        processor = DocumentProcessor()
        logger.info("✅ AI Document Processor loaded")
    else:
        processor = None
        logger.warning("⚠️ AI Processor not available - using basic processing")
    
    print("📁 Monitoring folders:")
    for folder in config['watch_folders']:
        if os.path.exists(folder):
            print(f"   ✅ {folder}")
        else:
            print(f"   ❌ {folder} (not found)")
    
    print()
    print("💡 Instructions:")
    print("   1. Drop documents into the input folders")
    print("   2. Files will be automatically processed")
    print("   3. Check the 'processed' folders for organized files")
    print("   4. Check the 'results' folder for AI analysis")
    print("   5. Press Ctrl+C to stop")
    print()
    
    # Main monitoring loop
    try:
        scan_interval = 5  # seconds
        logger.info(f"👀 Starting monitoring (scan every {scan_interval}s)")
        
        while True:
            processed_count = scan_and_process_folders(config, logger, processor)
            
            if processed_count > 0:
                logger.info(f"📊 Processed {processed_count} files in this scan")
            
            time.sleep(scan_interval)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Stopping monitor...")
        print("\n✅ Monitor stopped successfully")

if __name__ == "__main__":
    main()