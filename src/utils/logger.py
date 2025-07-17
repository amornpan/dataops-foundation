#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Advanced Logger
ระบบ logging ขั้นสูงสำหรับ DataOps Foundation

Features:
- Multiple log levels and handlers
- Structured logging with JSON format
- Log rotation and archiving
- Performance monitoring
- Error tracking and alerting
- Integration with external systems
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import traceback


class JSONFormatter(logging.Formatter):
    """JSON Formatter สำหรับ structured logging"""
    
    def format(self, record):
        """จัดรูปแบบ log record เป็น JSON"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'thread_name': record.threadName,
        }
        
        # เพิ่มข้อมูล exception หากมี
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # เพิ่ม extra fields หากมี
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)


class DataOpsLogger:
    """
    Advanced Logger สำหรับ DataOps Foundation
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """เริ่มต้น DataOps Logger"""
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(name)
        
        # ป้องกันการตั้งค่าซ้ำ
        if not self.logger.handlers:
            self._setup_logger()
    
    def _setup_logger(self):
        """ตั้งค่า logger"""
        # ตั้งค่า log level
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # ตั้งค่า console handler
        self._setup_console_handler()
        
        # ตั้งค่า file handler หากเปิดใช้งาน
        if self.config.get('logging', {}).get('file', {}).get('enabled', True):
            self._setup_file_handler()
        
        # ตั้งค่า external handlers หากเปิดใช้งาน
        self._setup_external_handlers()
    
    def _setup_console_handler(self):
        """ตั้งค่า console handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        
        # กำหนด format สำหรับ console
        console_format = self.config.get('logging', {}).get('format', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        formatter = logging.Formatter(console_format)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """ตั้งค่า file handler พร้อม rotation"""
        file_config = self.config.get('logging', {}).get('file', {})
        
        # สร้างไดเรกทอรี logs หากไม่มี
        log_path = file_config.get('path', 'logs/dataops.log')
        log_dir = os.path.dirname(log_path)
        os.makedirs(log_dir, exist_ok=True)
        
        # ตั้งค่า rotating file handler
        max_bytes = self._parse_size(file_config.get('max_size', '10MB'))
        backup_count = file_config.get('backup_count', 5)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # ใช้ JSON formatter สำหรับไฟล์
        json_formatter = JSONFormatter()
        file_handler.setFormatter(json_formatter)
        
        self.logger.addHandler(file_handler)
    
    def _setup_external_handlers(self):
        """ตั้งค่า external handlers (Elasticsearch, etc.)"""
        # Elasticsearch handler
        es_config = self.config.get('logging', {}).get('external', {}).get('elasticsearch', {})
        if es_config.get('enabled', False):
            try:
                from elasticsearch import Elasticsearch
                from cmreslogging.handlers import CMRESHandler
                
                es_client = Elasticsearch([{
                    'host': es_config.get('host', 'localhost'),
                    'port': es_config.get('port', 9200)
                }])
                
                es_handler = CMRESHandler(
                    hosts=[{'host': es_config.get('host', 'localhost'), 
                           'port': es_config.get('port', 9200)}],
                    auth_type=CMRESHandler.AuthType.NO_AUTH,
                    es_index_name=es_config.get('index', 'dataops-logs'),
                    es_doc_type='log'
                )
                
                self.logger.addHandler(es_handler)
                
            except ImportError:
                self.logger.warning("Elasticsearch logging requires cmreslogging package")
            except Exception as e:
                self.logger.error(f"Failed to setup Elasticsearch handler: {e}")
    
    def _parse_size(self, size_str: str) -> int:
        """แปลงขนาดไฟล์จาก string เป็น bytes"""
        size_str = size_str.upper()
        
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def log_with_context(self, level: str, message: str, **kwargs):
        """Log พร้อม context ข้อมูลเพิ่มเติม"""
        # สร้าง LogRecord ใหม่
        record = self.logger.makeRecord(
            self.logger.name,
            getattr(logging, level.upper()),
            __file__,
            0,
            message,
            (),
            None
        )
        
        # เพิ่ม extra fields
        record.extra_fields = kwargs
        
        # Handle the record
        self.logger.handle(record)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        self.log_with_context(
            'INFO',
            f"Performance: {operation} completed in {duration:.2f}s",
            operation=operation,
            duration=duration,
            metric_type='performance',
            **kwargs
        )
    
    def log_data_quality(self, check_name: str, score: float, passed: bool, **kwargs):
        """Log data quality results"""
        self.log_with_context(
            'INFO' if passed else 'WARNING',
            f"Data Quality: {check_name} - Score: {score:.2f}% - {'PASS' if passed else 'FAIL'}",
            check_name=check_name,
            score=score,
            passed=passed,
            metric_type='data_quality',
            **kwargs
        )
    
    def log_etl_stage(self, stage: str, status: str, records: int = 0, **kwargs):
        """Log ETL pipeline stages"""
        self.log_with_context(
            'INFO',
            f"ETL Stage: {stage} - Status: {status} - Records: {records}",
            stage=stage,
            status=status,
            records=records,
            metric_type='etl_pipeline',
            **kwargs
        )
    
    def log_error_with_context(self, error: Exception, operation: str, **kwargs):
        """Log error พร้อม context และ traceback"""
        self.logger.error(
            f"Error in {operation}: {str(error)}",
            exc_info=True,
            extra={
                'operation': operation,
                'error_type': type(error).__name__,
                'metric_type': 'error',
                **kwargs
            }
        )
    
    def debug(self, message: str, **kwargs):
        """Debug level logging"""
        if kwargs:
            self.log_with_context('DEBUG', message, **kwargs)
        else:
            self.logger.debug(message)
    
    def info(self, message: str, **kwargs):
        """Info level logging"""
        if kwargs:
            self.log_with_context('INFO', message, **kwargs)
        else:
            self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Warning level logging"""
        if kwargs:
            self.log_with_context('WARNING', message, **kwargs)
        else:
            self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """Error level logging"""
        if kwargs:
            self.log_with_context('ERROR', message, **kwargs)
        else:
            self.logger.error(message)
    
    def critical(self, message: str, **kwargs):
        """Critical level logging"""
        if kwargs:
            self.log_with_context('CRITICAL', message, **kwargs)
        else:
            self.logger.critical(message)


def setup_logger(name: str, config: Optional[Dict] = None) -> DataOpsLogger:
    """สร้าง DataOps Logger instance"""
    return DataOpsLogger(name, config)


class LoggingContext:
    """Context manager สำหรับ logging พร้อม automatic performance tracking"""
    
    def __init__(self, logger: DataOpsLogger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting operation: {self.operation}", **self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            # Success
            self.logger.log_performance(self.operation, duration, **self.context)
            self.logger.info(f"Completed operation: {self.operation}", **self.context)
        else:
            # Error
            self.logger.log_error_with_context(exc_val, self.operation, 
                                             duration=duration, **self.context)
        
        return False  # Don't suppress exceptions


def main():
    """ตัวอย่างการใช้งาน DataOps Logger"""
    print("=== DataOps Foundation Advanced Logger ===")
    
    # ตั้งค่า logger
    config = {
        'logging': {
            'level': 'INFO',
            'file': {
                'enabled': True,
                'path': 'logs/example.log',
                'max_size': '5MB',
                'backup_count': 3
            }
        }
    }
    
    logger = setup_logger('dataops.example', config)
    
    # ตัวอย่างการ log แบบต่างๆ
    logger.info("DataOps Foundation logger initialized")
    
    # Log พร้อม context
    logger.log_with_context('INFO', 'Processing data batch', 
                           batch_id=12345, records=1000, source='csv')
    
    # Log performance
    logger.log_performance('data_loading', 2.5, records=1000, source='database')
    
    # Log data quality
    logger.log_data_quality('completeness_check', 95.5, True, 
                           dataset='loans', columns=15)
    
    # Log ETL stage
    logger.log_etl_stage('transformation', 'completed', records=950,
                        stage_duration=1.2)
    
    # ตัวอย่างการใช้ LoggingContext
    try:
        with LoggingContext(logger, 'complex_operation', task_id='task_001'):
            # Simulate some work
            import time
            time.sleep(1)
            # Simulate an operation that might fail
            if False:  # Change to True to test error logging
                raise ValueError("Simulated error")
    except Exception as e:
        pass
    
    print("✅ Logging examples completed. Check logs/example.log for output.")


if __name__ == "__main__":
    main()
