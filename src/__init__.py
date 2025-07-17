"""
DataOps Foundation - Main Package
Enterprise DataOps platform combining ETL processing, CI/CD, and data quality management

Features:
- Advanced ETL Processing (from ETL-dev (1).py)
- CI/CD Pipeline Integration (from python-jenkins)
- Data Quality Framework
- Monitoring & Observability
- Container-ready Architecture
- Enterprise Security & Scaling
"""

__version__ = "1.0.0"
__author__ = "DataOps Foundation Team"
__email__ = "dataops@company.com"
__description__ = "Enterprise DataOps platform for modern data engineering"

# Core modules
from .data_pipeline.etl_processor import ETLProcessor, ProcessingResult
from .data_quality.quality_checker import DataQualityChecker, QualityResult
from .monitoring.metrics_collector import MetricsCollector
from .utils.config_manager import ConfigManager
from .utils.logger import setup_logger, DataOpsLogger

# Version info
VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'patch': 0,
    'release': 'stable'
}

# Package metadata
PACKAGE_INFO = {
    'name': 'dataops-foundation',
    'version': __version__,
    'description': __description__,
    'author': __author__,
    'email': __email__,
    'url': 'https://github.com/amornpan/dataops-foundation',
    'license': 'MIT',
    'keywords': ['dataops', 'etl', 'data-quality', 'ci-cd', 'monitoring', 'data-engineering'],
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Database',
        'Topic :: System :: Monitoring',
    ]
}

# Export main classes
__all__ = [
    'ETLProcessor',
    'ProcessingResult', 
    'DataQualityChecker',
    'QualityResult',
    'MetricsCollector',
    'ConfigManager',
    'setup_logger',
    'DataOpsLogger',
    'VERSION_INFO',
    'PACKAGE_INFO'
]


def get_version():
    """Get package version"""
    return __version__


def get_package_info():
    """Get package information"""
    return PACKAGE_INFO


def print_banner():
    """Print DataOps Foundation banner"""
    banner = """
    ██████╗  █████╗ ████████╗ █████╗  ██████╗ ██████╗ ███████╗
    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔═══██╗██╔══██╗██╔════╝
    ██║  ██║███████║   ██║   ███████║██║   ██║██████╔╝███████╗
    ██║  ██║██╔══██║   ██║   ██╔══██║██║   ██║██╔═══╝ ╚════██║
    ██████╔╝██║  ██║   ██║   ██║  ██║╚██████╔╝██║     ███████║
    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝
    
    🚀 DataOps Foundation v{version}
    📊 Enterprise DataOps Platform
    🔗 https://github.com/amornpan/dataops-foundation
    """.format(version=__version__)
    
    print(banner)


# Initialize logging when package is imported
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create package logger
logger = logging.getLogger('dataops-foundation')
logger.info(f"DataOps Foundation v{__version__} initialized")
