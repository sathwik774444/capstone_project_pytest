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

        stage('Create Report Directories') {
            steps {
                bat '''
                if not exist Reports mkdir Reports
                if not exist Screenshots mkdir Screenshots
                if not exist Logs mkdir Logs
                if not exist allure-results mkdir allure-results
                '''
            }
        }

        stage('Start Selenium Grid') {
            steps {
                script {
                    try {
                        // Force stop and remove all containers including orphaned ones
                        bat '''
                        docker-compose down -v --remove-orphans || true
                        docker stop selenium-hub chrome-node-1 chrome-node-2 chrome-node-3 chrome-node-4 firefox-node-1 firefox-node-2 || true
                        docker rm selenium-hub chrome-node-1 chrome-node-2 chrome-node-3 chrome-node-4 firefox-node-1 firefox-node-2 || true
                        docker network prune -f || true
                        '''
                        
                        // Wait a moment for cleanup
                        bat 'timeout /t 5 /nobreak'
                        
                        // Start Selenium Grid with 6 nodes
                        bat 'docker-compose up -d'
                        
                        // Wait for Grid initialization
                        bat 'timeout /t 30 /nobreak'
                        
                        // Check Grid status
                        bat 'curl -f http://localhost:4444/status || exit /b 1'
                        
                        echo "✅ Selenium Grid started successfully with 6 nodes"
                        
                    } catch (Exception e) {
                        echo "❌ Failed to start Selenium Grid: ${e}"
                        
                        // Try to get diagnostic information
                        bat '''
                        echo "=== Docker Container Status ==="
                        docker ps -a
                        echo "=== Docker Compose Status ==="
                        docker-compose ps
                        echo "=== Network Status ==="
                        docker network ls
                        '''
                        
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Configure Remote Execution') {
            steps {
                script {
                    try {
                        // Update config.yaml for remote execution
                        bat '''
                        powershell -Command "(Get-Content config\\config.yaml) -replace 'mode: \\"local\\"', 'mode: \\"remote\\"' | Set-Content config\\config.yaml"
                        '''
                        
                        echo "✅ Configuration updated for Selenium Grid execution"
                        
                    } catch (Exception e) {
                        echo "❌ Failed to configure remote execution: ${e}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Run Parallel Tests on Grid') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script {
                        try {
                            // Run tests in parallel using all 6 Grid nodes
                            bat '''
                            pytest -v -n 6 --dist=loadscope --html=Reports/report.html --self-contained-html --alluredir=allure-results
                            '''
                            
                            echo "✅ Parallel tests completed on Selenium Grid"
                            
                        } catch (Exception e) {
                            echo "❌ Parallel test execution failed: ${e}"
                            currentBuild.result = 'UNSTABLE'
                        }
                    }
                }
            }
        }

        stage('Stop Selenium Grid') {
            steps {
                script {
                    try {
                        // Force stop and remove all containers
                        bat '''
                        docker-compose down -v --remove-orphans || true
                        docker stop selenium-hub chrome-node-1 chrome-node-2 chrome-node-3 chrome-node-4 firefox-node-1 firefox-node-2 || true
                        docker rm selenium-hub chrome-node-1 chrome-node-2 chrome-node-3 chrome-node-4 firefox-node-1 firefox-node-2 || true
                        docker network prune -f || true
                        '''
                        
                        // Restore local execution configuration
                        bat '''
                        powershell -Command "(Get-Content config\\config.yaml) -replace 'mode: \\"remote\\"', 'mode: \\"local\\"' | Set-Content config\\config.yaml"
                        '''
                        
                        echo "✅ Selenium Grid stopped and configuration restored"
                        
                    } catch (Exception e) {
                        echo "⚠️ Failed to stop Selenium Grid: ${e}"
                        // Don't fail the build for cleanup issues
                    }
                }
            }
        }

       
        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'Reports/*',
                                fingerprint: true,
                                allowEmptyArchive: true

                archiveArtifacts artifacts: 'Screenshots/*',
                                fingerprint: true,
                                allowEmptyArchive: true

                archiveArtifacts artifacts: 'Logs/*',
                                fingerprint: true,
                                allowEmptyArchive: true
            }
        }

        stage('Generate Allure Report') {
            steps {
                allure([
                    includeProperties: false,
                    jdk: '',
                    results: [[path: 'allure-results']],
                    commandline: 'Allure'
                ])
            }
        }
    }

    post {
        always {
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'Reports',
                reportFiles: 'report.html',
                reportName: 'Pytest HTML Report'
            ])
        }
    }
}