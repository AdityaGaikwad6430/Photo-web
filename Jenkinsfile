@Library('Shared') _

pipeline {
    agent {label "Node1"}

    stages {
        stage("Code") {
            steps {
                script {
                    clone("https://github.com/AdityaGaikwad6430/Photo-web.git", "main")
                }
            }
        }

        stage("Build") {
            steps {
                script {
                    build2("photo-app", "latest")
                }
            }
        }
        stage("Deploy") {
            steps {
                script {
                    deploy2()
                }
            }
        }
        stage("Clean workshop") {
            steps {
                script {
                    cleanWs()
                }
            }
        }
    }
}


