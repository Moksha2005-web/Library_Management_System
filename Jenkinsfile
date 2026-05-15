// ============================================================
//  Library Management System - Jenkins CI/CD Pipeline
//  Windows-compatible (bat commands + explicit Python path)
// ============================================================
 
pipeline {
    agent any
 
    environment {
        APP_NAME      = 'library-ms'
        DOCKER_IMAGE  = "library-ms:${BUILD_NUMBER}"
        DOCKER_LATEST = 'library-ms:latest'
        // Update PYTHON_HOME to match your installation path
        // Run 'where.exe python' in PowerShell to find yours
        PYTHON_HOME   = 'C:\\Users\\rajan\\AppData\\Local\\Programs\\Python\\Python311'
    }
 
    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 20, unit: 'MINUTES')
    }
 
    stages {
 
        // 1. Checkout
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
                bat 'git log --oneline -5'
            }
        }
 
        // 2. Setup Python Environment
        stage('Setup Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                bat """
                    set PATH=%PYTHON_HOME%;%PYTHON_HOME%\\Scripts;%PATH%
                    python --version
                    python -m venv venv
                    call venv\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }
 
        // 3. Lint
        stage('Lint') {
            steps {
                echo 'Running flake8 linting...'
                bat """
                    set PATH=%PYTHON_HOME%;%PYTHON_HOME%\\Scripts;%PATH%
                    call venv\\Scripts\\activate.bat
                    pip install flake8 --quiet
                    python -m flake8 app/ run.py --max-line-length=120 --exclude=venv,__pycache__ --statistics
                """
            }
        }
 
        // 4. Unit Tests
        stage('Unit Tests') {
            steps {
                echo 'Running unit tests with pytest...'
                bat """
                    set PATH=%PYTHON_HOME%;%PYTHON_HOME%\\Scripts;%PATH%
                    if not exist reports mkdir reports
                    call venv\\Scripts\\activate.bat
                    set PYTHONPATH=%CD%
                    pytest tests/ -v --tb=short --junitxml=reports/test-results.xml
                """
            }
            post {
                always {
                    junit allowEmptyResults: true,
                          testResults: 'reports/test-results.xml'
                }
            }
        }
 
        // 5. Docker Build
        stage('Docker Build') {
            steps {
                echo "Building Docker image: ${DOCKER_IMAGE}"
                bat """
                    docker build ^
                        --tag ${DOCKER_IMAGE} ^
                        --tag ${DOCKER_LATEST} ^
                        --label build.number=${BUILD_NUMBER} ^
                        .
                """
            }
        }
 
        // 6. Image Verification
        stage('Image Verification') {
            steps {
                echo 'Verifying Docker image health...'
                bat """
                    docker run -d --name test-container-${BUILD_NUMBER} -p 5001:5000 ${DOCKER_IMAGE}
                    timeout /t 10 /nobreak
                    curl -f http://localhost:5001/health
                    echo Health check passed!
                """
            }
            post {
                always {
                    bat """
                        docker stop test-container-${BUILD_NUMBER} || exit /b 0
                        docker rm   test-container-${BUILD_NUMBER} || exit /b 0
                    """
                }
            }
        }
 
        // 7. Push to Registry (main branch only)
        stage('Push to Registry') {
            when { branch 'main' }
            steps {
                echo 'Skipping push - configure Docker Hub credentials to enable'
            }
        }
 
        // 8. Deploy
        stage('Deploy') {
            when { branch 'main' }
            steps {
                echo 'Deploying with Docker Compose...'
                bat '''
                    docker-compose down --remove-orphans || exit /b 0
                    docker-compose up -d app
                    timeout /t 10 /nobreak
                    docker-compose ps
                '''
            }
        }
    }
 
    post {
        always {
            echo 'Cleaning up workspace...'
            bat '''
                if exist venv rmdir /s /q venv || exit /b 0
                docker image prune -f || exit /b 0
            '''
        }
        success {
            echo 'Pipeline completed SUCCESSFULLY!'
        }
        failure {
            echo 'Pipeline FAILED!'
        }
    }
}
