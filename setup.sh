#!/bin/bash
# DataOps Foundation - Quick Setup Script (Linux/macOS)

echo "🚀 DataOps Foundation - Quick Setup"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
print_status "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Create virtual environment
print_status "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed successfully"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data logs temp output examples/sample_data
print_success "Directories created"

# Generate sample data
print_status "Generating sample data..."
if [ -f "examples/generate_sample_data.py" ]; then
    python examples/generate_sample_data.py
    print_success "Sample data generated"
else
    print_warning "Sample data generator not found"
fi

# Run tests
print_status "Running tests..."
if [ -f "tests/test_enhanced_etl.py" ]; then
    python tests/test_enhanced_etl.py
    if [ $? -eq 0 ]; then
        print_success "All tests passed!"
    else
        print_warning "Some tests failed. Check the output above."
    fi
else
    print_warning "Test file not found"
fi

# Check if Docker is available
print_status "Checking Docker availability..."
if command -v docker &> /dev/null; then
    if command -v docker-compose &> /dev/null; then
        print_success "Docker and Docker Compose are available"
        echo ""
        echo "🐳 To start with Docker:"
        echo "   docker-compose -f docker/docker-compose.yml up -d"
    else
        print_warning "Docker is available but Docker Compose is not installed"
    fi
else
    print_warning "Docker is not installed. Container features will not be available."
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Quick Start Commands:"
echo "   # Activate virtual environment"
echo "   source venv/bin/activate"
echo ""
echo "   # Run ETL processor"
echo "   python src/data_pipeline/etl_processor.py"
echo ""
echo "   # Run data quality checker"
echo "   python src/data_quality/quality_checker.py"
echo ""
echo "   # Run full test suite"
echo "   python tests/test_enhanced_etl.py"
echo ""
echo "📚 Documentation:"
echo "   - Quick Start: docs/quick-start.md"
echo "   - README: README.md"
echo ""
echo "Happy DataOps! 🚀"
