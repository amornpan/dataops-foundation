#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Quick Test Script
สคริปต์ทดสอบรวดเร็วเพื่อตรวจสอบการทำงานของระบบ
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_system():
    """ทดสอบระบบอย่างรวดเร็ว"""
    
    print("🚀 DataOps Foundation - Quick System Test")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Import main modules
    print("\n1️⃣ Testing module imports...")
    tests_total += 1
    try:
        from src.data_pipeline.etl_processor import ETLProcessor
        from src.data_quality.quality_checker import DataQualityChecker
        from src.monitoring.metrics_collector import MetricsCollector
        from src.utils.config_manager import ConfigManager
        from src.utils.logger import setup_logger
        print("   ✅ All main modules imported successfully")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Module import failed: {e}")
    
    # Test 2: Configuration loading
    print("\n2️⃣ Testing configuration...")
    tests_total += 1
    try:
        config = ConfigManager()
        db_config = config.get_database_config()
        print(f"   ✅ Configuration loaded successfully")
        print(f"      Database host: {db_config.get('host', 'Not configured')}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
    
    # Test 3: Sample data generation
    print("\n3️⃣ Testing sample data generation...")
    tests_total += 1
    try:
        from examples.generate_sample_data import generate_loan_data
        
        # Generate small sample
        df = generate_loan_data(n_records=100, output_file=None)
        
        if len(df) == 100 and len(df.columns) > 10:
            print(f"   ✅ Sample data generated: {len(df)} records, {len(df.columns)} columns")
            tests_passed += 1
        else:
            print(f"   ❌ Sample data validation failed")
            
    except Exception as e:
        print(f"   ❌ Sample data generation failed: {e}")
    
    # Test 4: ETL Processor initialization
    print("\n4️⃣ Testing ETL Processor...")
    tests_total += 1
    try:
        processor = ETLProcessor()
        
        # Test column type inference
        import tempfile
        import pandas as pd
        
        # Create temporary CSV
        sample_data = pd.DataFrame({
            'loan_amnt': [1000, 2000, 3000],
            'int_rate': ['5.5%', '6.0%', '7.2%'],
            'home_ownership': ['RENT', 'OWN', 'MORTGAGE']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        success, column_types = processor.guess_column_types(temp_file)
        os.unlink(temp_file)  # Clean up
        
        if success and len(column_types) > 0:
            print(f"   ✅ ETL Processor working: detected {len(column_types)} column types")
            tests_passed += 1
        else:
            print(f"   ❌ ETL Processor test failed")
            
    except Exception as e:
        print(f"   ❌ ETL Processor test failed: {e}")
    
    # Test 5: Data Quality Checker
    print("\n5️⃣ Testing Data Quality Checker...")
    tests_total += 1
    try:
        import pandas as pd
        
        # Create test data
        test_data = pd.DataFrame({
            'loan_amnt': [1000, 2000, 3000, 4000, 5000],
            'funded_amnt': [950, 1900, 2950, 3900, 4900],
            'int_rate': [0.055, 0.06, 0.072, 0.08, 0.095],
            'home_ownership': ['RENT', 'OWN', 'MORTGAGE', 'RENT', 'OWN']
        })
        
        checker = DataQualityChecker()
        result = checker.run_checks(test_data)
        
        if result.overall_score > 0:
            print(f"   ✅ Data Quality Checker working: score {result.overall_score:.1f}%")
            tests_passed += 1
        else:
            print(f"   ❌ Data Quality Checker test failed")
            
    except Exception as e:
        print(f"   ❌ Data Quality Checker test failed: {e}")
    
    # Test 6: Metrics Collector
    print("\n6️⃣ Testing Metrics Collector...")
    tests_total += 1
    try:
        collector = MetricsCollector()
        
        # Record test metrics
        collector.record_etl_records(100, 'test_pipeline', 'test_stage')
        collector.record_data_quality_score(95.5, 'test_dataset', 'completeness')
        
        summary = collector.get_metrics_summary()
        
        if summary['total_metrics'] > 0:
            print(f"   ✅ Metrics Collector working: {summary['total_metrics']} metrics recorded")
            tests_passed += 1
        else:
            print(f"   ❌ Metrics Collector test failed")
            
    except Exception as e:
        print(f"   ❌ Metrics Collector test failed: {e}")
    
    # Test 7: Logger
    print("\n7️⃣ Testing Logger...")
    tests_total += 1
    try:
        logger = setup_logger('test_logger')
        logger.info("Test log message")
        
        # Test structured logging
        logger.log_with_context('INFO', 'Test context message', test_id=123, component='test')
        
        print(f"   ✅ Logger working: structured logging available")
        tests_passed += 1
        
    except Exception as e:
        print(f"   ❌ Logger test failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Passed: {tests_passed}/{tests_total}")
    print(f"❌ Tests Failed: {tests_total - tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print(f"🎉 ALL TESTS PASSED! DataOps Foundation is ready to use.")
        success_rate = 100.0
    else:
        success_rate = (tests_passed / tests_total) * 100
        print(f"⚠️  Some tests failed. Success rate: {success_rate:.1f}%")
    
    print(f"\n💡 Next Steps:")
    if tests_passed == tests_total:
        print(f"   1. Generate sample data: python main.py --mode generate-data")
        print(f"   2. Run ETL pipeline: python main.py --mode etl --input examples/sample_data/generated_data.csv")
        print(f"   3. Run full tests: python tests/test_enhanced_etl.py")
        print(f"   4. Start with Docker: docker-compose -f docker/docker-compose.yml up -d")
    else:
        print(f"   1. Check missing dependencies: pip install -r requirements.txt")
        print(f"   2. Verify Python version: python --version (should be 3.9+)")
        print(f"   3. Check configuration: cat config/config.yaml")
    
    return 0 if tests_passed == tests_total else 1


if __name__ == "__main__":
    exit_code = test_system()
    sys.exit(exit_code)
