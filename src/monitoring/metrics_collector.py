#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Metrics Collector
ระบบเก็บและติดตาม metrics สำหรับ DataOps Pipeline

Features:
- Prometheus metrics integration
- ETL pipeline metrics
- Data quality metrics
- Performance monitoring
- Custom business metrics
- Real-time dashboards
"""

import time
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server, REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


@dataclass
class MetricData:
    """ข้อมูล metric"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    metric_type: str


class MetricsCollector:
    """
    Metrics Collector สำหรับ DataOps Foundation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """เริ่มต้น Metrics Collector"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.metrics_storage = []
        self._lock = threading.Lock()
        
        # Initialize Prometheus metrics if available
        if PROMETHEUS_AVAILABLE and self.config.get('monitoring', {}).get('prometheus', {}).get('enabled', True):
            self._init_prometheus_metrics()
            self._start_prometheus_server()
        else:
            self.logger.warning("Prometheus client not available or disabled")
            self.prometheus_metrics = None
    
    def _init_prometheus_metrics(self):
        """เริ่มต้น Prometheus metrics"""
        try:
            # ETL Pipeline Metrics
            self.etl_records_processed = Counter(
                'dataops_etl_records_processed_total',
                'Total number of records processed by ETL pipeline',
                ['pipeline', 'stage', 'source']
            )
            
            self.etl_processing_duration = Histogram(
                'dataops_etl_processing_duration_seconds',
                'Time spent processing ETL stages',
                ['pipeline', 'stage'],
                buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
            )
            
            self.etl_errors = Counter(
                'dataops_etl_errors_total',
                'Total number of ETL errors',
                ['pipeline', 'stage', 'error_type']
            )
            
            # Data Quality Metrics
            self.data_quality_score = Gauge(
                'dataops_data_quality_score',
                'Current data quality score (0-100)',
                ['dataset', 'check_type']
            )
            
            self.data_quality_checks = Counter(
                'dataops_data_quality_checks_total',
                'Total number of data quality checks performed',
                ['dataset', 'check_type', 'result']
            )
            
            # Database Metrics
            self.database_connections = Gauge(
                'dataops_database_connections_active',
                'Number of active database connections',
                ['database', 'type']
            )
            
            self.database_query_duration = Histogram(
                'dataops_database_query_duration_seconds',
                'Time spent on database queries',
                ['database', 'operation'],
                buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0]
            )
            
            # System Metrics
            self.system_memory_usage = Gauge(
                'dataops_system_memory_usage_bytes',
                'Memory usage in bytes',
                ['component']
            )
            
            self.system_cpu_usage = Gauge(
                'dataops_system_cpu_usage_percent',
                'CPU usage percentage',
                ['component']
            )
            
            # Business Metrics
            self.business_metric = Gauge(
                'dataops_business_metric',
                'Custom business metrics',
                ['metric_name', 'category']
            )
            
            self.prometheus_metrics = {
                'etl_records_processed': self.etl_records_processed,
                'etl_processing_duration': self.etl_processing_duration,
                'etl_errors': self.etl_errors,
                'data_quality_score': self.data_quality_score,
                'data_quality_checks': self.data_quality_checks,
                'database_connections': self.database_connections,
                'database_query_duration': self.database_query_duration,
                'system_memory_usage': self.system_memory_usage,
                'system_cpu_usage': self.system_cpu_usage,
                'business_metric': self.business_metric
            }
            
            self.logger.info("Prometheus metrics initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing Prometheus metrics: {e}")
            self.prometheus_metrics = None
    
    def _start_prometheus_server(self):
        """เริ่มต้น Prometheus HTTP server"""
        try:
            prometheus_config = self.config.get('monitoring', {}).get('prometheus', {})
            port = prometheus_config.get('port', 8000)
            
            start_http_server(port)
            self.logger.info(f"Prometheus metrics server started on port {port}")
            
        except Exception as e:
            self.logger.error(f"Error starting Prometheus server: {e}")
    
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None,
                     metric_type: str = 'gauge'):
        """บันทึก metric"""
        labels = labels or {}
        
        # Store in internal storage
        with self._lock:
            metric_data = MetricData(
                name=name,
                value=value,
                timestamp=datetime.now(),
                labels=labels,
                metric_type=metric_type
            )
            self.metrics_storage.append(metric_data)
            
            # Keep only last 1000 metrics to prevent memory issues
            if len(self.metrics_storage) > 1000:
                self.metrics_storage = self.metrics_storage[-1000:]
        
        # Update Prometheus metrics if available
        if self.prometheus_metrics:
            self._update_prometheus_metric(name, value, labels, metric_type)
    
    def _update_prometheus_metric(self, name: str, value: float, labels: Dict[str, str],
                                 metric_type: str):
        """อัปเดต Prometheus metric"""
        try:
            if name in self.prometheus_metrics:
                metric = self.prometheus_metrics[name]
                
                if metric_type == 'counter':
                    metric.labels(**labels).inc(value)
                elif metric_type == 'gauge':
                    metric.labels(**labels).set(value)
                elif metric_type == 'histogram':
                    metric.labels(**labels).observe(value)
                    
        except Exception as e:
            self.logger.error(f"Error updating Prometheus metric {name}: {e}")
    
    def record_etl_records(self, records: int, pipeline: str = 'default', 
                          stage: str = 'processing', source: str = 'unknown'):
        """บันทึกจำนวน records ที่ประมวลผลใน ETL"""
        self.record_metric(
            'etl_records_processed',
            records,
            {'pipeline': pipeline, 'stage': stage, 'source': source},
            'counter'
        )
    
    def record_etl_duration(self, duration: float, pipeline: str = 'default',
                           stage: str = 'processing'):
        """บันทึกเวลาการประมวลผล ETL"""
        self.record_metric(
            'etl_processing_duration',
            duration,
            {'pipeline': pipeline, 'stage': stage},
            'histogram'
        )
    
    def record_etl_error(self, error_type: str, pipeline: str = 'default',
                        stage: str = 'processing'):
        """บันทึกข้อผิดพลาดใน ETL"""
        self.record_metric(
            'etl_errors',
            1,
            {'pipeline': pipeline, 'stage': stage, 'error_type': error_type},
            'counter'
        )
    
    def record_data_quality_score(self, score: float, dataset: str, check_type: str):
        """บันทึกคะแนนคุณภาพข้อมูล"""
        self.record_metric(
            'data_quality_score',
            score,
            {'dataset': dataset, 'check_type': check_type},
            'gauge'
        )
    
    def record_data_quality_check(self, dataset: str, check_type: str, passed: bool):
        """บันทึกผลการตรวจสอบคุณภาพข้อมูล"""
        result = 'pass' if passed else 'fail'
        self.record_metric(
            'data_quality_checks',
            1,
            {'dataset': dataset, 'check_type': check_type, 'result': result},
            'counter'
        )
    
    def get_metrics_summary(self, last_minutes: int = 60) -> Dict[str, Any]:
        """ดึงสรุป metrics ในช่วงเวลาที่กำหนด"""
        cutoff_time = datetime.now() - timedelta(minutes=last_minutes)
        
        with self._lock:
            recent_metrics = [
                m for m in self.metrics_storage 
                if m.timestamp >= cutoff_time
            ]
        
        summary = {
            'total_metrics': len(recent_metrics),
            'time_range': f"Last {last_minutes} minutes",
            'metrics_by_type': {},
            'latest_values': {}
        }
        
        # Group by metric type
        for metric in recent_metrics:
            metric_type = metric.metric_type
            if metric_type not in summary['metrics_by_type']:
                summary['metrics_by_type'][metric_type] = 0
            summary['metrics_by_type'][metric_type] += 1
            
            # Keep latest value for each metric name
            summary['latest_values'][metric.name] = {
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat(),
                'labels': metric.labels
            }
        
        return summary


class MetricsContext:
    """Context manager สำหรับ automatic metrics recording"""
    
    def __init__(self, collector: MetricsCollector, operation: str, **labels):
        self.collector = collector
        self.operation = operation
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.collector.record_metric(
            f'{self.operation}_started',
            1,
            self.labels,
            'counter'
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        # Record duration
        self.collector.record_metric(
            f'{self.operation}_duration',
            duration,
            self.labels,
            'histogram'
        )
        
        # Record completion or error
        if exc_type is None:
            self.collector.record_metric(
                f'{self.operation}_completed',
                1,
                self.labels,
                'counter'
            )
        else:
            error_labels = self.labels.copy()
            error_labels['error_type'] = exc_type.__name__
            self.collector.record_metric(
                f'{self.operation}_errors',
                1,
                error_labels,
                'counter'
            )
        
        return False


def main():
    """ตัวอย่างการใช้งาน Metrics Collector"""
    print("=== DataOps Foundation Metrics Collector ===")
    
    # เริ่มต้น metrics collector
    config = {
        'monitoring': {
            'prometheus': {
                'enabled': True,
                'port': 8000
            }
        }
    }
    
    collector = MetricsCollector(config)
    
    # ตัวอย่างการบันทึก metrics
    print("Recording sample metrics...")
    
    # ETL metrics
    collector.record_etl_records(1000, 'loan_pipeline', 'extraction', 'csv')
    collector.record_etl_duration(2.5, 'loan_pipeline', 'transformation')
    
    # Data quality metrics
    collector.record_data_quality_score(95.5, 'loans', 'completeness')
    collector.record_data_quality_check('loans', 'uniqueness', True)
    
    # ตัวอย่างการใช้ MetricsContext
    with MetricsContext(collector, 'data_processing', pipeline='example'):
        time.sleep(1)  # Simulate work
    
    # แสดงสรุป metrics
    summary = collector.get_metrics_summary()
    print(f"✅ Metrics recorded: {summary['total_metrics']} metrics in {summary['time_range']}")
    
    if PROMETHEUS_AVAILABLE:
        print("📊 Prometheus metrics server running on http://localhost:8000/metrics")
    else:
        print("⚠️ Prometheus client not available - install with: pip install prometheus-client")


if __name__ == "__main__":
    main()
