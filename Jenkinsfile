@Library('Shared') _

pipeline {
    agent any
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
                    docker_build("photo-app", "${params.DOCKER_TAG}", "dockerHubCreds")
                }
            }
        }

        stage("DockerPush") {
            steps {
                script {
                    dpush("photo-app", "${params.DOCKER_TAG}", "dockerHubCreds")
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
    }
}

