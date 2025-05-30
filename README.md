# Bible API - Quick Start Guide

## Local Development Setup

### 1. Setup Environment
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings (no database needed)
SECRET_KEY=your-secret-key-here
```

### 3. Run the Application
```bash
# Start the server
uvicorn main:app --reload
```

### 4. Access the API
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Test endpoint: http://localhost:8000/test

That's it! The API is now running locally. 🚀 # Bible-FastAPI-Agent
