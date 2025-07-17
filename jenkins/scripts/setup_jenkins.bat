@echo off
REM Jenkins Setup Helper Script for Windows
REM สคริปต์ช่วยตั้งค่า Jenkins สำหรับ DataOps Foundation บน Windows

echo ================================================== 
echo 🔧 DataOps Foundation Jenkins Setup Helper (Windows)
echo ==================================================

REM Check if Docker is installed
echo [STEP] Checking prerequisites...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)
echo [SUCCESS] Docker is installed

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)
echo [SUCCESS] Docker Compose is installed

REM Check if we're in the right directory
if not exist "docker\Dockerfile.jenkins" (
    echo [ERROR] DataOps Foundation project not found. Please run this script from the project root.
    pause
    exit /b 1
)
echo [SUCCESS] All prerequisites are met

REM Create .env file if not exists
echo [STEP] Setting up environment...
if not exist ".env" (
    echo Creating .env file with default values...
    (
        echo # Jenkins Configuration
        echo JENKINS_ADMIN_PASSWORD=DataOps123!
        echo JENKINS_URL=http://localhost:8081/
        echo.
        echo # GitHub Configuration
        echo GITHUB_USERNAME=your-github-username
        echo GITHUB_TOKEN=your-github-token
        echo.
        echo # Database Configuration
        echo DB_USERNAME=sa
        echo DB_PASSWORD=DataOps123!
        echo.
        echo # Email Configuration
        echo SMTP_HOST=smtp.gmail.com
        echo SMTP_PORT=587
        echo SMTP_USERNAME=your-email@gmail.com
        echo SMTP_PASSWORD=your-app-password
        echo.
        echo # Docker Hub Configuration
        echo DOCKERHUB_USERNAME=your-dockerhub-username
        echo DOCKERHUB_TOKEN=your-dockerhub-token
    ) > .env
    echo [WARNING] Created .env file with default values. Please update it with your actual credentials.
    echo [WARNING] Edit .env file and then press any key to continue...
    pause
) else (
    echo [SUCCESS] .env file already exists
)

REM Build Jenkins image
echo [STEP] Building Jenkins Docker image with Python and DataOps tools...
docker build -f docker\Dockerfile.jenkins -t dataops-jenkins .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build Jenkins image
    pause
    exit /b 1
)
echo [SUCCESS] Jenkins image built successfully

REM Create Docker network
echo [STEP] Creating Docker network...
docker network ls | findstr "dataops-network" >nul 2>&1
if %errorlevel% neq 0 (
    docker network create dataops-network
    echo [SUCCESS] Docker network 'dataops-network' created
) else (
    echo [SUCCESS] Docker network 'dataops-network' already exists
)

REM Stop existing Jenkins container if running
echo [STEP] Starting Jenkins container...
docker ps -a | findstr "dataops-jenkins" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] Stopping existing Jenkins container...
    docker stop dataops-jenkins >nul 2>&1
    docker rm dataops-jenkins >nul 2>&1
)

REM Start Jenkins container
docker run -d ^
    --name dataops-jenkins ^
    --network dataops-network ^
    -p 8081:8080 ^
    -p 50000:50000 ^
    -v jenkins-data:/var/jenkins_home ^
    -v /var/run/docker.sock:/var/run/docker.sock ^
    -v "%cd%":/workspace ^
    --env-file .env ^
    -e TZ=Asia/Bangkok ^
    -e JAVA_OPTS="-Djenkins.install.runSetupWizard=false" ^
    -e CASC_JENKINS_CONFIG="/var/jenkins_home/casc_configs/jenkins.yaml" ^
    --restart unless-stopped ^
    dataops-jenkins

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Jenkins container
    pause
    exit /b 1
)
echo [SUCCESS] Jenkins container started

REM Wait for Jenkins to start
echo [STEP] Waiting for Jenkins to start...
timeout /t 30 /nobreak >nul

REM Try to get initial password
echo [STEP] Getting Jenkins initial admin password...
timeout /t 10 /nobreak >nul

docker exec dataops-jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>nul > temp_password.txt
if %errorlevel% equ 0 (
    echo ==================================================
    echo 🔑 Jenkins Initial Admin Password:
    type temp_password.txt
    echo ==================================================
    del temp_password.txt
) else (
    echo [WARNING] Initial password not found (Jenkins may be using Configuration as Code)
    echo [WARNING] Default admin credentials:
    echo    Username: admin
    echo    Password: DataOps123!
)

REM Display access information
echo.
echo ==================================================
echo 🚀 DataOps Foundation Jenkins Setup Complete!
echo ==================================================
echo.
echo 📋 Access Information:
echo    🌐 Jenkins URL: http://localhost:8081
echo    👤 Username: admin
echo    🔐 Password: DataOps123! (or see above)
echo.
echo 📊 Additional Services:
echo    🎯 Prometheus: http://localhost:9090 (if running full stack)
echo    📈 Grafana: http://localhost:3000 (admin/DataOps123!)
echo.
echo 🔧 Next Steps:
echo    1. Access Jenkins at http://localhost:8081
echo    2. Log in with admin credentials
echo    3. Update GitHub credentials in Jenkins
echo    4. Test the DataOps Foundation pipeline
echo    5. Configure GitHub webhooks
echo.
echo 📚 Documentation:
echo    📖 Jenkins Setup: docs\jenkins-setup.md
echo    🚀 Quick Start: docs\quick-start.md
echo.
echo 🛠️ Useful Commands:
echo    View logs: docker logs -f dataops-jenkins
echo    Restart: docker restart dataops-jenkins
echo    Stop: docker stop dataops-jenkins
echo    Full stack: docker-compose -f docker\docker-compose.yml up -d
echo.

echo 🔧 Troubleshooting:
echo.
echo 1. If Jenkins doesn't start:
echo    docker logs dataops-jenkins
echo.
echo 2. If port 8081 is busy:
echo    netstat -ano ^| findstr :8081
echo    # Kill the process using the port
echo.
echo 3. If Python not found in Jenkins:
echo    docker exec dataops-jenkins python3 --version
echo    # Should show Python 3.11+
echo.
echo 4. To restart everything:
echo    docker stop dataops-jenkins && docker rm dataops-jenkins
echo    jenkins\scripts\setup_jenkins.bat
echo.

echo [SUCCESS] Jenkins setup completed successfully! 🎉
echo.
echo Press any key to open Jenkins in your browser...
pause
start http://localhost:8081
