#!/usr/bin/env python3
"""
VendorPay AI - Folder-Based Document Processing System
Automatically processes documents when they're added to watched folders
Perfect for QNAP integration - no web interface needed!
"""

import os
import time
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import our document processor
try:
    from src.ai_models.document_processor import DocumentProcessor
    PROCESSOR_AVAILABLE = True
except ImportError:
    PROCESSOR_AVAILABLE = False
    print("⚠️ Document processor not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vendorpay_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VendorPayFileHandler(FileSystemEventHandler):
    """Handles file system events for automatic document processing"""
    
    def __init__(self, config: Dict):
        """
        Initialize the file handler
        
        Args:
            config: Configuration dictionary with folder paths and settings
        """
        self.config = config
        self.processor = DocumentProcessor() if PROCESSOR_AVAILABLE else None
        self.processed_files = set()
        
        # Create necessary directories
        self._setup_directories()
        
        logger.info("🎯 VendorPay File Handler initialized")
        logger.info(f"📁 Watching: {config['watch_folders']}")
        logger.info(f"📤 Processing to: {config['processed_folder']}")
    
    def _setup_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.config['processed_folder'],
            self.config['archive_folder'],
            self.config['failed_folder'],
            self.config['results_folder']
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        logger.info("📁 Directory structure created/verified")
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Wait a moment for file to be fully written
        time.sleep(1)
        
        # Check if it's a document we can process
        if self._is_processable_file(file_path):
            logger.info(f"📄 New file detected: {file_path}")
            self._process_document(file_path)
    
    def on_moved(self, event):
        """Handle file move events"""
        if event.is_directory:
            return
        
        file_path = Path(event.dest_path)
        
        if self._is_processable_file(file_path):
            logger.info(f"📄 File moved to watched folder: {file_path}")
            self._process_document(file_path)
    
    def _is_processable_file(self, file_path: Path) -> bool:
        """Check if file can be processed"""
        # Skip hidden files, temp files, etc.
        if file_path.name.startswith('.') or file_path.name.startswith('~'):
            return False
        
        # Check if already processed
        if str(file_path) in self.processed_files:
            return False
        
        # Check file extension
        supported_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.txt', '.csv', '.json', '.tiff', '.tif', '.bmp'}
        if file_path.suffix.lower() in supported_extensions:
            return True
        
        return False
    
    def _process_document(self, file_path: Path):
        """Process a document and move it to appropriate folder"""
        try:
            # Mark as being processed
            self.processed_files.add(str(file_path))
            
            logger.info(f"🤖 Processing: {file_path.name}")
            
            # Generate unique file ID
            file_id = self._generate_file_id(file_path)
            
            # Process with AI if available
            if self.processor:
                result = self.processor.process_document(file_path)
                success = result.processing_status == 'success'
                processing_data = {
                    'file_id': file_id,
                    'original_path': str(file_path),
                    'original_name': file_path.name,
                    'processed_at': datetime.now().isoformat(),
                    'document_type': result.document_type,
                    'confidence': result.confidence_score,
                    'extraction_method': result.extraction_method,
                    'extracted_fields': result.extracted_fields,
                    'financial_data': result.financial_data,
                    'text_content': result.text_content,
                    'processing_status': result.processing_status
                }
            else:
                # Fallback processing
                success = True
                processing_data = {
                    'file_id': file_id,
                    'original_path': str(file_path),
                    'original_name': file_path.name,
                    'processed_at': datetime.now().isoformat(),
                    'document_type': 'unknown',
                    'confidence': 0.0,
                    'extraction_method': 'fallback',
                    'processing_status': 'processed_without_ai'
                }
            
            # Determine destination folder based on document type and success
            if success:
                dest_folder = self._get_destination_folder(processing_data['document_type'])
                status_folder = self.config['processed_folder']
            else:
                dest_folder = self.config['failed_folder']
                status_folder = self.config['failed_folder']
            
            # Create destination directory
            Path(dest_folder).mkdir(parents=True, exist_ok=True)
            
            # Move file to destination
            new_filename = f"{file_id}_{file_path.name}"
            dest_path = Path(dest_folder) / new_filename
            shutil.move(str(file_path), str(dest_path))
            
            # Update processing data with new location
            processing_data['processed_path'] = str(dest_path)
            processing_data['processed_filename'] = new_filename
            
            # Save processing results
            results_file = Path(self.config['results_folder']) / f"{file_id}_results.json"
            with open(results_file, 'w') as f:
                json.dump(processing_data, f, indent=2)
            
            # Log success
            if success:
                logger.info(f"✅ Processed successfully: {file_path.name}")
                logger.info(f"   📋 Type: {processing_data['document_type']}")
                logger.info(f"   📊 Confidence: {processing_data['confidence']:.1f}%")
                logger.info(f"   📁 Moved to: {dest_path}")
                
                # Print extracted data summary
                if processing_data.get('extracted_fields'):
                    logger.info(f"   🔑 Extracted: {list(processing_data['extracted_fields'].keys())}")
                if processing_data.get('financial_data'):
                    logger.info(f"   💰 Financial: {list(processing_data['financial_data'].keys())}")
            else:
                logger.error(f"❌ Processing failed: {file_path.name}")
                logger.error(f"   📁 Moved to: {dest_path}")
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {str(e)}")
            
            # Move to failed folder
            try:
                failed_path = Path(self.config['failed_folder']) / file_path.name
                shutil.move(str(file_path), str(failed_path))
                logger.info(f"📁 Moved failed file to: {failed_path}")
            except Exception as move_error:
                logger.error(f"❌ Could not move failed file: {move_error}")
    
    def _generate_file_id(self, file_path: Path) -> str:
        """Generate unique file ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{hash(str(file_path)) % 10000:04d}"
    
    def _get_destination_folder(self, doc_type: str) -> str:
        """Get destination folder based on document type"""
        type_folders = {
            'invoice': 'invoices',
            'bank_statement': 'bank_statements',
            'check': 'checks',
            'sales_report': 'sales_reports',
            'receipt': 'receipts',
            'general_document': 'general',
            'unknown': 'unknown'
        }
        
        folder_name = type_folders.get(doc_type, 'unknown')
        return str(Path(self.config['processed_folder']) / folder_name)


class VendorPayFolderProcessor:
    """Main class for folder-based document processing"""
    
    def __init__(self, config_file: str = "folder_config.json"):
        """
        Initialize the folder processor
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.observer = Observer()
        self.file_handler = VendorPayFileHandler(self.config)
        
        logger.info("🎯 VendorPay Folder Processor initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"📋 Loaded config from: {self.config_file}")
        else:
            # Create default configuration
            config = self._create_default_config()
            self._save_config(config)
            logger.info(f"📋 Created default config: {self.config_file}")
        
        return config
    
    def _create_default_config(self) -> Dict:
        """Create default configuration"""
        return {
            "watch_folders": [
                "qnap_watch/invoices",
                "qnap_watch/statements", 
                "qnap_watch/receipts",
                "qnap_watch/general"
            ],
            "processed_folder": "qnap_processed",
            "archive_folder": "qnap_archive",
            "failed_folder": "qnap_failed",
            "results_folder": "qnap_results",
            "auto_process": True,
            "move_originals": True,
            "create_summary_reports": True
        }
    
    def _save_config(self, config: Dict):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def setup_qnap_folders(self, qnap_base_path: str):
        """
        Setup folder structure for QNAP integration
        
        Args:
            qnap_base_path: Base path on your QNAP where folders should be created
        """
        qnap_path = Path(qnap_base_path)
        
        # Update config with QNAP paths
        self.config.update({
            "watch_folders": [
                str(qnap_path / "vendorpay_input" / "invoices"),
                str(qnap_path / "vendorpay_input" / "statements"),
                str(qnap_path / "vendorpay_input" / "receipts"),
                str(qnap_path / "vendorpay_input" / "general")
            ],
            "processed_folder": str(qnap_path / "vendorpay_processed"),
            "archive_folder": str(qnap_path / "vendorpay_archive"),
            "failed_folder": str(qnap_path / "vendorpay_failed"),
            "results_folder": str(qnap_path / "vendorpay_results")
        })
        
        # Create all directories
        for folder_list in [self.config["watch_folders"]]:
            for folder in folder_list:
                Path(folder).mkdir(parents=True, exist_ok=True)
        
        for folder in [
            self.config["processed_folder"],
            self.config["archive_folder"], 
            self.config["failed_folder"],
            self.config["results_folder"]
        ]:
            Path(folder).mkdir(parents=True, exist_ok=True)
        
        # Save updated config
        self._save_config(self.config)
        
        logger.info(f"🎯 QNAP folder structure created at: {qnap_base_path}")
        logger.info("📁 Input folders (drop your files here):")
        for folder in self.config["watch_folders"]:
            logger.info(f"   • {folder}")
        logger.info("📁 Output folders:")
        logger.info(f"   • Processed: {self.config['processed_folder']}")
        logger.info(f"   • Results: {self.config['results_folder']}")
        logger.info(f"   • Failed: {self.config['failed_folder']}")
    
    def start_watching(self):
        """Start watching folders for new files"""
        logger.info("👀 Starting folder monitoring...")
        
        # Set up observers for each watch folder
        for folder in self.config["watch_folders"]:
            if os.path.exists(folder):
                self.observer.schedule(self.file_handler, folder, recursive=True)
                logger.info(f"📁 Watching: {folder}")
            else:
                logger.warning(f"⚠️ Watch folder doesn't exist: {folder}")
        
        # Start the observer
        self.observer.start()
        logger.info("✅ Folder monitoring started!")
        logger.info("📋 Drop files into watch folders to process them automatically")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("⏹️ Stopping folder monitoring...")
            self.observer.stop()
        
        self.observer.join()
        logger.info("✅ Folder monitoring stopped")
    
    def process_existing_files(self):
        """Process any existing files in watch folders"""
        logger.info("🔍 Processing existing files in watch folders...")
        
        total_processed = 0
        for folder in self.config["watch_folders"]:
            if os.path.exists(folder):
                for file_path in Path(folder).rglob("*"):
                    if file_path.is_file() and self.file_handler._is_processable_file(file_path):
                        logger.info(f"📄 Processing existing file: {file_path}")
                        self.file_handler._process_document(file_path)
                        total_processed += 1
        
        logger.info(f"✅ Processed {total_processed} existing files")


def main():
    """Main function"""
    print("🎯 VendorPay AI - Folder-Based Document Processor")
    print("=" * 60)
    print("Perfect for QNAP integration - no web interface needed!")
    print()
    
    processor = VendorPayFolderProcessor()
    
    # Check if user wants to setup QNAP folders
    print("📁 Setup Options:")
    print("1. Use default local folders (for testing)")
    print("2. Setup QNAP folder structure")
    print("3. Start monitoring with current config")
    print()
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        # Use default local folders
        print("📁 Using default local folders...")
        processor.setup_qnap_folders("./qnap_test")
        
    elif choice == "2":
        # Setup QNAP folders
        qnap_path = input("Enter your QNAP base path (e.g., /share/VendorPay): ").strip()
        if qnap_path:
            processor.setup_qnap_folders(qnap_path)
        else:
            print("❌ No path provided, using default")
            processor.setup_qnap_folders("./qnap_test")
    
    # Process any existing files
    processor.process_existing_files()
    
    # Start monitoring
    print("\n🚀 Starting folder monitoring...")
    print("💡 Drop files into the input folders to process them automatically!")
    print("📋 Press Ctrl+C to stop")
    
    processor.start_watching()


if __name__ == "__main__":
    main()