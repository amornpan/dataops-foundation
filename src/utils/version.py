# DataOps Foundation - Version Information

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

# Build information
BUILD_DATE = "2025-01-17"
BUILD_COMMIT = "initial"
BUILD_BRANCH = "main"

# Version history
VERSION_HISTORY = {
    "1.0.0": {
        "date": "2025-01-17",
        "features": [
            "Enhanced ETL Processor (from ETL-dev (1).py)",
            "Jenkins CI/CD Pipeline (from python-jenkins)",
            "Data Quality Framework",
            "Prometheus Metrics Integration",
            "Docker Container Support",
            "Comprehensive Testing Suite"
        ],
        "breaking_changes": [],
        "bug_fixes": []
    }
}

def get_version():
    """Get the current version string"""
    return __version__

def get_version_info():
    """Get version information tuple"""
    return __version_info__

def print_version_info():
    """Print detailed version information"""
    print(f"DataOps Foundation v{__version__}")
    print(f"Build Date: {BUILD_DATE}")
    print(f"Build Commit: {BUILD_COMMIT}")
    print(f"Build Branch: {BUILD_BRANCH}")
