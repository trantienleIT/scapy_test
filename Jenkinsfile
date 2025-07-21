pipeline {
    agent { label 'wsl2' }
    tools {
        jdk 'JDK17'
    }
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/trantienleIT/scapy_test.git', branch: 'main', credentialsId: 'PasswordAfterChanged'
            }
        }
        // ... (rest of the pipeline as in previous response)
    }
}