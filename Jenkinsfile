pipeline{
    agent{
        docker{
            image '169.254.149.20:6001/arch_python_git_baw:0.15.0'
            args  '-v $WORKSPACE:/var/workdir'
        }
    }

    parameters{
        string(name: 'BRANCH', defaultValue: 'master')
        booleanParam(name: 'RELEASE', defaultValue: false)
    }

    environment{
        GITEA_SERVER_URL = '169.254.149.20:6300'
        GIT_AUTHOR_NAME='Automated Release'
        GIT_AUTHOR_EMAIL='automated_release@ostia.la'
        CAELUM_DOCKER_TEST = '169.254.149.20:6001'
        CAELUM_DOCKER_RUNTIME='169.254.149.20:2375'
    }

    stages{
        stage('sync'){
            steps{
                sh 'baw sync all'
                sh 'pip install -e .'
                sh 'baw sync all'
                script{
                    env.IMAGE_NAME = sh(script: 'baw info image', returnStdout: true).trim()
                }
                sh 'baw image create'
            }
        }
        stage('doctest'){
            steps{
                sh 'baw test docs -n1'
            }
        }
        stage('fast'){
            steps{
                sh 'baw test fast -n5'
            }
        }
        stage('long'){
            steps{
                sh 'baw test long -n8'
            }
        }
        stage('lint'){
            steps{
                sh 'baw lint'
            }
        }
        stage('all'){
            steps{
                sh 'baw test all --cov --junit_xml=report.xml'
                junit '**/report.xml'
            }
        }
        stage('release'){
            when {
                expression { return params.RELEASE }
            }
            steps{
                sh 'baw install && baw release && baw publish'
                // TODO: GIT COMMIT?
            }
        }
    }
}

@NonCPS
def get_image_name() {
    return sh(script: "baw image info")
}
