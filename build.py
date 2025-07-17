#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Build Script
สคริปต์สำหรับ build และ package โปรเจค
"""

import os
import sys
import subprocess
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def run_command(command, description=""):
    """รันคำสั่งและตรวจสอบผลลัพธ์"""
    print(f"🔧 {description or command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Command failed: {command}")
        print(f"Error: {result.stderr}")
        return False
    
    if result.stdout.strip():
        print(f"   {result.stdout.strip()}")
    
    return True

def clean_build():
    """ทำความสะอาดไฟล์ build เก่า"""
    print("🧹 Cleaning build directories...")
    
    directories_to_clean = [
        'build',
        'dist', 
        'htmlcov',
        '__pycache__',
        '.pytest_cache',
        '*.egg-info'
    ]
    
    for dir_pattern in directories_to_clean:
        if '*' in dir_pattern:
            # Handle wildcards
            import glob
            for path in glob.glob(dir_pattern):
                if os.path.exists(path):
                    shutil.rmtree(path)
                    print(f"   Removed: {path}")
        else:
            if os.path.exists(dir_pattern):
                shutil.rmtree(dir_pattern)
                print(f"   Removed: {dir_pattern}")
    
    # Remove Python cache files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
        for dir_name in dirs[:]:
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
                dirs.remove(dir_name)

def run_tests():
    """รันการทดสอบทั้งหมด"""
    print("🧪 Running comprehensive tests...")
    
    # Quick system test
    if not run_command("python test_quick.py", "Quick system test"):
        return False
    
    # Enhanced ETL tests
    if not run_command("python tests/test_enhanced_etl.py", "Enhanced ETL tests"):
        return False
    
    # Unit tests with pytest (if available)
    if shutil.which('pytest'):
        if not run_command("pytest tests/ -v --tb=short", "Unit tests with pytest"):
            return False
    
    return True

def run_quality_checks():
    """รันการตรวจสอบคุณภาพโค้ด"""
    print("🔍 Running code quality checks...")
    
    # Check if tools are available and run them
    quality_tools = [
        ('black', "python -m black --check src/ tests/ --diff", "Code formatting check"),
        ('flake8', "python -m flake8 src/ tests/ --max-line-length=88", "Linting check"),
        ('bandit', "python -m bandit -r src/ -f json", "Security check")
    ]
    
    for tool, command, description in quality_tools:
        if shutil.which('python') and tool in ['black', 'flake8', 'bandit']:
            try:
                # Try to import the module first
                __import__(tool.replace('-', '_'))
                if not run_command(command, description):
                    print(f"⚠️ {description} had issues (continuing...)")
            except ImportError:
                print(f"⚠️ {tool} not installed, skipping {description}")
    
    return True

def generate_documentation():
    """สร้าง documentation"""
    print("📚 Generating documentation...")
    
    # Create docs directory if not exists
    os.makedirs('build/docs', exist_ok=True)
    
    # Copy documentation files
    doc_files = [
        'README.md',
        'CHANGELOG.md', 
        'CONTRIBUTING.md',
        'LICENSE',
        'docs/quick-start.md'
    ]
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            dest = f"build/docs/{os.path.basename(doc_file)}"
            shutil.copy2(doc_file, dest)
            print(f"   Copied: {doc_file} -> {dest}")
    
    return True

def build_package():
    """สร้าง package สำหรับ distribution"""
    print("📦 Building package...")
    
    # Create build directory
    os.makedirs('build', exist_ok=True)
    
    # Build Python package
    if not run_command("python setup.py sdist bdist_wheel", "Building Python package"):
        return False
    
    return True

def create_release_package():
    """สร้าง release package"""
    print("🎁 Creating release package...")
    
    # Create release directory
    release_dir = f"build/release"
    os.makedirs(release_dir, exist_ok=True)
    
    # Copy essential files
    essential_files = [
        'src/',
        'config/',
        'docker/',
        'examples/',
        'tests/',
        'requirements.txt',
        'setup.py',
        'main.py',
        'test_quick.py',
        'README.md',
        'LICENSE'
    ]
    
    for item in essential_files:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, f"{release_dir}/{item}", dirs_exist_ok=True)
            else:
                shutil.copy2(item, f"{release_dir}/{item}")
            print(f"   Packaged: {item}")
    
    # Create version info
    version_info = {
        'version': '1.0.0',
        'build_date': datetime.now().isoformat(),
        'build_type': 'release'
    }
    
    with open(f"{release_dir}/build_info.txt", 'w') as f:
        for key, value in version_info.items():
            f.write(f"{key}: {value}\n")
    
    # Create ZIP archive
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"build/dataops-foundation-v1.0.0-{timestamp}.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, release_dir)
                zipf.write(file_path, arcname)
    
    print(f"   ✅ Release package created: {zip_name}")
    
    # Get package size
    size_mb = os.path.getsize(zip_name) / (1024 * 1024)
    print(f"   📏 Package size: {size_mb:.2f} MB")
    
    return zip_name

def main():
    """Main build function"""
    print("🚀 DataOps Foundation - Build Script")
    print("=" * 60)
    
    start_time = datetime.now()
    
    try:
        # Step 1: Clean previous builds
        clean_build()
        
        # Step 2: Run tests
        if not run_tests():
            print("❌ Tests failed. Build stopped.")
            return 1
        
        # Step 3: Run quality checks
        if not run_quality_checks():
            print("⚠️ Quality checks had issues, but continuing...")
        
        # Step 4: Generate documentation
        if not generate_documentation():
            print("⚠️ Documentation generation failed, but continuing...")
        
        # Step 5: Build package
        if not build_package():
            print("❌ Package build failed. Build stopped.")
            return 1
        
        # Step 6: Create release package
        release_package = create_release_package()
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("🎉 BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"⏱️ Build time: {duration:.2f} seconds")
        print(f"📦 Release package: {release_package}")
        print(f"📚 Documentation: build/docs/")
        print(f"🐍 Python package: dist/")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Test the release package")
        print(f"   2. Upload to PyPI: twine upload dist/*")
        print(f"   3. Create GitHub release")
        print(f"   4. Deploy with Docker: docker-compose up -d")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Build cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Build failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
