#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Version Information
การจัดการข้อมูลเวอร์ชันของระบบ
"""

import os
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional

# Version information
__version__ = "1.0.0"
__build__ = "20250117"
__author__ = "DataOps Foundation Team"
__email__ = "dataops@company.com"
__license__ = "MIT"

# Version components
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_PRERELEASE = None  # 'alpha', 'beta', 'rc'
VERSION_BUILD = None


def get_version() -> str:
    """ดึงเวอร์ชันปัจจุบัน"""
    return __version__


def get_build() -> str:
    """ดึงหมายเลข build"""
    return __build__


def get_version_info() -> Dict[str, Any]:
    """ดึงข้อมูลเวอร์ชันทั้งหมด"""
    return {
        'version': __version__,
        'build': __build__,
        'major': VERSION_MAJOR,
        'minor': VERSION_MINOR,
        'patch': VERSION_PATCH,
        'prerelease': VERSION_PRERELEASE,
        'build_info': VERSION_BUILD,
        'author': __author__,
        'email': __email__,
        'license': __license__
    }


def get_git_info() -> Dict[str, Optional[str]]:
    """ดึงข้อมูลจาก Git repository"""
    git_info = {
        'commit_hash': None,
        'branch': None,
        'tag': None,
        'dirty': False,
        'commit_date': None
    }
    
    try:
        # Get current commit hash
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            git_info['commit_hash'] = result.stdout.strip()
        
        # Get current branch
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            git_info['branch'] = result.stdout.strip()
        
        # Get latest tag
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            git_info['tag'] = result.stdout.strip()
        
        # Check if working directory is dirty
        result = subprocess.run(
            ['git', 'diff-index', '--quiet', 'HEAD', '--'],
            capture_output=True,
            timeout=10
        )
        git_info['dirty'] = result.returncode != 0
        
        # Get commit date
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%cd', '--date=iso'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            git_info['commit_date'] = result.stdout.strip()
            
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return git_info


def get_extended_version_info() -> Dict[str, Any]:
    """ดึงข้อมูลเวอร์ชันแบบขยาย"""
    info = get_version_info()
    
    # เพิ่มข้อมูล Git
    git_info = get_git_info()
    info['git'] = git_info
    
    # เพิ่มข้อมูลระบบ
    info['system'] = {
        'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        'platform': os.sys.platform,
        'build_date': datetime.now().isoformat(),
        'cwd': os.getcwd()
    }
    
    return info


def print_version_info():
    """แสดงข้อมูลเวอร์ชันแบบละเอียด"""
    info = get_extended_version_info()
    
    print(f"DataOps Foundation v{info['version']}")
    print(f"Build: {info['build']}")
    print(f"Author: {info['author']}")
    print(f"License: {info['license']}")
    print()
    
    # Git information
    git = info['git']
    if git['commit_hash']:
        print(f"Git Commit: {git['commit_hash'][:8]}")
        print(f"Git Branch: {git['branch']}")
        if git['tag']:
            print(f"Git Tag: {git['tag']}")
        print(f"Working Directory: {'dirty' if git['dirty'] else 'clean'}")
        if git['commit_date']:
            print(f"Commit Date: {git['commit_date']}")
    else:
        print("Git information not available")
    
    print()
    
    # System information
    system = info['system']
    print(f"Python Version: {system['python_version']}")
    print(f"Platform: {system['platform']}")
    print(f"Build Date: {system['build_date']}")


def get_version_string() -> str:
    """ดึงข้อมูลเวอร์ชันแบบสั้น"""
    git_info = get_git_info()
    
    version_str = f"v{__version__}"
    
    if git_info['commit_hash']:
        version_str += f"-{git_info['commit_hash'][:8]}"
    
    if git_info['dirty']:
        version_str += "-dirty"
    
    if __build__:
        version_str += f"+{__build__}"
    
    return version_str


if __name__ == "__main__":
    print_version_info()
