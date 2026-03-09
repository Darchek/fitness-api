pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        DOCKER_CONFIG   = '/var/jenkins_home/.docker'
        DOCKER_BUILDKIT = '0'
        REPO_URL        = 'https://github.com/Darchek/fitness-api.git'
        DEPLOY_DIR      = '/Users/mbusq/deployments/fitness'
        HOST            = 'host.docker.internal'
        UNIT_TEST_IMAGE = "fitness-api-test-${BUILD_NUMBER}"
        TEST_IMAGE      = "fitness-api-integration-${BUILD_NUMBER}"
        TEST_NET        = "fitness-api-net-${BUILD_NUMBER}"
        TEST_CTR        = "fitness-api-ctr-${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: "${REPO_URL}"
            }
        }

        stage('Unit Tests') {
            steps {
                script {
                    sh "DOCKER_BUILDKIT=0 docker build -f Dockerfile.test -t ${UNIT_TEST_IMAGE} ."
                    try {
                        sh "docker run --rm ${UNIT_TEST_IMAGE}"
                    } finally {
                        sh "docker rmi ${UNIT_TEST_IMAGE} || true"
                    }
                }
            }
        }

        stage('Integration Test') {
            steps {
                script {
                    sh "DOCKER_BUILDKIT=0 docker build -t ${TEST_IMAGE} ."
                    try {
                        sh "docker network create ${TEST_NET}"
                        sh "docker run -d --name ${TEST_CTR} --network ${TEST_NET} -e DATABASE_URL=postgresql://test:test@localhost/test -e SECRET_KEY=test-secret-key ${TEST_IMAGE}"
                        sh 'sleep 10'
                        sh "docker run --rm --network ${TEST_NET} curlimages/curl:latest curl -sf --retry 5 --retry-delay 3 http://${TEST_CTR}:8000/docs -o /dev/null && echo 'Health check passed'"
                    } finally {
                        sh "docker rm -f ${TEST_CTR} || true"
                        sh "docker network rm ${TEST_NET} || true"
                        sh "docker rmi ${TEST_IMAGE} || true"
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'host-ssh-key', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no -i \$SSH_KEY \$SSH_USER@\${HOST} '
                            export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
                            export DOCKER_BUILDKIT=0
                            set -e
                            cd /Users/mbusq/deployments/fitness/fitness-api
                            git pull origin main
                            /usr/local/bin/docker build -t fitness-api:latest .
                            cd /Users/mbusq/deployments/fitness
                            /usr/local/bin/docker compose up -d --force-recreate fitness-api
                            /usr/local/bin/docker image prune -f
                            echo "fitness-api deploy complete"
                        '
                    """
                }
            }
        }
    }

    post {
        success { echo 'fitness-api redeployed successfully!' }
        failure { echo 'Pipeline failed - fitness-api was NOT redeployed.' }
    }
}
