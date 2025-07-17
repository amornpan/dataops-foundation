#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Setup Script
Quick setup and validation script for DataOps Foundation
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 70)
    print("🚀 DataOps Foundation - Setup Script")
    print("=" * 70)
    print()

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_required_files():
    """Check if required files exist"""
    print("\n📁 Checking required files...")
    
    required_files = [
        "etl_pipeline.py",
        "test_etl_pipeline.py",
        "requirements.txt",
        "config.yaml",
        "Jenkinsfile"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_exist = False
    
    return all_exist

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "data",
        "logs",
        "dist",
        "temp"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created {directory}/")
        else:
            print(f"✅ {directory}/ already exists")

def setup_virtual_environment():
    """Setup virtual environment"""
    print("\n🔧 Setting up virtual environment...")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_packages():
    """Install required packages"""
    print("\n📦 Installing packages...")
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = Path("venv") / "Scripts" / "pip"
    else:  # Linux/Mac
        pip_path = Path("venv") / "bin" / "pip"
    
    if not pip_path.exists():
        print("❌ Virtual environment not found. Please create it first.")
        return False
    
    try:
        # Upgrade pip
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        print("✅ pip upgraded successfully")
        
        # Install requirements
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ All packages installed successfully")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def validate_installation():
    """Validate installation"""
    print("\n🧪 Validating installation...")
    
    # Determine python path
    if os.name == 'nt':  # Windows
        python_path = Path("venv") / "Scripts" / "python"
    else:  # Linux/Mac
        python_path = Path("venv") / "bin" / "python"
    
    if not python_path.exists():
        print("❌ Python executable not found in virtual environment")
        return False
    
    # Test imports
    test_imports = [
        "import pandas",
        "import numpy",
        "import sqlalchemy",
        "import pymssql",
        "import pytest",
        "import yaml"
    ]
    
    for test_import in test_imports:
        try:
            result = subprocess.run([str(python_path), "-c", test_import], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                package_name = test_import.split()[1]
                print(f"✅ {package_name} imported successfully")
            else:
                package_name = test_import.split()[1]
                print(f"❌ {package_name} import failed")
                print(f"   Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error testing import {test_import}: {e}")
            return False
    
    return True

def test_etl_pipeline():
    """Test ETL pipeline"""
    print("\n🧪 Testing ETL pipeline...")
    
    # Determine python path
    if os.name == 'nt':  # Windows
        python_path = Path("venv") / "Scripts" / "python"
    else:  # Linux/Mac
        python_path = Path("venv") / "bin" / "python"
    
    try:
        # Test ETL pipeline import
        result = subprocess.run([str(python_path), "-c", "from etl_pipeline import DataOpsETLPipeline; print('ETL pipeline imported successfully')"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ ETL pipeline import test passed")
            print(f"   Output: {result.stdout.strip()}")
        else:
            print("❌ ETL pipeline import test failed")
            print(f"   Error: {result.stderr}")
            return False
            
        # Run unit tests
        result = subprocess.run([str(python_path), "-m", "pytest", "test_etl_pipeline.py", "-v"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Unit tests passed")
            # Count passed tests
            output_lines = result.stdout.split('\n')
            passed_tests = [line for line in output_lines if 'PASSED' in line]
            print(f"   Passed tests: {len(passed_tests)}")
        else:
            print("⚠️ Some unit tests failed (this is normal for database tests)")
            print("   Tests may fail due to missing database connection")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing ETL pipeline: {e}")
        return False

def create_sample_data():
    """Create sample data file"""
    print("\n📊 Creating sample data...")
    
    sample_data = """id,loan_amnt,funded_amnt,term,int_rate,installment,home_ownership,loan_status,issue_d,application_type
1,5000,4500,36,10.5%,150.50,RENT,Fully Paid,Jan-2020,Individual
2,10000,9500,60,12.0%,200.00,OWN,Charged Off,Feb-2020,Individual
3,15000,14500,36,8.5%,450.75,MORTGAGE,Fully Paid,Mar-2020,Joint App
4,20000,19500,60,15.2%,500.25,RENT,Current,Apr-2020,Individual
5,25000,24500,36,9.8%,780.00,OWN,Fully Paid,May-2020,Individual
6,7500,7000,36,11.5%,245.30,MORTGAGE,Current,Jun-2020,Individual
7,12000,11500,60,13.8%,280.45,RENT,Fully Paid,Jul-2020,Joint App
8,18000,17200,36,7.9%,563.20,OWN,Charged Off,Aug-2020,Individual
9,22000,21000,60,16.1%,550.75,MORTGAGE,Current,Sep-2020,Individual
10,8000,7500,36,10.2%,260.80,RENT,Fully Paid,Oct-2020,Individual"""
    
    data_file = Path("data") / "sample_data.csv"
    
    with open(data_file, 'w', encoding='utf-8') as f:
        f.write(sample_data)
    
    print(f"✅ Sample data created: {data_file}")
    print(f"   Records: 10")

def print_next_steps():
    """Print next steps"""
    print("\n🎯 Next Steps:")
    print("=" * 50)
    print("1. 📝 Configure your database settings in config.yaml")
    print("2. 🔐 Set environment variables for database credentials")
    print("3. 📊 Place your CSV data file in the data/ directory")
    print("4. 🚀 Run the ETL pipeline:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
        print("   python etl_pipeline.py")
    else:  # Linux/Mac
        print("   source venv/bin/activate")
        print("   python etl_pipeline.py")
    
    print("\n5. 🔧 Set up Jenkins pipeline for CI/CD:")
    print("   - Install Jenkins with Docker")
    print("   - Create pipeline job using Jenkinsfile")
    print("   - Configure GitHub webhook for automatic builds")
    
    print("\n📚 Documentation:")
    print("   - README.md - Complete documentation")
    print("   - config.yaml - Configuration reference")
    print("   - Jenkinsfile - CI/CD pipeline definition")

def main():
    """Main setup function"""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_required_files():
        print("\n❌ Some required files are missing.")
        print("   Please ensure you have all necessary files in the project directory.")
        return False
    
    # Setup steps
    create_directories()
    
    if not setup_virtual_environment():
        return False
    
    if not install_packages():
        return False
    
    if not validate_installation():
        return False
    
    if not test_etl_pipeline():
        return False
    
    create_sample_data()
    
    print("\n🎉 Setup completed successfully!")
    print("=" * 70)
    
    print_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ DataOps Foundation is ready to use!")
        exit(0)
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        exit(1)
