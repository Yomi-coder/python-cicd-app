pipeline {
    agent any

    environment {
        APP_NAME  = "myapp"
        REGISTRY  = "yourdockerhub/myapp"
        IMAGE_TAG = "${BUILD_NUMBER}"
        PYTHON = "C:\\Users\\admin\\AppData\\Local\\Python\\bin\\python.exe"
    }

    stages {

        // -----------------------------------------------
        // STAGE 1: Checkout
        // -----------------------------------------------
        stage('Checkout') {
            steps {
                echo "Pulling latest code from GitHub..."
                checkout scm
            }
        }

        // -----------------------------------------------
        // STAGE 2: Install Dependencies
        // -----------------------------------------------
        stage('Install Dependencies') {
            steps {
                echo "Installing Python dependencies..."
                bat '''
                %PYTHON% -m venv venv
                call venv\\Scripts\\activate.bat
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        // -----------------------------------------------
        // STAGE 3: Test
        // -----------------------------------------------
        stage('Test') {
            steps {
                echo "Running unit tests..."
                bat '''
                call venv\\Scripts\\activate.bat
                pytest test_app.py ^
                    --cov=app ^
                    --cov-report=xml:coverage.xml ^
                    --junitxml=test-results.xml ^
                    -v
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        // -----------------------------------------------
        // STAGE 4: SonarQube
        // -----------------------------------------------
        stage('SonarQube Scan') {
            steps {
                echo "Running SonarQube scan..."
                withSonarQubeEnv('sonarqube-server') {
                    bat '''
                    sonar-scanner ^
                      -Dsonar.projectKey=myapp ^
                      -Dsonar.sources=. ^
                      -Dsonar.python.coverage.reportPaths=coverage.xml ^
                      -Dsonar.python.xunit.reportPath=test-results.xml
                    '''
                }
            }
        }

        // -----------------------------------------------
        // STAGE 5: Docker Build
        // -----------------------------------------------
        stage('Docker Build') {
            steps {
                echo "Building Docker Image..."
                bat "docker build -t %REGISTRY%:%IMAGE_TAG% ."
                bat "docker tag %REGISTRY%:%IMAGE_TAG% %REGISTRY%:latest"
            }
        }

        // -----------------------------------------------
        // STAGE 6: Trivy Scan
        // -----------------------------------------------
        stage('Trivy Security Scan') {
            steps {
                echo "Running Trivy Security Scan..."
                bat """
                trivy image ^
                --exit-code 1 ^
                --severity HIGH,CRITICAL ^
                --no-progress ^
                %REGISTRY%:%IMAGE_TAG%
                """
            }
        }

        // -----------------------------------------------
        // STAGE 7: Push DockerHub
        // -----------------------------------------------
        stage('Push to DockerHub') {
            steps {
                echo "Pushing Docker Image..."
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat "echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin"
                    bat "docker push %REGISTRY%:%IMAGE_TAG%"
                    bat "docker push %REGISTRY%:latest"
                }
            }
        }

        // -----------------------------------------------
        // STAGE 8: Deploy Kubernetes
        // -----------------------------------------------
        stage('Deploy to Kubernetes') {
            steps {
                echo "Deploying to Kubernetes..."
                bat "kubectl apply -f k8s\\secret.yaml"
                bat "kubectl apply -f k8s\\deployment.yaml"
                bat "kubectl apply -f k8s\\service.yaml"
                bat "kubectl apply -f k8s\\ingress.yaml"
                bat "kubectl set image deployment/%APP_NAME% %APP_NAME%=%REGISTRY%:%IMAGE_TAG%"
                bat "kubectl rollout status deployment/%APP_NAME% --timeout=120s"
            }
        }
    }

    post {

        success {
            echo "Deployment Successful — Version ${IMAGE_TAG} Live"
        }

        failure {
            echo "Pipeline Failed — Rolling Back"
            bat "kubectl rollout undo deployment/%APP_NAME% || exit 0"
        }

        always {
            echo "Cleaning workspace..."

            bat '''
            rmdir /s /q venv 2>nul
            docker rmi %REGISTRY%:%IMAGE_TAG% 2>nul
            '''
        }
    }
}