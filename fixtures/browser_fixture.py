"""Browser fixture with WebDriver management."""

import pytest
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import allure
import os
from datetime import datetime

from config.environment import env_config


class BrowserManager:
    """Manages browser setup and teardown."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None
        
    def create_driver(self, browser_name=None, headless=None):
        """Create WebDriver instance based on configuration."""
        browser_name = browser_name or env_config.get("browser.name", "chrome")
        headless = headless if headless is not None else env_config.get("browser.headless", False)
        
        if browser_name.lower() == "chrome":
            return self._create_chrome_driver(headless)
        elif browser_name.lower() == "firefox":
            return self._create_firefox_driver(headless)
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")
    
    def _create_chrome_driver(self, headless):
        """Create Chrome WebDriver."""
        options = ChromeOptions()
        
        if headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Add options to prevent renderer timeouts
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
        options.add_argument("--max_old_space_size=4096")
        
        # Set page load strategy to normal (more tolerant)
        options.page_load_strategy = 'normal'
        
        # Get ChromeDriver path and ensure it's the executable
        driver_path = ChromeDriverManager().install()
        
        # Handle the webdriver-manager path issue
        import os
        if "chromedriver-win32" in driver_path and not driver_path.endswith("chromedriver.exe"):
            # Extract the directory and find the actual executable
            driver_dir = os.path.dirname(driver_path)
            if "chromedriver-win32" in driver_dir:
                actual_exe = os.path.join(driver_dir, "chromedriver.exe")
                if os.path.exists(actual_exe):
                    driver_path = actual_exe
                else:
                    # Try to find any .exe file in the directory
                    for file in os.listdir(driver_dir):
                        if file.endswith(".exe") and "chromedriver" in file.lower():
                            driver_path = os.path.join(driver_dir, file)
                            break
            
        service = ChromeService(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        # Set timeouts
        driver.implicitly_wait(env_config.get("browser.implicit_wait", 10))
        driver.set_page_load_timeout(env_config.get("browser.explicit_wait", 30))
        
        return driver
    
    def _create_firefox_driver(self, headless):
        """Create Firefox WebDriver."""
        options = FirefoxOptions()
        
        if headless:
            options.add_argument("--headless")
        
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        
        # Set timeouts
        driver.implicitly_wait(env_config.get("browser.implicit_wait", 10))
        driver.set_page_load_timeout(env_config.get("browser.explicit_wait", 30))
        
        return driver
    
    def quit_driver(self):
        """Quit WebDriver instance."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Error quitting driver: {e}")


@pytest.fixture(scope="function")
def browser():
    """Pytest fixture for browser setup and teardown."""
    browser_manager = BrowserManager()
    driver = None
    
    try:
        # Create driver
        driver = browser_manager.create_driver()
        browser_manager.driver = driver
        
        # Set implicit wait
        implicit_wait = env_config.get("browser.implicit_wait", 10)
        driver.implicitly_wait(implicit_wait)
        
        yield driver
        
    except Exception as e:
        # Take screenshot on failure
        if driver:
            try:
                screenshot_path = take_screenshot(driver, "failure")
                allure.attach.file(screenshot_path, name="Failure Screenshot", attachment_type=allure.attachment_type.PNG)
            except Exception as screenshot_error:
                logging.error(f"Failed to take screenshot: {screenshot_error}")
        
        raise e
    
    finally:
        # Cleanup
        if driver:
            browser_manager.quit_driver()


@pytest.fixture(scope="function")
def wait(browser):
    """Pytest fixture for WebDriverWait."""
    explicit_wait = env_config.get("browser.explicit_wait", 30)
    return WebDriverWait(browser, explicit_wait)


def take_screenshot(driver, test_name=None):
    """Take screenshot and return file path."""
    try:
        # Create screenshots directory if it doesn't exist
        screenshots_dir = env_config.get("reporting.screenshots_dir", "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = test_name or "screenshot"
        filename = f"{test_name}_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, filename)
        
        # Take screenshot
        driver.save_screenshot(filepath)
        logging.info(f"Screenshot saved: {filepath}")
        
        return filepath
        
    except Exception as e:
        logging.error(f"Failed to take screenshot: {e}")
        return None


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to take screenshot on test failure."""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        try:
            # Get browser fixture from test item
            if hasattr(item, "funcargs") and "browser" in item.funcargs:
                driver = item.funcargs["browser"]
                screenshot_path = take_screenshot(driver, item.name)
                
                if screenshot_path:
                    allure.attach.file(
                        screenshot_path,
                        name=f"Screenshot - {item.name}",
                        attachment_type=allure.attachment_type.PNG
                    )
        except Exception as e:
            logging.error(f"Failed to capture screenshot on failure: {e}")


@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    """Configure logging for the test session."""
    log_level = env_config.get("logging.level", "WARNING")
    log_format = env_config.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Create logs directory
    logs_dir = env_config.get("reporting.logs_dir", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, "test_execution.log")),
            logging.StreamHandler()
        ]
    )
    
    # Suppress Selenium debug logs
    selenium_logger = logging.getLogger('selenium')
    selenium_logger.setLevel(logging.WARNING)
    
    urllib3_logger = logging.getLogger('urllib3.connectionpool')
    urllib3_logger.setLevel(logging.WARNING)
