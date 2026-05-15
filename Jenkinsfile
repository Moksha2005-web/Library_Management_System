pipeline {
agent any

```
options {
    timestamps()
    timeout(time: 20, unit: 'MINUTES')
}

environment {
    IMAGE_NAME = "library-ms"
    CONTAINER_NAME = "library-ms-app"
}

stages {

    stage('Checkout') {
        steps {
            echo 'Checking out source code...'
            checkout scm
        }
    }

    stage('Docker Build') {
        steps {
            echo 'Building Docker image...'

            powershell '''
            docker build -t $env:IMAGE_NAME .
            '''
        }
    }

    stage('Stop Old Container') {
        steps {
            echo 'Stopping old container if exists...'

            powershell '''
            docker stop $env:CONTAINER_NAME 2>$null
            docker rm $env:CONTAINER_NAME 2>$null
            '''
        }
    }

    stage('Deploy Container') {
        steps {
            echo 'Deploying application container...'

            powershell '''
            docker run -d --name $env:CONTAINER_NAME -p 5000:5000 $env:IMAGE_NAME
            '''
        }
    }

    stage('Verify Deployment') {
        steps {
            echo 'Verifying deployment...'

            powershell '''
            docker ps
            '''
        }
    }
}

post {

    success {
        echo 'Pipeline completed successfully!'
    }

    failure {
        echo 'Pipeline FAILED!'
    }

    always {
        echo 'Cleaning workspace...'
        cleanWs()
    }
}
```

}
