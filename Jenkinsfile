pipeline {
    agent any

    environment {
        APP_NAME  = "myapp"
        REGISTRY  = "yourdockerhub/myapp"    // Replace with your DockerHub username
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        // -----------------------------------------------
        // STAGE 1: Pull code from GitHub
        // -----------------------------------------------
        stage('Checkout') {
            steps {
                echo "Pulling latest code from GitHub..."
                checkout scm
            }
        }

        // -----------------------------------------------
        // STAGE 2: Install Python dependencies
        // No compilation needed — Python is interpreted!
        // -----------------------------------------------
        stage('Install Dependencies') {
            steps {
                echo "Installing Python dependencies..."
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip -q
                    pip install -r requirements.txt -q
                '''
            }
        }

        // -----------------------------------------------
        // STAGE 3: Run pytest unit tests
        // --cov = generate coverage report for SonarQube
        // -----------------------------------------------
        stage('Test') {
            steps {
                echo "Running unit tests with pytest..."
                sh '''
                    . venv/bin/activate
                    pytest test_app.py \
                        --cov=app \
                        --cov-report=xml:coverage.xml \
                        --junitxml=test-results.xml \
                        -v
                '''
            }
            post {
                always {
                    // Show test results in Jenkins UI
                    junit 'test-results.xml'
                }
            }
        }

        // -----------------------------------------------
        // STAGE 4: SonarQube — scan code quality
        // -----------------------------------------------
        stage('SonarQube Scan') {
            steps {
                echo "Running SonarQube code quality scan..."
                withSonarQubeEnv('sonarqube-server') {
                    sh '''
                        sonar-scanner \
                          -Dsonar.projectKey=myapp \
                          -Dsonar.sources=. \
                          -Dsonar.python.coverage.reportPaths=coverage.xml \
                          -Dsonar.python.xunit.reportPath=test-results.xml
                    '''
                }
            }
        }

        // -----------------------------------------------
        // STAGE 5: Build Docker image (multi-stage)
        // -----------------------------------------------
        stage('Docker Build') {
            steps {
                echo "Building Docker image..."
                sh "docker build -t ${REGISTRY}:${IMAGE_TAG} ."
                sh "docker tag  ${REGISTRY}:${IMAGE_TAG} ${REGISTRY}:latest"
            }
        }

        // -----------------------------------------------
        // STAGE 6: Trivy — scan image for CVEs
        // -----------------------------------------------
        stage('Trivy Security Scan') {
            steps {
                echo "Scanning image for vulnerabilities..."
                sh """
                    trivy image \
                      --exit-code 1 \
                      --severity HIGH,CRITICAL \
                      --no-progress \
                      ${REGISTRY}:${IMAGE_TAG}
                """
            }
        }

        // -----------------------------------------------
        // STAGE 7: Push to DockerHub
        // -----------------------------------------------
        stage('Push to DockerHub') {
            steps {
                echo "Pushing image to DockerHub..."
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                    sh "docker push ${REGISTRY}:${IMAGE_TAG}"
                    sh "docker push ${REGISTRY}:latest"
                }
            }
        }

        // -----------------------------------------------
        // STAGE 8: Deploy to Kubernetes
        // -----------------------------------------------
        stage('Deploy to Kubernetes') {
            steps {
                echo "Deploying to Kubernetes..."
                sh "kubectl apply -f k8s/secret.yaml"
                sh "kubectl apply -f k8s/deployment.yaml"
                sh "kubectl apply -f k8s/service.yaml"
                sh "kubectl apply -f k8s/ingress.yaml"
                sh "kubectl set image deployment/${APP_NAME} ${APP_NAME}=${REGISTRY}:${IMAGE_TAG}"
                sh "kubectl rollout status deployment/${APP_NAME} --timeout=120s"
            }
        }
    }

    post {
        success {
            echo "Deployed successfully! Version ${IMAGE_TAG} is live."
        }
        failure {
            echo "Pipeline failed — rolling back..."
            sh "kubectl rollout undo deployment/${APP_NAME} || true"
        }
        always {
            // Clean up virtual environment and Docker image
            sh "rm -rf venv || true"
            sh "docker rmi ${REGISTRY}:${IMAGE_TAG} || true"
        }
    }
}