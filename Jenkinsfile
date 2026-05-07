pipeline {
    agent any

    stages {
        stage('Checkout Source Code') {
            steps {
                git branch: 'main',
                url: 'https://github.com/sathwik774444/capstone_project_pytest.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Run Parallel Tests') {
            steps {
                bat 'pytest -n 4 --html=Reports/report.html --self-contained-html'
            }
        }

        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'Reports/*', fingerprint: true
            }
        }
    }

    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'Reports',
                reportFiles: 'report.html',
                reportName: 'Pytest HTML Report'
            ])
        }
    }
}
