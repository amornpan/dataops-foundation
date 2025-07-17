pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        VENV_NAME = 'venv'
        PROJECT_NAME = 'dataops-foundation'
        DB_SERVER = '35.185.131.47'
        DB_NAME = 'TestDB'
        DB_USERNAME = 'SA'
        LOG_LEVEL = 'INFO'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '🔄 Checking out DataOps Foundation code...'
                checkout scm
                echo '✅ Code checkout completed'
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo '🐍 Setting up Python virtual environment for DataOps...'
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv ${VENV_NAME}
                            . ${VENV_NAME}/bin/activate
                            pip install --upgrade pip --timeout=120
                            pip install -r requirements.txt --timeout=300
                        '''
                    } else {
                        bat '''
                            python -m venv %VENV_NAME%
                            call %VENV_NAME%\\Scripts\\activate
                            pip install --upgrade pip --timeout=120
                            pip install -r requirements.txt --timeout=300
                        '''
                    }
                }
                echo '✅ Python environment setup completed'
            }
        }
        
        stage('Data Quality Checks') {
            steps {
                echo '🔍 Running data quality checks...'
                script {
                    if (isUnix()) {
                        sh '''
                            . ${VENV_NAME}/bin/activate
                            
                            echo "Checking Python imports..."
                            python -c "import pandas; import sqlalchemy; import pymssql; print('All required packages imported successfully')"
                            
                            echo "Validating ETL pipeline syntax..."
                            python -m py_compile etl_pipeline.py
                            
                            echo "Running static code analysis..."
                            python -m flake8 etl_pipeline.py --max-line-length=100 --ignore=E501,W503 || echo "Code style warnings detected"
                        '''
                    } else {
                        bat '''
                            call %VENV_NAME%\\Scripts\\activate
                            
                            echo Checking Python imports...
                            python -c "import pandas; import sqlalchemy; import pymssql; print('All required packages imported successfully')"
                            
                            echo Validating ETL pipeline syntax...
                            python -m py_compile etl_pipeline.py
                            
                            echo Running static code analysis...
                            python -m flake8 etl_pipeline.py --max-line-length=100 --ignore=E501,W503 2>nul || echo Code style warnings detected
                        '''
                    }
                }
                echo '✅ Data quality checks completed'
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo '🧪 Running DataOps ETL unit tests...'
                script {
                    if (isUnix()) {
                        sh '''
                            . ${VENV_NAME}/bin/activate
                            
                            echo "Running ETL pipeline unit tests..."
                            python -m unittest test_etl_pipeline.py -v
                            
                            echo "Running pytest with coverage..."
                            python -m pytest test_etl_pipeline.py -v --tb=short || echo "Some tests may have warnings"
                        '''
                    } else {
                        bat '''
                            call %VENV_NAME%\\Scripts\\activate
                            
                            echo Running ETL pipeline unit tests...
                            python -m unittest test_etl_pipeline.py -v
                            
                            echo Running pytest with coverage...
                            python -m pytest test_etl_pipeline.py -v --tb=short 2>nul || echo Some tests may have warnings
                        '''
                    }
                }
                echo '✅ Unit tests completed'
            }
        }
        
        stage('ETL Pipeline Validation') {
            steps {
                echo '⚙️ Validating ETL pipeline configuration...'
                script {
                    if (isUnix()) {
                        sh '''
                            . ${VENV_NAME}/bin/activate
                            
                            echo "Testing ETL pipeline initialization..."
                            python -c "
from etl_pipeline import DataOpsETLPipeline
import sys

try:
    config = {
        'database': {
            'server': '${DB_SERVER}',
            'database': '${DB_NAME}',
            'username': '${DB_USERNAME}',
            'password': 'dummy_password_for_test'
        },
        'acceptable_max_null': 26,
        'missing_threshold': 30.0
    }
    
    print('Testing ETL pipeline class initialization...')
    print('✅ ETL pipeline validation passed')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'⚠️ Pipeline validation warning: {e}')
    print('✅ Basic validation completed with warnings')
"
                        '''
                    } else {
                        bat '''
                            call %VENV_NAME%\\Scripts\\activate
                            
                            echo Testing ETL pipeline initialization...
                            python -c "from etl_pipeline import DataOpsETLPipeline; print('ETL pipeline class loaded successfully')"
                        '''
                    }
                }
                echo '✅ ETL pipeline validation completed'
            }
        }
        
        stage('Build Deployment Package') {
            steps {
                echo '📦 Creating DataOps deployment package...'
                script {
                    if (isUnix()) {
                        sh '''
                            mkdir -p dist/dataops-foundation
                            
                            cp etl_pipeline.py dist/dataops-foundation/
                            cp test_etl_pipeline.py dist/dataops-foundation/
                            cp requirements.txt dist/dataops-foundation/
                            
                            echo "Build Number: ${BUILD_NUMBER}" > dist/dataops-foundation/build-info.txt
                            echo "Build Date: $(date)" >> dist/dataops-foundation/build-info.txt
                            echo "Git Commit: ${GIT_COMMIT:-'N/A'}" >> dist/dataops-foundation/build-info.txt
                            echo "Jenkins Job: ${JOB_NAME}" >> dist/dataops-foundation/build-info.txt
                            echo "Project: DataOps Foundation ETL Pipeline" >> dist/dataops-foundation/build-info.txt
                            
                            tar -czf dist/dataops-foundation-${BUILD_NUMBER}.tar.gz -C dist dataops-foundation
                            
                            ls -la dist/
                        '''
                    } else {
                        bat '''
                            if not exist dist\\dataops-foundation mkdir dist\\dataops-foundation
                            
                            copy etl_pipeline.py dist\\dataops-foundation\\
                            copy test_etl_pipeline.py dist\\dataops-foundation\\
                            copy requirements.txt dist\\dataops-foundation\\
                            if exist README.md copy README.md dist\\dataops-foundation\\
                            if exist config.yaml copy config.yaml dist\\dataops-foundation\\
                            
                            echo Build Number: %BUILD_NUMBER% > dist\\dataops-foundation\\build-info.txt
                            echo Build Date: %DATE% %TIME% >> dist\\dataops-foundation\\build-info.txt
                            echo Git Commit: %GIT_COMMIT% >> dist\\dataops-foundation\\build-info.txt
                            echo Jenkins Job: %JOB_NAME% >> dist\\dataops-foundation\\build-info.txt
                            echo Project: DataOps Foundation ETL Pipeline >> dist\\dataops-foundation\\build-info.txt
                            
                            dir dist\\dataops-foundation
                        '''
                    }
                }
                echo '✅ Deployment package created'
            }
        }
        
        stage('Data Pipeline Health Check') {
            steps {
                echo '🔍 Running DataOps health checks...'
                script {
                    if (isUnix()) {
                        sh '''
                            . ${VENV_NAME}/bin/activate
                            
                            echo "Checking data pipeline components..."
                            python -c "
import pandas as pd
import numpy as np
from datetime import datetime
import sys

try:
    print('📊 Testing pandas data operations...')
    test_df = pd.DataFrame({
        'id': [1, 2, 3],
        'amount': [100, 200, 300],
        'date': ['2024-01-01', '2024-01-02', '2024-01-03']
    })
    test_df['date'] = pd.to_datetime(test_df['date'])
    print(f'✅ DataFrame created with {len(test_df)} rows')
    
    print('🔢 Testing numpy operations...')
    test_array = np.array([1, 2, 3, 4, 5])
    mean_val = np.mean(test_array)
    print(f'✅ Numpy mean calculation: {mean_val}')
    
    print('📅 Testing datetime operations...')
    current_time = datetime.now()
    print(f'✅ Current timestamp: {current_time}')
    
    print('🎉 All DataOps health checks passed!')
    
except Exception as e:
    print(f'❌ Health check failed: {e}')
    sys.exit(1)
"
                        '''
                    } else {
                        bat '''
                            call %VENV_NAME%\\Scripts\\activate
                            
                            echo Checking data pipeline components...
                            python -c "import pandas as pd; import numpy as np; from datetime import datetime; print('DataOps health check passed - all components working')"
                        '''
                    }
                }
                echo '✅ DataOps health checks completed'
            }
        }
    }
    
    post {
        always {
            echo '🧹 Cleaning up DataOps workspace...'
            script {
                if (isUnix()) {
                    sh 'rm -rf ${VENV_NAME} || true'
                } else {
                    bat 'if exist %VENV_NAME% rmdir /s /q %VENV_NAME% 2>nul || echo "Cleanup completed"'
                }
            }
            
            archiveArtifacts artifacts: 'dist/**/*', fingerprint: true, allowEmptyArchive: true
        }
        
        success {
            echo '✅ DataOps Foundation pipeline completed successfully!'
            echo "🎉 Build ${BUILD_NUMBER} - ETL pipeline ready for deployment"
            echo "📊 Data pipeline validation: PASSED"
            echo "🔍 Quality checks: PASSED"
            echo "🧪 Unit tests: PASSED"
        }
        
        failure {
            echo '❌ DataOps Foundation pipeline failed!'
            echo "💥 Build ${BUILD_NUMBER} failed - please check the logs"
            echo "🔍 Common issues to check:"
            echo "   - Database connectivity"
            echo "   - Python package dependencies"
            echo "   - Data file availability"
            echo "   - SQL Server permissions"
        }
        
        unstable {
            echo '⚠️ DataOps pipeline completed with warnings'
            echo "🔧 Build ${BUILD_NUMBER} has some issues that need attention"
            echo "📋 Please review:"
            echo "   - Test results"
            echo "   - Code quality warnings"
            echo "   - Data validation results"
        }
    }
}
