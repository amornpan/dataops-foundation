#!/bin/bash
# DataOps Foundation Setup Script for Linux/macOS

echo "========================================"
echo "  DataOps Foundation Setup (Linux/macOS)"
echo "========================================"

set -e  # Exit on any error

echo
echo "[1/7] Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Found: $PYTHON_VERSION"
else
    echo "❌ ERROR: Python3 is not installed"
    echo "Please install Python 3.9+ from your package manager or https://python.org"
    exit 1
fi

echo
echo "[2/7] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "✅ Virtual environment already exists"
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

echo
echo "[3/7] Activating virtual environment and upgrading pip..."
source venv/bin/activate
python -m pip install --upgrade pip

echo
echo "[4/7] Installing dependencies..."
pip install -r requirements.txt

echo
echo "[5/7] Creating necessary directories..."
mkdir -p data temp logs backup examples/sample_data
echo "✅ Directories created"

echo
echo "[6/7] Running quick tests..."
python test_quick.py

echo
echo "[7/7] Setup completed!"
echo
echo "========================================"
echo "  Setup Complete! Next Steps:"
echo "========================================"
echo
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo
echo "2. Check system status:"
echo "   python main.py --mode info"
echo
echo "3. Generate sample data:"
echo "   python main.py --mode generate-data --records 1000"
echo
echo "4. Run ETL pipeline:"
echo "   python main.py --mode etl --input examples/sample_data/generated_data.csv"
echo
echo "5. Check data quality:"
echo "   python main.py --mode quality --input examples/sample_data/generated_data.csv"
echo
echo "For more information, see README.md"
echo "========================================"
