-- VendorPay AI Financial Management System Database Schema
-- This schema supports document processing, financial reconciliation, and money flow tracking

-- =============================================
-- CORE ENTITIES
-- =============================================

-- Vendors and Suppliers
CREATE TABLE vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    vendor_type VARCHAR(50) NOT NULL, -- 'supplier', 'utility', 'service', 'royalty'
    tax_id VARCHAR(50),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    payment_terms VARCHAR(100), -- 'Net 30', 'COD', etc.
    preferred_payment_method VARCHAR(50), -- 'bank_transfer', 'check', 'credit_card'
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'suspended'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bank Accounts and Credit Cards
CREATE TABLE payment_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL, -- 'bank_account', 'credit_card', 'cash'
    account_number VARCHAR(100), -- masked for security
    bank_name VARCHAR(255),
    routing_number VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    balance DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- DOCUMENT MANAGEMENT
-- =============================================

-- Document Storage and Processing
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_path TEXT NOT NULL, -- Supabase storage path
    file_size INTEGER,
    mime_type VARCHAR(100),
    document_type VARCHAR(50) NOT NULL, -- 'bank_statement', 'credit_card_statement', 'vendor_bill', 'handwritten_note', 'sales_report', 'check'
    processing_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed', 'manual_review'
    extraction_confidence DECIMAL(3,2), -- 0.00 to 1.00
    extracted_data JSONB, -- Raw extracted data from OCR/parsing
    manual_verification BOOLEAN DEFAULT false,
    uploaded_by UUID, -- user who uploaded
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- =============================================
-- FINANCIAL TRANSACTIONS
-- =============================================

-- Money Going Out (Expenses/Payments)
CREATE TABLE outgoing_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(id),
    payment_account_id UUID REFERENCES payment_accounts(id),
    document_id UUID REFERENCES documents(id), -- Source document
    
    -- Transaction Details
    transaction_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50) NOT NULL, -- 'bank_transfer', 'credit_card', 'check', 'cash'
    check_number VARCHAR(50),
    reference_number VARCHAR(100),
    
    -- Categorization
    category VARCHAR(100), -- 'utilities', 'supplies', 'royalties', 'rent', etc.
    subcategory VARCHAR(100),
    description TEXT,
    
    -- Processing Status
    reconciliation_status VARCHAR(20) DEFAULT 'unreconciled', -- 'unreconciled', 'matched', 'disputed', 'manual'
    reconciled_with UUID, -- Reference to matching bank transaction
    
    -- Metadata
    is_recurring BOOLEAN DEFAULT false,
    is_manual_entry BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Money Coming In (Revenue/Sales)
CREATE TABLE incoming_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_account_id UUID REFERENCES payment_accounts(id),
    document_id UUID REFERENCES documents(id), -- Source document (sales report)
    
    -- Transaction Details
    transaction_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50) NOT NULL, -- 'card', 'cash', 'gift_card', 'bank_transfer'
    
    -- Sales Specific
    store_location VARCHAR(100),
    terminal_id VARCHAR(50),
    transaction_id VARCHAR(100),
    
    -- Categorization
    revenue_type VARCHAR(50), -- 'sales', 'royalty', 'refund', 'adjustment'
    product_category VARCHAR(100),
    
    -- Processing Status
    reconciliation_status VARCHAR(20) DEFAULT 'unreconciled',
    reconciled_with UUID,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bank/Credit Card Statement Transactions (Raw data from statements)
CREATE TABLE statement_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_account_id UUID REFERENCES payment_accounts(id),
    document_id UUID REFERENCES documents(id), -- Source statement
    
    -- Raw Statement Data
    transaction_date DATE NOT NULL,
    posted_date DATE,
    amount DECIMAL(15,2) NOT NULL,
    transaction_type VARCHAR(20), -- 'debit', 'credit'
    description TEXT,
    reference_number VARCHAR(100),
    
    -- Matching Status
    is_matched BOOLEAN DEFAULT false,
    matched_transaction_type VARCHAR(20), -- 'outgoing', 'incoming'
    matched_transaction_id UUID,
    confidence_score DECIMAL(3,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- RECONCILIATION AND MATCHING
-- =============================================

-- Reconciliation Records
CREATE TABLE reconciliation_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    statement_transaction_id UUID REFERENCES statement_transactions(id),
    business_transaction_id UUID, -- Can reference either outgoing or incoming
    business_transaction_type VARCHAR(20), -- 'outgoing', 'incoming'
    
    match_type VARCHAR(20), -- 'exact', 'fuzzy', 'manual'
    confidence_score DECIMAL(3,2),
    amount_difference DECIMAL(15,2), -- For partial matches
    
    reconciled_by UUID, -- user who confirmed the match
    reconciled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

-- =============================================
-- REPORTING AND ANALYTICS
-- =============================================

-- Monthly Financial Summary
CREATE TABLE monthly_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    
    total_income DECIMAL(15,2) DEFAULT 0,
    total_expenses DECIMAL(15,2) DEFAULT 0,
    net_cash_flow DECIMAL(15,2) DEFAULT 0,
    
    -- Breakdown by category
    sales_revenue DECIMAL(15,2) DEFAULT 0,
    card_payments DECIMAL(15,2) DEFAULT 0,
    cash_payments DECIMAL(15,2) DEFAULT 0,
    gift_card_payments DECIMAL(15,2) DEFAULT 0,
    
    -- Expenses by category
    vendor_payments DECIMAL(15,2) DEFAULT 0,
    royalty_payments DECIMAL(15,2) DEFAULT 0,
    utility_payments DECIMAL(15,2) DEFAULT 0,
    other_expenses DECIMAL(15,2) DEFAULT 0,
    
    -- Reconciliation stats
    reconciled_transactions INTEGER DEFAULT 0,
    unreconciled_transactions INTEGER DEFAULT 0,
    reconciliation_percentage DECIMAL(5,2) DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(year, month)
);

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- Transaction lookups
CREATE INDEX idx_outgoing_transactions_date ON outgoing_transactions(transaction_date);
CREATE INDEX idx_outgoing_transactions_vendor ON outgoing_transactions(vendor_id);
CREATE INDEX idx_outgoing_transactions_reconciliation ON outgoing_transactions(reconciliation_status);

CREATE INDEX idx_incoming_transactions_date ON incoming_transactions(transaction_date);
CREATE INDEX idx_incoming_transactions_account ON incoming_transactions(payment_account_id);

CREATE INDEX idx_statement_transactions_date ON statement_transactions(transaction_date);
CREATE INDEX idx_statement_transactions_account ON statement_transactions(payment_account_id);
CREATE INDEX idx_statement_transactions_matched ON statement_transactions(is_matched);

-- Document processing
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_status ON documents(processing_status);
CREATE INDEX idx_documents_date ON documents(created_at);

-- Reconciliation
CREATE INDEX idx_reconciliation_statement ON reconciliation_records(statement_transaction_id);
CREATE INDEX idx_reconciliation_business ON reconciliation_records(business_transaction_id);