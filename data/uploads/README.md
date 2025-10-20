# Document Uploads Directory

This directory contains all uploaded documents organized by type:

- `bank_statements/` - Bank statement PDFs and CSV files
- `credit_cards/` - Credit card statement PDFs  
- `vendor_invoices/` - Vendor bills and invoices
- `handwritten_notes/` - Scanned handwritten notes and receipts
- `sales_reports/` - Daily/weekly sales reports
- `checks/` - Check images (front and back)
- `temp/` - Temporary files during processing

## File Naming Convention
Files are automatically renamed to: `{type}_{source}_{date}_{uuid}.{ext}`

Example: `bank_stmt_chase_20241020_143022_a1b2c3d4.pdf`
