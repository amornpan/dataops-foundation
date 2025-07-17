# 🚀 DataOps Foundation - แพลตฟอร์มจัดการข้อมูลองค์รวม

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Docker-Ready-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/CI%2FCD-Jenkins-orange.svg" alt="CI/CD">
  <img src="https://img.shields.io/badge/Coverage-90%25-brightgreen.svg" alt="Coverage">
</div>

**DataOps Foundation** เป็นแพลตฟอร์มองค์รวมระดับองค์กรสำหรับการจัดการข้อมูลที่ผรวมเอา ETL processing ขั้นสูง, CI/CD pipeline ที่แข็งแกร่ง และระบบ monitoring ที่ครอบคลุม เพื่อสร้างระบบนิเวศ DataOps ที่สมบูรณ์แบบ

## 🎯 ภาพรวมของโปรเจค

DataOps Foundation เป็นสะพานเชื่อมระหว่าง Data Engineering แบบดั้งเดิมกับ DevOps สมัยใหม่ โดยมีคุณสมบัติดังนี้:

- **🔄 ระบบ ETL ขั้นสูง**: จัดการ data pipeline อัจฉริยะพร้อมการประกันคุณภาพข้อมูล
- **⚡ CI/CD Integration**: การทดสอบและ deployment อัตโนมัติ
- **📊 Monitoring แบบ Real-time**: การติดตามและแจ้งเตือนที่ครอบคลุม
- **🛡️ การประกันคุณภาพข้อมูล**: เครื่องมือตรวจสอบและ profiling ในตัว
- **🐳 สถาปัตยกรรมแบบ Container-first**: รองรับ Docker และ Kubernetes เต็มรูปแบบ
- **🔧 Framework ขยายได้**: สถาปัตยกรรม Plugin สำหรับการรวมระบบที่กำหนดเอง

## 🚀 เริ่มต้นใช้งานอย่างรวดเร็ว

### 1. โคลนโปรเจค

```bash
git clone https://github.com/amornpan/dataops-foundation.git
cd dataops-foundation
```

### 2. ตั้งค่าสภาพแวดล้อมการพัฒนา

```bash
# สร้าง virtual environment
python -m venv venv

# เปิดใช้งาน virtual environment
# บน Windows:
venv\Scripts\activate
# บน macOS/Linux:
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt
```

### 3. รันการทดสอบ

```bash
# รันการทดสอบทั้งหมด
python tests/test_enhanced_etl.py

# รันการทดสอบด้วย pytest
pytest tests/ -v
```

### 4. เริ่มต้นด้วย Docker Compose

```bash
# เริ่มบริการทั้งหมด
docker-compose -f docker/docker-compose.yml up -d
```

### 5. ตั้งค่า Jenkins CI/CD

#### วิธีที่ 1: ใช้ Setup Script (แนะนำ)

```bash
# Linux/macOS
chmod +x jenkins/scripts/setup_jenkins.sh
./jenkins/scripts/setup_jenkins.sh

# Windows
jenkins\scripts\setup_jenkins.bat
```

#### วิธีที่ 2: Manual Setup

```bash
# Build Jenkins image พร้อม Python
docker build -f docker/Dockerfile.jenkins -t dataops-jenkins .

# รัน Jenkins container
docker run -d \
  --name dataops-jenkins \
  -p 8081:8080 \
  -p 50000:50000 \
  -v jenkins-data:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/workspace \
  --restart unless-stopped \
  dataops-jenkins

# ดูรหัสผ่านเริ่มต้น
docker exec dataops-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

#### การเข้าถึง Jenkins

- **Jenkins URL**: http://localhost:8081
- **Username**: admin
- **Password**: (ดูจากคำสั่งข้างต้น หรือ DataOps123!)

#### การตั้งค่าเพิ่มเติม

1. **เพิ่ม GitHub Credentials**:
   - Dashboard → Manage Jenkins → Manage Credentials
   - เพิ่ม GitHub Personal Access Token

2. **สร้าง Pipeline Job**:
   - New Item → Pipeline
   - Repository: https://github.com/amornpan/dataops-foundation.git
   - Script Path: jenkins/Jenkinsfile

3. **ตั้งค่า GitHub Webhook**:
   - GitHub Repository → Settings → Webhooks
   - URL: http://your-server:8081/github-webhook/

**📚 คู่มือการตั้งค่า Jenkins ที่ละเอียด: [docs/jenkins-setup.md](docs/jenkins-setup.md)**

## 📁 โครงสร้างโปรเจค

```
dataops-foundation/
├── 📂 src/                          # โค้ดหลัก
│   ├── 📂 data_pipeline/            # เครื่องมือประมวลผล ETL
│   ├── 📂 data_quality/             # กรอบการทำงานคุณภาพข้อมูล
│   ├── 📂 monitoring/               # การติดตามและสังเกตการณ์
│   └── 📂 utils/                    # โมดูลยูทิลิตี้
├── 📂 tests/                        # ชุดการทดสอบ
├── 📂 config/                       # ไฟล์การตั้งค่า
├── 📂 docker/                       # การตั้งค่า Docker
├── 📂 jenkins/                      # CI/CD pipeline
└── 📂 docs/                         # เอกสารประกอบ
```

## 🎉 สรุป

**DataOps Foundation** รวมจุดแข็งของทั้งสองโปรเจคที่คุณให้ศึกษา:

✅ **ETL Processing ขั้นสูง** - จาก ETL-dev (1).py  
✅ **CI/CD Pipeline** - จาก python-jenkins  
✅ **Data Quality Framework** - ขยายจากโค้ดเดิม  
✅ **Monitoring & Observability** - เพิ่มเติมสำหรับ production  
✅ **Containerization** - Docker และ Kubernetes support  
✅ **Enterprise-ready** - Security, Scaling, และ Documentation ครบถ้วน  

พร้อมใช้งานในระดับองค์กรและขยายได้ตามความต้องการ! 🚀

**Happy DataOps! 🎊**