#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Quick Test
ทดสอบระบบอย่างรวดเร็วเพื่อตรวจสอบการทำงาน
"""

import os
import sys
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_header():
    """แสดง header ของโปรแกรม"""
    print("=" * 70)
    print("🚀 DataOps Foundation - Quick Test")
    print("=" * 70)
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def test_imports():
    """ทดสอบการ import modules"""
    print("📦 Testing Module Imports...")
    
    try:
        # Core modules
        import pandas as pd
        import numpy as np
        import yaml
        print("   ✅ Core modules (pandas, numpy, yaml)")
        
        # DataOps modules
        from src.utils.config_manager import ConfigManager
        from src.utils.logger import setup_logger
        from src.data_pipeline.etl_processor import ETLProcessor
        from src.data_quality.quality_checker import DataQualityChecker
        from src.monitoring.metrics_collector import MetricsCollector
        print("   ✅ DataOps modules")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_configuration():
    """ทดสอบการตั้งค่า"""
    print("\n⚙️ Testing Configuration...")
    
    try:
        from src.utils.config_manager import ConfigManager
        
        config = ConfigManager('config/config.yaml')
        validation = config.validate_config()
        
        print(f"   Configuration Status: {'✅ VALID' if validation['valid'] else '❌ INVALID'}")
        
        if validation['errors']:
            print("   ❌ Errors found:")
            for error in validation['errors'][:3]:
                print(f"      - {error}")
                
        if validation['warnings']:
            print("   ⚠️ Warnings found:")
            for warning in validation['warnings'][:3]:
                print(f"      - {warning}")
        
        return validation['valid']
        
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False

def test_sample_data_generation():
    """ทดสอบการสร้างข้อมูลตัวอย่าง"""
    print("\n🏭 Testing Sample Data Generation...")
    
    try:
        sys.path.insert(0, 'examples')
        from examples.generate_sample_data import generate_loan_data
        
        print("   Generating 100 sample records...")
        df = generate_loan_data(100, 'temp/test_data.csv')
        
        print(f"   ✅ Generated {len(df)} records with {len(df.columns)} columns")
        return True
        
    except Exception as e:
        print(f"   ❌ Sample data generation error: {e}")
        return False

def test_etl_processor():
    """ทดสอบ ETL Processor"""
    print("\n🔄 Testing ETL Processor...")
    
    try:
        from src.data_pipeline.etl_processor import ETLProcessor
        
        # ตรวจสอบว่ามีไฟล์ทดสอบหรือไม่
        test_file = 'temp/test_data.csv'
        if not os.path.exists(test_file):
            print("   ⚠️ Test data file not found, skipping ETL test")
            return True
        
        processor = ETLProcessor()
        result = processor.load_data(test_file)
        
        if result.success:
            print(f"   ✅ ETL test passed - processed {result.processed_records} records")
            return True
        else:
            print(f"   ❌ ETL test failed: {result.errors}")
            return False
            
    except Exception as e:
        print(f"   ❌ ETL processor error: {e}")
        return False

def test_data_quality():
    """ทดสอบ Data Quality Checker"""
    print("\n📊 Testing Data Quality Checker...")
    
    try:
        import pandas as pd
        from src.data_quality.quality_checker import DataQualityChecker
        
        # สร้างข้อมูลทดสอบ
        test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'age': [25, 30, 35, 28, 32],
            'salary': [50000, 60000, 70000, 55000, 65000]
        })
        
        checker = DataQualityChecker()
        result = checker.run_checks(test_data)
        
        print(f"   ✅ Quality Score: {result.overall_score:.1f}%")
        print(f"   ✅ Grade: {result.grade}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Data quality checker error: {e}")
        return False

def test_monitoring():
    """ทดสอบ Monitoring System"""
    print("\n📈 Testing Monitoring System...")
    
    try:
        from src.monitoring.metrics_collector import MetricsCollector
        
        collector = MetricsCollector()
        
        # ทดสอบการบันทึกเมตริก
        collector.record_metric('test_metric', 75.5, {'unit': 'percent'})
        
        # ทดสอบการดูภาพรวม
        overview = collector.get_system_overview()
        
        print(f"   ✅ Monitoring system status: {overview['monitoring_status']}")
        print(f"   ✅ Total metrics collected: {overview['total_metrics_collected']}")
        
        # ทำความสะอาด
        collector.stop_monitoring_service()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Monitoring system error: {e}")
        return False

def test_logging():
    """ทดสอบ Logging System"""
    print("\n📝 Testing Logging System...")
    
    try:
        from src.utils.logger import setup_logger
        
        logger = setup_logger('test_logger')
        
        logger.info("Test log message")
        logger.debug("Test debug message")
        logger.warning("Test warning message")
        
        print("   ✅ Logging system working")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Logging system error: {e}")
        return False

def cleanup():
    """ทำความสะอาดไฟล์ทดสอบ"""
    print("\n🧹 Cleaning up...")
    
    cleanup_files = [
        'temp/test_data.csv'
    ]
    
    for file_path in cleanup_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"   🗑️ Removed {file_path}")
            except:
                pass

def main():
    """รันการทดสอบทั้งหมด"""
    print_header()
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Sample Data Generation", test_sample_data_generation),
        ("ETL Processor", test_etl_processor),
        ("Data Quality Checker", test_data_quality),
        ("Monitoring System", test_monitoring),
        ("Logging System", test_logging)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    start_time = time.time()
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # แสดงผลลัพธ์
    print("\n" + "=" * 70)
    print("📊 Test Results Summary:")
    print("=" * 70)
    print(f"✅ Passed: {passed_tests}/{total_tests} tests")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests} tests")
    print(f"⏱️ Duration: {duration:.2f} seconds")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! DataOps Foundation is ready to use.")
        status = "SUCCESS"
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
        status = "PARTIAL"
    
    # ทำความสะอาด
    cleanup()
    
    print(f"\n⏰ End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return status

if __name__ == "__main__":
    result = main()
    
    # Exit with appropriate code
    if result == "SUCCESS":
        sys.exit(0)
    else:
        sys.exit(1)
