@echo off
REM Script to initialize Git repository and push to GitHub

echo 🚀 Initializing DataOps Foundation Git Repository
echo ==================================================

REM Initialize git repository if not exists
if not exist ".git" (
    echo 📦 Initializing Git repository...
    git init
    git branch -M main
) else (
    echo ✅ Git repository already exists
)

REM Add all files
echo 📁 Adding files to Git...
git add .

REM Create initial commit
echo 💾 Creating initial commit...
git commit -m "🚀 Initial commit: DataOps Foundation v1.0.0 - Features: Enhanced ETL Processor, Jenkins CI/CD Pipeline, Data Quality Framework, Monitoring System, Docker Support, Comprehensive Testing - Ready for production! 🎉"

REM Instructions for GitHub setup
echo.
echo 🔗 Next Steps for GitHub Setup:
echo ================================
echo.
echo 1. Create new repository on GitHub:
echo    - Go to: https://github.com/new
echo    - Repository name: dataops-foundation
echo    - Description: 🚀 Enterprise DataOps platform for modern data engineering
echo    - Make it Public
echo    - DO NOT initialize with README (we already have one)
echo.
echo 2. Add GitHub remote and push:
echo    git remote add origin https://github.com/amornpan/dataops-foundation.git
echo    git push -u origin main
echo.
echo 3. Verify Jenkinsfile is in root directory:
echo    - Check: https://github.com/amornpan/dataops-foundation/blob/main/jenkins/Jenkinsfile
echo.
echo 4. Update Jenkins pipeline configuration:
echo    - Script Path: jenkins/Jenkinsfile
echo    - Or move Jenkinsfile to root: move jenkins\Jenkinsfile .
echo.

pause
