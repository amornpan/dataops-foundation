#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Enhanced Tests
ทดสอบระบบ ETL ขั้นสูงที่รวมโค้ดจาก ETL-dev (1).py และ python-jenkins

Features:
- Unit tests for ETL processor
- Data quality testing
- Performance testing
- Integration testing
- CI/CD pipeline testing
"""

import unittest
import pandas as pd
import numpy as np
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import sys
import logging
from datetime import datetime, timedelta
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.data_pipeline.etl_processor import ETLProcessor, ProcessingResult
from src.data_quality.quality_checker import DataQualityChecker, QualityResult
from src.monitoring.metrics_collector import MetricsCollector
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger


class TestETLProcessor(unittest.TestCase):
    """ทดสอบ ETL Processor (จาก ETL-dev (1).py)"""
    
    def setUp(self):
        """ตั้งค่าก่อนแต่ละการทดสอบ"""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, 'config.yaml')
        
        # สร้าง config สำหรับทดสอบ
        test_config = {
            'data_quality': {
                'max_null_percentage': 30.0,
                'acceptable_max_null': 26
            },
            'database': {
                'primary': {
                    'type': 'mssql',
                    'host': 'localhost',
                    'database': 'test_db',
                    'username': 'test',
                    'password': 'test'
                }
            }
        }
        
        import yaml
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        self.processor = ETLProcessor(self.config_path)
        
        # สร้างข้อมูลตัวอย่าง
        self.sample_data = self._create_sample_data()
        self.sample_file = os.path.join(self.test_dir, 'test_data.csv')
        self.sample_data.to_csv(self.sample_file, index=False)
    
    def tearDown(self):
        """ทำความสะอาดหลังแต่ละการทดสอบ"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _create_sample_data(self):
        """สร้างข้อมูลตัวอย่างสำหรับทดสอบ"""
        data = {
            'id': range(1, 101),
            'loan_amnt': np.random.uniform(1000, 50000, 100),
            'funded_amnt': np.random.uniform(1000, 50000, 100),
            'term': [' 36 months'] * 70 + [' 60 months'] * 30,
            'int_rate': [f'{rate:.2f}%' for rate in np.random.uniform(5, 25, 100)],
            'installment': np.random.uniform(100, 2000, 100),
            'home_ownership': np.random.choice(['RENT', 'OWN', 'MORTGAGE'], 100),
            'loan_status': np.random.choice(['Fully Paid', 'Current', 'Charged Off'], 100),
            'issue_d': pd.date_range(start='2023-01-01', periods=100, freq='D').strftime('%b-%Y'),
            'application_type': np.random.choice(['Individual', 'Joint App'], 100),
            'annual_inc': np.random.uniform(30000, 150000, 100),
            'dti': np.random.uniform(0, 40, 100),
            'delinq_2yrs': np.random.randint(0, 5, 100),
            'earliest_cr_line': pd.date_range(start='2010-01-01', periods=100, freq='D').strftime('%b-%Y'),
            'open_acc': np.random.randint(1, 20, 100),
            'pub_rec': np.random.randint(0, 3, 100),
            'revol_bal': np.random.uniform(0, 50000, 100),
            'revol_util': np.random.uniform(0, 100, 100),
            'total_acc': np.random.randint(5, 50, 100)
        }
        
        df = pd.DataFrame(data)
        
        # เพิ่ม null values บางส่วน
        df.loc[95:99, 'home_ownership'] = None
        df.loc[90:94, 'loan_status'] = None
        df.loc[85:89, 'revol_util'] = None
        
        # เพิ่มคอลัมน์ที่มี null เกิน 30%
        df['mostly_null_column'] = None
        df.loc[0:20, 'mostly_null_column'] = 'some_value'
        
        return df
    
    def test_load_data(self):
        """ทดสอบการโหลดข้อมูล"""
        result = self.processor.load_data(self.sample_file)
        
        self.assertTrue(result.success)
        self.assertEqual(result.processed_records, 100)
        self.assertIsNotNone(self.processor.raw_df)
        self.assertEqual(len(self.processor.raw_df), 100)
    
    def test_load_data_file_not_found(self):
        """ทดสอบการโหลดข้อมูลเมื่อไฟล์ไม่พบ"""
        result = self.processor.load_data('non_existent_file.csv')
        
        self.assertFalse(result.success)
        self.assertEqual(result.processed_records, 0)
        self.assertTrue(len(result.errors) > 0)
    
    def test_guess_column_types(self):
        """ทดสอบการเดาประเภทคอลัมน์"""
        success, column_types = self.processor.guess_column_types(self.sample_file)
        
        self.assertTrue(success)
        self.assertIsInstance(column_types, dict)
        self.assertIn('id', column_types)
        self.assertIn('loan_amnt', column_types)
        self.assertIn('int_rate', column_types)
    
    def test_filter_by_null_percentage(self):
        """ทดสอบการกรองคอลัมน์ตาม null percentage"""
        # โหลดข้อมูลก่อน
        self.processor.load_data(self.sample_file)
        
        # กรองด้วย null percentage
        result = self.processor.filter_by_null_percentage(30.0)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(self.processor.processed_df)
        
        # ตรวจสอบว่าคอลัมน์ที่มี null เกิน 30% ถูกกรองออก
        self.assertNotIn('mostly_null_column', self.processor.processed_df.columns)
    
    def test_filter_by_row_completeness(self):
        """ทดสอบการกรองแถวตามความสมบูรณ์"""
        # โหลดและกรองข้อมูลก่อน
        self.processor.load_data(self.sample_file)
        self.processor.filter_by_null_percentage(30.0)
        
        # กรองแถว
        result = self.processor.filter_by_row_completeness(26)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(self.processor.processed_df)
        
        # ตรวจสอบว่าไม่มี null values
        self.assertEqual(self.processor.processed_df.isnull().sum().sum(), 0)
    
    def test_apply_data_transformations(self):
        """ทดสอบการแปลงข้อมูล"""
        # เตรียมข้อมูล
        self.processor.load_data(self.sample_file)
        self.processor.filter_by_null_percentage(30.0)
        self.processor.filter_by_row_completeness(26)
        
        # ทดสอบการแปลง
        result = self.processor.apply_data_transformations()
        
        self.assertTrue(result.success)
        
        # ตรวจสอบการแปลงข้อมูล
        if 'issue_d' in self.processor.processed_df.columns:
            self.assertEqual(self.processor.processed_df['issue_d'].dtype, 'datetime64[ns]')
        
        if 'int_rate' in self.processor.processed_df.columns:
            self.assertTrue(self.processor.processed_df['int_rate'].dtype in ['float64', 'float32'])
    
    def test_create_dimensional_model(self):
        """ทดสอบการสร้าง dimensional model"""
        # เตรียมข้อมูล
        self.processor.load_data(self.sample_file)
        self.processor.filter_by_null_percentage(30.0)
        self.processor.filter_by_row_completeness(26)
        self.processor.apply_data_transformations()
        
        # สร้าง dimensional model
        result = self.processor.create_dimensional_model()
        
        self.assertTrue(result.success)
        self.assertIsNotNone(self.processor.dimension_tables)
        
        # ตรวจสอบ dimension tables
        if 'home_ownership' in self.processor.dimension_tables:
            home_ownership_dim = self.processor.dimension_tables['home_ownership']
            self.assertIn('home_ownership_id', home_ownership_dim.columns)
            self.assertIn('home_ownership', home_ownership_dim.columns)
    
    def test_create_fact_table(self):
        """ทดสอบการสร้าง fact table"""
        # เตรียมข้อมูล
        self.processor.load_data(self.sample_file)
        self.processor.filter_by_null_percentage(30.0)
        self.processor.filter_by_row_completeness(26)
        self.processor.apply_data_transformations()
        self.processor.create_dimensional_model()
        
        # สร้าง fact table
        result = self.processor.create_fact_table()
        
        self.assertTrue(result.success)
        self.assertIsNotNone(self.processor.fact_table)
        
        # ตรวจสอบ foreign keys
        if 'home_ownership_id' in self.processor.fact_table.columns:
            self.assertFalse(self.processor.fact_table['home_ownership_id'].isnull().all())
    
    @patch('src.data_pipeline.etl_processor.create_engine')
    def test_save_to_database(self, mock_create_engine):
        """ทดสอบการบันทึกลงฐานข้อมูล"""
        # Mock engine
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        # เตรียมข้อมูล
        self.processor.load_data(self.sample_file)
        self.processor.filter_by_null_percentage(30.0)
        self.processor.filter_by_row_completeness(26)
        self.processor.apply_data_transformations()
        self.processor.create_dimensional_model()
        self.processor.create_fact_table()
        
        # บันทึกลงฐานข้อมูล
        result = self.processor.save_to_database()
        
        self.assertTrue(result.success)
        mock_create_engine.assert_called_once()
    
    def test_run_full_pipeline(self):
        """ทดสอบการรัน pipeline เต็ม"""
        with patch('src.data_pipeline.etl_processor.create_engine') as mock_create_engine:
            mock_engine = Mock()
            mock_create_engine.return_value = mock_engine
            
            result = self.processor.run_full_pipeline(self.sample_file)
            
            self.assertTrue(result.success)
            self.assertGreater(result.processed_records, 0)
            self.assertGreater(result.quality_score, 0)
            self.assertGreater(result.processing_time, 0)


class TestDataQualityChecker(unittest.TestCase):
    """ทดสอบ Data Quality Checker"""
    
    def setUp(self):
        """ตั้งค่าก่อนแต่ละการทดสอบ"""
        self.checker = DataQualityChecker()
        self.sample_data = self._create_sample_data()
    
    def _create_sample_data(self):
        """สร้างข้อมูลตัวอย่าง"""
        data = {
            'id': [1, 2, 3, 4, 5, 5],  # มีข้อมูลซ้ำ
            'name': ['John', 'Jane', '', 'Bob', 'Alice', 'Alice'],  # มีข้อมูลว่าง
            'email': ['john@test.com', 'jane@test.com', 'invalid-email', 'bob@test.com', None, 'alice@test.com'],
            'age': [25, 30, -5, 35, 28, 28],  # มีอายุติดลบ
            'salary': [50000, 60000, 70000, None, 55000, 55000],  # มีค่าว่าง
            'phone': ['123-456-7890', '987-654-3210', 'invalid', '555-123-4567', None, '555-987-6543'],
            'date_joined': ['2023-01-01', '2023-02-01', '2023-13-01', '2023-04-01', '2023-05-01', '2023-05-01']
        }
        
        return pd.DataFrame(data)
    
    def test_calculate_completeness(self):
        """ทดสอบการคำนวณความสมบูรณ์"""
        metric = self.checker.calculate_completeness(self.sample_data)
        
        self.assertEqual(metric.name, 'completeness')
        self.assertIsInstance(metric.value, float)
        self.assertGreaterEqual(metric.value, 0)
        self.assertLessEqual(metric.value, 1)
        self.assertIsInstance(metric.passed, bool)
    
    def test_calculate_uniqueness(self):
        """ทดสอบการคำนวณความเป็นเอกลักษณ์"""
        metric = self.checker.calculate_uniqueness(self.sample_data)
        
        self.assertEqual(metric.name, 'uniqueness')
        self.assertIsInstance(metric.value, float)
        self.assertGreaterEqual(metric.value, 0)
        self.assertLessEqual(metric.value, 1)
        self.assertIsInstance(metric.passed, bool)
    
    def test_calculate_consistency(self):
        """ทดสอบการคำนวณความสม่ำเสมอ"""
        metric = self.checker.calculate_consistency(self.sample_data)
        
        self.assertEqual(metric.name, 'consistency')
        self.assertIsInstance(metric.value, float)
        self.assertGreaterEqual(metric.value, 0)
        self.assertLessEqual(metric.value, 1)
        self.assertIsInstance(metric.passed, bool)
    
    def test_calculate_validity(self):
        """ทดสอบการคำนวณความถูกต้อง"""
        metric = self.checker.calculate_validity(self.sample_data)
        
        self.assertEqual(metric.name, 'validity')
        self.assertIsInstance(metric.value, float)
        self.assertGreaterEqual(metric.value, 0)
        self.assertLessEqual(metric.value, 1)
        self.assertIsInstance(metric.passed, bool)
    
    def test_run_checks(self):
        """ทดสอบการรันการตรวจสอบทั้งหมด"""
        result = self.checker.run_checks(self.sample_data)
        
        self.assertIsInstance(result, QualityResult)
        self.assertIsInstance(result.overall_score, float)
        self.assertIn(result.grade, ['A', 'B', 'C', 'D', 'F'])
        self.assertIsInstance(result.passed, bool)
        self.assertIsInstance(result.metrics, list)
        self.assertEqual(len(result.metrics), 4)  # completeness, uniqueness, consistency, validity
    
    def test_generate_report(self):
        """ทดสอบการสร้างรายงาน"""
        result = self.checker.run_checks(self.sample_data)
        report = self.checker.generate_report(result)
        
        self.assertIsInstance(report, str)
        self.assertIn('DATA QUALITY ASSESSMENT REPORT', report)
        self.assertIn('OVERALL QUALITY SCORE', report)
        self.assertIn('DETAILED METRICS', report)
        self.assertIn('RECOMMENDATIONS', report)
    
    def test_empty_dataframe(self):
        """ทดสอบกับ DataFrame ว่าง"""
        empty_df = pd.DataFrame()
        result = self.checker.run_checks(empty_df)
        
        self.assertFalse(result.passed)
        self.assertEqual(result.overall_score, 0.0)
        self.assertEqual(result.grade, 'F')


class TestMetricsCollector(unittest.TestCase):
    """ทดสอบ Metrics Collector"""
    
    def setUp(self):
        """ตั้งค่าก่อนแต่ละการทดสอบ"""
        self.collector = MetricsCollector()
    
    def tearDown(self):
        """ทำความสะอาดหลังแต่ละการทดสอบ"""
        self.collector.stop_monitoring_service()
    
    def test_record_metric(self):
        """ทดสอบการบันทึกเมตริก"""
        self.collector.record_metric('test_metric', 75.5, {'unit': 'percent'})
        
        self.assertIn('test_metric', self.collector.metrics)
        self.assertEqual(len(self.collector.metrics['test_metric']), 1)
        
        metric = self.collector.metrics['test_metric'][0]
        self.assertEqual(metric.name, 'test_metric')
        self.assertEqual(metric.value, 75.5)
        self.assertEqual(metric.tags['unit'], 'percent')
    
    def test_record_pipeline_metrics(self):
        """ทดสอบการบันทึกเมตริกจาก pipeline"""
        self.collector.record_pipeline_metrics(
            pipeline_name='test_pipeline',
            duration=120.5,
            processed_records=10000,
            quality_score=85.5,
            success=True
        )
        
        # ตรวจสอบว่าเมตริกถูกบันทึก
        self.assertIn('pipeline_duration', self.collector.metrics)
        self.assertIn('pipeline_records_processed', self.collector.metrics)
        self.assertIn('data_quality_score', self.collector.metrics)
        self.assertIn('pipeline_success', self.collector.metrics)
    
    def test_get_metric_summary(self):
        """ทดสอบการดึงสรุปเมตริก"""
        # บันทึกเมตริกหลายตัว
        for i in range(5):
            self.collector.record_metric('cpu_usage', 70 + i, {'unit': 'percent'})
        
        summary = self.collector.get_metric_summary('cpu_usage', 60)
        
        self.assertEqual(summary['metric_name'], 'cpu_usage')
        self.assertEqual(summary['count'], 5)
        self.assertEqual(summary['current'], 74.0)
        self.assertEqual(summary['min'], 70.0)
        self.assertEqual(summary['max'], 74.0)
        self.assertEqual(summary['avg'], 72.0)
    
    def test_get_system_overview(self):
        """ทดสอบการดึงข้อมูลภาพรวม"""
        overview = self.collector.get_system_overview()
        
        self.assertIn('monitoring_status', overview)
        self.assertIn('uptime_minutes', overview)
        self.assertIn('total_metrics_collected', overview)
        self.assertIn('active_alerts', overview)
        self.assertIn('metrics_available', overview)
    
    def test_export_metrics_json(self):
        """ทดสอบการ export เมตริกเป็น JSON"""
        self.collector.record_metric('test_metric', 100.0)
        
        json_export = self.collector.export_metrics('json')
        
        self.assertIsInstance(json_export, str)
        self.assertIn('test_metric', json_export)
        self.assertIn('timestamp', json_export)
    
    def test_export_metrics_prometheus(self):
        """ทดสอบการ export เมตริกเป็น Prometheus format"""
        self.collector.record_metric('test_metric', 100.0, unit='percent')
        
        prometheus_export = self.collector.export_metrics('prometheus')
        
        self.assertIsInstance(prometheus_export, str)
        self.assertIn('test_metric', prometheus_export)
        self.assertIn('# HELP', prometheus_export)
        self.assertIn('# TYPE', prometheus_export)
    
    def test_monitoring_start_stop(self):
        """ทดสอบการเริ่มและหยุดการติดตาม"""
        # เริ่มการติดตาม
        self.collector.start_monitoring()
        self.assertTrue(self.collector.monitoring_thread.is_alive())
        
        # รอสักครู่
        time.sleep(2)
        
        # หยุดการติดตาม
        self.collector.stop_monitoring_service()
        time.sleep(1)
        
        # ตรวจสอบว่าหยุดแล้ว
        self.assertFalse(self.collector.monitoring_thread.is_alive())


class TestConfigManager(unittest.TestCase):
    """ทดสอบ Configuration Manager"""
    
    def setUp(self):
        """ตั้งค่าก่อนแต่ละการทดสอบ"""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, 'test_config.yaml')
        
        # สร้าง config file สำหรับทดสอบ
        test_config = {
            'app': {
                'name': 'Test App',
                'version': '1.0.0',
                'debug': True
            },
            'database': {
                'primary': {
                    'type': 'mssql',
                    'host': 'localhost',
                    'database': 'test_db',
                    'username': 'test_user',
                    'password': 'test_pass'
                }
            },
            'monitoring': {
                'enabled': True,
                'interval': 60
            }
        }
        
        import yaml
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        self.config_manager = ConfigManager(self.config_path)
    
    def tearDown(self):
        """ทำความสะอาดหลังแต่ละการทดสอบ"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_get_config_value(self):
        """ทดสอบการดึงค่า config"""
        app_name = self.config_manager.get('app.name')
        self.assertEqual(app_name, 'Test App')
        
        db_host = self.config_manager.get('database.primary.host')
        self.assertEqual(db_host, 'localhost')
        
        # ทดสอบค่า default
        non_existent = self.config_manager.get('non.existent.key', 'default_value')
        self.assertEqual(non_existent, 'default_value')
    
    def test_set_config_value(self):
        """ทดสอบการตั้งค่า config"""
        self.config_manager.set('app.debug', False)
        self.assertFalse(self.config_manager.get('app.debug'))
        
        self.config_manager.set('new.nested.key', 'new_value')
        self.assertEqual(self.config_manager.get('new.nested.key'), 'new_value')
    
    def test_validate_config(self):
        """ทดสอบการตรวจสอบ config"""
        validation = self.config_manager.validate_config()
        
        self.assertIsInstance(validation, dict)
        self.assertIn('valid', validation)
        self.assertIn('errors', validation)
        self.assertIn('warnings', validation)
        self.assertIsInstance(validation['valid'], bool)
        self.assertIsInstance(validation['errors'], list)
        self.assertIsInstance(validation['warnings'], list)
    
    def test_get_database_url(self):
        """ทดสอบการสร้าง database URL"""
        db_url = self.config_manager.get_database_url('primary')
        
        self.assertIsInstance(db_url, str)
        self.assertIn('mssql+pymssql://', db_url)
        self.assertIn('localhost', db_url)
        self.assertIn('test_db', db_url)
    
    def test_get_config_summary(self):
        """ทดสอบการดึงสรุป config"""
        summary = self.config_manager.get_config_summary()
        
        self.assertIn('config_file', summary)
        self.assertIn('sections', summary)
        self.assertIn('total_keys', summary)
        self.assertIn('validation', summary)
        self.assertIn('app_info', summary)
    
    @patch.dict(os.environ, {'DATAOPS_APP_NAME': 'Test App Override'})
    def test_environment_override(self):
        """ทดสอบการ override ด้วย environment variables"""
        # สร้าง config manager ใหม่เพื่อให้ apply env overrides
        config_manager = ConfigManager(self.config_path)
        
        app_name = config_manager.get('app.name')
        self.assertEqual(app_name, 'Test App Override')


class TestIntegration(unittest.TestCase):
    """ทดสอบการทำงานร่วมกันของระบบ"""
    
    def setUp(self):
        """ตั้งค่าก่อนแต่ละการทดสอบ"""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, 'config.yaml')
        
        # สร้าง config
        test_config = {
            'data_quality': {
                'max_null_percentage': 30.0,
                'acceptable_max_null': 26,
                'quality_thresholds': {
                    'completeness': 0.85,
                    'uniqueness': 0.90,
                    'consistency': 0.90,
                    'validity': 0.85
                }
            },
            'monitoring': {
                'enabled': True,
                'interval': 60
            }
        }
        
        import yaml
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # สร้างข้อมูลตัวอย่าง
        self.sample_data = pd.DataFrame({
            'id': range(1, 51),
            'name': [f'User_{i}' for i in range(1, 51)],
            'age': np.random.randint(18, 65, 50),
            'salary': np.random.uniform(30000, 100000, 50),
            'department': np.random.choice(['IT', 'HR', 'Finance'], 50),
            'hire_date': pd.date_range(start='2020-01-01', periods=50, freq='D')
        })
        
        self.sample_file = os.path.join(self.test_dir, 'test_data.csv')
        self.sample_data.to_csv(self.sample_file, index=False)
    
    def tearDown(self):
        """ทำความสะอาดหลังแต่ละการทดสอบ"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_etl_with_quality_check(self):
        """ทดสอบ ETL Pipeline พร้อม Quality Check"""
        # Load config
        config = ConfigManager(self.config_path)
        
        # ETL Processing
        processor = ETLProcessor(self.config_path)
        result = processor.load_data(self.sample_file)
        
        self.assertTrue(result.success)
        
        # Quality Check
        checker = DataQualityChecker(config.config)
        quality_result = checker.run_checks(processor.raw_df)
        
        self.assertIsInstance(quality_result, QualityResult)
        self.assertGreater(quality_result.overall_score, 0)
    
    def test_etl_with_monitoring(self):
        """ทดสอบ ETL Pipeline พร้อม Monitoring"""
        # Setup monitoring
        collector = MetricsCollector()
        
        # ETL Processing
        processor = ETLProcessor(self.config_path)
        start_time = time.time()
        
        result = processor.load_data(self.sample_file)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Record metrics
        collector.record_pipeline_metrics(
            pipeline_name='test_pipeline',
            duration=duration,
            processed_records=result.processed_records,
            quality_score=85.0,
            success=result.success
        )
        
        # Check metrics
        metrics = collector.get_system_overview()
        self.assertIn('monitoring_status', metrics)
        
        # Cleanup
        collector.stop_monitoring_service()
    
    def test_full_workflow(self):
        """ทดสอบ workflow เต็ม"""
        # 1. Load configuration
        config = ConfigManager(self.config_path)
        validation = config.validate_config()
        self.assertTrue(validation['valid'])
        
        # 2. Setup monitoring
        collector = MetricsCollector(config.config)
        collector.start_monitoring()
        
        # 3. ETL Processing
        processor = ETLProcessor(self.config_path)
        
        with patch('src.data_pipeline.etl_processor.create_engine') as mock_create_engine:
            mock_engine = Mock()
            mock_create_engine.return_value = mock_engine
            
            start_time = time.time()
            result = processor.run_full_pipeline(self.sample_file)
            end_time = time.time()
            
            self.assertTrue(result.success)
        
        # 4. Quality assessment
        checker = DataQualityChecker(config.config)
        quality_result = checker.run_checks(processor.raw_df)
        
        self.assertIsInstance(quality_result, QualityResult)
        
        # 5. Record metrics
        collector.record_pipeline_metrics(
            pipeline_name='full_test_pipeline',
            duration=end_time - start_time,
            processed_records=result.processed_records,
            quality_score=quality_result.overall_score,
            success=result.success
        )
        
        # 6. Generate reports
        quality_report = checker.generate_report(quality_result)
        self.assertIsInstance(quality_report, str)
        
        metrics_export = collector.export_metrics('json')
        self.assertIsInstance(metrics_export, str)
        
        # Cleanup
        collector.stop_monitoring_service()


class TestPerformance(unittest.TestCase):
    """ทดสอบประสิทธิภาพระบบ"""
    
    def setUp(self):
        """ตั้งค่าก่อนแต่ละการทดสอบ"""
        self.test_dir = tempfile.mkdtemp()
        
        # สร้างข้อมูลขนาดใหญ่
        self.large_data = pd.DataFrame({
            'id': range(1, 10001),
            'value': np.random.randn(10000),
            'category': np.random.choice(['A', 'B', 'C'], 10000),
            'timestamp': pd.date_range(start='2023-01-01', periods=10000, freq='H')
        })
        
        self.large_file = os.path.join(self.test_dir, 'large_data.csv')
        self.large_data.to_csv(self.large_file, index=False)
    
    def tearDown(self):
        """ทำความสะอาดหลังแต่ละการทดสอบ"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_etl_performance(self):
        """ทดสอบประสิทธิภาพ ETL"""
        processor = ETLProcessor()
        
        start_time = time.time()
        result = processor.load_data(self.large_file)
        end_time = time.time()
        
        duration = end_time - start_time
        
        self.assertTrue(result.success)
        self.assertLess(duration, 10.0)  # ควรเสร็จภายใน 10 วินาที
        
        # ทดสอบ memory usage
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        self.assertLess(memory_mb, 500)  # ควรใช้ memory น้อยกว่า 500MB
    
    def test_quality_check_performance(self):
        """ทดสอบประสิทธิภาพ Quality Check"""
        checker = DataQualityChecker()
        
        start_time = time.time()
        result = checker.run_checks(self.large_data)
        end_time = time.time()
        
        duration = end_time - start_time
        
        self.assertIsInstance(result, QualityResult)
        self.assertLess(duration, 5.0)  # ควรเสร็จภายใน 5 วินาที
    
    def test_monitoring_overhead(self):
        """ทดสอบ overhead ของการติดตาม"""
        collector = MetricsCollector()
        
        # ทดสอบการบันทึกเมตริกจำนวนมาก
        start_time = time.time()
        
        for i in range(1000):
            collector.record_metric(f'test_metric_{i % 10}', i, {'test': 'value'})
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertLess(duration, 2.0)  # ควรเสร็จภายใน 2 วินาที
        
        # ทดสอบการ export
        start_time = time.time()
        json_export = collector.export_metrics('json')
        end_time = time.time()
        
        export_duration = end_time - start_time
        self.assertLess(export_duration, 1.0)  # ควรเสร็จภายใน 1 วินาที
        
        # Cleanup
        collector.stop_monitoring_service()


class TestCICDIntegration(unittest.TestCase):
    """ทดสอบการทำงานร่วมกับ CI/CD Pipeline (จาก python-jenkins)"""
    
    def setUp(self):
        """ตั้งค่าก่อนแต่ละการทดสอบ"""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, 'config.yaml')
        
        # สร้าง config
        test_config = {
            'app': {
                'name': 'DataOps Foundation',
                'version': '1.0.0',
                'environment': 'test'
            },
            'data_quality': {
                'quality_thresholds': {
                    'completeness': 0.80,
                    'uniqueness': 0.85,
                    'consistency': 0.85,
                    'validity': 0.80
                }
            }
        }
        
        import yaml
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
    
    def tearDown(self):
        """ทำความสะอาดหลังแต่ละการทดสอบ"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_pipeline_health_check(self):
        """ทดสอบการตรวจสอบสุขภาพ pipeline"""
        # สร้างข้อมูลทดสอบ
        test_data = pd.DataFrame({
            'id': range(1, 101),
            'name': [f'Test_{i}' for i in range(1, 101)],
            'value': np.random.randn(100),
            'category': np.random.choice(['A', 'B', 'C'], 100)
        })
        
        test_file = os.path.join(self.test_dir, 'health_check.csv')
        test_data.to_csv(test_file, index=False)
        
        # ทดสอบ ETL pipeline
        processor = ETLProcessor(self.config_path)
        result = processor.load_data(test_file)
        
        self.assertTrue(result.success)
        self.assertGreater(result.processed_records, 0)
        
        # ทดสอบ quality check
        checker = DataQualityChecker()
        quality_result = checker.run_checks(test_data)
        
        self.assertIsInstance(quality_result, QualityResult)
        self.assertGreater(quality_result.overall_score, 0)
    
    def test_automated_testing_workflow(self):
        """ทดสอบ workflow การทดสอบอัตโนมัติ"""
        # 1. Configuration validation
        config = ConfigManager(self.config_path)
        validation = config.validate_config()
        self.assertTrue(validation['valid'])
        
        # 2. System health check
        collector = MetricsCollector()
        overview = collector.get_system_overview()
        self.assertIn('monitoring_status', overview)
        
        # 3. Data quality baseline
        baseline_data = pd.DataFrame({
            'id': range(1, 51),
            'name': [f'Baseline_{i}' for i in range(1, 51)],
            'score': np.random.uniform(0.8, 1.0, 50)
        })
        
        checker = DataQualityChecker()
        baseline_result = checker.run_checks(baseline_data)
        
        # ตรวจสอบว่าผ่านเกณฑ์คุณภาพ
        self.assertGreaterEqual(baseline_result.overall_score, 80.0)
        
        # 4. Performance baseline
        start_time = time.time()
        
        # จำลองการประมวลผล
        for i in range(100):
            collector.record_metric('test_performance', i, {'iteration': str(i)})
        
        end_time = time.time()
        duration = end_time - start_time
        
        # ตรวจสอบประสิทธิภาพ
        self.assertLess(duration, 1.0)
        
        # Cleanup
        collector.stop_monitoring_service()
    
    def test_deployment_readiness(self):
        """ทดสอบความพร้อมสำหรับ deployment"""
        # ตรวจสอบ components หลัก
        components = {
            'config_manager': ConfigManager(self.config_path),
            'etl_processor': ETLProcessor(self.config_path),
            'quality_checker': DataQualityChecker(),
            'metrics_collector': MetricsCollector()
        }
        
        for component_name, component in components.items():
            self.assertIsNotNone(component, f"{component_name} should be initialized")
        
        # ตรวจสอบ configuration
        config = components['config_manager']
        validation = config.validate_config()
        
        # ใน production environment ควรมี error = 0
        if config.get('app.environment') == 'production':
            self.assertEqual(len(validation['errors']), 0)
        
        # ตรวจสอบ dependencies
        required_modules = ['pandas', 'numpy', 'sqlalchemy', 'yaml']
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                self.fail(f"Required module {module} is not available")
        
        # Cleanup
        components['metrics_collector'].stop_monitoring_service()


def run_all_tests():
    """รันการทดสอบทั้งหมด"""
    # สร้าง test suite
    test_suite = unittest.TestSuite()
    
    # เพิ่มทุก test class
    test_classes = [
        TestETLProcessor,
        TestDataQualityChecker,
        TestMetricsCollector,
        TestConfigManager,
        TestIntegration,
        TestPerformance,
        TestCICDIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # รันการทดสอบ
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result


if __name__ == '__main__':
    print("=== DataOps Foundation Enhanced Tests ===")
    print("รวมโค้ดจาก ETL-dev (1).py และ python-jenkins")
    print("=" * 60)
    
    # ตั้งค่า logging สำหรับทดสอบ
    logging.basicConfig(level=logging.WARNING)
    
    # รันการทดสอบทั้งหมด
    result = run_all_tests()
    
    # สรุปผล
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"   - {test}")
    
    if result.errors:
        print(f"\n💥 Errors ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"   - {test}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        exit_code = 0
    else:
        print("\n❌ Some tests failed!")
        exit_code = 1
    
    print("=" * 60)
    exit(exit_code)
