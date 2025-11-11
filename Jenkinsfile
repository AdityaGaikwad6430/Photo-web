@Library('Shared') _

pipeline {
    agent any

    stages {
        stage('Clean workshop') {
            steps {
                script {
                    cleanWs()
                }
            }
        }
        stage('Code') {
            steps {
                script {
                    clone('https://github.com/AdityaGaikwad6430/Photo-web.git', 'main')
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    dockerbuild('photo-app', 'latest')
                }
            }
        }
        stage('push') {
            steps {
                script {
                    dpush('photo-app', 'latest')
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    deploy2()
                }
            }
        }
    }
}



