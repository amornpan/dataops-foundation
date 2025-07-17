#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Metrics Collector
ตัวเก็บรวบรวมและติดตามเมตริกต์ระบบ

Features:
- System performance monitoring
- Data pipeline metrics
- Quality metrics tracking
- Alerting capabilities
- Prometheus integration
- Real-time dashboard support
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import psutil
import os
import json
from collections import defaultdict, deque


@dataclass
class Metric:
    """เก็บข้อมูลเมตริกแต่ละตัว"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""


@dataclass
class Alert:
    """เก็บข้อมูลการแจ้งเตือน"""
    metric_name: str
    current_value: float
    threshold_value: float
    threshold_type: str  # 'min', 'max'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    timestamp: datetime
    resolved: bool = False


class MetricsCollector:
    """
    ตัวเก็บรวบรวมและติดตามเมตริกต์ระบบ
    รองรับการติดตามประสิทธิภาพและการแจ้งเตือน
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """เริ่มต้น Metrics Collector"""
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # เก็บข้อมูลเมตริก
        self.metrics = defaultdict(lambda: deque(maxlen=1000))  # เก็บแค่ 1000 ค่าล่าสุด
        self.alerts = deque(maxlen=500)  # เก็บ alert 500 ตัวล่าสุด
        
        # การตั้งค่า threshold
        self.thresholds = {
            'cpu_usage': {'max': 80.0, 'severity': 'medium'},
            'memory_usage': {'max': 85.0, 'severity': 'medium'},
            'disk_usage': {'max': 90.0, 'severity': 'high'},
            'pipeline_duration': {'max': 3600.0, 'severity': 'medium'},  # 1 hour
            'data_quality_score': {'min': 80.0, 'severity': 'high'},
            'error_rate': {'max': 0.05, 'severity': 'high'}  # 5%
        }
        
        # Override thresholds from config
        if 'monitoring' in self.config and 'thresholds' in self.config['monitoring']:
            self.thresholds.update(self.config['monitoring']['thresholds'])
        
        # Monitoring flags
        self.monitoring_enabled = self.config.get('monitoring', {}).get('enabled', True)
        self.collection_interval = self.config.get('monitoring', {}).get('interval', 60)  # seconds
        
        # Threading
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        # Statistics
        self.stats = {
            'total_metrics_collected': 0,
            'alerts_generated': 0,
            'start_time': datetime.now()
        }
        
        self.logger.info("Metrics Collector initialized")
    
    def start_monitoring(self):
        """เริ่มต้นการติดตามระบบ"""
        if not self.monitoring_enabled:
            self.logger.info("Monitoring is disabled")
            return
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.logger.warning("Monitoring already running")
            return
        
        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.logger.info(f"Started monitoring with {self.collection_interval}s interval")
    
    def stop_monitoring_service(self):
        """หยุดการติดตามระบบ"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.stop_monitoring.set()
            self.monitoring_thread.join(timeout=5)
            self.logger.info("Monitoring stopped")
    
    def _monitoring_loop(self):
        """Loop หลักสำหรับเก็บข้อมูลเมตริก"""
        while not self.stop_monitoring.is_set():
            try:
                # เก็บข้อมูลระบบ
                self._collect_system_metrics()
                
                # ตรวจสอบ thresholds
                self._check_thresholds()
                
                # รอตามช่วงเวลาที่กำหนด
                if self.stop_monitoring.wait(self.collection_interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # รอสักครู่ก่อนลองใหม่
    
    def _collect_system_metrics(self):
        """เก็บข้อมูลเมตริกระบบ"""
        try:
            now = datetime.now()
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric('cpu_usage', cpu_percent, {'unit': 'percent'})
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.record_metric('memory_usage', memory.percent, {'unit': 'percent'})
            self.record_metric('memory_available', memory.available / 1024**3, {'unit': 'GB'})
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric('disk_usage', disk_percent, {'unit': 'percent'})
            self.record_metric('disk_available', disk.free / 1024**3, {'unit': 'GB'})
            
            # Process information
            try:
                current_process = psutil.Process()
                self.record_metric('process_memory', current_process.memory_info().rss / 1024**2, {'unit': 'MB'})
                self.record_metric('process_cpu', current_process.cpu_percent(), {'unit': 'percent'})
            except:
                pass
            
            # Network I/O (if available)
            try:
                net_io = psutil.net_io_counters()
                self.record_metric('network_bytes_sent', net_io.bytes_sent / 1024**2, {'unit': 'MB'})
                self.record_metric('network_bytes_recv', net_io.bytes_recv / 1024**2, {'unit': 'MB'})
            except:
                pass
            
            self.stats['total_metrics_collected'] += 1
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None, 
                     unit: str = "", description: str = ""):
        """บันทึกเมตริกใหม่"""
        try:
            metric = Metric(
                name=name,
                value=value,
                timestamp=datetime.now(),
                tags=tags or {},
                unit=unit,
                description=description
            )
            
            self.metrics[name].append(metric)
            
            # Log เมตริกที่สำคัญ
            if name in ['cpu_usage', 'memory_usage', 'disk_usage']:
                self.logger.debug(f"Metric {name}: {value:.2f}{unit}")
            
        except Exception as e:
            self.logger.error(f"Error recording metric {name}: {e}")
    
    def record_pipeline_metrics(self, pipeline_name: str, duration: float, 
                               processed_records: int, quality_score: float, 
                               success: bool, errors: List[str] = None):
        """บันทึกเมตริกจาก ETL pipeline"""
        try:
            tags = {'pipeline': pipeline_name}
            
            # Duration
            self.record_metric('pipeline_duration', duration, tags, 'seconds')
            
            # Processed records
            self.record_metric('pipeline_records_processed', processed_records, tags, 'records')
            
            # Quality score
            self.record_metric('data_quality_score', quality_score, tags, 'percent')
            
            # Success rate
            self.record_metric('pipeline_success', 1.0 if success else 0.0, tags, 'boolean')
            
            # Error rate
            error_rate = len(errors) / max(processed_records, 1) if errors else 0.0
            self.record_metric('error_rate', error_rate, tags, 'rate')
            
            # Throughput (records per second)
            throughput = processed_records / duration if duration > 0 else 0
            self.record_metric('pipeline_throughput', throughput, tags, 'records/sec')
            
            self.logger.info(f"Pipeline metrics recorded: {pipeline_name}")
            
        except Exception as e:
            self.logger.error(f"Error recording pipeline metrics: {e}")
    
    def _check_thresholds(self):
        """ตรวจสอบ threshold และสร้าง alert"""
        try:
            for metric_name, threshold_config in self.thresholds.items():
                if metric_name in self.metrics:
                    # Get latest value
                    latest_metric = self.metrics[metric_name][-1]
                    current_value = latest_metric.value
                    
                    # Check max threshold
                    if 'max' in threshold_config and current_value > threshold_config['max']:
                        self._generate_alert(
                            metric_name, current_value, threshold_config['max'],
                            'max', threshold_config.get('severity', 'medium')
                        )
                    
                    # Check min threshold
                    if 'min' in threshold_config and current_value < threshold_config['min']:
                        self._generate_alert(
                            metric_name, current_value, threshold_config['min'],
                            'min', threshold_config.get('severity', 'medium')
                        )
                        
        except Exception as e:
            self.logger.error(f"Error checking thresholds: {e}")
    
    def _generate_alert(self, metric_name: str, current_value: float, 
                       threshold_value: float, threshold_type: str, severity: str):
        """สร้าง alert"""
        try:
            # ตรวจสอบว่ามี alert ที่ยังไม่ resolve สำหรับ metric นี้หรือไม่
            existing_alert = None
            for alert in reversed(self.alerts):
                if (alert.metric_name == metric_name and 
                    alert.threshold_type == threshold_type and 
                    not alert.resolved):
                    existing_alert = alert
                    break
            
            if existing_alert:
                # Update existing alert
                existing_alert.current_value = current_value
                existing_alert.timestamp = datetime.now()
                return
            
            # สร้าง alert ใหม่
            if threshold_type == 'max':
                message = f"{metric_name} exceeded threshold: {current_value:.2f} > {threshold_value:.2f}"
            else:
                message = f"{metric_name} below threshold: {current_value:.2f} < {threshold_value:.2f}"
            
            alert = Alert(
                metric_name=metric_name,
                current_value=current_value,
                threshold_value=threshold_value,
                threshold_type=threshold_type,
                severity=severity,
                message=message,
                timestamp=datetime.now()
            )
            
            self.alerts.append(alert)
            self.stats['alerts_generated'] += 1
            
            # Log alert
            if severity in ['high', 'critical']:
                self.logger.warning(f"🚨 {severity.upper()} ALERT: {message}")
            else:
                self.logger.info(f"⚠️ {severity.upper()} ALERT: {message}")
                
        except Exception as e:
            self.logger.error(f"Error generating alert: {e}")
    
    def get_metric_summary(self, metric_name: str, duration_minutes: int = 60) -> Dict[str, Any]:
        """ดึงสรุปข้อมูลเมตริก"""
        try:
            if metric_name not in self.metrics:
                return {'error': f'Metric {metric_name} not found'}
            
            # Filter by time
            cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
            recent_metrics = [
                m for m in self.metrics[metric_name] 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {'error': f'No recent data for {metric_name}'}
            
            values = [m.value for m in recent_metrics]
            
            summary = {
                'metric_name': metric_name,
                'duration_minutes': duration_minutes,
                'count': len(values),
                'current': values[-1] if values else 0,
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'latest_timestamp': recent_metrics[-1].timestamp.isoformat()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting metric summary: {e}")
            return {'error': str(e)}
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """ดึงรายการ alert ที่ยังไม่ resolve"""
        try:
            active_alerts = []
            
            for alert in self.alerts:
                if not alert.resolved:
                    active_alerts.append({
                        'metric_name': alert.metric_name,
                        'current_value': alert.current_value,
                        'threshold_value': alert.threshold_value,
                        'threshold_type': alert.threshold_type,
                        'severity': alert.severity,
                        'message': alert.message,
                        'timestamp': alert.timestamp.isoformat(),
                        'duration_minutes': int((datetime.now() - alert.timestamp).total_seconds() / 60)
                    })
            
            return sorted(active_alerts, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []
    
    def resolve_alert(self, metric_name: str, threshold_type: str):
        """Resolve alert"""
        try:
            for alert in reversed(self.alerts):
                if (alert.metric_name == metric_name and 
                    alert.threshold_type == threshold_type and 
                    not alert.resolved):
                    alert.resolved = True
                    self.logger.info(f"Alert resolved: {metric_name} {threshold_type}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error resolving alert: {e}")
            return False
    
    def get_system_overview(self) -> Dict[str, Any]:
        """ดึงข้อมูลภาพรวมระบบ"""
        try:
            overview = {
                'monitoring_status': 'active' if self.monitoring_enabled else 'disabled',
                'uptime_minutes': int((datetime.now() - self.stats['start_time']).total_seconds() / 60),
                'total_metrics_collected': self.stats['total_metrics_collected'],
                'active_alerts': len(self.get_active_alerts()),
                'total_alerts_generated': self.stats['alerts_generated'],
                'metrics_available': list(self.metrics.keys()),
                'collection_interval': self.collection_interval,
                'timestamp': datetime.now().isoformat()
            }
            
            # เพิ่มเมตริกล่าสุด
            latest_metrics = {}
            for metric_name in ['cpu_usage', 'memory_usage', 'disk_usage']:
                if metric_name in self.metrics:
                    latest_metrics[metric_name] = self.metrics[metric_name][-1].value
            
            overview['latest_metrics'] = latest_metrics
            
            return overview
            
        except Exception as e:
            self.logger.error(f"Error getting system overview: {e}")
            return {'error': str(e)}
    
    def export_metrics(self, format_type: str = 'json') -> str:
        """Export เมตริกในรูปแบบต่างๆ"""
        try:
            if format_type == 'json':
                return self._export_json()
            elif format_type == 'prometheus':
                return self._export_prometheus()
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return ""
    
    def _export_json(self) -> str:
        """Export เป็น JSON format"""
        try:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'system_overview': self.get_system_overview(),
                'metrics': {},
                'active_alerts': self.get_active_alerts()
            }
            
            # Export เมตริกล่าสุด
            for metric_name, metric_deque in self.metrics.items():
                if metric_deque:
                    latest_metric = metric_deque[-1]
                    export_data['metrics'][metric_name] = {
                        'value': latest_metric.value,
                        'timestamp': latest_metric.timestamp.isoformat(),
                        'tags': latest_metric.tags,
                        'unit': latest_metric.unit
                    }
            
            return json.dumps(export_data, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error exporting JSON: {e}")
            return "{}"
    
    def _export_prometheus(self) -> str:
        """Export เป็น Prometheus format"""
        try:
            lines = []
            
            for metric_name, metric_deque in self.metrics.items():
                if metric_deque:
                    latest_metric = metric_deque[-1]
                    
                    # HELP line
                    lines.append(f"# HELP {metric_name} {latest_metric.description or metric_name}")
                    
                    # TYPE line
                    lines.append(f"# TYPE {metric_name} gauge")
                    
                    # Metric line
                    tags_str = ""
                    if latest_metric.tags:
                        tag_pairs = [f'{k}="{v}"' for k, v in latest_metric.tags.items()]
                        tags_str = "{" + ",".join(tag_pairs) + "}"
                    
                    lines.append(f"{metric_name}{tags_str} {latest_metric.value}")
            
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"Error exporting Prometheus: {e}")
            return ""
    
    def cleanup_old_metrics(self, days_to_keep: int = 7):
        """ทำความสะอาดเมตริกเก่า"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            cleaned_count = 0
            
            for metric_name, metric_deque in self.metrics.items():
                original_size = len(metric_deque)
                
                # กรองเฉพาะข้อมูลใหม่
                new_deque = deque([
                    m for m in metric_deque 
                    if m.timestamp >= cutoff_time
                ], maxlen=1000)
                
                self.metrics[metric_name] = new_deque
                cleaned_count += original_size - len(new_deque)
            
            self.logger.info(f"Cleaned {cleaned_count} old metrics (older than {days_to_keep} days)")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up metrics: {e}")


def main():
    """ตัวอย่างการใช้งาน Metrics Collector"""
    print("=== DataOps Foundation Metrics Collector ===")
    
    # สร้าง collector
    collector = MetricsCollector()
    
    # เริ่มต้นการติดตาม
    collector.start_monitoring()
    
    try:
        # รอสักครู่เพื่อเก็บข้อมูล
        time.sleep(10)
        
        # ดูข้อมูลภาพรวม
        overview = collector.get_system_overview()
        print("\n📊 System Overview:")
        for key, value in overview.items():
            print(f"   {key}: {value}")
        
        # ดูเมตริกล่าสุด
        print("\n📈 Recent Metrics:")
        for metric_name in ['cpu_usage', 'memory_usage', 'disk_usage']:
            summary = collector.get_metric_summary(metric_name, 5)
            if 'error' not in summary:
                print(f"   {metric_name}: {summary['current']:.2f}% (avg: {summary['avg']:.2f}%)")
        
        # ทดสอบ pipeline metrics
        print("\n🔄 Recording pipeline metrics...")
        collector.record_pipeline_metrics(
            pipeline_name='test_pipeline',
            duration=120.5,
            processed_records=10000,
            quality_score=85.5,
            success=True
        )
        
        # ดู alerts
        alerts = collector.get_active_alerts()
        print(f"\n🚨 Active Alerts: {len(alerts)}")
        for alert in alerts[:3]:  # แสดงแค่ 3 alert แรก
            print(f"   {alert['severity'].upper()}: {alert['message']}")
        
        # Export metrics
        print("\n📤 Exporting metrics...")
        json_export = collector.export_metrics('json')
        print(f"JSON export size: {len(json_export)} characters")
        
    finally:
        # หยุดการติดตาม
        collector.stop_monitoring_service()
        print("\n✅ Monitoring stopped")


if __name__ == "__main__":
    main()
