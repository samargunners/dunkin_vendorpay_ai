# VendorPay AI Frontend Dashboard

This directory will contain the React/Next.js frontend for the VendorPay AI system.

## Features to Implement

### 📊 Dashboard Overview
- **Money Flow Visualization**: Interactive charts showing income vs expenses
- **Key Metrics**: Total revenue, expenses, net cash flow, reconciliation rate
- **Recent Activity**: Latest transactions, document uploads, reconciliation matches
- **Alerts**: Unreconciled transactions, failed document processing, unusual patterns

### 📄 Document Management
- **Upload Interface**: Drag & drop for bank statements, bills, receipts
- **Processing Status**: Real-time updates on document processing
- **Document Viewer**: Preview uploaded documents with extracted data overlay
- **Manual Review**: Interface for correcting OCR errors

### 💰 Transaction Management
- **Transaction Lists**: Filterable tables of income/expenses
- **Manual Entry Forms**: For handwritten notes, cash payments, checks
- **Reconciliation Interface**: Side-by-side view for matching transactions
- **Bulk Operations**: Mark multiple transactions as reconciled

### 🏪 Vendor Management
- **Vendor Directory**: Search and manage vendor information
- **Payment History**: Track payments to specific vendors
- **Vendor Analytics**: Spending patterns, payment frequency

### 📈 Reports & Analytics
- **Cash Flow Reports**: Daily, weekly, monthly views
- **Category Analysis**: Spending breakdown by category
- **Reconciliation Reports**: Track reconciliation performance
- **Export Functionality**: PDF/CSV export for accounting

### ⚙️ Settings
- **Account Management**: Bank account and credit card setup
- **User Preferences**: Dashboard layout, notification settings
- **System Configuration**: OCR settings, reconciliation thresholds

## Tech Stack

### Frontend Framework
- **Next.js 14**: React framework with app router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Shadcn/ui**: Modern component library

### Data Visualization
- **Chart.js** or **Recharts**: Interactive charts and graphs
- **D3.js**: Advanced visualizations for money flow

### State Management
- **Zustand**: Lightweight state management
- **React Query**: Server state management and caching

### File Management
- **React Dropzone**: File upload interface
- **PDF.js**: PDF preview and annotation

### Real-time Updates
- **Supabase Realtime**: Live updates for processing status

## Project Structure
```
frontend/
├── src/
│   ├── app/                    # Next.js app router
│   │   ├── dashboard/          # Main dashboard pages
│   │   ├── documents/          # Document management
│   │   ├── transactions/       # Transaction pages
│   │   ├── vendors/           # Vendor management
│   │   ├── reports/           # Reports and analytics
│   │   └── settings/          # Settings pages
│   ├── components/            # Reusable components
│   │   ├── ui/               # Base UI components
│   │   ├── charts/           # Chart components
│   │   ├── forms/            # Form components
│   │   └── tables/           # Table components
│   ├── lib/                  # Utilities and configurations
│   │   ├── api/              # API client functions
│   │   ├── types/            # TypeScript types
│   │   └── utils/            # Helper functions
│   └── hooks/                # Custom React hooks
├── public/                   # Static assets
└── docs/                     # Frontend documentation
```

## Getting Started

### 1. Setup Next.js Project
```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app
cd frontend
```

### 2. Install Dependencies
```bash
npm install @supabase/supabase-js
npm install @tanstack/react-query
npm install zustand
npm install react-dropzone
npm install chart.js react-chartjs-2
npm install date-fns
npm install lucide-react
npm install @radix-ui/react-*  # For Shadcn components
```

### 3. Configure Environment
```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 4. Development
```bash
npm run dev
```

## Key Components to Build

### 1. Money Flow Dashboard
```typescript
// components/dashboard/MoneyFlowChart.tsx
interface MoneyFlowData {
  income: number[];
  expenses: number[];
  dates: string[];
  netFlow: number[];
}

const MoneyFlowChart: React.FC<{data: MoneyFlowData}> = ({data}) => {
  // Chart implementation
};
```

### 2. Document Upload
```typescript
// components/documents/DocumentUpload.tsx
interface DocumentUploadProps {
  onUpload: (file: File, type: string) => void;
  acceptedTypes: string[];
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({onUpload, acceptedTypes}) => {
  // Drag & drop implementation
};
```

### 3. Reconciliation Interface
```typescript
// components/reconciliation/ReconciliationPanel.tsx
interface ReconciliationPanelProps {
  statementTransactions: Transaction[];
  businessTransactions: Transaction[];
  onMatch: (stmt: Transaction, business: Transaction) => void;
}
```

### 4. Transaction Table
```typescript
// components/transactions/TransactionTable.tsx
interface TransactionTableProps {
  transactions: Transaction[];
  onEdit: (transaction: Transaction) => void;
  onDelete: (id: string) => void;
  filters: TransactionFilters;
}
```

## API Integration

### Supabase Client Setup
```typescript
// lib/supabase.ts
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'

export const supabase = createClientComponentClient()
```

### API Client Functions
```typescript
// lib/api/transactions.ts
export const transactionAPI = {
  getUnreconciled: () => fetch('/api/financial/transactions/unreconciled'),
  createOutgoing: (data) => fetch('/api/financial/transactions/outgoing', {method: 'POST', body: JSON.stringify(data)}),
  // ... other API functions
}
```

## Implementation Priority

### Phase 1: Core Dashboard
1. ✅ Basic Next.js setup
2. ⏳ Money flow visualization
3. ⏳ Document upload interface
4. ⏳ Transaction table with basic CRUD

### Phase 2: Advanced Features
1. ⏳ Reconciliation interface
2. ⏳ Vendor management
3. ⏳ Advanced filtering and search
4. ⏳ Real-time updates

### Phase 3: Analytics & Reporting
1. ⏳ Advanced charts and analytics
2. ⏳ Report generation
3. ⏳ Export functionality
4. ⏳ Custom dashboards

This frontend will provide a comprehensive interface for managing your financial documents, transactions, and reconciliation process.