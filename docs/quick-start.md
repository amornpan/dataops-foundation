# 🚀 DataOps Foundation - Quick Start Guide

เริ่มต้นใช้งาน DataOps Foundation ใน 15 นาที!

## 📋 ข้อกำหนดเบื้องต้น

- **Python 3.11+**
- **Git**
- **Docker & Docker Compose** (ไม่บังคับ)

## 🚀 การติดตั้งอย่างรวดเร็ว

### 1. Clone Repository

```bash
git clone https://github.com/amornpan/dataops-foundation.git
cd dataops-foundation
```

### 2. ตั้งค่า Python Environment

```bash
# สร้าง virtual environment
python -m venv venv

# เปิดใช้งาน virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt
```

### 3. ตั้งค่าเริ่มต้น

```bash
# คัดลอกไฟล์การตั้งค่า
cp config/config.yaml config/config.local.yaml

# แก้ไขการตั้งค่าตามต้องการ (ไม่บังคับ)
```

### 4. ทดสอบการติดตั้ง

```bash
# รันการทดสอบ ETL ขั้นสูง
python tests/test_enhanced_etl.py

# รันการทดสอบด้วย pytest
pytest tests/ -v
```

## 💡 การใช้งานพื้นฐาน

### ETL Processing

```python
from src.data_pipeline.etl_processor import ETLProcessor

# เริ่มต้น processor
processor = ETLProcessor()

# รัน ETL pipeline แบบ end-to-end
result = processor.run_full_pipeline('data/input.csv')

if result.success:
    print(f"✅ Processed {result.processed_records} records")
    print(f"🎯 Quality score: {result.quality_score}%")
else:
    print("❌ Pipeline failed:")
    for error in result.errors:
        print(f"   - {error}")
```

### Data Quality Checks

```python
from src.data_quality.quality_checker import DataQualityChecker
import pandas as pd

# โหลดข้อมูล
df = pd.read_csv('data/input.csv')

# ตรวจสอบคุณภาพ
checker = DataQualityChecker()
quality_result = checker.run_checks(df)

# แสดงรายงาน
report = checker.generate_report(quality_result)
print(report)
```

## 🐳 การใช้งานด้วย Docker

### เริ่มต้นบริการทั้งหมด

```bash
# เริ่มบริการ DataOps Foundation
docker-compose -f docker/docker-compose.yml up -d

# ตรวจสอบสถานะ
docker-compose -f docker/docker-compose.yml ps
```

### เข้าถึงบริการ

- **แอปพลิเคชันหลัก**: http://localhost:8080
- **Jenkins CI/CD**: http://localhost:8081 (admin/DataOps123!)
- **Grafana Monitoring**: http://localhost:3000 (admin/DataOps123!)
- **Prometheus Metrics**: http://localhost:9090
- **Jupyter Notebooks**: http://localhost:8888 (token: DataOps123!)

## 🔧 การตั้งค่าขั้นสูง

### Environment Variables

```bash
# Database
export DATAOPS_DB_HOST=your-db-host
export DATAOPS_DB_USER=your-username
export DATAOPS_DB_PASSWORD=your-password

# Quality Thresholds
export DATAOPS_MAX_NULL_PCT=30
export DATAOPS_QUALITY_THRESHOLD=80

# Monitoring
export DATAOPS_ENABLE_METRICS=true
```

### Configuration File

แก้ไข `config/config.yaml`:

```yaml
database:
  primary:
    host: "your-database-host"
    database: "your-database"
    username: "your-username"
    password: "your-password"

data_quality:
  max_null_percentage: 30.0
  quality_threshold: 80.0

monitoring:
  enabled: true
  prometheus:
    enabled: true
    port: 8000
```

## 📊 การติดตาม (Monitoring)

### Prometheus Metrics

DataOps Foundation ส่งออก metrics ดังนี้:

- `dataops_etl_records_processed_total` - จำนวน records ที่ประมวลผล
- `dataops_etl_processing_duration_seconds` - เวลาการประมวลผล
- `dataops_data_quality_score` - คะแนนคุณภาพข้อมูล
- `dataops_etl_errors_total` - จำนวนข้อผิดพลาด

### Grafana Dashboards

เข้าถึง Grafana ที่ http://localhost:3000 และ import dashboard ที่กำหนดไว้ล่วงหน้า

## 🧪 การทดสอบ

### รันการทดสอบทั้งหมด

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests  
pytest tests/integration/ -v

# Enhanced ETL tests
python tests/test_enhanced_etl.py

# Performance tests
pytest tests/performance/ -v --benchmark-only
```

### Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html
# เปิด htmlcov/index.html เพื่อดูรายงาน
```

## 🚀 CI/CD Pipeline

### Jenkins Setup

1. เข้าถึง Jenkins ที่ http://localhost:8081
2. สร้าง Pipeline job ใหม่
3. ใช้ `jenkins/Jenkinsfile` เป็น pipeline script
4. Configure GitHub webhooks สำหรับ auto-triggering

### Pipeline Stages

- **Code Quality Checks** - Linting, formatting, security scan
- **Unit Tests** - ทดสอบหน่วยพร้อม coverage
- **Integration Tests** - ทดสอบการรวมระบบ
- **Data Quality Tests** - ทดสอบ ETL และ data quality
- **Performance Tests** - ทดสอบประสิทธิภาพ
- **Build Artifacts** - สร้าง deployment packages
- **Docker Build** - สร้าง container images

## 🎯 Use Cases

### 1. การประมวลผล CSV ขนาดใหญ่

```python
processor = ETLProcessor()

# กำหนดเกณฑ์คุณภาพข้อมูล
processor.max_null_percentage = 25
processor.acceptable_max_null = 20

# ประมวลผล
result = processor.run_full_pipeline('large_dataset.csv')
```

### 2. การตรวจสอบคุณภาพข้อมูลแบบ Real-time

```python
from src.monitoring.metrics_collector import MetricsCollector

collector = MetricsCollector()
checker = DataQualityChecker()

# ตรวจสอบและบันทึก metrics
quality_result = checker.run_checks(df)
collector.record_data_quality_score(
    quality_result.overall_score, 
    'production_data', 
    'completeness'
)
```

### 3. การสร้าง Data Warehouse

```python
# สร้าง dimensional model
processor.create_dimensional_model()

# สร้าง fact table
processor.create_fact_table()

# บันทึกลงฐานข้อมูล
processor.save_to_database()
```

## 🆘 การแก้ไขปัญหา

### ปัญหาเชื่อมต่อฐานข้อมูล

```bash
# ตรวจสอบการเชื่อมต่อ
python -c "
from src.utils.config_manager import ConfigManager
config = ConfigManager()
print(config.get_connection_string())
"
```

### ปัญหา Performance

```bash
# เปิดใช้งาน debug logging
export DATAOPS_LOG_LEVEL=DEBUG

# ตรวจสอบ memory usage
python -c "
import psutil
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'CPU: {psutil.cpu_percent()}%')
"
```

## 📚 เอกสารเพิ่มเติม

- **[Architecture Guide](docs/architecture.md)** - สถาปัตยกรรมระบบ
- **[API Reference](docs/api_reference.md)** - เอกสาร API
- **[Deployment Guide](docs/deployment.md)** - คู่มือการติดตั้ง Production
- **[Contributing Guide](CONTRIBUTING.md)** - คู่มือการพัฒนา

## 💬 การสนับสนุน

- 📋 **Issues**: https://github.com/amornpan/dataops-foundation/issues
- 💬 **Discussions**: https://github.com/amornpan/dataops-foundation/discussions
- 📧 **Email**: dataops@company.com

---

**Happy DataOps! 🎉**
