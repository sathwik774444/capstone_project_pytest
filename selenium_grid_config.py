"""
Selenium Grid configuration for distributed parallel execution.
Supports both local Grid setup and cloud-based Grid services.
"""

import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.remote_connection import RemoteConnection
from config.environment import env_config


class SeleniumGridConfig:
    """Configuration for Selenium Grid distributed execution."""
    
    def __init__(self):
        self.grid_url = env_config.get("selenium_grid.url", "http://localhost:4444")
        self.enable_grid = env_config.get("selenium_grid.enabled", False)
        self.max_sessions = env_config.get("selenium_grid.max_sessions", 4)
        self.browser_timeout = env_config.get("selenium_grid.browser_timeout", 300)
        
    def create_grid_driver(self, browser_name="chrome", headless=False, worker_id=None):
        """
        Create WebDriver instance connected to Selenium Grid.
        
        Args:
            browser_name: Browser type (chrome, firefox)
            headless: Whether to run in headless mode
            worker_id: Worker ID for parallel execution tracking
        
        Returns:
            WebDriver instance connected to Grid
        """
        try:
            if browser_name.lower() == "chrome":
                return self._create_chrome_grid_driver(headless, worker_id)
            elif browser_name.lower() == "firefox":
                return self._create_firefox_grid_driver(headless, worker_id)
            else:
                raise ValueError(f"Unsupported browser: {browser_name}")
                
        except Exception as e:
            logging.error(f"Failed to create Grid driver for {browser_name}: {e}")
            raise
    
    def _create_chrome_grid_driver(self, headless, worker_id):
        """Create Chrome WebDriver for Grid."""
        options = ChromeOptions()
        
        # Basic Chrome options
        if headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Grid-specific options
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
        
        # Worker-specific options for tracking
        if worker_id:
            options.add_argument(f"--user-data-dir=/tmp/chrome_{worker_id}")
            options.set_capability("workerId", worker_id)
        
        # Grid capabilities
        options.set_capability("browserName", "chrome")
        options.set_capability("browserVersion", "latest")
        options.set_capability("platformName", "ANY")
        
        # Note: timeout is set at page level, not as a capability
        # Session timeout is managed by Grid configuration
        
        # Create remote driver
        driver = webdriver.Remote(
            command_executor=self.grid_url,
            options=options
        )
        
        logging.info(f"Chrome Grid driver created for worker {worker_id}")
        return driver
    
    def _create_firefox_grid_driver(self, headless, worker_id):
        """Create Firefox WebDriver for Grid."""
        options = FirefoxOptions()
        
        # Basic Firefox options
        if headless:
            options.add_argument("--headless")
        
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        
        # Grid-specific options
        options.set_capability("browserName", "firefox")
        options.set_capability("browserVersion", "latest")
        options.set_capability("platformName", "ANY")
        
        # Worker-specific options for tracking
        if worker_id:
            options.set_capability("workerId", worker_id)
        
        # Note: timeout is set at page level, not as a capability
        # Session timeout is managed by Grid configuration
        
        # Create remote driver
        driver = webdriver.Remote(
            command_executor=self.grid_url,
            options=options
        )
        
        logging.info(f"Firefox Grid driver created for worker {worker_id}")
        return driver
    
    def get_grid_status(self):
        """Check Selenium Grid status and available nodes."""
        try:
            import requests
            
            response = requests.get(f"{self.grid_url}/status", timeout=10)
            if response.status_code == 200:
                grid_status = response.json()
                return {
                    "ready": grid_status.get("value", {}).get("ready", False),
                    "nodes": grid_status.get("value", {}).get("nodes", []),
                    "message": "Grid is ready"
                }
            else:
                return {
                    "ready": False,
                    "error": f"Grid returned status {response.status_code}",
                    "message": "Grid is not responding"
                }
        except Exception as e:
            return {
                "ready": False,
                "error": str(e),
                "message": "Cannot connect to Grid"
            }
    
    def wait_for_grid_ready(self, timeout=60):
        """Wait for Selenium Grid to be ready."""
        import time
        
        logging.info("Waiting for Selenium Grid to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_grid_status()
            if status["ready"]:
                logging.info("Selenium Grid is ready!")
                return True
            
            logging.info(f"Grid not ready, waiting... ({status['message']})")
            time.sleep(5)
        
        logging.error("Selenium Grid did not become ready within timeout")
        return False


class GridBrowserManager:
    """Browser manager specifically for Selenium Grid execution."""
    
    def __init__(self, grid_config=None):
        self.grid_config = grid_config or SeleniumGridConfig()
        self.driver = None
        
    def create_driver(self, browser_name="chrome", headless=False, worker_id=None):
        """Create WebDriver using Grid configuration."""
        if not self.grid_config.enable_grid:
            # Fallback to local driver if Grid is disabled
            from fixtures.browser_fixture import BrowserManager
            local_manager = BrowserManager()
            return local_manager.create_driver()
        
        self.driver = self.grid_config.create_grid_driver(
            browser_name=browser_name,
            headless=headless,
            worker_id=worker_id
        )
        return self.driver
    
    def quit_driver(self):
        """Quit the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("Grid driver quit successfully")
            except Exception as e:
                logging.error(f"Error quitting Grid driver: {e}")
            finally:
                self.driver = None


# Grid setup utilities
def setup_local_grid():
    """
    Setup local Selenium Grid using Docker Compose.
    This is a helper function for local development.
    """
    import subprocess
    
    try:
        # Use Docker Compose for easier setup
        compose_file = "docker-compose.simple-grid.yml"
        
        # Stop and remove existing containers
        subprocess.run(["docker-compose", "-f", compose_file, "down"], 
                      capture_output=True)
        
        # Start Grid with Docker Compose
        subprocess.run(["docker-compose", "-f", compose_file, "up", "-d"], 
                      check=True)
        
        # Wait for Grid to be ready
        import time
        time.sleep(10)
        
        logging.info("Local Selenium Grid setup completed using Docker Compose")
        return True
        
    except Exception as e:
        logging.error(f"Failed to setup local Grid: {e}")
        return False


def cleanup_local_grid():
    """Cleanup local Selenium Grid containers."""
    import subprocess
    
    try:
        compose_file = "docker-compose.simple-grid.yml"
        subprocess.run(["docker-compose", "-f", compose_file, "down"], 
                      capture_output=True)
        logging.info("Local Selenium Grid cleaned up")
        return True
    except Exception as e:
        logging.error(f"Failed to cleanup local Grid: {e}")
        return False


# Cloud Grid configurations
CLOUD_GRID_CONFIGS = {
    "browserstack": {
        "url": "https://hub-cloud.browserstack.com/wd/hub",
        "capabilities": {
            "bstack:options": {
                "os": "Windows",
                "osVersion": "10",
                "buildName": "Test Automation Build",
                "sessionName": "Parallel Test Execution",
                "local": False,
                "seleniumVersion": "4.0.0"
            }
        }
    },
    "saucelabs": {
        "url": "https://ondemand.us-central-1.saucelabs.com:443/wd/hub",
        "capabilities": {
            "sauce:options": {
                "build": "Test Automation Build",
                "name": "Parallel Test Execution",
                "extendedDebugging": True
            }
        }
    }
}


def create_cloud_grid_driver(cloud_provider, browser_name="chrome", capabilities=None):
    """
    Create WebDriver for cloud-based Grid services.
    
    Args:
        cloud_provider: 'browserstack' or 'saucelabs'
        browser_name: Browser type
        capabilities: Additional capabilities to merge
    
    Returns:
        WebDriver instance connected to cloud Grid
    """
    if cloud_provider not in CLOUD_GRID_CONFIGS:
        raise ValueError(f"Unsupported cloud provider: {cloud_provider}")
    
    config = CLOUD_GRID_CONFIGS[cloud_provider]
    
    # Get credentials from environment variables
    if cloud_provider == "browserstack":
        username = os.getenv("BROWSERSTACK_USERNAME")
        access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")
        if not username or not access_key:
            raise ValueError("BrowserStack credentials not found in environment variables")
        
        config["url"] = f"https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub"
    
    elif cloud_provider == "saucelabs":
        username = os.getenv("SAUCE_USERNAME")
        access_key = os.getenv("SAUCE_ACCESS_KEY")
        if not username or not access_key:
            raise ValueError("Sauce Labs credentials not found in environment variables")
        
        config["url"] = f"https://{username}:{access_key}@ondemand.us-central-1.saucelabs.com:443/wd/hub"
    
    # Merge capabilities
    final_capabilities = config["capabilities"].copy()
    if capabilities:
        final_capabilities.update(capabilities)
    
    # Add browser-specific capabilities
    final_capabilities["browserName"] = browser_name
    
    # Create remote driver
    driver = webdriver.Remote(
        command_executor=config["url"],
        desired_capabilities=final_capabilities
    )
    
    logging.info(f"Cloud Grid driver created for {cloud_provider}")
    return driver
