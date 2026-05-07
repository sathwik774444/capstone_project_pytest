"""
Parallel execution configuration for pytest-xdist.
Provides per-worker WebDriver instances and distributed testing capabilities.
"""

import pytest
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from fixtures.browser_fixture import BrowserManager


def pytest_configure(config):
    """Configure parallel execution settings."""
    # Enable xdist plugin
    if hasattr(config, 'workerinput'):
        # This is a worker process
        worker_id = config.workerinput['workerid']
        logging.info(f"Initializing worker {worker_id}")
        
        # Set worker-specific environment variables
        os.environ['PYTEST_XDIST_WORKER'] = worker_id
        os.environ['PYTEST_XDIST_WORKER_COUNT'] = str(config.workerinput['workercount'])


@pytest.fixture(scope="session")
def worker_id(request):
    """Get the current worker ID for parallel execution."""
    if hasattr(request.config, 'workerinput'):
        return request.config.workerinput['workerid']
    return "main"


@pytest.fixture(scope="session")
def worker_count(request):
    """Get the total number of workers."""
    if hasattr(request.config, 'workerinput'):
        return request.config.workerinput['workercount']
    return 1


@pytest.fixture(scope="function")
def parallel_browser(worker_id):
    """
    Per-worker WebDriver instance for parallel execution.
    Each worker gets its own isolated browser instance.
    """
    browser_manager = BrowserManager()
    driver = None
    
    try:
        # Create driver with worker-specific configuration
        driver = browser_manager.create_driver()
        
        # Set worker-specific window position to avoid conflicts
        window_width = 1920
        window_height = 1080
        worker_index = int(worker_id.replace('gw', '')) if worker_id != 'main' else 0
        
        # Position windows side by side for visual debugging
        x_position = worker_index * 100  # Small offset to avoid overlap
        y_position = worker_index * 100
        
        driver.set_window_position(x_position, y_position)
        driver.set_window_size(window_width, window_height)
        
        # Set worker-specific capabilities
        driver.execute_script(f"window.workerId = '{worker_id}';")
        
        # Set implicit wait
        from config.environment import env_config
        implicit_wait = env_config.get("browser.implicit_wait", 10)
        driver.implicitly_wait(implicit_wait)
        
        logging.info(f"Browser initialized for worker {worker_id}")
        
        yield driver
        
    except Exception as e:
        logging.error(f"Error setting up browser for worker {worker_id}: {e}")
        # Take screenshot on failure
        if driver:
            try:
                screenshot_path = f"screenshots/worker_{worker_id}_setup_failure.png"
                driver.save_screenshot(screenshot_path)
                logging.error(f"Setup failure screenshot saved: {screenshot_path}")
            except:
                pass
        raise e
    
    finally:
        # Cleanup
        if driver:
            try:
                browser_manager.quit_driver()
                logging.info(f"Browser cleaned up for worker {worker_id}")
            except Exception as e:
                logging.error(f"Error cleaning up browser for worker {worker_id}: {e}")


@pytest.fixture(scope="function")
def parallel_wait(parallel_browser):
    """WebDriverWait instance for parallel execution."""
    from config.environment import env_config
    from selenium.webdriver.support.ui import WebDriverWait
    
    explicit_wait = env_config.get("browser.explicit_wait", 30)
    return WebDriverWait(parallel_browser, explicit_wait)


@pytest.fixture(scope="function")
def parallel_take_screenshot(parallel_browser):
    """Screenshot function for parallel execution."""
    def take_screenshot(name="screenshot"):
        try:
            import os
            from datetime import datetime
            
            # Create screenshots directory if it doesn't exist
            os.makedirs("screenshots", exist_ok=True)
            
            # Generate unique filename with worker ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
            filename = f"screenshots/{worker_id}_{name}_{timestamp}.png"
            
            parallel_browser.save_screenshot(filename)
            logging.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logging.error(f"Failed to take screenshot: {e}")
            return None
    
    return take_screenshot


# Parallel execution hooks
def pytest_xdist_setupnodes(config, specs):
    """Called before xdist starts worker processes."""
    logging.info(f"Setting up {len(specs)} worker processes for parallel execution")


def pytest_xdist_newgateway(gateway):
    """Called when a new worker gateway is created."""
    logging.info(f"New worker gateway created: {gateway.id}")


def pytest_xdist_worker_ready(worker):
    """Called when a worker is ready to receive work."""
    logging.info(f"Worker {worker.id} is ready")


def pytest_xdist_worker_finished(worker):
    """Called when a worker finishes its work."""
    logging.info(f"Worker {worker.id} finished")


# Test distribution strategies
def pytest_collection_modifyitems(config, items):
    """Modify test collection for better parallel distribution."""
    # Sort tests by module and function name for consistent distribution
    items.sort(key=lambda x: (x.module.__name__, x.name))
    
    # Add markers for parallel execution
    for item in items:
        if not hasattr(item, 'parallel_marker'):
            item.parallel_marker = True


# Worker-specific test data management
@pytest.fixture(scope="session")
def worker_test_data(worker_id):
    """
    Generate worker-specific test data to avoid conflicts.
    Each worker gets unique test data to prevent collisions.
    """
    from config.environment import env_config
    
    # Get base test data
    base_data = env_config.test_data.copy()
    
    # Modify data for this worker to avoid conflicts
    if worker_id != 'main':
        worker_index = int(worker_id.replace('gw', ''))
        
        # Add worker suffix to unique fields
        if 'note_data' in base_data:
            base_data['note_data']['title'] = f"{base_data['note_data']['title']} (Worker {worker_id})"
        
        # You can add more worker-specific data modifications here
        logging.info(f"Generated test data for worker {worker_id}")
    
    return base_data


# Parallel execution reporting
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Generate parallel execution reports with worker information.
    """
    outcome = yield
    report = outcome.get_result()
    
    # Add worker information to report
    if hasattr(item.config, 'workerinput'):
        worker_id = item.config.workerinput['workerid']
        report.worker_id = worker_id
        
        # Add worker info to nodeid for better reporting
        if report.when == 'call':
            report.nodeid = f"[{worker_id}] {report.nodeid}"


# Resource cleanup for parallel execution
def pytest_sessionfinish(session, exitstatus):
    """Clean up resources after parallel test session."""
    logging.info(f"Parallel test session finished with exit status: {exitstatus}")
    
    # Clean up any temporary files created by workers
    import glob
    import os
    
    # Clean up worker-specific temp files (optional)
    temp_patterns = [
        "temp_worker_*",
        "worker_*_temp.*"
    ]
    
    for pattern in temp_patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                logging.info(f"Cleaned up temp file: {file_path}")
            except:
                pass
