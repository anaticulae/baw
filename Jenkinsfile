@Library('caelum@refs/tags/v0.14.0') _

pipeline{
    agent{
        dockerfile{filename 'Dockerfile'}
    }
    // image '169.254.149.20:6001/arch_python_git_baw:v1.55.0'
    stages{
        stage('integrate'){
            steps{script{baw.integrate()}}
        }
        stage('setup'){
            steps{script{baw.setup()}}
        }
        stage('test'){
            failFast true
            parallel{
                stage('doctest'){
                    steps{
                        script{baw.doctest()}
                    }
                }
                stage('fast'){
                    steps{
                        script{baw.fast()}
                    }
                }
                stage('long'){
                    steps{
                        script{baw.longrun()}
                    }
                }
            }
        }
        stage('quality'){
            failFast true
            parallel{
                stage('lint'){
                    steps{
                        script{baw.lint()}
                    }
                }
                stage('format'){
                    steps{
                        script{baw.format()}
                    }
                }
            }
        }
        stage('docker'){
            steps{script{baw.run("sh ./make")}}
        }
        stage('pre'){
            steps{script{baw.pre()}}
        }
        stage('all'){
            steps{
                script{baw.cov(32, false, true)}
            }
        }
        stage('others'){
            when{branch 'develop'}
            parallel{
                stage('utila'){steps{build job: 'caelum/utila/integrate'}}
                stage('utilatest'){steps{build job: 'caelum/utilatest/integrate'}}
                stage('dockers'){steps{build job: 'caelum/dockers/integrate'}}
            }
        }
        stage('release'){
            steps{
                script{
                    publish.release()
                    baw.rebase()
                }
            }
        }
    }
}
