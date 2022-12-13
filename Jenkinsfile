pipeline{
    agent{
        dockerfile{filename 'Dockerfile'}
    }
    // image '169.254.149.20:6001/arch_python_git_baw:v1.33.0-20-g45a9b98'
    stages{
        stage('integrate'){
            when {branch 'integrate'}
            steps{
                integrate()
            }
        }
        stage('sync'){
            steps{
                image_setup()
            }
        }
        stage('test'){
            failFast true
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
            failFast true
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
        stage('upgrade'){
            when {branch 'integrate'}
            steps{
                sh 'git push origin/integrate'
            }
        }
        stage('release'){
            when {branch 'master'}
            steps{
                sh 'baw release --no_test --no_linter --no_install --no_venv --no_sync'
                sh 'baw publish'
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
def integrate(){
    sh 'git rebase origin/master'
    sh 'baw upgrade all'
    sh 'baw upgrade all --pre'
}
