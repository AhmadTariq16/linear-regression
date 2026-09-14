pipeline {
    agent any

    environment {
        // Maps to: workflow-level `vars.*` (GitHub Actions repo variables)
        AWS_REGION     = 'us-east-1'
        ECR_REPOSITORY = 'linear-regression'
    }

    stages {
        stage('Test') {
            // Maps to: GitHub Actions job `test`
            steps {
                sh 'pip install uv'
                sh 'uv sync --locked --all-extras'
                sh 'uv run pytest'
            }
        }

        stage('Build') {
            // Maps to: GitHub Actions steps "Compute image tag" + "Set up Docker Buildx" + "Build image"
            when {
                branch 'main'
            }
            steps {
                script {
                    env.IMAGE_TAG = "sha-" + sh(script: 'git rev-parse --short=7 HEAD', returnStdout: true).trim()
                }
                sh 'docker buildx build --load -t ${ECR_REPOSITORY}:${IMAGE_TAG} .'
            }
        }

        stage('Scan') {
            // Maps to: "Scan image with Trivy" step
            when {
                branch 'main'
            }
            steps {
                sh 'trivy image --severity HIGH,CRITICAL --exit-code 1 ${ECR_REPOSITORY}:${IMAGE_TAG}'
            }
        }

        stage('Push') {
            // Maps to: "Configure AWS credentials" + "Login to Amazon ECR" + "Push image" steps.
            // No OIDC equivalent exists in Jenkins (see chat) — this assumes the Jenkins
            // agent runs on an EC2 instance with an IAM instance profile attached, granting
            // it the same permissions as the github-actions-ecr-push role. No static
            // AWS keys are configured here or anywhere in this Jenkinsfile.
            when {
                branch 'main'
            }
            steps {
                sh '''
                    REGISTRY=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION}.amazonaws.com
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${REGISTRY}
                    docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                    docker push ${REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                '''
            }
        }
    }

    post {
        success {
            // Maps to: job output `image-tag` (GitHub Actions' `outputs:` block)
            echo "Pushed image tag: ${env.IMAGE_TAG}"
        }
    }
}