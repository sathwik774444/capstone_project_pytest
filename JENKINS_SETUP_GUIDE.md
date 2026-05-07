# Jenkins CI/CD Setup Guide for Selenium + Pytest Framework

## 🚀 **Quick Setup**

### **Required Files**
1. ✅ `requirements.txt` - Python dependencies
2. ✅ `Jenkinsfile` - Pipeline configuration
3. ✅ Project structure with tests/, pages/, utils/

### **Step 1: Install Jenkins Plugins**
Go to **Manage Jenkins → Plugins** and install:
- ✅ Pipeline
- ✅ HTML Publisher
- ✅ Git
- ✅ Allure Jenkins Plugin (optional)
- ✅ Workspace Cleanup

### **Step 2: Configure Python**
Go to **Manage Jenkins → Global Tool Configuration**
- Add Python installation path
- Example: `C:\Python313\` (Windows)

### **Step 3: Create Pipeline Job**
1. Open Jenkins → **New Item**
2. Select **Pipeline**
3. Enter project name
4. In Pipeline section:
   - Choose **Pipeline script from SCM**
   - SCM → **Git**
   - Add GitHub repository URL
   - Script Path: **Jenkinsfile**

### **Step 4: Push to GitHub**
```bash
git init
git add .
git commit -m "Initial CI/CD setup"
git branch -M main
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### **Step 5: Run Pipeline**
Click **Build Now** in Jenkins

## 📁 **Project Structure**
```
Project/
├── tests/
├── pages/
├── utils/
├── Reports/
├── Screenshots/
├── Logs/
├── requirements.txt
├── pytest.ini
├── Jenkinsfile
└── conftest.py
```

## 🐧 **Linux vs Windows**
- **Windows**: Use `Jenkinsfile` with `bat` commands
- **Linux**: Use `Jenkinsfile-Linux` with `sh` commands
- **Enterprise**: Use `Jenkinsfile-Enterprise` for advanced features

## 🎯 **Pipeline Flow**
1. Developer pushes code → GitHub
2. Jenkins triggers automatically
3. Install dependencies
4. Run parallel tests (`-n 4`)
5. Generate HTML reports
6. Archive artifacts (screenshots, logs)
7. Publish reports

## 📊 **Reports Generated**
- ✅ HTML Report: Interactive test results
- ✅ Screenshots: Failure evidence
- ✅ Logs: Execution details
- ✅ Allure Report: Advanced analytics (optional)

## 🔧 **Customization**
Change these in `Jenkinsfile`:
- **Workers**: `-n 4` → `-n 8` for more parallelism
- **Browser**: Add `--browser=chrome` parameter
- **Test suite**: Add `tests/test_login_*.py` for specific tests

## 🎉 **Success Indicators**
- ✅ Green build in Jenkins
- ✅ HTML report published
- ✅ Artifacts archived
- ✅ Tests executed in parallel

Your CI/CD pipeline is now ready! 🚀
