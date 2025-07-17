# 🚀 DataOps Foundation - ETL Pipeline

**โปรเจค DataOps Foundation** เป็น ETL Pipeline ที่มีประสิทธิภาพสูง สำหรับการประมวลผลข้อมูลสินเชื่อ (Loan Data) และโหลดเข้าสู่ SQL Server Data Warehouse พร้อมระบบ CI/CD โดยใช้ Jenkins

> **พัฒนาจาก:** `ETL-dev.py` โดยปรับปรุงให้เหมาะสมกับ production environment

---

## 📋 สารบัญ

1. [ภาพรวมโปรเจค](#ภาพรวมโปรเจค)
2. [ฟีเจอร์หลัก](#ฟีเจอร์หลัก)
3. [โครงสร้างโปรเจค](#โครงสร้างโปรเจค)
4. [ความต้องการของระบบ](#ความต้องการของระบบ)
5. [การติดตั้งและตั้งค่า](#การติดตั้งและตั้งค่า)
6. [วิธีการใช้งาน](#วิธีการใช้งาน)
7. [การทดสอบ](#การทดสอบ)
8. [Jenkins CI/CD Pipeline](#jenkins-cicd-pipeline)
9. [การกำหนดค่า](#การกำหนดค่า)
10. [การแก้ไขปัญหา](#การแก้ไขปัญหา)
11. [การพัฒนาต่อยอด](#การพัฒนาต่อยอด)

---

## 🎯 ภาพรวมโปรเจค

### 📊 Data Flow Architecture
```
┌─────────────────────────────────────────────────────────────────────┐
│                    DataOps Foundation Pipeline                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  📁 CSV Input  →  🔍 Data Analysis  →  🧹 Data Cleaning            │
│       ↓                ↓                    ↓                      │
│  📊 Transform  →  📋 Dimension Tables  →  📈 Fact Table             │
│       ↓                ↓                    ↓                      │
│  💾 SQL Server  →  ✅ Validation  →  📊 Quality Report             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 🎯 ปัญหาที่แก้ไข
- **Manual ETL Process**: แปลงเป็น automated pipeline
- **No Testing**: เพิ่ม comprehensive unit tests
- **Hard-coded Values**: ใช้ configuration files
- **No Error Handling**: เพิ่ม robust error handling
- **No Logging**: เพิ่ม professional logging system
- **No CI/CD**: สร้าง Jenkins pipeline

---

## ✨ ฟีเจอร์หลัก

### 🔧 **ETL Pipeline Features**
| Feature | Description | Status |
|---------|-------------|--------|
| **Automated Data Ingestion** | อ่านและประมวลผล CSV files | ✅ |
| **Data Quality Validation** | ตรวจสอบคุณภาพข้อมูลครอบคลุม | ✅ |
| **Dimensional Modeling** | สร้าง Star Schema แบบมืออาชีพ | ✅ |
| **Error Handling** | จัดการข้อผิดพลาดอย่างมีประสิทธิภาพ | ✅ |
| **Logging & Monitoring** | ระบบติดตามและบันทึกการทำงาน | ✅ |
| **Configuration Management** | ปรับแต่งผ่าน YAML files | ✅ |
| **Database Integration** | เชื่อมต่อ SQL Server | ✅ |
| **Performance Optimization** | ปรับปรุงประสิทธิภาพการทำงาน | ✅ |

### 🏗️ **Data Warehouse Components**
```sql
-- Data Warehouse Schema
📊 Fact Table: loans_fact
├── loan_amnt (FLOAT)
├── funded_amnt (FLOAT)
├── term (INT)
├── int_rate (FLOAT)
├── installment (FLOAT)
├── home_ownership_id (INT) → FK
├── loan_status_id (INT) → FK
└── issue_d_id (INT) → FK

📋 Dimension Tables:
├── home_ownership_dim
│   ├── home_ownership_id (PK)
│   └── home_ownership (VARCHAR)
├── loan_status_dim
│   ├── loan_status_id (PK)
│   └── loan_status (VARCHAR)
└── issue_d_dim
    ├── issue_d_id (PK)
    ├── issue_d (DATE)
    ├── month (INT)
    ├── year (INT)
    ├── quarter (INT)
    └── month_name (VARCHAR)
```

### 🤖 **DevOps & CI/CD Features**
- **Jenkins Pipeline**: 7-stage automated pipeline
- **Unit Testing**: 15+ comprehensive test cases
- **Code Quality Checks**: Flake8, syntax validation
- **Automated Deployment**: Package creation and distribution
- **Health Monitoring**: System health checks
- **Artifact Management**: Build artifact storage

---

## 📁 โครงสร้างโปรเจค

```
dataops-foundation/
├── 📄 etl_pipeline.py              # 🔧 ETL Pipeline หลัก (Object-Oriented)
├── 🧪 test_etl_pipeline.py         # 🧪 Unit Tests (15+ test cases)
├── 📦 requirements.txt             # 📦 Python Dependencies
├── ⚙️ config.yaml                 # ⚙️ Configuration File
├── 🔧 Jenkinsfile                 # 🔧 Jenkins Pipeline Definition
├── 📚 README.md                   # 📚 Documentation (this file)
├── 🚫 .gitignore                  # 🚫 Git Ignore Rules
│
├── 📁 scripts/                    # 🛠️ Helper Scripts
│   ├── run_local.bat              # 🖥️ Windows Runner
│   └── run_local.sh               # 🐧 Linux/Mac Runner
│
├── 📁 data/                       # 📊 Data Directory
│   ├── sample_data.csv            # 📊 Sample Data (10 records)
│   └── README.md                  # 📊 Data Documentation
│
├── 📁 logs/                       # 📋 Log Directory
│   ├── etl_pipeline.log           # 📋 ETL Logs
│   └── audit.log                  # 📋 Audit Logs
│
├── 📁 tests/                      # 🧪 Extended Tests
│   ├── integration_tests.py       # 🧪 Integration Tests
│   ├── performance_tests.py       # 🧪 Performance Tests
│   └── data_quality_tests.py      # 🧪 Data Quality Tests
│
├── 📁 docs/                       # 📖 Documentation
│   ├── architecture.md            # 📖 Architecture Guide
│   ├── deployment.md              # 📖 Deployment Guide
│   └── troubleshooting.md         # 📖 Troubleshooting Guide
│
├── 📁 config/                     # ⚙️ Configuration Files
│   ├── dev.yaml                   # ⚙️ Development Config
│   ├── staging.yaml               # ⚙️ Staging Config
│   └── production.yaml            # ⚙️ Production Config
│
└── 📁 docker/                     # 🐳 Docker Files
    ├── Dockerfile                 # 🐳 Docker Image
    ├── docker-compose.yml         # 🐳 Docker Compose
    └── jenkins/                   # 🐳 Jenkins Docker Setup
```

---

## 🔧 ความต้องการของระบบ

### 💻 **สำหรับการพัฒนา Local**
| Component | Requirement | Version |
|-----------|-------------|---------|
| **Python** | Programming Language | 3.8+ |
| **pip** | Package Manager | Latest |
| **Git** | Version Control | 2.0+ |
| **Virtual Environment** | Isolation | venv/conda |

### 🌐 **สำหรับ Production Environment**
| Component | Requirement | Details |
|-----------|-------------|---------|
| **SQL Server** | Database Server | 2016+ |
| **Jenkins** | CI/CD Platform | 2.400+ |
| **Docker** | Container Platform | 20.10+ (Optional) |
| **Windows/Linux** | Operating System | Any |

### 📦 **Python Dependencies**
```python
# Core Data Processing
pandas>=1.5.0,<2.1.0          # Data manipulation
numpy>=1.21.0,<1.25.0         # Numerical computing
sqlalchemy>=1.4.0,<2.1.0      # Database ORM
pymssql>=2.2.0,<2.3.0         # SQL Server connector

# Testing & Quality
pytest>=7.0.0,<8.0.0          # Testing framework
black>=22.0.0,<24.0.0         # Code formatter
flake8>=5.0.0,<7.0.0          # Code linter
coverage>=6.0,<8.0            # Test coverage

# Configuration & Utilities
pyyaml>=6.0,<7.0              # YAML parser
python-dotenv>=1.0.0,<1.1.0   # Environment variables
```

---

## 🛠️ การติดตั้งและตั้งค่า

### 📝 **ขั้นตอนที่ 1: เตรียมสิ่งแวดล้อม**

#### 🔽 **1.1 Clone Repository**
```bash
# Clone โปรเจคจาก GitHub
git clone https://github.com/amornpan/dataops-foundation.git

# เข้าไปยัง project directory
cd dataops-foundation

# ตรวจสอบไฟล์ที่จำเป็น
ls -la
```

#### 🐍 **1.2 ติดตั้ง Python Environment**
```bash
# ตรวจสอบ Python version
python --version  # หรือ python3 --version

# สร้าง virtual environment
python -m venv venv

# เปิดใช้งาน virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# ตรวจสอบว่า virtual environment ทำงาน
which python  # ควรชี้ไปที่ venv/bin/python
```

#### 📦 **1.3 ติดตั้ง Dependencies**
```bash
# อัพเกรด pip
python -m pip install --upgrade pip

# ติดตั้ง packages จาก requirements.txt
pip install -r requirements.txt

# ตรวจสอบการติดตั้ง
pip list | grep -E "(pandas|sqlalchemy|pymssql|pytest)"
```

### 🗄️ **ขั้นตอนที่ 2: ตั้งค่า Database**

#### 🔧 **2.1 เตรียม SQL Server**
```sql
-- เชื่อมต่อ SQL Server และสร้าง database
CREATE DATABASE TestDB;
USE TestDB;

-- สร้าง user สำหรับ ETL (Optional)
CREATE LOGIN etl_user WITH PASSWORD = 'YourStrongPassword123!';
CREATE USER etl_user FOR LOGIN etl_user;
ALTER ROLE db_datareader ADD MEMBER etl_user;
ALTER ROLE db_datawriter ADD MEMBER etl_user;
ALTER ROLE db_ddladmin ADD MEMBER etl_user;
```

#### 🔐 **2.2 ตั้งค่า Connection String**
```bash
# ตั้งค่า environment variables
# Windows:
set DB_PASSWORD=Passw0rd123456
set DB_SERVER=x.x.x.x
set DB_NAME=TestDB
set DB_USERNAME=SA

# Linux/Mac:
export DB_PASSWORD=Passw0rd123456
export DB_SERVER=x.x.x.x
export DB_NAME=TestDB
export DB_USERNAME=SA
```

### ⚙️ **ขั้นตอนที่ 3: ปรับแต่ง Configuration**

#### 📝 **3.1 แก้ไขไฟล์ config.yaml**
```yaml
# config.yaml
database:
  server: "${DB_SERVER}"
  database: "${DB_NAME}"
  username: "${DB_USERNAME}"
  password: "${DB_PASSWORD}"
  port: 1433
  connection_timeout: 30

etl:
  acceptable_max_null: 26
  missing_threshold: 30.0
  batch_size: 10000
  
logging:
  level: "INFO"
  file: "logs/etl_pipeline.log"
```

#### 🧪 **3.2 ทดสอบการตั้งค่า**
```bash
# ทดสอบการเชื่อมต่อ database
python -c "
import pymssql
conn = pymssql.connect(
    server='x.x.x.x',
    user='SA',
    password='Passw0rd123456',
    database='TestDB'
)
print('✅ Database connection successful!')
conn.close()
"

# ทดสอบการ import ETL pipeline
python -c "
from etl_pipeline import DataOpsETLPipeline
print('✅ ETL pipeline import successful!')
"
```

---

## 🚀 วิธีการใช้งาน

### 🖥️ **การรันบน Windows**

#### 🔧 **วิธีที่ 1: ใช้ Automated Script**
```batch
# เปิด Command Prompt หรือ PowerShell
cd C:\path\to\dataops-foundation

# รัน automated script
scripts\run_local.bat

# Script จะทำงานดังนี้:
# 1. ตรวจสอบ Python installation
# 2. สร้าง virtual environment
# 3. ติดตั้ง packages
# 4. รัน unit tests
# 5. รัน ETL pipeline
# 6. สร้าง summary report
```

#### 🔧 **วิธีที่ 2: Manual Steps**
```batch
# 1. เปิดใช้งาน virtual environment
venv\Scripts\activate

# 2. ตรวจสอบ data file
dir data\sample_data.csv

# 3. รัน ETL pipeline
python etl_pipeline.py

# 4. ดูผลลัพธ์
type logs\etl_pipeline.log
```

### 🐧 **การรันบน Linux/Mac**

#### 🔧 **วิธีที่ 1: ใช้ Automated Script**
```bash
# เปิด Terminal
cd /path/to/dataops-foundation

# ทำให้ script สามารถรันได้
chmod +x scripts/run_local.sh

# รัน automated script
./scripts/run_local.sh

# Script จะทำงานดังนี้:
# 1. ตรวจสอบ Python installation
# 2. สร้าง virtual environment
# 3. ติดตั้ง packages
# 4. รัน unit tests
# 5. รัน ETL pipeline
# 6. สร้าง summary report
```

#### 🔧 **วิธีที่ 2: Manual Steps**
```bash
# 1. เปิดใช้งาน virtual environment
source venv/bin/activate

# 2. ตรวจสอบ data file
ls -la data/sample_data.csv

# 3. รัน ETL pipeline
python etl_pipeline.py

# 4. ดูผลลัพธ์
tail -f logs/etl_pipeline.log
```

---

## 📞 การสนับสนุนและติดต่อ

### 🆘 **หากพบปัญหา**

#### 📋 **ขั้นตอนการแก้ไขปัญหา**
1. **ตรวจสอบ [การแก้ไขปัญหา](#การแก้ไขปัญหา)** ในเอกสาร
2. **ตรวจสอบ log files** ใน `logs/` directory
3. **รัน health check script** เพื่อตรวจสอบระบบ
4. **ตรวจสอบ Jenkins console output** (หากใช้ CI/CD)
5. **สร้าง Issue** ใน GitHub repository

#### 🔍 **ข้อมูลที่ควรรวม**
- **ระบบปฏิบัติการ**: Windows/Linux/Mac
- **Python version**: `python --version`
- **Error message**: Complete error traceback
- **Log files**: Relevant log entries
- **Configuration**: Masked config files
- **Steps to reproduce**: Detailed steps

### 📞 **ช่องทางการติดต่อ**
- **GitHub Repository**: https://github.com/amornpan/dataops-foundation
- **Issue Tracker**: https://github.com/amornpan/dataops-foundation/issues
- **Email**: amornpan@gmail.com

---

## 📄 License

โปรเจคนี้ใช้ **MIT License** - ดูรายละเอียดในไฟล์ [LICENSE](LICENSE)

---

## 🙏 ขอบคุณ

### 🛠️ **Technologies Used**
- **[Python](https://python.org/)** - Programming Language
- **[pandas](https://pandas.pydata.org/)** - Data Manipulation Library
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - SQL Toolkit and ORM
- **[Jenkins](https://jenkins.io/)** - CI/CD Automation Platform
- **[Docker](https://docker.com/)** - Container Platform
- **[pytest](https://pytest.org/)** - Testing Framework
- **[YAML](https://yaml.org/)** - Configuration Language

### 👥 **Contributors**
- **Lead Developer**: Amornpan Phornchaicharoen
- **Data Engineer**: Amornpan Phornchaicharoen
- **DevOps Engineer**: Amornpan Phornchaicharoen

---

## 🎓 สรุป

**DataOps Foundation** แสดงให้เห็นการสร้าง modern data pipeline ที่สมบูรณ์โดยใช้:

- **🐍 Python** สำหรับ ETL processing
- **🗄️ SQL Server** สำหรับ data warehouse
- **🔧 Jenkins** สำหรับ CI/CD automation
- **🧪 pytest** สำหรับ automated testing
- **⚙️ YAML** สำหรับ configuration management
- **🐳 Docker** สำหรับ containerization

**เหมาะสำหรับการเรียนรู้ DataOps, DevOps และการพัฒนา data pipeline สมัยใหม่!** 🚀

**Happy Data Engineering!** 🎉

---

## 📈 Quick Start Guide

### 🚀 **รันใน 5 นาที**

```bash
# 1. Clone และเข้าโฟลเดอร์
git clone https://github.com/amornpan/dataops-foundation.git
cd dataops-foundation

# 2. ตั้งค่า environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ venv\Scripts\activate  # Windows

# 3. ติดตั้ง packages
pip install -r requirements.txt

# 4. รัน tests
python -m pytest test_etl_pipeline.py -v

# 5. รัน ETL pipeline
python etl_pipeline.py

# 🎉 เสร็จสิ้น! ตรวจสอบผลลัพธ์ใน logs/etl_pipeline.log
```

---

**🔥 พร้อมใช้งานแล้ว! Happy Coding!** 🔥
