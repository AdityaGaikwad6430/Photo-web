@Library('Shared') _

pipeline {
    agent any

    parameters {
        string(name: 'DOCKER_TAG', defaultValue: '', description: 'Setting docker image for latest push')
    }

    stages {
        stage("Validate Parameters") {
            steps {
                script {
                    if (params.DOCKER_TAG == '') {
                        error("DOCKER_TAG is required.")
                    }
                }
            }
        }

        stage("Workspace cleanup") {
            steps {
                cleanWs()
            }
        }

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
