# Selenium Grid Command Reference

## 🚀 **Correct Command Line Options**

The `--selenium-grid-enabled=true` argument is not recognized by pytest by default. Use these correct options:

### ✅ **Valid Grid Commands**

#### **1. Use Grid Flag**
```bash
# Enable Selenium Grid
python -m pytest tests/ --use-grid -v

# With specific Grid URL
python -m pytest tests/ --use-grid --selenium-grid-url=http://localhost:4444 -v

# Run specific test file
python -m pytest tests/test_login_valid_credentials.py --use-grid -v
```

#### **2. Using Environment Variables**
```bash
# Set environment variables
set SELENIUM_GRID_ENABLED=true
set SELENIUM_GRID_URL=http://localhost:4444

# Run tests (will automatically use Grid)
python -m pytest tests/ -v
```

#### **3. Cloud Provider Execution**
```bash
# BrowserStack
python -m pytest tests/ --cloud-provider=browserstack -v

# Sauce Labs
python -m pytest tests/ --cloud-provider=saucelabs -v
```

#### **4. Advanced Test Runner**
```bash
# Use the advanced test runner (recommended)
python run_parallel_tests.py --mode grid --workers 4

# Local parallel execution
python run_parallel_tests.py --mode local --workers 4
```

### ❌ **Incorrect Commands (Don't Use)**

```bash
# These will NOT work
python -m pytest tests/ --selenium-grid-enabled=true  # ❌
python -m pytest tests/ --grid-enabled=true            # ❌
```

## 📋 **Command Options Reference**

| Option | Description | Example |
|--------|-------------|---------|
| `--use-grid` | Enable Selenium Grid execution | `--use-grid` |
| `--selenium-grid-url` | Specify Grid URL | `--selenium-grid-url=http://localhost:4444` |
| `--cloud-provider` | Use cloud provider | `--cloud-provider=browserstack` |
| `-p conftest_grid` | Load Grid configuration | `-p conftest_grid` |

## 🎯 **Quick Start Commands**

### **1. Start Selenium Grid**
```bash
docker-compose -f docker-compose.simple-grid.yml up -d
```

### **2. Run Tests on Grid**
```bash
# Simple Grid execution
python -m pytest tests/ --use-grid -v

# Parallel Grid execution
python -m pytest -n 4 tests/ --use-grid -v

# With custom configuration
python -m pytest tests/ --use-grid --selenium-grid-url=http://localhost:4444 -p conftest_grid -v
```

### **3. Check Grid Status**
```bash
# Check Grid console
# Open: http://localhost:4444/grid/console

# Check Grid status via API
curl http://localhost:4444/status
```

## 🔧 **Configuration Files**

### **conftest_grid.py** - Grid Configuration
- Adds custom command line options
- Provides Grid browser fixtures
- Handles cloud provider integration

### **selenium_grid_config.py** - Grid Implementation
- Selenium Grid connection logic
- Browser configuration for Grid
- Cloud provider implementations

## 📊 **Execution Modes**

| Mode | Command | Description |
|------|---------|-------------|
| **Local** | `python -m pytest tests/` | Local browser execution |
| **Grid** | `python -m pytest tests/ --use-grid` | Selenium Grid execution |
| **Parallel Local** | `python -m pytest -n 4 tests/` | Local parallel execution |
| **Parallel Grid** | `python -m pytest -n 4 tests/ --use-grid` | Parallel Grid execution |
| **Cloud** | `python -m pytest tests/ --cloud-provider=browserstack` | Cloud execution |

## 🌐 **Cloud Provider Setup**

### **BrowserStack**
```bash
# Set credentials
set BROWSERSTACK_USERNAME=your_username
set BROWSERSTACK_ACCESS_KEY=your_access_key

# Run tests
python -m pytest tests/ --cloud-provider=browserstack -v
```

### **Sauce Labs**
```bash
# Set credentials
set SAUCE_USERNAME=your_username
set SAUCE_ACCESS_KEY=your_access_key

# Run tests
python -m pytest tests/ --cloud-provider=saucelabs -v
```

## 📈 **Performance Tips**

### **Optimal Worker Count**
```bash
# Auto-detect workers
python -m pytest -n auto tests/ --use-grid

# Specify worker count
python -m pytest -n 4 tests/ --use-grid
```

### **Grid Optimization**
```bash
# Use Grid for multiple browsers
python -m pytest tests/ --use-grid -v --browser chrome
python -m pytest tests/ --use-grid -v --browser firefox
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **1. Command Not Recognized**
```bash
# ❌ Wrong
python -m pytest tests/ --selenium-grid-enabled=true

# ✅ Correct
python -m pytest tests/ --use-grid
```

#### **2. Grid Connection Failed**
```bash
# Check Grid status
curl http://localhost:4444/status

# Restart Grid
docker-compose -f docker-compose.simple-grid.yml restart
```

#### **3. Cloud Provider Issues**
```bash
# Check credentials
echo %BROWSERSTACK_USERNAME%
echo %BROWSERSTACK_ACCESS_KEY%

# Test connection
python -c "from selenium_grid_config import create_cloud_grid_driver; print('Cloud connection OK')"
```

## 🎉 **Success Indicators**

When Grid execution is working, you'll see:
- `🚀 Selenium Grid Enabled: http://localhost:4444`
- `✅ Distributed test execution completed`
- Tests running on remote browsers
- Grid console showing active sessions

## 📝 **Examples**

### **Basic Grid Test**
```bash
# Start Grid
docker-compose -f docker-compose.simple-grid.yml up -d

# Run single test
python -m pytest tests/test_login_valid_credentials.py --use-grid -v

# Run all tests
python -m pytest tests/ --use-grid -v
```

### **Parallel Grid Test**
```bash
# Run 4 tests in parallel on Grid
python -m pytest -n 4 tests/ --use-grid -v

# Run specific test suite in parallel
python -m pytest -n 2 tests/test_login_*.py --use-grid -v
```

### **Cloud Execution**
```bash
# BrowserStack execution
python -m pytest tests/ --cloud-provider=browserstack -v

# Sauce Labs execution
python -m pytest tests/ --cloud-provider=saucelabs -v
```

Use these correct commands for successful Selenium Grid execution! 🚀
