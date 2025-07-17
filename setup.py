"""
DataOps Foundation - Setup Configuration
Installation script for the DataOps Foundation package
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get version
def get_version():
    version_file = os.path.join("src", "utils", "version.py")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            exec(f.read())
            return locals().get("__version__", "0.1.0")
    return "0.1.0"

setup(
    name="dataops-foundation",
    version=get_version(),
    author="DataOps Foundation Team",
    author_email="dataops@company.com",
    description="Enterprise DataOps platform combining ETL processing, CI/CD, and data quality management",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/amornpan/dataops-foundation",
    project_urls={
        "Documentation": "https://github.com/amornpan/dataops-foundation/docs",
        "Issues": "https://github.com/amornpan/dataops-foundation/issues",
        "Source": "https://github.com/amornpan/dataops-foundation",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: System :: Monitoring",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0",
        ],
        "cloud": [
            "boto3>=1.26.0",
            "azure-storage-blob>=12.16.0",
            "google-cloud-storage>=2.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dataops-etl=data_pipeline.etl_processor:main",
            "dataops-quality=data_quality.quality_checker:main",
            "dataops-monitor=monitoring.metrics_collector:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.sql", "*.md"],
    },
    zip_safe=False,
)
