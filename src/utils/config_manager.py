#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Configuration Manager
ตัวจัดการการตั้งค่าระบบ

Features:
- YAML configuration file support
- Environment variable overrides
- Configuration validation
- Dynamic configuration reloading
- Secure credential management
"""

import yaml
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import re
from datetime import datetime


class ConfigManager:
    """
    ตัวจัดการการตั้งค่าระบบที่ครอบคลุม
    รองรับการโหลดจากไฟล์ YAML และ environment variables
    """
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """เริ่มต้น Configuration Manager"""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.config = {}
        self.last_modified = None
        
        # โหลดการตั้งค่า
        self._load_config()
        
        # Override ด้วย environment variables
        self._apply_env_overrides()
        
        self.logger.info(f"Configuration loaded from: {config_path}")
    
    def _load_config(self):
        """โหลดการตั้งค่าจากไฟล์ YAML"""
        try:
            if os.path.exists(self.config_path):
                # ตรวจสอบการเปลี่ยนแปลงไฟล์
                current_modified = os.path.getmtime(self.config_path)
                
                if self.last_modified is None or current_modified > self.last_modified:
                    with open(self.config_path, 'r', encoding='utf-8') as file:
                        self.config = yaml.safe_load(file) or {}
                    self.last_modified = current_modified
                    self.logger.info(f"Configuration reloaded from {self.config_path}")
                
            else:
                # สร้างการตั้งค่าเริ่มต้น
                self.config = self._get_default_config()
                self._save_default_config()
                self.logger.warning(f"Config file not found. Created default config: {self.config_path}")
                
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """ได้การตั้งค่าเริ่มต้น"""
        return {
            'app': {
                'name': 'DataOps Foundation',
                'version': '1.0.0',
                'environment': 'development',
                'debug': False
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'dataops.log',
                'max_size': '10MB',
                'backup_count': 5
            },
            'database': {
                'primary': {
                    'type': 'mssql',
                    'host': 'localhost',
                    'port': 1433,
                    'database': 'dataops',
                    'username': 'sa',
                    'password': 'changeme',
                    'connection_timeout': 30,
                    'command_timeout': 300
                },
                'secondary': {
                    'type': 'postgresql',
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'dataops_staging',
                    'username': 'postgres',
                    'password': 'changeme'
                }
            },
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
                'interval': 60,
                'thresholds': {
                    'cpu_usage': {'max': 80.0, 'severity': 'medium'},
                    'memory_usage': {'max': 85.0, 'severity': 'medium'},
                    'disk_usage': {'max': 90.0, 'severity': 'high'},
                    'pipeline_duration': {'max': 3600.0, 'severity': 'medium'},
                    'data_quality_score': {'min': 80.0, 'severity': 'high'},
                    'error_rate': {'max': 0.05, 'severity': 'high'}
                },
                'alerts': {
                    'enabled': True,
                    'channels': ['log', 'email'],
                    'email': {
                        'smtp_server': 'smtp.gmail.com',
                        'smtp_port': 587,
                        'username': 'alerts@company.com',
                        'password': 'changeme',
                        'to_addresses': ['admin@company.com']
                    }
                }
            },
            'etl': {
                'batch_size': 10000,
                'max_workers': 4,
                'timeout': 3600,
                'retry_attempts': 3,
                'retry_delay': 60
            },
            'security': {
                'encryption_key': 'change-this-secret-key',
                'jwt_secret': 'jwt-secret-key',
                'password_min_length': 8,
                'session_timeout': 3600
            },
            'storage': {
                'data_directory': 'data',
                'temp_directory': 'temp',
                'backup_directory': 'backup',
                'max_file_size': '100MB',
                'allowed_file_types': ['csv', 'json', 'xlsx', 'parquet']
            }
        }
    
    def _save_default_config(self):
        """บันทึกการตั้งค่าเริ่มต้นลงไฟล์"""
        try:
            # สร้างโฟลเดอร์ถ้าไม่มี
            config_dir = os.path.dirname(self.config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
            
            self.logger.info(f"Default configuration saved to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving default config: {e}")
    
    def _apply_env_overrides(self):
        """ใช้ environment variables override การตั้งค่า"""
        try:
            # รูปแบบ environment variable: DATAOPS_SECTION_KEY
            env_prefix = 'DATAOPS_'
            
            for env_key, env_value in os.environ.items():
                if env_key.startswith(env_prefix):
                    # แปลง DATAOPS_DATABASE_PRIMARY_HOST เป็น database.primary.host
                    config_key = env_key[len(env_prefix):].lower().replace('_', '.')
                    
                    # ตั้งค่าใน config
                    self._set_nested_value(self.config, config_key, env_value)
                    self.logger.debug(f"Environment override: {config_key} = {env_value}")
                    
        except Exception as e:
            self.logger.error(f"Error applying environment overrides: {e}")
    
    def _set_nested_value(self, config_dict: Dict[str, Any], key_path: str, value: str):
        """ตั้งค่าใน nested dictionary"""
        try:
            keys = key_path.split('.')
            current = config_dict
            
            # สร้าง nested structure ถ้าไม่มี
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # แปลงประเภทข้อมูล
            final_key = keys[-1]
            converted_value = self._convert_env_value(value)
            current[final_key] = converted_value
            
        except Exception as e:
            self.logger.error(f"Error setting nested value {key_path}: {e}")
    
    def _convert_env_value(self, value: str) -> Any:
        """แปลงค่าจาก environment variable เป็นประเภทที่เหมาะสม"""
        try:
            # Boolean values
            if value.lower() in ['true', 'false']:
                return value.lower() == 'true'
            
            # None/null values
            if value.lower() in ['none', 'null', '']:
                return None
            
            # Numbers
            if re.match(r'^-?\d+$', value):
                return int(value)
            
            if re.match(r'^-?\d+\.\d+$', value):
                return float(value)
            
            # Lists (comma-separated)
            if ',' in value:
                return [item.strip() for item in value.split(',')]
            
            # String (default)
            return value
            
        except Exception:
            return value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """ดึงค่าการตั้งค่าด้วย dotted notation"""
        try:
            keys = key_path.split('.')
            current = self.config
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
            
            return current
            
        except Exception as e:
            self.logger.error(f"Error getting config value {key_path}: {e}")
            return default
    
    def set(self, key_path: str, value: Any):
        """ตั้งค่าการตั้งค่าด้วย dotted notation"""
        try:
            keys = key_path.split('.')
            current = self.config
            
            # สร้าง nested structure ถ้าไม่มี
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # ตั้งค่า
            final_key = keys[-1]
            current[final_key] = value
            
            self.logger.debug(f"Configuration updated: {key_path} = {value}")
            
        except Exception as e:
            self.logger.error(f"Error setting config value {key_path}: {e}")
    
    def reload(self):
        """โหลดการตั้งค่าใหม่"""
        try:
            self.last_modified = None  # Force reload
            self._load_config()
            self._apply_env_overrides()
            self.logger.info("Configuration reloaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error reloading configuration: {e}")
    
    def validate_config(self) -> Dict[str, Any]:
        """ตรวจสอบความถูกต้องของการตั้งค่า"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # ตรวจสอบ required sections
            required_sections = ['app', 'logging', 'database', 'data_quality', 'monitoring']
            
            for section in required_sections:
                if section not in self.config:
                    validation_result['errors'].append(f"Missing required section: {section}")
                    validation_result['valid'] = False
            
            # ตรวจสอบ database configuration
            if 'database' in self.config:
                db_config = self.config['database']
                
                if 'primary' in db_config:
                    primary_db = db_config['primary']
                    required_db_fields = ['type', 'host', 'database', 'username', 'password']
                    
                    for field in required_db_fields:
                        if field not in primary_db:
                            validation_result['errors'].append(f"Missing database field: primary.{field}")
                            validation_result['valid'] = False
                    
                    # ตรวจสอบ default passwords
                    if primary_db.get('password') == 'changeme':
                        validation_result['warnings'].append("Using default password for primary database")
            
            # ตรวจสอบ security configuration
            if 'security' in self.config:
                security_config = self.config['security']
                
                if security_config.get('encryption_key') == 'change-this-secret-key':
                    validation_result['warnings'].append("Using default encryption key")
                
                if security_config.get('jwt_secret') == 'jwt-secret-key':
                    validation_result['warnings'].append("Using default JWT secret")
            
            # ตรวจสอบ data quality thresholds
            if 'data_quality' in self.config:
                dq_config = self.config['data_quality']
                
                if 'quality_thresholds' in dq_config:
                    thresholds = dq_config['quality_thresholds']
                    
                    for threshold_name, threshold_value in thresholds.items():
                        if not isinstance(threshold_value, (int, float)) or threshold_value < 0 or threshold_value > 1:
                            validation_result['errors'].append(
                                f"Invalid quality threshold: {threshold_name} = {threshold_value} (must be between 0 and 1)"
                            )
                            validation_result['valid'] = False
            
            # ตรวจสอบ monitoring configuration
            if 'monitoring' in self.config:
                monitoring_config = self.config['monitoring']
                
                if monitoring_config.get('enabled') and 'thresholds' in monitoring_config:
                    thresholds = monitoring_config['thresholds']
                    
                    for metric_name, threshold_config in thresholds.items():
                        if not isinstance(threshold_config, dict):
                            validation_result['errors'].append(f"Invalid threshold config for {metric_name}")
                            validation_result['valid'] = False
                            continue
                        
                        # ตรวจสอบ severity levels
                        severity = threshold_config.get('severity', 'medium')
                        if severity not in ['low', 'medium', 'high', 'critical']:
                            validation_result['warnings'].append(f"Invalid severity level for {metric_name}: {severity}")
            
            # ตรวจสอบ file paths
            if 'storage' in self.config:
                storage_config = self.config['storage']
                
                for path_key in ['data_directory', 'temp_directory', 'backup_directory']:
                    if path_key in storage_config:
                        path_value = storage_config[path_key]
                        if not isinstance(path_value, str) or not path_value.strip():
                            validation_result['errors'].append(f"Invalid storage path: {path_key}")
                            validation_result['valid'] = False
            
            self.logger.info(f"Configuration validation completed: {'VALID' if validation_result['valid'] else 'INVALID'}")
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Validation error: {str(e)}")
            self.logger.error(f"Error validating configuration: {e}")
        
        return validation_result
    
    def get_database_url(self, db_name: str = 'primary') -> str:
        """สร้าง database URL สำหรับ SQLAlchemy"""
        try:
            db_config = self.get(f'database.{db_name}')
            if not db_config:
                raise ValueError(f"Database configuration not found: {db_name}")
            
            db_type = db_config.get('type', 'mssql')
            host = db_config.get('host', 'localhost')
            port = db_config.get('port')
            database = db_config.get('database')
            username = db_config.get('username')
            password = db_config.get('password')
            
            if db_type == 'mssql':
                # MSSQL with pymssql
                if port:
                    return f'mssql+pymssql://{username}:{password}@{host}:{port}/{database}'
                else:
                    return f'mssql+pymssql://{username}:{password}@{host}/{database}'
            
            elif db_type == 'postgresql':
                # PostgreSQL
                if port:
                    return f'postgresql://{username}:{password}@{host}:{port}/{database}'
                else:
                    return f'postgresql://{username}:{password}@{host}/{database}'
            
            elif db_type == 'mysql':
                # MySQL
                if port:
                    return f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
                else:
                    return f'mysql+pymysql://{username}:{password}@{host}/{database}'
            
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
                
        except Exception as e:
            self.logger.error(f"Error creating database URL: {e}")
            raise
    
    def get_section(self, section_name: str) -> Dict[str, Any]:
        """ดึงการตั้งค่าทั้งหมดใน section"""
        return self.config.get(section_name, {})
    
    def update_section(self, section_name: str, section_data: Dict[str, Any]):
        """อัพเดตการตั้งค่าทั้งหมดใน section"""
        try:
            self.config[section_name] = section_data
            self.logger.info(f"Section updated: {section_name}")
            
        except Exception as e:
            self.logger.error(f"Error updating section {section_name}: {e}")
    
    def save_config(self):
        """บันทึกการตั้งค่าปัจจุบันลงไฟล์"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """ดึงสรุปการตั้งค่าสำหรับการแสดงผล"""
        try:
            summary = {
                'config_file': self.config_path,
                'last_modified': datetime.fromtimestamp(self.last_modified) if self.last_modified else None,
                'sections': list(self.config.keys()),
                'total_keys': self._count_keys(self.config),
                'validation': self.validate_config()
            }
            
            # เพิ่มข้อมูลสำคัญ
            summary['app_info'] = {
                'name': self.get('app.name', 'Unknown'),
                'version': self.get('app.version', '0.0.0'),
                'environment': self.get('app.environment', 'unknown')
            }
            
            summary['database_info'] = {
                'primary_type': self.get('database.primary.type', 'unknown'),
                'primary_host': self.get('database.primary.host', 'unknown'),
                'secondary_configured': bool(self.get('database.secondary'))
            }
            
            summary['monitoring_info'] = {
                'enabled': self.get('monitoring.enabled', False),
                'interval': self.get('monitoring.interval', 60),
                'thresholds_count': len(self.get('monitoring.thresholds', {}))
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting config summary: {e}")
            return {'error': str(e)}
    
    def _count_keys(self, obj: Any) -> int:
        """นับจำนวน keys ทั้งหมดใน nested dictionary"""
        count = 0
        
        if isinstance(obj, dict):
            count += len(obj)
            for value in obj.values():
                count += self._count_keys(value)
        elif isinstance(obj, list):
            for item in obj:
                count += self._count_keys(item)
        
        return count
    
    def __str__(self) -> str:
        """String representation"""
        return f"ConfigManager(config_path='{self.config_path}', sections={list(self.config.keys())})"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return f"ConfigManager(config_path='{self.config_path}', config={self.config})"


def main():
    """ตัวอย่างการใช้งาน Configuration Manager"""
    print("=== DataOps Foundation Configuration Manager ===")
    
    # สร้าง config manager
    config = ConfigManager()
    
    # ดูสรุปการตั้งค่า
    summary = config.get_config_summary()
    print("\n📋 Configuration Summary:")
    print(f"   Config file: {summary['config_file']}")
    print(f"   Sections: {summary['sections']}")
    print(f"   Total keys: {summary['total_keys']}")
    print(f"   App: {summary['app_info']['name']} v{summary['app_info']['version']}")
    print(f"   Environment: {summary['app_info']['environment']}")
    
    # ตรวจสอบความถูกต้อง
    validation = config.validate_config()
    print(f"\n🔍 Configuration Validation:")
    print(f"   Status: {'✅ VALID' if validation['valid'] else '❌ INVALID'}")
    
    if validation['errors']:
        print("   Errors:")
        for error in validation['errors']:
            print(f"     - {error}")
    
    if validation['warnings']:
        print("   Warnings:")
        for warning in validation['warnings']:
            print(f"     - {warning}")
    
    # ทดสอบการดึงค่า
    print(f"\n📊 Configuration Values:")
    print(f"   Database type: {config.get('database.primary.type', 'not set')}")
    print(f"   Monitoring enabled: {config.get('monitoring.enabled', False)}")
    print(f"   Quality threshold: {config.get('data_quality.quality_thresholds.completeness', 0.85)}")
    
    # ทดสอบ database URL
    try:
        db_url = config.get_database_url('primary')
        print(f"   Database URL: {db_url[:50]}...")
    except Exception as e:
        print(f"   Database URL error: {e}")
    
    # ทดสอบการตั้งค่า
    config.set('app.debug', True)
    print(f"   Debug mode: {config.get('app.debug')}")
    
    print("\n✅ Configuration Manager test completed")


if __name__ == "__main__":
    main()
