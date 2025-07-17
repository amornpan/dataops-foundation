#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Logger
ตัวจัดการการ logging ขั้นสูง

Features:
- Structured logging with JSON format
- Log rotation and compression
- Multiple log levels and handlers
- Context-aware logging
- Performance logging
- Error tracking
"""

import logging
import logging.handlers
import json
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import threading
import time


class DataOpsLogger:
    """
    Logger ขั้นสูงสำหรับ DataOps Foundation
    รองรับหลายรูปแบบการ logging และการจัดการไฟล์
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """เริ่มต้น DataOps Logger"""
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(name)
        self.context = {}
        self.performance_data = {}
        
        # ตั้งค่า logger
        self._setup_logger()
        
    def _setup_logger(self):
        """ตั้งค่า logger ตามการตั้งค่า"""
        # ป้องกันการตั้งค่าซ้ำ
        if self.logger.handlers:
            return
        
        # ตั้งค่า level
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # สร้าง formatter
        formatter = self._create_formatter()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (ถ้ามี)
        log_file = self.config.get('logging', {}).get('file')
        if log_file:
            file_handler = self._create_file_handler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Error file handler
        error_file = self.config.get('logging', {}).get('error_file', 'error.log')
        error_handler = self._create_file_handler(error_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # ป้องกัน propagation
        self.logger.propagate = False
    
    def _create_formatter(self) -> logging.Formatter:
        """สร้าง formatter สำหรับ log messages"""
        log_format = self.config.get('logging', {}).get('format', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # ตรวจสอบว่าต้องการ JSON format หรือไม่
        use_json = self.config.get('logging', {}).get('json_format', False)
        
        if use_json:
            return JsonFormatter()
        else:
            return ColoredFormatter(log_format)
    
    def _create_file_handler(self, log_file: str) -> logging.Handler:
        """สร้าง file handler พร้อม rotation"""
        # สร้างโฟลเดอร์ถ้าไม่มี
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # ตั้งค่า rotation
        max_size = self._parse_size(self.config.get('logging', {}).get('max_size', '10MB'))
        backup_count = self.config.get('logging', {}).get('backup_count', 5)
        
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_size, backupCount=backup_count
        )
        
        return handler
    
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
    
    def set_context(self, **kwargs):
        """ตั้งค่า context สำหรับ logging"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """ล้าง context"""
        self.context.clear()
    
    def debug(self, message: str, extra: Dict[str, Any] = None):
        """Log debug message"""
        self._log(logging.DEBUG, message, extra)
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        """Log info message"""
        self._log(logging.INFO, message, extra)
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Log warning message"""
        self._log(logging.WARNING, message, extra)
    
    def error(self, message: str, extra: Dict[str, Any] = None, exc_info: bool = False):
        """Log error message"""
        self._log(logging.ERROR, message, extra, exc_info)
    
    def critical(self, message: str, extra: Dict[str, Any] = None, exc_info: bool = False):
        """Log critical message"""
        self._log(logging.CRITICAL, message, extra, exc_info)
    
    def _log(self, level: int, message: str, extra: Dict[str, Any] = None, exc_info: bool = False):
        """Internal log method"""
        # รวม context และ extra
        log_extra = self.context.copy()
        if extra:
            log_extra.update(extra)
        
        # เพิ่มข้อมูลเกี่ยวกับ thread
        log_extra['thread_id'] = threading.current_thread().ident
        log_extra['thread_name'] = threading.current_thread().name
        
        # Log message
        self.logger.log(level, message, extra=log_extra, exc_info=exc_info)
    
    def log_exception(self, message: str = "Exception occurred", extra: Dict[str, Any] = None):
        """Log exception พร้อม stack trace"""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        if exc_type is not None:
            exception_info = {
                'exception_type': exc_type.__name__,
                'exception_message': str(exc_value),
                'stack_trace': traceback.format_tb(exc_traceback)
            }
            
            log_extra = extra.copy() if extra else {}
            log_extra.update(exception_info)
            
            self.error(message, log_extra, exc_info=True)
    
    def start_performance_timer(self, operation_name: str):
        """เริ่มต้นการวัดประสิทธิภาพ"""
        self.performance_data[operation_name] = {
            'start_time': time.time(),
            'thread_id': threading.current_thread().ident
        }
        
        self.debug(f"Started performance timer: {operation_name}")
    
    def end_performance_timer(self, operation_name: str, extra: Dict[str, Any] = None):
        """สิ้นสุดการวัดประสิทธิภาพ"""
        if operation_name not in self.performance_data:
            self.warning(f"Performance timer not found: {operation_name}")
            return
        
        start_data = self.performance_data[operation_name]
        end_time = time.time()
        duration = end_time - start_data['start_time']
        
        log_extra = extra.copy() if extra else {}
        log_extra.update({
            'operation_name': operation_name,
            'duration_seconds': duration,
            'start_time': start_data['start_time'],
            'end_time': end_time
        })
        
        self.info(f"Performance: {operation_name} completed in {duration:.3f}s", log_extra)
        
        # ลบข้อมูลการวัด
        del self.performance_data[operation_name]
    
    def log_data_quality(self, dataset_name: str, quality_score: float, 
                        details: Dict[str, Any] = None):
        """Log ข้อมูลคุณภาพข้อมูล"""
        log_extra = {
            'dataset_name': dataset_name,
            'quality_score': quality_score,
            'category': 'data_quality'
        }
        
        if details:
            log_extra.update(details)
        
        level = logging.INFO if quality_score >= 80 else logging.WARNING
        message = f"Data quality: {dataset_name} scored {quality_score:.1f}%"
        
        self._log(level, message, log_extra)
    
    def log_pipeline_event(self, pipeline_name: str, event_type: str, 
                          status: str, details: Dict[str, Any] = None):
        """Log pipeline events"""
        log_extra = {
            'pipeline_name': pipeline_name,
            'event_type': event_type,
            'status': status,
            'category': 'pipeline'
        }
        
        if details:
            log_extra.update(details)
        
        level = logging.INFO if status == 'success' else logging.ERROR
        message = f"Pipeline {pipeline_name}: {event_type} - {status}"
        
        self._log(level, message, log_extra)
    
    def log_system_metric(self, metric_name: str, value: float, 
                         unit: str = "", tags: Dict[str, str] = None):
        """Log system metrics"""
        log_extra = {
            'metric_name': metric_name,
            'metric_value': value,
            'metric_unit': unit,
            'category': 'system_metric'
        }
        
        if tags:
            log_extra.update(tags)
        
        self.debug(f"Metric: {metric_name} = {value}{unit}", log_extra)


class JsonFormatter(logging.Formatter):
    """JSON formatter สำหรับ structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record เป็น JSON"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # เพิ่มข้อมูลเพิ่มเติม
        if hasattr(record, 'thread_id'):
            log_entry['thread_id'] = record.thread_id
        
        if hasattr(record, 'thread_name'):
            log_entry['thread_name'] = record.thread_name
        
        # เพิ่ม extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'message']:
                log_entry[key] = value
        
        # เพิ่ม exception info
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class ColoredFormatter(logging.Formatter):
    """Colored formatter สำหรับ console output"""
    
    # สีสำหรับแต่ละ level
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m'    # Magenta
    }
    
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record พร้อมสี"""
        # เพิ่มสี
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        
        # Format message
        formatted = super().format(record)
        
        return formatted


def setup_logger(name: str, config: Dict[str, Any] = None) -> DataOpsLogger:
    """สร้าง logger ใหม่"""
    return DataOpsLogger(name, config)


def get_logger(name: str) -> DataOpsLogger:
    """ดึง logger ที่มีอยู่แล้ว"""
    return DataOpsLogger(name)


class LoggerContext:
    """Context manager สำหรับ logging"""
    
    def __init__(self, logger: DataOpsLogger, **context):
        self.logger = logger
        self.context = context
        self.original_context = None
    
    def __enter__(self):
        self.original_context = self.logger.context.copy()
        self.logger.set_context(**self.context)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.context = self.original_context
        
        # Log exception ถ้ามี
        if exc_type is not None:
            self.logger.log_exception(f"Exception in context: {exc_type.__name__}")


class PerformanceTimer:
    """Context manager สำหรับการวัดประสิทธิภาพ"""
    
    def __init__(self, logger: DataOpsLogger, operation_name: str, **extra):
        self.logger = logger
        self.operation_name = operation_name
        self.extra = extra
    
    def __enter__(self):
        self.logger.start_performance_timer(self.operation_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.end_performance_timer(self.operation_name, self.extra)


def main():
    """ตัวอย่างการใช้งาน Logger"""
    print("=== DataOps Foundation Logger ===")
    
    # ตั้งค่า config
    config = {
        'logging': {
            'level': 'DEBUG',
            'file': 'logs/dataops.log',
            'error_file': 'logs/error.log',
            'json_format': False,
            'max_size': '5MB',
            'backup_count': 3
        }
    }
    
    # สร้าง logger
    logger = setup_logger('test_logger', config)
    
    # ตั้งค่า context
    logger.set_context(user_id='admin', session_id='abc123')
    
    # ทดสอบ log levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    # ทดสอบ performance timer
    with PerformanceTimer(logger, 'test_operation'):
        time.sleep(0.1)  # จำลองการทำงาน
        logger.info("Operation in progress")
    
    # ทดสอบ exception logging
    try:
        raise ValueError("Test exception")
    except Exception:
        logger.log_exception("Test exception occurred")
    
    # ทดสอบ data quality logging
    logger.log_data_quality('test_dataset', 85.5, {
        'completeness': 0.90,
        'uniqueness': 0.95,
        'records': 10000
    })
    
    # ทดสอบ pipeline logging
    logger.log_pipeline_event('test_pipeline', 'start', 'success')
    logger.log_pipeline_event('test_pipeline', 'end', 'success', {
        'duration': 120.5,
        'processed_records': 10000
    })
    
    # ทดสอบ system metric logging
    logger.log_system_metric('cpu_usage', 75.2, '%', {'host': 'server1'})
    
    # ทดสอบ context manager
    with LoggerContext(logger, pipeline_name='test_pipeline', step='validation'):
        logger.info("Processing data validation")
        logger.warning("Found 5 invalid records")
    
    print("\n✅ Logger test completed. Check logs/ directory for output files.")


if __name__ == "__main__":
    main()
