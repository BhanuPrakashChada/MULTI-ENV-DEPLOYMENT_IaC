pipeline {
    agent { label 'Jenkins-Agent' }
     parameters {
        choice(name: 'ACTION', choices: ['Create', 'Destroy'], description: 'Choose the action to perform')
        activeChoiceReactiveParam(name: 'ENVIRONMENT', script: {
            def environments = ['Dev', 'QA', 'Prod']
            return environments
        }, description: 'Choose the environment', filterLength: 1, filterable: true)
    }

    tools {
        python 'Python3'
        docker 'docker'
    }

    environment {
        ACCESS_KEY = credentials('AWS_ACCESS_KEY_ID')
        SECRET_KEY = credentials('AWS_SECRET_KEY_ID')
        APP_NAME = "sys-monitoring"
        DOCKER_USER = credentials("DOCKER_HUB_USERNAME")
        DOCKER_PASS = credentials("DOCKER_HUB_TOKEN")
        IMAGE_NAME = "${DOCKER_USER}/${APP_NAME}"
        IMAGE_TAG = "${RELEASE}-${BUILD_NUMBER}"
        JENKINS_API_TOKEN = credentials("JENKINS_API_TOKEN")
        KUBE_NAMESPACE = "default"  
        KUBE_CONFIG = credentials("KUBE_CONFIG")
        KUBE_CONTEXT = "EKS"

    }
    stages {

        stage("Cleanup Workspace") {
            steps {
                cleanWs()
            }
        }

         stage('Initialize') {
            steps {
                script {
                    echo "Selected Action: ${params.ACTION}"
                    echo "Selected Environment: ${params.ENVIRONMENT}"
                }
            }
        }

        stage("Checkout from SCM") {
            when {expression { params.ACTION == 'Create'}}
            steps {
                git branch: 'main', credentialsId: 'github', url: 'https://github.com/BhanuPrakashChada/MULTI-ENV-DEPLOYMENT_IaC.git'
            }
        }

        stage("Build Application") {
            when {expression { params.ACTION == 'Create'}}
            steps {
                script {
                    sh 'pip install -r requirements.txt'
                    sh 'python setup.py build'
                }
            }
        }

        stage('Unit Tests') {
            when {expression { params.ACTION == 'Create'}}
            steps {
                script {
                    sh 'python -m unittest discover -s tests/unittest -p "test_unit*.py"'
                }
            }
            post {
                success { 
                    slackSend channel: '#bhanu_Jenkinstest', color: 'good', message: "Unittest Success", teamDomain: 'testnotifgroup', tokenCredentialId: 'slack-token'
                }
                failure { 
                    slackSend channel: '#bhanu_Jenkinstest', color: 'danger', message: "Unittest Failed", teamDomain: 'testnotifgroup', tokenCredentialId: 'slack-token'
                }
            }

        }

        stage('Integration Tests') {
            when {expression { params.ACTION == 'Create'}}
            steps {
                script {
                    sh 'python -m unittest discover -s tests/integration -p "test_integration*.py"'
                }
            }
            post {
                success { 
                    slackSend channel: '#bhanu_Jenkinstest', color: 'good', message: "Integration_test Success", teamDomain: 'testnotifgroup', tokenCredentialId: 'slack-token'
                }
                failure { 
                    slackSend channel: '#bhanu_Jenkinstest', color: 'danger', message: "Integartion_test Failed", teamDomain: 'testnotifgroup', tokenCredentialId: 'slack-token'
                }
            }
        }

        stage("Static Code Analysis") {
            when {expression { params.ACTION == 'Create'}}
            steps {
                script {
                    sh 'flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics'
                }
            }
        }

        stage("Build & Push Docker Image") {
            when {expression { params.ACTION == 'Create'}}
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                    sh "docker login -u ${DOCKER_USER} -p ${DOCKER_PASS}"
                    sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest"
                    sh "docker push ${IMAGE_NAME}:latest"
                }
            }
        }

        stage("Security Scanning") {
        steps {
            script {
                sh "trivy --format json --output ${./trivyReportPath} ${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }
    }

        stage('Terraform Apply/Destroy') {
            when {
                expression { params.ACTION == 'Create' }
            }
            steps {
                script {
                    def KUBE_CLUSTER

                    if (params.ENVIRONMENT == 'Dev') {
                        KUBE_CLUSTER = 'eks-dev-cluster'
                    } else if (params.ENVIRONMENT == 'Prod') {
                        KUBE_CLUSTER = 'eks-prod-cluster'
                    } else if (params.ENVIRONMENT == 'QA') {
                        KUBE_CLUSTER = 'eks-qa-cluster'
                    } else {
                        error "Invalid environment selected"
                    }
                    echo "${params.ACTION}ing EKS cluster server: ${eksClusterServer}"
                    dir('EKS-cluster-from-Jenkins_using-IaC\eks-cluster\eks-node-group') {
                        sh "terraform init"
                        sh "terraform validate"
                        sh "terraform plan"
                        sh "terraform apply -auto-approve"
                    }
                }
            }
        }

        stage('Connect to EKS Cluster') {
            when {expression { params.ACTION == 'Create' }}
            steps {
                script {
                    echo "Connecting to EKS cluster..."
                    sh 'aws eks --region us-east-1 update-kubeconfig --name ${KUBE_CLUSTER}'
                }
            }
        }

        stage("Health Checks") {
            when {expression { params.ACTION == 'Create' }}
            steps {
                script {
                    sh "kubectl wait --for=condition=ready pod -l app=${KUBE_DEPLOYMENT_NAME} --timeout=300s --namespace=${KUBE_NAMESPACE}"
                }
            }
        }

        stage("Deploy to Kubernetes") {
            when {expression { params.ACTION == 'Create' }}
            steps {
                script {
                    def KUBE_NAMESPACE

                    if (params.ENVIRONMENT == 'Dev') {
                        KUBE_NAMESPACE = 'eks-dev-default'
                    } else if (params.ENVIRONMENT == 'Prod') {
                        KUBE_NAMESPACE = 'eks-prod-default'
                    } else if (params.ENVIRONMENT == 'QA') {
                        KUBE_NAMESPACE = 'eks-qa-default'
                    } else {
                        error "Invalid namespace"
                    }
                    echo "Deploying application on EKS cluster server: ${eksClusterServer} -- ${KUBE_NAMESPACE}"
                    dir('EKS-cluster-from-Jenkins_using-IaC\kubernetes') {
                        sh "kubectl config use-context ${KUBE_CONTEXT}"
                        sh "kubectl apply -f kubernetes/deployment.yaml --namespace=${KUBE_NAMESPACE}"
                        sh "kubectl apply -f kubernetes/service.yaml --namespace=${KUBE_NAMESPACE}"
                        sh "kubectl apply -f kubernetes/autoscaling.yaml
                    }
                    
                }
            }
        }

        stage("settingup Prometheus"){
            steps {
                script{
                    sh "kubectl apply -f EKS-cluster-from-Jenkins_using-IaC\kubernetes\prometheus\prometheus-config.yaml --namespace=${KUBE_NAMESPACE}"
                    sh "kubectl apply -f EKS-cluster-from-Jenkins_using-IaC\kubernetes\prometheus\prometheus-deployment.yaml --namespace=${KUBE_NAMESPACE}"
                }
            }
        }

        post {
            always {
                prometheusMonitoring()
            }
        }

        post {
                success { 
                    slackSend channel: '#bhanu_Jenkinstest', color: 'good', message: "CICD pipeline Success", teamDomain: 'testnotifgroup', tokenCredentialId: 'slack-token'
                }
                failure { 
                    slackSend channel: '#bhanu_Jenkinstest', color: 'danger', message: "Pipeline Failed!! PLease check logs for more details", teamDomain: 'testnotifgroup', tokenCredentialId: 'slack-token'
                }
            }

    }
}