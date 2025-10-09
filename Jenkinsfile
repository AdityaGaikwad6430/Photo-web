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
                    docker_build("photo-app", "latest", "dockerHubCreds")
                }
            }
        }

        stage("DockerPush") {
            steps {
                script {
                    dpush("photo-app", "latest", "dockerHubCreds")
                }
            }
        }

        stage("Deploy") {
            steps {
                script {
                    deploy()
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



