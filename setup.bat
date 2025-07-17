@echo off
REM DataOps Foundation - Quick Setup Script (Windows)

echo 🚀 DataOps Foundation - Quick Setup
echo ====================================

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo [SUCCESS] Python %PYTHON_VERSION% found

REM Create virtual environment
echo [INFO] Creating virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists
) else (
    python -m venv venv
    echo [SUCCESS] Virtual environment created
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate
echo [SUCCESS] Virtual environment activated

REM Upgrade pip
echo [INFO] Upgrading pip...
pip install --upgrade pip

REM Install requirements
echo [INFO] Installing Python dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
    echo [SUCCESS] Dependencies installed successfully
) else (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist temp mkdir temp
if not exist output mkdir output
if not exist examples\sample_data mkdir examples\sample_data
echo [SUCCESS] Directories created

REM Generate sample data
echo [INFO] Generating sample data...
if exist examples\generate_sample_data.py (
    python examples\generate_sample_data.py
    echo [SUCCESS] Sample data generated
) else (
    echo [WARNING] Sample data generator not found
)

REM Run tests
echo [INFO] Running tests...
if exist tests\test_enhanced_etl.py (
    python tests\test_enhanced_etl.py
    if %errorlevel% equ 0 (
        echo [SUCCESS] All tests passed!
    ) else (
        echo [WARNING] Some tests failed. Check the output above.
    )
) else (
    echo [WARNING] Test file not found
)

REM Check if Docker is available
echo [INFO] Checking Docker availability...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    docker-compose --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [SUCCESS] Docker and Docker Compose are available
        echo.
        echo 🐳 To start with Docker:
        echo    docker-compose -f docker/docker-compose.yml up -d
    ) else (
        echo [WARNING] Docker is available but Docker Compose is not installed
    )
) else (
    echo [WARNING] Docker is not installed. Container features will not be available.
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 Quick Start Commands:
echo    # Activate virtual environment
echo    venv\Scripts\activate
echo.
echo    # Run ETL processor
echo    python src\data_pipeline\etl_processor.py
echo.
echo    # Run data quality checker
echo    python src\data_quality\quality_checker.py
echo.
echo    # Run full test suite
echo    python tests\test_enhanced_etl.py
echo.
echo 📚 Documentation:
echo    - Quick Start: docs\quick-start.md
echo    - README: README.md
echo.
echo Happy DataOps! 🚀
pause
