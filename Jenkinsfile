pipeline {
    agent {
        docker {
            image '169.254.149.20:6001/test:0.2.0'
            args '--privileged -u root -v $WORKSPACE:/var/test'
        }
    }

    parameters {
        string(name: 'BRANCH', defaultValue: 'master')
        booleanParam(name: 'RELEASE', defaultValue: false)
    }

    stages{
        stage('sync'){
            steps{
                sh 'ls -al /tmp'
                sh 'baw sync all'
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
                sh 'baw --lint'
            }
        }
        stage('nightly'){
            steps{
                sh 'baw test nightly -n16'
            }
        }
        stage('release'){
            when {
                expression { return params.RELEASE }
            }
            steps{
                sh 'baw install && baw release'
            }
        }
    }
}
