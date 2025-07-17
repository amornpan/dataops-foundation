#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Build Script
สคริปต์สำหรับการ build และ setup โปรเจค
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path
import json
from datetime import datetime

def print_banner():
    """แสดง banner ของโปรแกรม"""
    banner = """
    ██████╗  █████╗ ████████╗ █████╗  ██████╗ ██████╗ ███████╗
    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔═══██╗██╔══██╗██╔════╝
    ██║  ██║███████║   ██║   ███████║██║   ██║██████╔╝███████╗
    ██║  ██║██╔══██║   ██║   ██╔══██║██║   ██║██╔═══╝ ╚════██║
    ██████╔╝██║  ██║   ██║   ██║  ██║╚██████╔╝██║     ███████║
    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝
    
    🚀 DataOps Foundation Build System
    📊 Enterprise DataOps Platform
    🔗 https://github.com/amornpan/dataops-foundation
    """
    print(banner)

def run_command(command, description="", check=True):
    """รันคำสั่งและแสดงผลลัพธ์"""
    if description:
        print(f"🔄 {description}...")
    
    print(f"   $ {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(f"   ✅ Output: {result.stdout.strip()}")
        
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   ❌ Stderr: {e.stderr.strip()}")
        return False

def check_requirements():
    """ตรวจสอบความต้องการของระบบ"""
    print("🔍 Checking system requirements...")
    
    requirements = {
        'python': ['python3', '--version'],
        'pip': ['python3', '-m', 'pip', '--version'],
        'git': ['git', '--version']
    }
    
    all_ok = True
    
    for name, command in requirements.items():
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            version = result.stdout.strip().split('\n')[0]
            print(f"   ✅ {name}: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"   ❌ {name}: Not found or not working")
            all_ok = False
    
    return all_ok

def setup_virtual_environment():
    """ตั้งค่า virtual environment"""
    print("\n🐍 Setting up virtual environment...")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("   ⚠️ Virtual environment already exists")
        return True
    
    # สร้าง virtual environment
    if not run_command("python3 -m venv venv", "Creating virtual environment"):
        return False
    
    # ตรวจสอบ activation script
    if sys.platform == "win32":
        activate_script = venv_path / "Scripts" / "activate.bat"
        pip_command = "venv\\Scripts\\pip"
    else:
        activate_script = venv_path / "bin" / "activate"
        pip_command = "venv/bin/pip"
    
    if not activate_script.exists():
        print(f"   ❌ Activation script not found: {activate_script}")
        return False
    
    # อัพเกรด pip
    if not run_command(f"{pip_command} install --upgrade pip", "Upgrading pip"):
        return False
    
    print("   ✅ Virtual environment created successfully")
    return True

def install_dependencies():
    """ติดตั้ง dependencies"""
    print("\n📦 Installing dependencies...")
    
    if sys.platform == "win32":
        pip_command = "venv\\Scripts\\pip"
    else:
        pip_command = "venv/bin/pip"
    
    # ติดตั้ง main dependencies
    if not run_command(f"{pip_command} install -r requirements.txt", "Installing main dependencies"):
        return False
    
    # ติดตั้ง development dependencies (optional)
    dev_packages = [
        "jupyter",
        "ipykernel",
        "sphinx",
        "sphinx-rtd-theme"
    ]
    
    for package in dev_packages:
        run_command(f"{pip_command} install {package}", f"Installing {package} (optional)", check=False)
    
    print("   ✅ Dependencies installed successfully")
    return True

def create_directories():
    """สร้างโฟลเดอร์ที่จำเป็น"""
    print("\n📁 Creating necessary directories...")
    
    directories = [
        "data",
        "temp",
        "logs",
        "backup",
        "examples/sample_data",
        "tests/fixtures",
        "docs/build",
        "docker/jenkins-config"
    ]
    
    for dir_path in directories:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"   📂 Created: {dir_path}")
        else:
            print(f"   ✅ Exists: {dir_path}")
    
    return True

def setup_configuration():
    """ตั้งค่า configuration files"""
    print("\n⚙️ Setting up configuration...")
    
    config_path = Path("config/config.yaml")
    
    if config_path.exists():
        print("   ✅ Configuration file already exists")
        return True
    
    # สร้าง config directory ถ้าไม่มี
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("   ✅ Configuration setup completed")
    return True

def run_tests():
    """รันการทดสอบ"""
    print("\n🧪 Running tests...")
    
    if sys.platform == "win32":
        python_command = "venv\\Scripts\\python"
    else:
        python_command = "venv/bin/python"
    
    # รัน quick test
    if Path("test_quick.py").exists():
        if run_command(f"{python_command} test_quick.py", "Running quick tests"):
            print("   ✅ Quick tests passed")
        else:
            print("   ⚠️ Some quick tests failed")
    
    # รัน main test suite
    if Path("tests/test_enhanced_etl.py").exists():
        if run_command(f"{python_command} tests/test_enhanced_etl.py", "Running main test suite", check=False):
            print("   ✅ Main tests passed")
        else:
            print("   ⚠️ Some main tests failed")
    
    return True

def generate_sample_data():
    """สร้างข้อมูลตัวอย่าง"""
    print("\n🏭 Generating sample data...")
    
    if sys.platform == "win32":
        python_command = "venv\\Scripts\\python"
    else:
        python_command = "venv/bin/python"
    
    sample_script = Path("examples/generate_sample_data.py")
    
    if sample_script.exists():
        if run_command(f"{python_command} {sample_script}", "Generating sample datasets"):
            print("   ✅ Sample data generated successfully")
        else:
            print("   ⚠️ Sample data generation failed")
    else:
        print("   ⚠️ Sample data generator not found")
    
    return True

def build_docker_images():
    """สร้าง Docker images"""
    print("\n🐳 Building Docker images...")
    
    dockerfile_path = Path("docker/Dockerfile")
    
    if not dockerfile_path.exists():
        print("   ⚠️ Dockerfile not found, skipping Docker build")
        return True
    
    # Build main application image
    if run_command(
        "docker build -f docker/Dockerfile -t dataops-foundation:latest .",
        "Building main application image",
        check=False
    ):
        print("   ✅ Main application image built successfully")
    else:
        print("   ⚠️ Main application image build failed")
    
    # Build Jenkins image
    jenkins_dockerfile = Path("docker/Dockerfile.jenkins")
    if jenkins_dockerfile.exists():
        if run_command(
            "docker build -f docker/Dockerfile.jenkins -t dataops-jenkins:latest docker/",
            "Building Jenkins image",
            check=False
        ):
            print("   ✅ Jenkins image built successfully")
        else:
            print("   ⚠️ Jenkins image build failed")
    
    return True

def create_build_info():
    """สร้างข้อมูล build"""
    print("\n📋 Creating build information...")
    
    try:
        # Get Git information
        git_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False
        ).stdout.strip()
        
        git_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=False
        ).stdout.strip()
        
        build_info = {
            "build_timestamp": datetime.now().isoformat(),
            "git_commit": git_commit if git_commit else "unknown",
            "git_branch": git_branch if git_branch else "unknown",
            "python_version": sys.version,
            "platform": sys.platform,
            "project_name": "DataOps Foundation",
            "version": "1.0.0"
        }
        
        with open("build_info.json", "w") as f:
            json.dump(build_info, f, indent=2)
        
        print("   ✅ Build information created")
        return True
        
    except Exception as e:
        print(f"   ⚠️ Failed to create build info: {e}")
        return False

def cleanup():
    """ทำความสะอาด"""
    print("\n🧹 Cleaning up...")
    
    cleanup_patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "temp/*.csv",
        "*.log"
    ]
    
    for pattern in cleanup_patterns:
        for path in Path(".").glob(pattern):
            if path.is_file():
                path.unlink()
                print(f"   🗑️ Removed file: {path}")
            elif path.is_dir():
                shutil.rmtree(path)
                print(f"   🗑️ Removed directory: {path}")
    
    print("   ✅ Cleanup completed")

def main():
    """ฟังก์ชันหลัก"""
    parser = argparse.ArgumentParser(description="DataOps Foundation Build System")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker image building")
    parser.add_argument("--cleanup-only", action="store_true", help="Only run cleanup")
    parser.add_argument("--dev-mode", action="store_true", help="Development mode setup")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.cleanup_only:
        cleanup()
        return
    
    print(f"🚀 Starting DataOps Foundation build process...")
    print(f"⏰ Build started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Build steps
    steps = [
        ("System Requirements", check_requirements),
        ("Virtual Environment", setup_virtual_environment),
        ("Dependencies", install_dependencies),
        ("Directories", create_directories),
        ("Configuration", setup_configuration),
        ("Sample Data", generate_sample_data),
        ("Build Info", create_build_info),
    ]
    
    if not args.skip_tests:
        steps.append(("Tests", run_tests))
    
    if not args.skip_docker:
        steps.append(("Docker Images", build_docker_images))
    
    # Execute steps
    failed_steps = []
    start_time = datetime.now()
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed with exception: {e}")
            failed_steps.append(step_name)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Build Summary")
    print("=" * 70)
    print(f"⏰ Duration: {duration}")
    print(f"✅ Successful steps: {len(steps) - len(failed_steps)}/{len(steps)}")
    
    if failed_steps:
        print(f"❌ Failed steps: {', '.join(failed_steps)}")
        print("\n⚠️ Build completed with some failures.")
        print("Please review the error messages above and fix any issues.")
    else:
        print("\n🎉 Build completed successfully!")
        print("\n🚀 Next steps:")
        print("   1. Run: python main.py --mode info")
        print("   2. Generate data: python main.py --mode generate-data")
        print("   3. Run ETL: python main.py --mode etl --input examples/sample_data/generated_data.csv")
        print("   4. Check quality: python main.py --mode quality --input examples/sample_data/generated_data.csv")
    
    print("=" * 70)
    
    return len(failed_steps) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
