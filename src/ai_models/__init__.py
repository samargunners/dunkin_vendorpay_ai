"""
AI Models Package for VendorPay AI

This package contains all AI/ML model implementations for:
- Document processing and OCR
- Vendor matching algorithms
- Payment prediction models
- Financial reconciliation
"""

# Import the main models as they are implemented
try:
    from .document_processor import DocumentProcessor
except ImportError:
    DocumentProcessor = None

try:
    from .document_processing_pipeline import DocumentProcessor as DocumentProcessingPipeline
except ImportError:
    DocumentProcessingPipeline = None

try:
    from .reconciliation_engine import ReconciliationEngine, CashFlowAnalyzer
except ImportError:
    ReconciliationEngine = None
    CashFlowAnalyzer = None

# Placeholder imports - these will be implemented later
VendorMatcher = None
PaymentPredictor = None

__all__ = [
    'DocumentProcessor',
    'DocumentProcessingPipeline', 
    'VendorMatcher',
    'PaymentPredictor',
    'ReconciliationEngine',
    'CashFlowAnalyzer'
]