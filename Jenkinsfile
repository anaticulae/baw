pipeline{
    agent{
        dockerfile{filename 'Dockerfile'}
    }
    // image '169.254.149.20:6001/arch_python_git_baw:0.15.0'

    environment{
        BAW='/tmp/dev'
        PIP_TRUSTED_HOST='169.254.149.20'
        PIP_INDEX_URL='http://169.254.149.20:6101'
        PIP_EXTRA_INDEX_URL='http://169.254.149.20:6103'
        GITEA_SERVER_URL = '169.254.149.20:6300'
        GIT_AUTHOR_NAME='Automated Release'
        GIT_AUTHOR_EMAIL='automated_release@ostia.la'
        CAELUM_DOCKER_TEST = '169.254.149.20:6001'
        CAELUM_DOCKER_RUNTIME='169.254.149.20:2375'
    }

    stages{
        stage('sync'){
            steps{
                image_setup()
            }
        }
        stage('test'){
            parallel{
                stage('doctest'){
                    steps{
                        doctest()
                    }
                }
                stage('fast'){
                    steps{
                        baw('test fast -n5')
                    }
                }
                stage('long'){
                    steps{
                        baw('test long -n8')
                    }
                }
            }
        }
        stage('ready?'){
            parallel{
                stage('lint'){
                    steps{
                        baw('lint')
                    }
                }
                stage('format'){
                    steps{
                        baw('format && baw info clean')
                    }
                }
                stage('all'){
                    steps{
                        alls()
                    }
                }
            }
        }
        stage('docker'){
            steps{
                sh './make'
            }
        }
        stage('clean workspace'){
            steps{
                sh 'baw info clean'
            }
        }
        stage('release'){
            when {branch 'master'}
            steps{
                sh 'baw release --no_test --no_linter --no_install --no_venv'
            }
        }
    }
}

@NonCPS
def image_name() {
    return sh(script: "baw image info")
}
def image_setup(){
    env.IMAGE_NAME = sh(script: 'baw info image', returnStdout: true).trim()
    sh 'baw image create'
}
def baw(cmd){
    sh 'baw --docker ' + cmd
    //#sh 'docker run --rm -u 1005:1006 -v ${WORKSPACE}:/var/workdir ${IMAGE_NAME} "baw ' + cmd + '"'
}
def doctest(){
    baw('test docs -n1 --junit_xml=docs.xml')
    //junit '**/docs.xml'
}
def alls(){
    baw('test all --junit_xml=all.xml')
    //junit '**/all.xml'
}
