# Dunkin VendorPay AI - Phase 1

A comprehensive AI-powered vendor payment processing and management system for Dunkin operations.

## Project Overview

Dunkin VendorPay AI is an intelligent system designed to streamline vendor payment processes using artificial intelligence for document processing, payment prediction, and vendor matching.

## Phase 1 Features

- **Document Processing**: AI-powered invoice and document extraction
- **Vendor Management**: Comprehensive vendor database and matching
- **Payment Processing**: Automated payment workflow management
- **API Services**: RESTful APIs for frontend integration
- **Web Interface**: Modern React-based dashboard

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **AI/ML**: TensorFlow/PyTorch, scikit-learn, OpenCV
- **Database**: PostgreSQL, Redis (caching)
- **Frontend**: React 18, Next.js 14, TypeScript
- **Infrastructure**: Docker, Docker Compose

## Project Structure

```
dunkin_vendorpay_ai/
├── src/                    # Main application source
│   ├── ai_models/          # AI/ML model implementations
│   ├── api/                # FastAPI backend services
│   ├── core/               # Core business logic
│   ├── database/           # Database models and migrations
│   └── utils/              # Utility functions
├── frontend/               # React/Next.js frontend
├── data/                   # Data processing and ETL
├── tests/                  # Test suites
├── docs/                   # Documentation
├── config/                 # Configuration files
├── scripts/                # Deployment and utility scripts
└── docker/                 # Docker configurations
```

## Quick Start

### Prerequisites
- Python 3.11+
- VS Code (recommended)

### Setup Instructions

1. **Open the project in VS Code**
   ```
   cd C:\Projects\Dunkin_vendorpay_ai
   code .
   ```

2. **Activate the virtual environment**
   ```powershell
   # PowerShell
   venv\Scripts\Activate.ps1
   
   # Command Prompt
   venv\Scripts\activate.bat
   ```

3. **Install remaining dependencies** (if not already installed)
   ```
   pip install -r requirements.txt
   ```

4. **Run the development server**
   
   **Option A: Using VS Code Tasks**
   - Press `Ctrl+Shift+P`
   - Type "Tasks: Run Task"
   - Select "Run VendorPay AI Dev Server"
   
   **Option B: Using Terminal**
   ```
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   **Option C: Using VS Code Debugger**
   - Press `F5` or go to Run & Debug panel
   - Select "FastAPI VendorPay AI" configuration
   - Click the play button

5. **Access the application**
   - API Server: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### Development Notes
- The server runs with hot-reload enabled for development
- AI/ML models are currently placeholder implementations
- Database connection will be configured in future phases

## API Documentation

Once running, visit:
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000

## Development Guidelines

- Follow Python PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive tests
- Document all API endpoints
- Use async/await for database operations

## License

Internal Use - Dunkin' Brands Inc.