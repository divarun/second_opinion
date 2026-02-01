@echo off
REM Second Opinion Startup Script for Windows

echo 🔍 Second Opinion - Pre-mortem Review Tool
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Virtual environment not found!
    echo Run: python -m venv venv
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from example...
    copy .env.example .env
    echo ✅ Created .env file. Please review and update if needed.
)

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
)

REM Check if Ollama is running (simplified check)
echo 🔌 Checking Ollama connection...
echo Note: Make sure Ollama is running before starting

REM Start the application
echo.
echo 🚀 Starting Second Opinion...
echo 📱 Open http://localhost:8000 in your browser
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app:app --reload --host 0.0.0.0 --port 8000