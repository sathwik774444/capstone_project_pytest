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

        stage('Clean Previous Allure Results') {
            steps {
                script {
                    try {
                        // Clean up Allure results from previous runs to prevent duplicate test cases
                        bat '''
                        if exist allure-results (
                            echo "Cleaning up previous Allure results..."
                            rmdir /s /q allure-results
                            mkdir allure-results
                            echo "✅ Allure results cleaned successfully"
                        ) else (
                            echo "No previous Allure results to clean"
                        )
                        '''
                        
                        echo "✅ Allure cleanup completed"
                        
                    } catch (Exception e) {
                        echo "⚠️ Failed to clean Allure results: ${e}"
                        // Don't fail the build for cleanup issues
                    }
                }
            }
        }

        stage('Start Selenium Grid') {
            steps {
                script {
                    try {

                        bat '''
                        docker compose down -v --remove-orphans
                        docker stop selenium-hub chrome-node-1 chrome-node-2 chrome-node-3 chrome-node-4 firefox-node-1 firefox-node-2
                        docker rm selenium-hub chrome-node-1 chrome-node-2 chrome-node-3 chrome-node-4 firefox-node-1 firefox-node-2
                        docker network prune -f
                        '''

                        // Wait for cleanup
                        bat 'ping 127.0.0.1 -n 6 > nul'

                        // Start Grid
                        bat 'docker compose up -d'

                        // Wait for Grid startup
                        bat 'ping 127.0.0.1 -n 31 > nul'

                        // Verify Grid
                        bat 'curl -f http://localhost:4444/status'

                        echo "✅ Selenium Grid started successfully"

                    } catch (Exception e) {

                        echo "❌ Failed to start Selenium Grid: ${e}"

                        bat '''
                        docker ps -a
                        docker compose ps
                        '''

                        currentBuild.result = 'FAILURE'
                        throw e
                    }
                }
            }
        }

        // stage('Configure Remote Execution') {
        //     steps {
        //         script {
        //             try {
        //                 // Update config.yaml for remote execution
        //                 bat '''
        //                 powershell -Command "(Get-Content config\\config.yaml) -replace 'mode: \\"local\\"', 'mode: \\"remote\\"' | Set-Content config\\config.yaml"
        //                 '''
                        
        //                 echo "✅ Configuration updated for Selenium Grid execution"
                        
        //             } catch (Exception e) {
        //                 echo "❌ Failed to configure remote execution: ${e}"
        //                 currentBuild.result = 'UNSTABLE'
        //             }
        //         }
        //     }
        // }

        stage('Run Parallel Tests on Grid') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    script {
                        try {
                            // Run tests in parallel using all 6 Grid nodes
                            bat '''
                            pytest -v -n 4 --dist=loadscope --html=Reports/report.html --self-contained-html --alluredir=allure-results
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
                        docker compose down -v --remove-orphans
                        docker stop selenium-hub chrome-node-1 chrome-node-2 chrome-node-3 chrome-node-4 firefox-node-1 firefox-node-2
                        docker rm selenium-hub chrome-node-1 chrome-node-2 chrome-node-3 chrome-node-4 firefox-node-1 firefox-node-2
                        docker network prune -f
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
                script {
                    try {
                        // Verify Allure results before generating report
                        bat '''
                        if exist allure-results (
                            echo "Allure results found. Counting result files..."
                            dir /b allure-results | find /c "*.json" > temp_count.txt
                            set /p result_count=<temp_count.txt
                            echo "Found %result_count% Allure result files"
                            del temp_count.txt
                        ) else (
                            echo "⚠️ No Allure results found to generate report"
                            exit /b 1
                        )
                        '''
                        
                        // Generate Allure report
                        allure([
                            includeProperties: false,
                            jdk: '',
                            results: [[path: 'allure-results']],
                            commandline: 'Allure'
                        ])
                        
                        echo "✅ Allure report generated successfully"
                        
                    } catch (Exception e) {
                        echo "❌ Failed to generate Allure report: ${e}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
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