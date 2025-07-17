#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Configuration Manager
จัดการการตั้งค่าและ environment variables

Features:
- YAML configuration loading
- Environment variable override
- Configuration validation
- Dynamic configuration updates
- Secure credential management
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
import json


class ConfigManager:
    """
    Configuration Manager สำหรับ DataOps Foundation
    """
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """เริ่มต้น Configuration Manager"""
        self.config_path = config_path
        self.config = {}
        self.logger = logging.getLogger(__name__)
        
        # โหลดการตั้งค่า
        self._load_config()
        
        # โหลด environment variables
        self._load_environment_variables()
    
    def _load_config(self):
        """โหลดการตั้งค่าจากไฟล์ YAML"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self.config = yaml.safe_load(file) or {}
                self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.logger.warning(f"Configuration file not found: {self.config_path}")
                self.config = {}
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.config = {}
    
    def _load_environment_variables(self):
        """โหลดและ override การตั้งค่าจาก environment variables"""
        env_mappings = {
            # Database settings
            'DATAOPS_DB_HOST': 'database.primary.host',
            'DATAOPS_DB_PORT': 'database.primary.port',
            'DATAOPS_DB_NAME': 'database.primary.database',
            'DATAOPS_DB_USER': 'database.primary.username',
            'DATAOPS_DB_PASSWORD': 'database.primary.password',
            
            # Data Quality settings
            'DATAOPS_MAX_NULL_PCT': 'data_quality.max_null_percentage',
            'DATAOPS_ACCEPTABLE_NULL': 'data_quality.acceptable_max_null',
            'DATAOPS_QUALITY_THRESHOLD': 'data_quality.quality_threshold',
            
            # Processing settings
            'DATAOPS_BATCH_SIZE': 'processing.batch_size',
            'DATAOPS_MAX_WORKERS': 'processing.max_workers',
            'DATAOPS_ENABLE_PARALLEL': 'processing.enable_parallel',
            
            # Logging settings
            'DATAOPS_LOG_LEVEL': 'logging.level',
            'DATAOPS_LOG_FILE': 'logging.file.path',
            
            # Monitoring settings
            'DATAOPS_ENABLE_METRICS': 'monitoring.enabled',
            'DATAOPS_PROMETHEUS_PORT': 'monitoring.prometheus.port',
            
            # Environment
            'DATAOPS_ENV': 'environment.name',
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_config(config_path, self._convert_env_value(env_value))
                self.logger.debug(f"Environment variable {env_var} applied to {config_path}")
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """แปลงค่าจาก environment variable ให้เป็นประเภทที่เหมาะสม"""
        # Boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # String value
        return value
    
    def _set_nested_config(self, path: str, value: Any):
        """ตั้งค่าโดยใช้ nested path (เช่น 'database.primary.host')"""
        keys = path.split('.')
        config = self.config
        
        # Navigate to the parent of the final key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the final value
        config[keys[-1]] = value
    
    def get(self, path: str, default: Any = None) -> Any:
        """ดึงค่าการตั้งค่าโดยใช้ nested path"""
        try:
            keys = path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
        except Exception as e:
            self.logger.error(f"Error getting config value for {path}: {e}")
            return default
    
    def set(self, path: str, value: Any):
        """ตั้งค่าโดยใช้ nested path"""
        self._set_nested_config(path, value)
    
    def get_database_config(self, db_name: str = 'primary') -> Dict[str, Any]:
        """ดึงการตั้งค่าฐานข้อมูล"""
        return self.get(f'database.{db_name}', {})
    
    def get_data_quality_config(self) -> Dict[str, Any]:
        """ดึงการตั้งค่าคุณภาพข้อมูล"""
        return self.get('data_quality', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """ดึงการตั้งค่าการประมวลผล"""
        return self.get('processing', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """ดึงการตั้งค่าการติดตาม"""
        return self.get('monitoring', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """ดึงการตั้งค่า logging"""
        return self.get('logging', {})
    
    def is_development(self) -> bool:
        """ตรวจสอบว่าอยู่ใน development environment หรือไม่"""
        return self.get('environment.name', 'development').lower() == 'development'
    
    def is_production(self) -> bool:
        """ตรวจสอบว่าอยู่ใน production environment หรือไม่"""
        return self.get('environment.name', 'development').lower() == 'production'
    
    def validate_config(self) -> Dict[str, Any]:
        """ตรวจสอบความถูกต้องของการตั้งค่า"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Required database settings
        db_config = self.get_database_config()
        required_db_fields = ['host', 'database', 'username', 'password']
        
        for field in required_db_fields:
            if not db_config.get(field):
                validation_results['errors'].append(f"Missing required database field: {field}")
                validation_results['valid'] = False
        
        # Data quality thresholds
        quality_config = self.get_data_quality_config()
        max_null_pct = quality_config.get('max_null_percentage', 30)
        if not isinstance(max_null_pct, (int, float)) or max_null_pct < 0 or max_null_pct > 100:
            validation_results['errors'].append("max_null_percentage must be between 0 and 100")
            validation_results['valid'] = False
        
        # Processing settings
        processing_config = self.get_processing_config()
        batch_size = processing_config.get('batch_size', 1000)
        if not isinstance(batch_size, int) or batch_size <= 0:
            validation_results['errors'].append("batch_size must be a positive integer")
            validation_results['valid'] = False
        
        max_workers = processing_config.get('max_workers', 4)
        if not isinstance(max_workers, int) or max_workers <= 0:
            validation_results['errors'].append("max_workers must be a positive integer")
            validation_results['valid'] = False
        
        # Environment-specific validations
        if self.is_production():
            # Production should have monitoring enabled
            if not self.get('monitoring.enabled', False):
                validation_results['warnings'].append("Monitoring should be enabled in production")
            
            # Production should have proper logging
            if self.get('logging.level', 'INFO') == 'DEBUG':
                validation_results['warnings'].append("DEBUG logging level not recommended for production")
        
        return validation_results
    
    def reload_config(self):
        """โหลดการตั้งค่าใหม่"""
        self._load_config()
        self._load_environment_variables()
        self.logger.info("Configuration reloaded")
    
    def save_config(self, output_path: Optional[str] = None):
        """บันทึกการตั้งค่าลงไฟล์"""
        output_path = output_path or self.config_path
        
        try:
            # สร้างไดเรกทอรีหากไม่มี
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"Configuration saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            raise
    
    def export_config(self, format: str = 'yaml') -> str:
        """ส่งออกการตั้งค่าในรูปแบบที่ต้องการ"""
        if format.lower() == 'json':
            return json.dumps(self.config, indent=2, ensure_ascii=False)
        elif format.lower() == 'yaml':
            return yaml.dump(self.config, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_connection_string(self, db_name: str = 'primary') -> str:
        """สร้าง connection string สำหรับฐานข้อมูล"""
        db_config = self.get_database_config(db_name)
        
        if not db_config:
            raise ValueError(f"Database configuration not found: {db_name}")
        
        db_type = db_config.get('type', 'mssql')
        host = db_config.get('host')
        port = db_config.get('port')
        database = db_config.get('database')
        username = db_config.get('username')
        password = db_config.get('password')
        
        if db_type == 'mssql':
            return f"mssql+pymssql://{username}:{password}@{host}:{port}/{database}"
        elif db_type == 'postgresql':
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        elif db_type == 'mysql':
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def __str__(self) -> str:
        """แสดงการตั้งค่าในรูปแบบ string"""
        return f"ConfigManager(config_path='{self.config_path}')"
    
    def __repr__(self) -> str:
        return self.__str__()


def main():
    """ตัวอย่างการใช้งาน Configuration Manager"""
    print("=== DataOps Foundation Configuration Manager ===")
    
    # เริ่มต้น ConfigManager
    config = ConfigManager()
    
    # แสดงการตั้งค่าฐานข้อมูล
    db_config = config.get_database_config()
    print(f"Database Host: {db_config.get('host', 'Not configured')}")
    print(f"Database Name: {db_config.get('database', 'Not configured')}")
    
    # แสดงการตั้งค่าคุณภาพข้อมูล
    quality_config = config.get_data_quality_config()
    print(f"Max Null Percentage: {quality_config.get('max_null_percentage', 30)}%")
    print(f"Quality Threshold: {quality_config.get('quality_threshold', 80)}%")
    
    # ตรวจสอบความถูกต้องของการตั้งค่า
    validation = config.validate_config()
    if validation['valid']:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration has errors:")
        for error in validation['errors']:
            print(f"   - {error}")
    
    if validation['warnings']:
        print("⚠️ Configuration warnings:")
        for warning in validation['warnings']:
            print(f"   - {warning}")


if __name__ == "__main__":
    main()
