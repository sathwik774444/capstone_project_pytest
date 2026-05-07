# Notes Application Test Automation Framework

A comprehensive Pytest Selenium automation framework for testing the Notes application with both UI and API testing capabilities, including hybrid end-to-end tests.

## 🏗️ Framework Architecture

```
project/
│
├── tests/                          # Test cases
│   ├── test_login.py              # Login functionality tests
│   ├── test_notes_ui.py           # UI notes management tests
│   ├── test_notes_api.py          # API notes management tests
│   └── test_e2e_hybrid.py         # End-to-end hybrid tests
│
├── pages/                          # Page Object Model
│   ├── base_page.py               # Base page with common utilities
│   ├── login_page.py              # Login page object
│   ├── home_page.py               # Home page object
│   └── notes_page.py              # Notes page object
│
├── api/                            # API testing module
│   └── api_client.py              # Centralized API client
│
├── fixtures/                       # Pytest fixtures
│   └── browser_fixture.py         # Browser setup and teardown
│
├── config/                         # Configuration management
│   ├── config.yaml                # Test configuration
│   └── environment.py             # Environment configuration class
│
├── requirements.txt                # Python dependencies
├── pytest.ini                     # Pytest configuration
├── conftest.py                     # Global pytest configuration
├── allure.ini                      # Allure reporting configuration
├── environment.properties          # Allure environment properties
├── categories.json                 # Allure test categories
└── README.md                       # This file
```

## 🚀 Features

### Core Features
- ✅ **Pytest Framework** - Modern Python testing framework
- ✅ **Selenium WebDriver** - Advanced browser automation
- ✅ **Page Object Model** - Maintainable UI test architecture
- ✅ **API Testing** - RESTful API testing with requests library
- ✅ **Hybrid E2E Tests** - UI + API integration testing
- ✅ **Allure Reporting** - Beautiful, interactive test reports
- ✅ **Parallel Execution** - Run tests in parallel with pytest-xdist
- ✅ **Configuration Management** - YAML-based configuration
- ✅ **Structured Logging** - Comprehensive logging system
- ✅ **Screenshot Capture** - Automatic screenshots on failure
- ✅ **Retry Mechanisms** - Handle flaky tests gracefully

### Advanced Features
- ✅ **WebDriver Manager** - Automatic driver management
- ✅ **Explicit Waits** - Robust synchronization
- ✅ **JavaScript Executor** - Advanced browser interactions
- ✅ **Reusable Components** - Modular test utilities
- ✅ **Error Handling** - Comprehensive exception handling
- ✅ **Response Time Validation** - API performance testing
- ✅ **Concurrent Testing** - Multi-threaded test execution
- ✅ **Environment Configuration** - Multi-environment support

## 📋 Prerequisites

- Python 3.8+
- Google Chrome browser
- Git

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd capstone_project_pytest/project
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Allure commandline (optional for local reporting):**
   ```bash
   # Windows (using scoop)
   scoop install allure
   
   # Mac
   brew install allure
   
   # Linux
   sudo apt-get install allure
   ```

## ⚙️ Configuration

### Environment Configuration

Edit `config/config.yaml` to customize:

```yaml
environment:
  base_url: "https://practice.expandtesting.com"
  ui_url: "https://practice.expandtesting.com/notes/app"
  api_url: "https://practice.expandtesting.com/notes/api"

browser:
  name: "chrome"
  headless: false
  window_size: "1920,1080"
  implicit_wait: 10
  explicit_wait: 30

test_data:
  valid_user:
    username: "your_username"
    password: "your_password"
```

### Test Data

Update test credentials in `config/config.yaml`:

```yaml
test_data:
  valid_user:
    username: "your_test_username"
    password: "your_test_password"
```

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Files
```bash
# Login tests
pytest tests/test_login.py

# UI tests
pytest tests/test_notes_ui.py

# API tests
pytest tests/test_notes_api.py

# E2E hybrid tests
pytest tests/test_e2e_hybrid.py
```

### Run with Markers
```bash
# Run only smoke tests
pytest -m smoke

# Run only UI tests
pytest -m ui

# Run only API tests
pytest -m api

# Run only critical tests
pytest -m critical
```

### Parallel Execution
```bash
# Run with 4 parallel workers
pytest -n 4

# Run with auto-detected workers
pytest -n auto
```

### Generate HTML Report
```bash
pytest --html=reports/report.html --self-contained-html
```

### Generate Allure Report
```bash
# Run tests with Allure
pytest --alluredir=allure-results

# Generate Allure report
allure serve allure-results

# Or generate static report
allure generate allure-results -o allure-report
```

## 📊 Test Categories

### UI Tests (`test_login.py`, `test_notes_ui.py`)
- User authentication
- Note creation, editing, deletion
- Search functionality
- Form validation
- Navigation
- Responsiveness

### API Tests (`test_notes_api.py`)
- Authentication and authorization
- CRUD operations
- Search and filtering
- Error handling
- Response time validation
- Concurrent requests

### E2E Hybrid Tests (`test_e2e_hybrid.py`)
- **Scenario 1**: Create note via UI → Validate via API
- **Scenario 2**: Delete note via API → Validate on UI
- **Scenario 3**: Update note via UI → Validate via API
- **Scenario 4**: Create note via API → Edit via UI
- **Scenario 5**: Concurrent UI and API operations

## 📈 Reporting

### Allure Reports
- Interactive test execution dashboard
- Test execution timeline
- Detailed test steps and attachments
- Screenshots on failure
- API request/response logs
- Environment information
- Test categorization

### HTML Reports
- Comprehensive test summary
- Test execution details
- Error messages and stack traces
- Execution statistics

## 🔧 Customization

### Adding New Tests

1. Create new test file in `tests/` directory
2. Use existing page objects and API client
3. Follow naming convention `test_*.py`
4. Use appropriate markers and documentation

### Adding New Page Objects

1. Create new page class in `pages/` directory
2. Inherit from `BasePage`
3. Define locators and page-specific methods
4. Add proper logging and error handling

### Extending API Client

1. Add new methods to `APIClient` class
2. Follow existing patterns for request/response handling
3. Add proper error handling and logging
4. Include Allure attachments

## 🐛 Debugging

### Debug Mode
```bash
pytest -s -v --pdb
```

### Headless Mode
Edit `config/config.yaml`:
```yaml
browser:
  headless: true
```

### Logging
- Test execution logs: `logs/pytest.log`
- Allure results: `allure-results/`
- Screenshots: `screenshots/`

## 📝 Best Practices

1. **Page Object Model**: Use page objects for UI interactions
2. **Explicit Waits**: Use explicit waits instead of sleep
3. **Error Handling**: Implement proper exception handling
4. **Logging**: Add comprehensive logging for debugging
5. **Test Data**: Use external configuration for test data
6. **Cleanup**: Clean up created test data after each test
7. **Documentation**: Use docstrings and Allure annotations
8. **Markers**: Use pytest markers for test categorization

## 🔍 Test Coverage

The framework covers:

- **Authentication**: Login, logout, session management
- **Note Management**: Create, read, update, delete operations
- **Search**: Text search and filtering
- **Validation**: Form validation and error handling
- **API Operations**: RESTful API endpoints
- **Performance**: Response time validation
- **Integration**: UI-API data consistency
- **Error Scenarios**: Invalid credentials, missing data
- **Edge Cases**: Concurrent operations, boundary conditions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or issues:
- Check the logs in `logs/` directory
- Review Allure reports for detailed test execution
- Refer to test documentation and docstrings
- Check configuration files for proper setup

---

**Built with ❤️ using Pytest, Selenium, and Allure**
