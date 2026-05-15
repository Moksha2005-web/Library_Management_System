// ============================================================
//  Library Management System – Jenkins CI/CD Pipeline
//  Stages: Checkout → Install → Lint → Test → Build → Push → Deploy
// ============================================================
 
pipeline {
    agent any
 
    environment {
        APP_NAME        = 'library-ms'
        DOCKER_IMAGE    = "library-ms:${BUILD_NUMBER}"
        DOCKER_LATEST   = 'library-ms:latest'
        // Set DOCKER_HUB_CREDENTIALS in Jenkins Credentials store
        // DOCKER_HUB_USER = credentials('docker-hub-user')
    }
 
    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 20, unit: 'MINUTES')
    }
 
    stages {
 
        // ── 1. Checkout ───────────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥  Checking out source code...'
                checkout scm
                sh 'git log --oneline -5'
            }
        }
 
        // ── 2. Set up Python environment ──────────────────────────────────────
        stage('Setup Environment') {
            steps {
                echo '🐍  Setting up Python virtual environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
 
        // ── 3. Lint ───────────────────────────────────────────────────────────
        stage('Lint') {
            steps {
                echo '🔍  Running code linting...'
                sh '''
                    . venv/bin/activate
                    pip install flake8 --quiet
                    flake8 app/ run.py --max-line-length=120 \
                        --exclude=venv,__pycache__ \
                        --statistics || true
                '''
            }
        }
 
        // ── 4. Unit Tests ─────────────────────────────────────────────────────
        stage('Unit Tests') {
            steps {
                echo '🧪  Running unit tests with pytest...'
                sh '''
                    . venv/bin/activate
                    pytest tests/ -v \
                        --tb=short \
                        --junitxml=reports/test-results.xml \
                        --html=reports/test-report.html \
                        --self-contained-html || true
                '''
            }
            post {
                always {
                    // Publish JUnit test results in Jenkins
                    junit allowEmptyResults: true,
                          testResults: 'reports/test-results.xml'
                }
            }
        }
 
        // ── 5. Docker Build ───────────────────────────────────────────────────
        stage('Docker Build') {
            steps {
                echo "🐳  Building Docker image: ${DOCKER_IMAGE}"
                sh """
                    docker build \
                        --target runtime \
                        --tag ${DOCKER_IMAGE} \
                        --tag ${DOCKER_LATEST} \
                        --label "build.number=${BUILD_NUMBER}" \
                        --label "build.url=${BUILD_URL}" \
                        .
                """
            }
        }
 
        // ── 6. Docker Image Verification ──────────────────────────────────────
        stage('Image Verification') {
            steps {
                echo '✅  Verifying Docker image health...'
                sh """
                    # Start container in background
                    docker run -d --name test-container-${BUILD_NUMBER} \
                        -p 5001:5000 \
                        ${DOCKER_IMAGE}
 
                    # Wait for container to start
                    sleep 8
 
                    # Check health endpoint
                    curl -f http://localhost:5001/health || \
                        (docker logs test-container-${BUILD_NUMBER} && exit 1)
 
                    echo 'Health check passed!'
                """
            }
            post {
                always {
                    sh "docker stop test-container-${BUILD_NUMBER} || true"
                    sh "docker rm  test-container-${BUILD_NUMBER} || true"
                }
            }
        }
 
        // ── 7. Push to Registry (only on main branch) ─────────────────────────
        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                echo '📤  Pushing image to Docker Hub...'
                // Uncomment and configure Docker Hub credentials in Jenkins:
                // withCredentials([usernamePassword(
                //     credentialsId: 'docker-hub-credentials',
                //     usernameVariable: 'DOCKER_USER',
                //     passwordVariable: 'DOCKER_PASS'
                // )]) {
                //     sh """
                //         echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                //         docker tag ${DOCKER_IMAGE} $DOCKER_USER/${APP_NAME}:${BUILD_NUMBER}
                //         docker tag ${DOCKER_IMAGE} $DOCKER_USER/${APP_NAME}:latest
                //         docker push $DOCKER_USER/${APP_NAME}:${BUILD_NUMBER}
                //         docker push $DOCKER_USER/${APP_NAME}:latest
                //     """
                // }
                echo 'Skipping push (configure Docker Hub credentials to enable)'
            }
        }
 
        // ── 8. Deploy ─────────────────────────────────────────────────────────
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo '🚀  Deploying application with Docker Compose...'
                sh '''
                    # Stop existing containers gracefully
                    docker-compose down --remove-orphans || true
 
                    # Deploy updated image
                    docker-compose up -d app
 
                    # Wait and verify
                    sleep 10
                    docker-compose ps
                    docker-compose logs --tail=20 app
                '''
            }
        }
    }
 
    // ── Post Actions ──────────────────────────────────────────────────────────
    post {
        always {
            echo '🧹  Cleaning up workspace...'
            sh 'rm -rf venv || true'
            // Remove dangling images
            sh 'docker image prune -f || true'
        }
        success {
            echo '✅  Pipeline completed SUCCESSFULLY!'
            // emailext(
            //     subject: "✅ Build #${BUILD_NUMBER} – ${APP_NAME} PASSED",
            //     body: "Build ${BUILD_URL} succeeded.",
            //     to: 'team@example.com'
            // )
        }
        failure {
            echo '❌  Pipeline FAILED!'
            // emailext(
            //     subject: "❌ Build #${BUILD_NUMBER} – ${APP_NAME} FAILED",
            //     body: "Build ${BUILD_URL} failed.",
            //     to: 'team@example.com'
            // )
        }
    }
}
