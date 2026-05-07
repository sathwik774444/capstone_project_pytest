# Quick Start Guide - Parallel Test Execution

## 🚀 **Fixed Docker Compose Issues**

The Docker Compose configuration has been fixed to resolve:
- ❌ Removed obsolete `version` attribute
- ❌ Fixed container name conflicts with `replicas`
- ✅ Created unique container names for multiple nodes
- ✅ Simplified setup with Docker Compose

## 📋 **Setup Options**

### Option 1: Simple Grid (Recommended)
```bash
# Start simple Selenium Grid
docker-compose -f docker-compose.simple-grid.yml up -d

# Check Grid status
curl http://localhost:4444/status

# Run parallel tests
python -m pytest -n 4 tests/
```

### Option 2: Advanced Grid (Multiple Nodes)
```bash
# Start advanced Grid with multiple Chrome nodes
docker-compose -f docker-compose.selenium-grid.yml up -d

# Grid Console: http://localhost:4444
# Runs: 1 Hub + 2 Chrome nodes + 1 Firefox node + 1 Edge node
```

### Option 3: Local Parallel (No Docker)
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (auto-detect CPU cores)
python -m pytest -n auto

# Specify worker count
python -m pytest -n 4
```

## 🛠️ **Using the Advanced Test Runner**

```bash
# Local parallel execution
python run_parallel_tests.py --mode local --workers 4

# Selenium Grid execution
python run_parallel_tests.py --mode grid --workers 4

# Setup Grid automatically
python run_parallel_tests.py --setup-grid

# Cleanup Grid
python run_parallel_tests.py --cleanup-grid
```

## 📊 **Grid Configuration**

### Simple Grid Setup
- **1 Hub** (port 4444)
- **1 Chrome Node** (4 sessions)
- **1 Firefox Node** (2 sessions)
- **Total Capacity**: 6 concurrent sessions

### Advanced Grid Setup
- **1 Hub** (port 4444)
- **2 Chrome Nodes** (4 sessions each = 8 total)
- **1 Firefox Node** (4 sessions)
- **1 Edge Node** (2 sessions)
- **Total Capacity**: 14 concurrent sessions

## 🔧 **Test Execution Examples**

### Basic Parallel Tests
```bash
# Run all tests in parallel
python -m pytest -n 4

# Run specific test files
python -m pytest -n 2 tests/test_login_*.py

# Run with browser selection
python -m pytest -n 4 --browser firefox
```

### Grid Execution
```bash
# Enable Grid in config
export SELENIUM_GRID_ENABLED=true
export SELENIUM_GRID_URL=http://localhost:4444

# Run tests on Grid
python -m pytest -n 4 --selenium-grid-enabled=true
```

### Cloud Execution
```bash
# BrowserStack
export BROWSERSTACK_USERNAME="your_user"
export BROWSERSTACK_ACCESS_KEY="your_key"
python run_parallel_tests.py --mode browserstack --workers 2

# Sauce Labs
export SAUCE_USERNAME="your_user"
export SAUCE_ACCESS_KEY="your_key"
python run_parallel_tests.py --mode saucelabs --workers 2
```

## 📈 **Performance Tips**

### Optimal Worker Count
```python
# Auto-detect optimal workers
import multiprocessing
workers = min(multiprocessing.cpu_count(), 8)
```

### Browser Optimization
- Use Chrome for parallel execution (faster startup)
- Disable GPU and unnecessary features
- Use headless mode in CI/CD

### Resource Management
- Monitor memory usage: `docker stats`
- Check Grid status: `curl http://localhost:4444/status`
- Limit workers based on available RAM

## 🐛 **Troubleshooting**

### Common Issues & Solutions

#### 1. Docker Compose Version Warning
```bash
# ✅ Fixed: Removed obsolete version attribute
# No more warnings about version being obsolete
```

#### 2. Container Name Conflicts
```bash
# ✅ Fixed: Unique container names
# chrome-node-1, chrome-node-2 instead of replicas
```

#### 3. Grid Connection Issues
```bash
# Check Grid status
curl http://localhost:4444/status

# Restart Grid
docker-compose -f docker-compose.simple-grid.yml restart
```

#### 4. Worker Timeout
```bash
# Increase timeout
python -m pytest -n 4 --timeout=600

# Reduce worker count
python -m pytest -n 2
```

## 📝 **Configuration Files**

### Key Files Created
- `docker-compose.simple-grid.yml` - Simple Grid setup
- `docker-compose.selenium-grid.yml` - Advanced Grid setup
- `conftest_parallel.py` - Parallel execution fixtures
- `selenium_grid_config.py` - Grid configuration
- `run_parallel_tests.py` - Advanced test runner
- `pytest_parallel.ini` - Pytest configuration

### Environment Variables
```bash
# Grid Configuration
SELENIUM_GRID_ENABLED=true
SELENIUM_GRID_URL=http://localhost:4444

# Cloud Providers
BROWSERSTACK_USERNAME=your_user
BROWSERSTACK_ACCESS_KEY=your_key
SAUCE_USERNAME=your_user
SAUCE_ACCESS_KEY=your_key
```

## 🎯 **Quick Commands**

### Start Testing in 3 Steps
```bash
# 1. Setup Grid (optional - for local parallel, skip this)
docker-compose -f docker-compose.simple-grid.yml up -d

# 2. Run tests
python -m pytest -n 4 tests/

# 3. View results
# HTML report: reports/report.html
# Allure report: allure serve allure-results
```

### Cleanup
```bash
# Stop Grid
docker-compose -f docker-compose.simple-grid.yml down

# Clean up all containers
docker-compose -f docker-compose.simple-grid.yml down -v
```

## 📚 **Next Steps**

1. **Try Local Parallel**: `python -m pytest -n auto`
2. **Setup Simple Grid**: `docker-compose -f docker-compose.simple-grid.yml up -d`
3. **Run Grid Tests**: `python -m pytest -n 4 --selenium-grid-enabled=true`
4. **Explore Cloud**: Configure BrowserStack/Sauce Labs credentials
5. **CI/CD Integration**: Add to your pipeline configuration

The parallel execution system is now ready for enterprise-scale testing! 🚀
