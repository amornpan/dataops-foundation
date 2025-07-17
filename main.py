#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Main Application Entry Point
รันแอปพลิเคชันหลักของ DataOps Foundation
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.data_pipeline.etl_processor import ETLProcessor
from src.data_quality.quality_checker import DataQualityChecker
from src.monitoring.metrics_collector import MetricsCollector
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger
from src import print_banner, get_version


def main():
    """Main application entry point"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='DataOps Foundation - Enterprise DataOps Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode etl --input data/sample.csv
  python main.py --mode quality --input data/sample.csv
  python main.py --mode generate-data --output examples/sample_data/test.csv
  python main.py --mode info
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['etl', 'quality', 'generate-data', 'info'],
        default='info',
        help='Operation mode (default: info)'
    )
    
    parser.add_argument(
        '--input', '-i',
        help='Input file path'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config/config.yaml',
        help='Configuration file path (default: config/config.yaml)'
    )
    
    parser.add_argument(
        '--records', '-r',
        type=int,
        default=1000,
        help='Number of records to generate (default: 1000)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'DataOps Foundation v{get_version()}'
    )
    
    args = parser.parse_args()
    
    # Show banner
    print_banner()
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logger = setup_logger(__name__, {'logging': {'level': log_level}})
    
    try:
        # Execute based on mode
        if args.mode == 'info':
            show_info()
            
        elif args.mode == 'etl':
            if not args.input:
                print("❌ Error: --input file is required for ETL mode")
                return 1
            return run_etl_pipeline(args.input, args.config)
            
        elif args.mode == 'quality':
            if not args.input:
                print("❌ Error: --input file is required for quality mode")
                return 1
            return run_quality_checks(args.input, args.config)
            
        elif args.mode == 'generate-data':
            output_file = args.output or 'examples/sample_data/generated_data.csv'
            return generate_sample_data(output_file, args.records)
            
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def show_info():
    """แสดงข้อมูลเกี่ยวกับระบบ"""
    print("📊 System Information:")
    print("=" * 50)
    
    # Python version
    import sys
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    
    # Check required modules
    required_modules = [
        'pandas', 'numpy', 'sqlalchemy', 'pymssql', 'yaml'
    ]
    
    print("\n📦 Required Modules:")
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} (not installed)")
    
    # Optional modules
    optional_modules = [
        'prometheus_client', 'docker', 'kubernetes'
    ]
    
    print("\n📦 Optional Modules:")
    for module in optional_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ⚠️  {module} (optional)")
    
    # Configuration
    try:
        config = ConfigManager()
        print(f"\n⚙️ Configuration:")
        print(f"   📁 Config File: config/config.yaml")
        print(f"   🗄️ Database: {config.get('database.primary.type', 'Not configured')}")
        print(f"   📊 Monitoring: {'Enabled' if config.get('monitoring.enabled') else 'Disabled'}")
        
        # Validate configuration
        validation = config.validate_config()
        if validation['valid']:
            print(f"   ✅ Configuration is valid")
        else:
            print(f"   ❌ Configuration has {len(validation['errors'])} error(s)")
            
    except Exception as e:
        print(f"   ⚠️ Configuration error: {e}")
    
    print(f"\n🚀 Quick Start:")
    print(f"   python main.py --mode generate-data --records 1000")
    print(f"   python main.py --mode etl --input examples/sample_data/generated_data.csv")
    print(f"   python main.py --mode quality --input examples/sample_data/generated_data.csv")


def run_etl_pipeline(input_file, config_file):
    """รัน ETL pipeline"""
    print(f"🔄 Starting ETL Pipeline")
    print(f"📁 Input file: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file not found: {input_file}")
        return 1
    
    try:
        # Initialize ETL processor
        processor = ETLProcessor(config_file)
        
        # Run full pipeline
        result = processor.run_full_pipeline(input_file)
        
        if result.success:
            print(f"\n✅ ETL Pipeline completed successfully!")
            print(f"📊 Processed records: {result.processed_records:,}")
            print(f"🎯 Quality score: {result.quality_score:.1f}%")
            print(f"⏱️ Processing time: {result.processing_time:.2f} seconds")
            
            if result.metadata:
                print(f"\n📋 Pipeline Details:")
                for key, value in result.metadata.items():
                    if isinstance(value, dict):
                        print(f"   {key}: {len(value)} items")
                    elif isinstance(value, list):
                        print(f"   {key}: {len(value)} items")
                    else:
                        print(f"   {key}: {value}")
            
            return 0
        else:
            print(f"\n❌ ETL Pipeline failed!")
            print(f"⏱️ Processing time: {result.processing_time:.2f} seconds")
            for error in result.errors:
                print(f"   Error: {error}")
            return 1
            
    except Exception as e:
        print(f"❌ ETL Pipeline error: {e}")
        return 1


def run_quality_checks(input_file, config_file):
    """รันการตรวจสอบคุณภาพข้อมูล"""
    print(f"🔍 Starting Data Quality Checks")
    print(f"📁 Input file: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file not found: {input_file}")
        return 1
    
    try:
        import pandas as pd
        
        # Load data
        df = pd.read_csv(input_file)
        print(f"📊 Loaded {len(df):,} records with {len(df.columns)} columns")
        
        # Initialize quality checker
        config = ConfigManager(config_file).config
        checker = DataQualityChecker(config)
        
        # Run quality checks
        result = checker.run_checks(df)
        
        # Generate and show report
        report = checker.generate_report(result)
        print(report)
        
        return 0 if result.overall_score >= 80 else 1
        
    except Exception as e:
        print(f"❌ Quality check error: {e}")
        return 1


def generate_sample_data(output_file, num_records):
    """สร้างข้อมูลตัวอย่าง"""
    print(f"🏭 Generating sample data")
    print(f"📊 Records: {num_records:,}")
    print(f"📁 Output file: {output_file}")
    
    try:
        # Import the generate function
        from examples.generate_sample_data import generate_loan_data
        
        # Generate data
        df = generate_loan_data(num_records, output_file)
        
        print(f"\n✅ Sample data generated successfully!")
        print(f"📁 File: {output_file}")
        print(f"📊 Records: {len(df):,}")
        print(f"📋 Columns: {len(df.columns)}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Data generation error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
