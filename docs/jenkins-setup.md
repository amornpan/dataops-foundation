# 🔧 Jenkins Setup Guide for DataOps Foundation

คู่มือการตั้งค่า Jenkins สำหรับ DataOps Foundation อย่างละเอียด

## 📋 สารบัญ

1. [การติดตั้ง Jenkins](#การติดตั้ง-jenkins)
2. [การตั้งค่าเบื้องต้น](#การตั้งค่าเบื้องต้น)
3. [การติดตั้ง Plugins](#การติดตั้ง-plugins)
4. [การตั้งค่า Credentials](#การตั้งค่า-credentials)
5. [การสร้าง Pipeline Job](#การสร้าง-pipeline-job)
6. [การตั้งค่า GitHub Integration](#การตั้งค่า-github-integration)
7. [การตั้งค่า Email Notifications](#การตั้งค่า-email-notifications)
8. [การแก้ไขปัญหา](#การแก้ไขปัญหา)

## 🚀 การติดตั้ง Jenkins

### วิธีที่ 1: ใช้ Docker (แนะนำ)

#### สร้าง Jenkins Container พร้อม Python และ DataOps Tools

```bash
# 1. สร้าง Docker network สำหรับ DataOps
docker network create dataops-network

# 2. Build Jenkins image พร้อม Python
cd dataops-foundation
docker build -f docker/Dockerfile.jenkins -t dataops-jenkins .

# 3. รัน Jenkins container
docker run -d \
  --name dataops-jenkins \
  --network dataops-network \
  -p 8081:8080 \
  -p 50000:50000 \
  -v jenkins-data:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/workspace \
  -e TZ=Asia/Bangkok \
  --restart unless-stopped \
  dataops-jenkins

# 4. ตรวจสอบสถานะ
docker ps | grep dataops-jenkins
docker logs dataops-jenkins
```

#### หรือใช้ Docker Compose (ง่ายกว่า)

```bash
# รันบริการทั้งหมดรวมทั้ง Jenkins
docker-compose -f docker/docker-compose.yml up -d

# ตรวจสอบสถานะ
docker-compose -f docker/docker-compose.yml ps
```

### วิธีที่ 2: ติดตั้ง Jenkins แบบ Native

#### Ubuntu/Debian

```bash
# 1. อัปเดต system
sudo apt update

# 2. ติดตั้ง Java
sudo apt install openjdk-11-jdk -y

# 3. เพิ่ม Jenkins repository
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
    /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
    https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
    /etc/apt/sources.list.d/jenkins.list > /dev/null

# 4. ติดตั้ง Jenkins
sudo apt update
sudo apt install jenkins -y

# 5. เริ่มบริการ Jenkins
sudo systemctl enable jenkins
sudo systemctl start jenkins
sudo systemctl status jenkins

# 6. ติดตั้ง Python และ tools
sudo apt install python3 python3-pip python3-venv -y
```

#### CentOS/RHEL/AlmaLinux

```bash
# 1. ติดตั้ง Java
sudo dnf install java-11-openjdk-devel -y

# 2. เพิ่ม Jenkins repository
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key

# 3. ติดตั้ง Jenkins
sudo dnf install jenkins -y

# 4. เริ่มบริการ Jenkins
sudo systemctl enable jenkins
sudo systemctl start jenkins

# 5. ติดตั้ง Python
sudo dnf install python3 python3-pip -y
```

#### Windows

```powershell
# 1. ดาวน์โหลด Jenkins WAR file
Invoke-WebRequest -Uri "https://get.jenkins.io/war-stable/latest/jenkins.war" -OutFile "jenkins.war"

# 2. รัน Jenkins (ต้องมี Java 11+ ติดตั้งแล้ว)
java -jar jenkins.war --httpPort=8080

# หรือใช้ Windows Service Installer
# ดาวน์โหลดจาก: https://www.jenkins.io/download/
```

## 🛠️ การตั้งค่าเบื้องต้น

### 1. เข้าถึง Jenkins Web Interface

```bash
# เปิด browser ไปที่
http://localhost:8081  # ถ้าใช้ Docker
# หรือ
http://localhost:8080  # ถ้าใช้ native installation
```

### 2. Unlock Jenkins

```bash
# ดึงรหัสผ่านเริ่มต้น
# สำหรับ Docker:
docker exec dataops-jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# สำหรับ Native Installation:
# Ubuntu/Debian:
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
# CentOS/RHEL:
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

**ขั้นตอน:**
1. Copy รหัสผ่านจากคำสั่งข้างต้น
2. Paste ในช่อง "Administrator password"
3. คลิก "Continue"

### 3. ติดตั้ง Plugins เริ่มต้น

**เลือก "Install suggested plugins"**

Jenkins จะติดตั้ง plugins พื้นฐาน:
- Git plugin
- GitHub plugin
- Pipeline plugin
- Build Timeout plugin
- Credentials Binding plugin
- และอื่นๆ

**รอการติดตั้ง (5-10 นาที)**

### 4. สร้าง Admin User

```
Username: admin
Password: [รหัสผ่านที่แข็งแกร่ง เช่น DataOps123!]
Confirm Password: [รหัสผ่านเดียวกัน]
Full name: DataOps Administrator
E-mail address: admin@dataops-foundation.local
```

### 5. ตั้งค่า Jenkins URL

```
Jenkins URL: http://localhost:8081/
```

คลิก "Save and Finish"

## 🔌 การติดตั้ง Plugins

### 1. เข้าสู่ Plugin Manager

**Dashboard → Manage Jenkins → Manage Plugins**

### 2. ติดตั้ง Plugins ที่จำเป็นสำหรับ DataOps

#### Essential Plugins:

```
Pipeline Plugins:
☑️ Pipeline
☑️ Pipeline: Stage View
☑️ Blue Ocean (UI ที่สวยกว่า)
☑️ Pipeline Utility Steps

Source Control:
☑️ Git plugin
☑️ GitHub plugin
☑️ GitHub Branch Source plugin

Build & Test:
☑️ Build Timeout plugin
☑️ Timestamper
☑️ Workspace Cleanup plugin
☑️ JUnit plugin
☑️ HTML Publisher plugin

Docker Integration:
☑️ Docker plugin
☑️ Docker Pipeline plugin
☑️ CloudBees Docker Build and Publish plugin

Quality & Security:
☑️ Warnings Next Generation plugin
☑️ Code Coverage API plugin
☑️ SonarQube Scanner plugin

Notifications:
☑️ Email Extension plugin
☑️ Slack Notification plugin

Monitoring:
☑️ Prometheus metrics plugin
☑️ Monitoring plugin
```

#### การติดตั้ง:

1. ไปที่ "Available" tab
2. ค้นหา plugin ที่ต้องการ
3. เลือก checkbox
4. คลิก "Install without restart" (แนะนำ)
5. หรือ "Download now and install after restart"

### 3. Restart Jenkins (หากจำเป็น)

```bash
# สำหรับ Docker:
docker restart dataops-jenkins

# สำหรับ Native Installation:
sudo systemctl restart jenkins
```

## 🔐 การตั้งค่า Credentials

### 1. เข้าสู่ Credentials Manager

**Dashboard → Manage Jenkins → Manage Credentials → System → Global credentials**

### 2. เพิ่ม GitHub Credentials

**คลิก "Add Credentials"**

#### สำหรับ Username/Password:
```
Kind: Username with password
Scope: Global
Username: [GitHub username]
Password: [GitHub Personal Access Token]
ID: github-credentials
Description: GitHub Access for DataOps Foundation
```

#### สำหรับ SSH Key:
```
Kind: SSH Username with private key
Scope: Global
ID: github-ssh-key
Username: git
Private Key: [เพิ่ม SSH private key]
Description: GitHub SSH Key for DataOps Foundation
```

### 3. เพิ่ม Database Credentials

```
Kind: Username with password
Scope: Global
Username: sa
Password: DataOps123!
ID: mssql-credentials
Description: MSSQL Database Credentials
```

### 4. เพิ่ม Docker Hub Credentials (ถ้าใช้)

```
Kind: Username with password
Scope: Global
Username: [Docker Hub username]
Password: [Docker Hub password/token]
ID: dockerhub-credentials
Description: Docker Hub Registry Access
```

### 5. เพิ่ม Email Credentials

```
Kind: Username with password
Scope: Global
Username: [SMTP username]
Password: [SMTP password]
ID: email-credentials
Description: SMTP Email Credentials
```

## 🔄 การสร้าง Pipeline Job

### 1. สร้าง New Job

1. คลิก "New Item" จาก Dashboard
2. ตั้งชื่อ: `dataops-foundation-pipeline`
3. เลือก "Pipeline"
4. คลิก "OK"

### 2. ตั้งค่า General Settings

#### General:
```
☑️ GitHub project
Project url: https://github.com/amornpan/dataops-foundation/

☑️ This project is parameterized (ถ้าต้องการ)
```

#### Build Triggers:
```
☑️ GitHub hook trigger for GITScm polling
☑️ Poll SCM
Schedule: H/5 * * * * (ตรวจสอบทุก 5 นาที)

☑️ Build when a change is pushed to GitHub (ถ้าตั้งค่า webhook)
```

### 3. ตั้งค่า Pipeline

#### Pipeline Definition:
```
Definition: Pipeline script from SCM

SCM: Git
Repository URL: https://github.com/amornpan/dataops-foundation.git
Credentials: [เลือก github-credentials ที่สร้างไว้]

Branches to build:
Branch Specifier: */main
(หรือ */master ขึ้นอยู่กับ default branch)

Repository browser: (auto)

Script Path: jenkins/Jenkinsfile
```

#### Additional Behaviours (Optional):
```
☑️ Clean before checkout
☑️ Checkout to specific local branch
Branch name: main
```

### 4. บันทึกการตั้งค่า

คลิก "Save"

## 🔗 การตั้งค่า GitHub Integration

### 1. สร้าง GitHub Personal Access Token

1. ไปที่ GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. คลิก "Generate new token (classic)"
3. ตั้งชื่อ: `Jenkins DataOps Foundation`
4. เลือก Scopes:
   ```
   ☑️ repo (Full control of private repositories)
   ☑️ admin:repo_hook (Full control of repository hooks)
   ☑️ admin:org_hook (Full control of organization hooks)
   ☑️ user:email (Access user email addresses)
   ```
5. คลิก "Generate token"
6. **Copy token ทันที** (จะแสดงครั้งเดียว)

### 2. ตั้งค่า GitHub Plugin ใน Jenkins

#### ไปที่ Jenkins Configuration:
**Dashboard → Manage Jenkins → Configure System**

#### หา "GitHub" section:
```
GitHub Servers:
API URL: https://api.github.com
Credentials: [เลือก github-credentials]
☑️ Manage hooks
☑️ Override Hook URL

Test connection → คลิกเพื่อทดสอบ
```

### 3. ตั้งค่า Webhook ใน GitHub Repository

#### วิธีที่ 1: Manual Setup

1. ไปที่ GitHub repository: `https://github.com/amornpan/dataops-foundation`
2. Settings → Webhooks → Add webhook
3. ตั้งค่า:
   ```
   Payload URL: http://your-jenkins-server:8081/github-webhook/
   Content type: application/json
   Secret: (ปล่อยว่าง หรือใส่ secret ถ้าต้องการ)
   
   Which events would you like to trigger this webhook?
   ☑️ Just the push event
   ☑️ Pull requests (ถ้าต้องการ)
   
   ☑️ Active
   ```
4. คลิก "Add webhook"

#### วิธีที่ 2: Automatic Setup (ถ้า Jenkins สามารถเข้าถึง GitHub ได้)

Jenkins จะสร้าง webhook อัตโนมัติถ้าตั้งค่า "Manage hooks" ใน GitHub plugin

### 4. ทดสอบ Integration

1. ไปที่ Pipeline job: `dataops-foundation-pipeline`
2. คลิก "Build Now"
3. ตรวจสอบ Console Output
4. ทดสอบโดย push code ใหม่ไปยัง GitHub

## 📧 การตั้งค่า Email Notifications

### 1. ตั้งค่า SMTP ใน Jenkins

**Dashboard → Manage Jenkins → Configure System**

#### หา "E-mail Notification" section:
```
SMTP server: smtp.gmail.com (สำหรับ Gmail)
Default user e-mail suffix: @dataops-foundation.local

☑️ Use SMTP Authentication
User Name: your-email@gmail.com
Password: [App Password สำหรับ Gmail]

☑️ Use SSL
SMTP Port: 465

Reply-To Address: noreply@dataops-foundation.local
Charset: UTF-8
```

#### ทดสอบการตั้งค่า:
```
Test configuration by sending test e-mail
Test e-mail recipient: your-email@gmail.com
→ คลิก "Test configuration"
```

### 2. ตั้งค่า Extended Email Plugin

#### หา "Extended E-mail Notification" section:
```
SMTP server: smtp.gmail.com
SMTP Port: 587
Credentials: [เลือก email-credentials]

☑️ Use STARTTLS
☑️ Require STARTTLS

Default Recipients: admin@dataops-foundation.local
Reply To List: $DEFAULT_REPLYTO
Emergency Recipients: admin@dataops-foundation.local

Default Subject: $PROJECT_NAME - Build # $BUILD_NUMBER - $BUILD_STATUS!
Default Content: 
$PROJECT_NAME - Build # $BUILD_NUMBER - $BUILD_STATUS:

Check console output at $BUILD_URL to view the results.

Build Summary:
- Duration: $BUILD_DURATION  
- Result: $BUILD_STATUS
- Changes: $CHANGES_SINCE_LAST_SUCCESS
```

### 3. ตั้งค่า Email ใน Pipeline

เพิ่มใน Jenkinsfile:

```groovy
post {
    always {
        emailext (
            subject: "DataOps Foundation Build ${currentBuild.result}: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
            body: """
                <h2>DataOps Foundation Pipeline Report</h2>
                <p><strong>Project:</strong> ${env.JOB_NAME}</p>
                <p><strong>Build Number:</strong> ${env.BUILD_NUMBER}</p>
                <p><strong>Build Status:</strong> ${currentBuild.result}</p>
                <p><strong>Build Duration:</strong> ${currentBuild.durationString}</p>
                
                <h3>Changes:</h3>
                <p>${env.CHANGE_LOG}</p>
                
                <p><a href="${env.BUILD_URL}">View Build Details</a></p>
                <p><a href="${env.BUILD_URL}console">View Console Output</a></p>
            """,
            mimeType: 'text/html',
            to: 'admin@dataops-foundation.local',
            recipientProviders: [
                buildUser(),
                developers(),
                requestor()
            ]
        )
    }
    
    failure {
        emailext (
            subject: "🚨 DataOps Foundation Build FAILED: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
            body: """
                <h2 style="color: red;">Build Failed!</h2>
                <p>The DataOps Foundation pipeline has failed.</p>
                <p><strong>Project:</strong> ${env.JOB_NAME}</p>
                <p><strong>Build Number:</strong> ${env.BUILD_NUMBER}</p>
                <p><strong>Failed Stage:</strong> Check console output</p>
                
                <p><strong>Console Output:</strong></p>
                <pre>${env.BUILD_LOG}</pre>
                
                <p><a href="${env.BUILD_URL}">View Build Details</a></p>
            """,
            mimeType: 'text/html',
            to: 'admin@dataops-foundation.local'
        )
    }
}
```

## 🔄 การทดสอบ Pipeline

### 1. Manual Build Test

1. ไปที่ Pipeline job
2. คลิก "Build Now"
3. ดู "Stage View" เพื่อติดตามความคืบหน้า
4. คลิก Console Output เพื่อดู logs แบบละเอียด

### 2. Automatic Build Test

1. ทำการแก้ไขไฟล์ใดๆ ใน repository
2. Commit และ push ไปยัง GitHub:
   ```bash
   git add .
   git commit -m "Test Jenkins trigger"
   git push origin main
   ```
3. ตรวจสอบว่า Jenkins ได้รับ webhook และเริ่ม build อัตโนมัติ

### 3. การตรวจสอบผลลัพธ์

#### Successful Build:
```
✅ ทุก Stage สำเร็จ (สีเขียว)
✅ ได้รับ email notification
✅ Artifacts ถูกสร้างและเก็บไว้
✅ Test results แสดงผล
```

#### Failed Build:
```
❌ Stage ที่ล้มเหลวแสดงสีแดง
❌ Console output แสดง error details
❌ ได้รับ failure email notification
❌ Build history แสดงสถานะ FAILED
```

## 🛠️ การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

#### 1. Python ไม่พบใน Jenkins

**อาการ:** `python: command not found`

**วิธีแก้:**
```bash
# สำหรับ Docker (rebuild image):
docker build -f docker/Dockerfile.jenkins -t dataops-jenkins .
docker stop dataops-jenkins && docker rm dataops-jenkins
docker run -d --name dataops-jenkins -p 8081:8080 -v jenkins-data:/var/jenkins_home dataops-jenkins

# สำหรับ Native Installation:
sudo apt install python3 python3-pip python3-venv -y
# แล้วเพิ่ม symbolic link:
sudo ln -s /usr/bin/python3 /usr/bin/python
```

#### 2. Git Credentials ไม่ทำงาน

**อาการ:** `Authentication failed` เมื่อ clone repository

**วิธีแก้:**
1. ตรวจสอบ Personal Access Token ยังใช้ได้
2. ตรวจสอบ Scopes ของ token
3. Update credentials ใน Jenkins:
   ```
   Dashboard → Manage Jenkins → Manage Credentials
   → เลือก credential → Update
   ```

#### 3. Webhook ไม่ทำงาน

**อาการ:** Jenkins ไม่ auto-build เมื่อ push code

**วิธีแก้:**
1. ตรวจสอบ Webhook URL:
   ```
   GitHub → Settings → Webhooks
   URL ต้องเป็น: http://your-server:8081/github-webhook/
   ```

2. ตรวจสอบ Recent Deliveries ใน GitHub Webhook

3. ตรวจสอบ Jenkins logs:
   ```bash
   docker logs dataops-jenkins | grep webhook
   ```

#### 4. Docker Permission Error

**อาการ:** `permission denied while trying to connect to the Docker daemon socket`

**วิธีแก้:**
```bash
# เพิ่ม jenkins user เข้า docker group:
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins

# หรือสำหรับ Docker container:
docker exec -u root dataops-jenkins usermod -aG docker jenkins
docker restart dataops-jenkins
```

#### 5. Email Notification ไม่ส่ง

**อาการ:** Email ไม่ถูกส่งหลัง build

**วิธีแก้:**
1. ทดสอบ SMTP configuration ใน Jenkins
2. ตรวจสอบ App Password สำหรับ Gmail:
   ```
   Google Account → Security → 2-Step Verification → App passwords
   ```
3. ตรวจสอบ firewall rules สำหรับ SMTP ports (587, 465)

#### 6. Pipeline Script Error

**อาการ:** `Pipeline script not found` หรือ syntax error

**วิธีแก้:**
1. ตรวจสอบ path ของ Jenkinsfile:
   ```
   ต้องอยู่ที่: jenkins/Jenkinsfile
   ```

2. Validate Jenkinsfile syntax:
   ```
   Dashboard → Pipeline job → Pipeline Syntax
   ```

3. ตรวจสอบ branch ที่ใช้:
   ```
   ตรวจสอบว่า Jenkinsfile อยู่ใน branch ที่ Jenkins กำลัง build
   ```

### การติดตาม Logs

#### Jenkins System Logs:
```bash
# Docker:
docker logs -f dataops-jenkins

# Native:
sudo tail -f /var/log/jenkins/jenkins.log
```

#### Build Logs:
```
Dashboard → Pipeline job → Build Number → Console Output
```

#### Plugin Logs:
```
Dashboard → Manage Jenkins → System Log → All Jenkins Logs
```

## 📋 Checklist การตั้งค่า Jenkins

### ✅ Pre-Installation
- [ ] ติดตั้ง Java 11+
- [ ] ติดตั้ง Docker (ถ้าใช้)
- [ ] เตรียม GitHub Personal Access Token
- [ ] เตรียม SMTP credentials

### ✅ Jenkins Installation
- [ ] ติดตั้ง Jenkins สำเร็จ
- [ ] เข้าถึง Web UI ได้
- [ ] สร้าง Admin user แล้ว
- [ ] ติดตั้ง essential plugins แล้ว

### ✅ Configuration
- [ ] เพิ่ม GitHub credentials
- [ ] เพิ่ม Database credentials  
- [ ] เพิ่ม Email credentials
- [ ] ตั้งค่า SMTP
- [ ] ตั้งค่า GitHub plugin

### ✅ Pipeline Setup
- [ ] สร้าง Pipeline job
- [ ] ตั้งค่า Git repository
- [ ] ตั้งค่า build triggers
- [ ] ตั้งค่า Jenkinsfile path

### ✅ GitHub Integration
- [ ] สร้าง webhook ใน GitHub
- [ ] ทดสอบ manual build
- [ ] ทดสอบ automatic trigger
- [ ] ตรวจสอบ webhook deliveries

### ✅ Testing & Monitoring
- [ ] ทดสอบ full pipeline
- [ ] ตรวจสอบ email notifications
- [ ] ตรวจสอบ artifacts
- [ ] ตรวจสอบ test results

## 🚀 Next Steps

หลังจากตั้งค่า Jenkins เสร็จ:

1. **ทดสอบ Full Pipeline:**
   ```bash
   # Push code changes เพื่อทดสอบ auto-trigger
   git add .
   git commit -m "Test Jenkins pipeline"
   git push origin main
   ```

2. **ตั้งค่า Branch Protection Rules ใน GitHub:**
   ```
   Settings → Branches → Add rule
   ☑️ Require status checks to pass before merging
   ☑️ Require branches to be up to date before merging
   Status checks: continuous-integration/jenkins
   ```

3. **ตั้งค่า Slack Notifications (Optional):**
   - ติดตั้ง Slack Notification plugin
   - เพิ่ม Slack webhook
   - เพิ่ม notification ใน Jenkinsfile

4. **Monitor และ Optimize:**
   - ติดตาม build performance
   - ปรับ build triggers ตามความเหมาะสม
   - เพิ่ม parallel stages ถ้าจำเป็น

---

**Jenkins Setup เสร็จสมบูรณ์! 🎉**

สำหรับข้อมูลเพิ่มเติม ดูที่:
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [GitHub Plugin Documentation](https://plugins.jenkins.io/github/)
