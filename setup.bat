@echo off
REM DataOps Foundation Setup Script for Windows
echo ========================================
echo   DataOps Foundation Setup (Windows)
echo ========================================

echo.
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)
python --version

echo.
echo [2/7] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)

echo.
echo [3/7] Activating virtual environment and upgrading pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip

echo.
echo [4/7] Installing dependencies...
pip install -r requirements.txt

echo.
echo [5/7] Creating necessary directories...
if not exist "data" mkdir data
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
if not exist "backup" mkdir backup
if not exist "examples\sample_data" mkdir examples\sample_data

echo.
echo [6/7] Running quick tests...
python test_quick.py

echo.
echo [7/7] Setup completed!
echo.
echo ========================================
echo   Setup Complete! Next Steps:
echo ========================================
echo.
echo 1. Activate virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 2. Check system status:
echo    python main.py --mode info
echo.
echo 3. Generate sample data:
echo    python main.py --mode generate-data --records 1000
echo.
echo 4. Run ETL pipeline:
echo    python main.py --mode etl --input examples\sample_data\generated_data.csv
echo.
echo 5. Check data quality:
echo    python main.py --mode quality --input examples\sample_data\generated_data.csv
echo.
echo For more information, see README.md
echo ========================================

pause
