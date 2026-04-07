pipeline {
    agent any

    environment {
        REGISTRY  = "your-dockerhub-username/myapp"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Pulling latest code from GitHub..."
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "Installing Python dependencies..."
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate.bat
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                echo "Running unit tests..."
                bat '''
                    call venv\\Scripts\\activate.bat
                    pytest test_app.py -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker image..."
                bat "docker build -t %REGISTRY%:%IMAGE_TAG% ."
                bat "docker tag %REGISTRY%:%IMAGE_TAG% %REGISTRY%:latest"
            }
        }

        stage('Push to DockerHub') {
            steps {
                echo "Pushing to DockerHub..."
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat "echo %DOCKER_PASS%| docker login -u %DOCKER_USER% --password-stdin"
                    bat "docker push %REGISTRY%:%IMAGE_TAG%"
                    bat "docker push %REGISTRY%:latest"
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline SUCCESS! Build #${BUILD_NUMBER} done."
        }
        failure {
            echo "Pipeline FAILED. Check logs above."
        }
        always {
            bat "docker rmi %REGISTRY%:%IMAGE_TAG% || exit 0"
        }
    }
}