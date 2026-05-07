"""Global pytest configuration and fixtures."""

import pytest
import logging
import os
import sys
import json
import allure
from pathlib import Path
from datetime import datetime
from selenium import webdriver
import requests

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import fixtures and utilities
sys.path.insert(0, str(project_root / "fixtures"))
from browser_fixture import browser, wait, take_screenshot

sys.path.insert(0, str(project_root / "utils"))
from allure_utils import allure_reporter



# Configure logging at the session level
def pytest_configure(config):
    """Configure pytest session and allure."""
    # Create necessary directories
    directories = [
        "allure-results",
        "screenshots", 
        "logs",
        "reports",
        "temp"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Configure enhanced logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('logs/pytest.log'),
            logging.FileHandler('logs/detailed_test.log'),
            logging.StreamHandler()
        ]
    )
    
    # Suppress debug logs for cleaner output
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
    
    # Configure Allure environment properties
    if not hasattr(config, '_allure_environment'):
        config._allure_environment = True
        
        # Copy environment.properties to allure-results
        env_file = Path(__file__).parent / "environment.properties"
        if env_file.exists():
            import shutil
            allure_results = Path("allure-results")
            allure_results.mkdir(exist_ok=True)
            shutil.copy(env_file, allure_results / "environment.properties")
        
        # Copy categories.json to allure-results
        categories_file = Path(__file__).parent / "categories.json"
        if categories_file.exists():
            import shutil
            allure_results = Path("allure-results")
            allure_results.mkdir(exist_ok=True)
            shutil.copy(categories_file, allure_results / "categories.json")
        
        # Create dynamic environment info
        _create_dynamic_environment_info()
    
    # Attach global environment information
    allure_reporter.attach_environment_info()


def _create_dynamic_environment_info():
    """Create dynamic environment information for Allure."""
    try:
        dynamic_env = {
            "Execution.Start.Time": datetime.now().isoformat(),
            "Python.Version": sys.version,
            "Platform": sys.platform,
            "Working.Directory": os.getcwd(),
            "Test.Framework": "pytest",
            "Allure.Version": "2.24.0",  # Update as needed
            "Selenium.Version": webdriver.__version__ if hasattr(webdriver, '__version__') else "Unknown",
            "Requests.Version": requests.__version__
        }
        
        # Write to environment.properties in allure-results
        env_file = Path("allure-results/environment.properties")
        with open(env_file, 'a') as f:
            f.write("\n# Dynamic Environment Information\n")
            for key, value in dynamic_env.items():
                f.write(f"{key}={value}\n")
                
    except Exception as e:
        logging.error(f"Failed to create dynamic environment info: {e}")


@pytest.fixture(scope="session")
def logger():
    """Provide logger instance for tests."""
    return logging.getLogger(__name__)


@pytest.fixture(scope="function")
def grid_browser():

    from fixtures.browser_fixture import BrowserManager

    browser_manager = BrowserManager()

    driver = browser_manager.create_driver()

    yield driver

    if driver:
        driver.quit()


@pytest.fixture(scope="function")
def browser(request, grid_browser):
    """
    Main browser fixture that delegates to appropriate browser.
    This maintains compatibility with existing tests.
    """
    return grid_browser


@pytest.fixture(scope="session", autouse=True)
def session_setup():
    """Setup and teardown for entire test session."""
    logging.info("Starting test session")
    
    # Attach session start information
    with allure.step("Test Session Setup"):
        allure.attach(
            f"Test session started at: {datetime.now().isoformat()}",
            name="Session Start Time",
            attachment_type=allure.attachment_type.TEXT
        )
    
    yield
    
    logging.info("Test session completed")
    
    # Attach session completion information
    with allure.step("Test Session Teardown"):
        allure.attach(
            f"Test session completed at: {datetime.now().isoformat()}",
            name="Session End Time",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Attach final log file
        allure_reporter.attach_log_file("logs/pytest.log", "Complete Test Log")


@pytest.fixture(scope="function", autouse=True)
def test_setup_teardown(request):
    """Setup and teardown for each test with enhanced Allure reporting."""
    test_name = request.node.name
    test_class = request.cls.__name__ if request.cls else "Unknown"
    
    logging.info(f"Starting test: {test_name}")
    
    # Attach test start information
    with allure.step(f"Test Setup: {test_name}"):
        allure.attach(
            f"Test Class: {test_class}\nTest Name: {test_name}\nStart Time: {datetime.now().isoformat()}",
            name="Test Information",
            attachment_type=allure.attachment_type.TEXT
        )
    
    yield
    
    logging.info(f"Completed test: {test_name}")
    
    # Attach test completion information
    with allure.step(f"Test Teardown: {test_name}"):
        allure.attach(
            f"Test completed at: {datetime.now().isoformat()}",
            name="Test Completion Time",
            attachment_type=allure.attachment_type.TEXT
        )


@pytest.fixture(scope="function")
def enhanced_browser(browser):
    """Enhanced browser fixture with comprehensive Allure reporting."""
    test_name = pytest.current_test_name if hasattr(pytest, 'current_test_name') else "test"
    
    # Attach browser setup information
    with allure.step("Browser Setup"):
        allure_reporter.attach_browser_info(browser, "Initial Browser State")
    
    yield browser
    
    # Attach browser teardown information
    with allure.step("Browser Teardown"):
        allure_reporter.attach_browser_info(browser, "Final Browser State")
        allure_reporter.attach_console_logs(browser, "Final Console Logs")


@pytest.fixture(scope="function")
def api_logger():
    """Fixture for API request/response logging."""
    
    class APILogger:
        def __init__(self):
            self.requests = []
            self.responses = []
        
        def log_request(self, request: requests.PreparedRequest, name: str = None):
            """Log API request with Allure attachment."""
            request_name = name or f"Request {len(self.requests) + 1}"
            allure_reporter.attach_api_request(request, request_name)
            self.requests.append(request)
        
        def log_response(self, response: requests.Response, name: str = None):
            """Log API response with Allure attachment."""
            response_name = name or f"Response {len(self.responses) + 1}"
            allure_reporter.attach_api_response(response, response_name)
            self.responses.append(response)
        
        def log_request_response_pair(self, request: requests.PreparedRequest, 
                                    response: requests.Response, name: str = None):
            """Log both request and response as a pair."""
            base_name = name or f"API Call {len(self.requests) + 1}"
            self.log_request(request, f"{base_name} - Request")
            self.log_response(response, f"{base_name} - Response")
    
    return APILogger()


@pytest.fixture(scope="function")
def performance_monitor():
    """Fixture for performance monitoring and reporting."""
    
    class PerformanceMonitor:
        def __init__(self):
            self.metrics = {}
            self.start_times = {}
        
        def start_timer(self, operation: str):
            """Start timing an operation."""
            self.start_times[operation] = datetime.now()
        
        def end_timer(self, operation: str):
            """End timing an operation and record duration."""
            if operation in self.start_times:
                duration = (datetime.now() - self.start_times[operation]).total_seconds()
                if operation not in self.metrics:
                    self.metrics[operation] = []
                self.metrics[operation].append(duration)
                return duration
            return None
        
        def record_metric(self, metric_name: str, value: any):
            """Record a custom metric."""
            if metric_name not in self.metrics:
                self.metrics[metric_name] = []
            self.metrics[metric_name].append(value)
        
        def attach_to_allure(self, name: str = "Performance Metrics"):
            """Attach all metrics to Allure report."""
            # Calculate statistics
            processed_metrics = {}
            for metric_name, values in self.metrics.items():
                if isinstance(values[0], (int, float)):
                    processed_metrics[metric_name] = {
                        "values": values,
                        "count": len(values),
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values)
                    }
                else:
                    processed_metrics[metric_name] = values
            
            allure_reporter.attach_performance_metrics(processed_metrics, name)
    
    return PerformanceMonitor()


# Enhanced hooks for better reporting
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Enhanced hook for comprehensive test failure reporting."""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        test_name = item.name
        
        if rep.failed:
            with allure.step("Test Failure Analysis"):
                # Attach failure information
                allure.attach(
                    f"Test failed: {test_name}\nPhase: {rep.when}\nDuration: {rep.duration:.3f}s",
                    name="Failure Information",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # Attach traceback
                if rep.longrepr:
                    allure.attach(
                        str(rep.longrepr),
                        name="Failure Traceback",
                        attachment_type=allure.attachment_type.TEXT
                    )
                
                # Take screenshot if browser is available
                if hasattr(item, "funcargs") and "browser" in item.funcargs:
                    driver = item.funcargs["browser"]
                    allure_reporter.attach_screenshot(driver, f"Failure - {test_name}")
                    allure_reporter.attach_console_logs(driver, f"Console Logs on Failure - {test_name}")
                
                # Attach relevant log files
                log_files = [
                    "logs/pytest.log",
                    "logs/detailed_test.log"
                ]
                
                for log_file in log_files:
                    if os.path.exists(log_file):
                        allure_reporter.attach_log_file(log_file, f"Log File on Failure - {test_name}")
        
        elif rep.passed:
            with allure.step("Test Success Summary"):
                allure.attach(
                    f"Test passed: {test_name}\nDuration: {rep.duration:.3f}s",
                    name="Success Information",
                    attachment_type=allure.attachment_type.TEXT
                )
        
        elif rep.skipped:
            with allure.step("Test Skip Information"):
                skip_reason = rep.longrepr or "No reason provided"
                allure.attach(
                    f"Test skipped: {test_name}\nReason: {skip_reason}",
                    name="Skip Information",
                    attachment_type=allure.attachment_type.TEXT
                )


def pytest_collection_modifyitems(config, items):
    """Enhanced test collection with better marker management."""
    for item in items:
        # Add markers based on test location and content
        test_path = str(item.fspath).lower()
        
        # UI tests marker
        if any(keyword in test_path for keyword in ["ui", "login", "notes", "dashboard"]):
            if "ui" not in [mark.name for mark in item.iter_markers()]:
                item.add_marker(pytest.mark.ui)
        
        # API tests marker
        if "api" in test_path:
            if "api" not in [mark.name for mark in item.iter_markers()]:
                item.add_marker(pytest.mark.api)
        
        # Performance tests marker
        if "performance" in test_path:
            if "performance" not in [mark.name for mark in item.iter_markers()]:
                item.add_marker(pytest.mark.performance)
        
        # Integration tests marker
        if any(keyword in test_path for keyword in ["sync", "integration", "e2e"]):
            if "integration" not in [mark.name for mark in item.iter_markers()]:
                item.add_marker(pytest.mark.integration)


# Store current test name for global access
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Store current test name globally."""
    pytest.current_test_name = item.name

@pytest.fixture(scope="session")
def logger():
    """Provide logger instance for tests."""
    return logging.getLogger(__name__)

@pytest.fixture(scope="session", autouse=True)
def session_setup():
    """Setup and teardown for entire test session."""
    logging.info("Starting test session")
    yield
    logging.info("Test session completed")

@pytest.fixture(scope="function", autouse=True)
def test_setup_teardown(request):
    """Setup and teardown for each test."""
    test_name = request.node.name
    logging.info(f"Starting test: {test_name}")
    
    yield
    
    logging.info(f"Completed test: {test_name}")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers dynamically."""
    for item in items:
        # Add UI marker to UI tests
        if "ui" in item.nodeid or "login" in item.nodeid or "notes" in item.nodeid:
            if "ui" not in [mark.name for mark in item.iter_markers()]:
                item.add_marker(pytest.mark.ui)
        
        # Add API marker to API tests
        if "api" in item.nodeid:
            if "api" not in [mark.name for mark in item.iter_markers()]:
                item.add_marker(pytest.mark.api)
        
        # Add E2E marker to E2E tests
        if "e2e" in item.nodeid or "hybrid" in item.nodeid:
            if "e2e" not in [mark.name for mark in item.iter_markers()]:
                item.add_marker(pytest.mark.e2e)

def pytest_html_report_title(report):
    """Customize HTML report title."""
    report.title = "Notes Application Test Report"

def pytest_html_results_summary(prefix, summary, postfix):
    """Add custom summary to HTML report."""
    prefix.extend([
        "<h2>Test Environment</h2>",
        "<p><strong>Application:</strong> Notes Application</p>",
        "<p><strong>Framework:</strong> Pytest + Selenium + Requests</p>",
        "<p><strong>Browser:</strong> Chrome</p>",
        "<p><strong>Environment:</strong> Test</p>"
    ])

