"""Base page class with common functionality for all page objects."""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import allure
from config.environment import env_config


class BasePage:
    """Base class for all page objects."""
    
    def __init__(self, driver):
        """Initialize BasePage with WebDriver instance."""
        self.driver = driver
        self.wait = WebDriverWait(driver, env_config.get("browser.explicit_wait", 30))
        self.logger = logging.getLogger(__name__)
    
    def navigate_to(self, url):
        """Navigate to specified URL."""
        try:
            self.driver.get(url)
            self.logger.info(f"Navigated to: {url}")
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            raise
    
    def wait_for_element(self, locator, timeout=None):
        """Wait for element to be visible."""
        wait = WebDriverWait(self.driver, timeout) if timeout else self.wait
        try:
            element = wait.until(EC.visibility_of_element_located(locator))
            return element
        except Exception as e:
            self.logger.error(f"Element not visible: {locator} - {e}")
            raise
    
    def wait_for_element_clickable(self, locator, timeout=None):
        """Wait for element to be clickable."""
        wait = WebDriverWait(self.driver, timeout) if timeout else self.wait
        try:
            element = wait.until(EC.element_to_be_clickable(locator))
            return element
        except Exception as e:
            self.logger.error(f"Element not clickable: {locator} - {e}")
            # Try one more time with shorter timeout
            try:
                short_wait = WebDriverWait(self.driver, 5)
                element = short_wait.until(EC.element_to_be_clickable(locator))
                self.logger.info(f"Element found on retry: {locator}")
                return element
            except Exception as retry_error:
                self.logger.error(f"Element not clickable even on retry: {locator} - {retry_error}")
                raise
    
    def click_element(self, locator):
        """Click on element."""
        try:
            element = self.wait_for_element_clickable(locator)
            element.click()
            self.logger.info(f"Clicked element: {locator}")
        except Exception as e:
            self.logger.error(f"Failed to click element: {locator} - {e}")
            raise
    
    def type_text(self, locator, text):
        """Type text into element."""
        try:
            element = self.wait_for_element(locator)
            element.clear()
            element.send_keys(text)
            self.logger.info(f"Typed text into element: {locator}")
        except Exception as e:
            self.logger.error(f"Failed to type text into element: {locator} - {e}")
            raise
    
    def get_text(self, locator):
        """Get text from element."""
        try:
            element = self.wait_for_element(locator)
            text = element.text
            self.logger.info(f"Retrieved text from element: {locator}")
            return text
        except Exception as e:
            self.logger.error(f"Failed to get text from element: {locator} - {e}")
            raise
    
    def is_element_visible(self, locator, timeout=10):
        """Check if element is visible."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.visibility_of_element_located(locator))
            return element is not None
        except Exception:
            return False
    
    def is_element_present(self, locator):
        """Check if element is present in DOM."""
        try:
            self.driver.find_element(*locator)
            return True
        except Exception:
            return False
    
    def wait_for_page_load(self, timeout=30):
        """Wait for page to load completely."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            self.logger.info("Page loaded successfully")
        except Exception as e:
            self.logger.error(f"Page load timeout: {e}")
            # Try to refresh the page and wait again
            try:
                self.logger.info("Attempting to refresh page due to timeout")
                self.driver.refresh()
                import time
                time.sleep(2)
                wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                self.logger.info("Page loaded successfully after refresh")
            except Exception as refresh_error:
                self.logger.error(f"Page load failed even after refresh: {refresh_error}")
                raise
    
    def handle_renderer_timeout(self):
        """Handle Chrome renderer timeout by refreshing or navigating."""
        try:
            # Check if page is responsive
            current_url = self.driver.current_url
            self.logger.info(f"Current URL before handling timeout: {current_url}")
            
            # Try to refresh the page
            self.driver.refresh()
            import time
            time.sleep(2)
            
            # Check if we can still interact with the page
            self.driver.execute_script("return document.readyState;")
            self.logger.info("Page is responsive after refresh")
            
        except Exception as e:
            self.logger.error(f"Renderer timeout handling failed: {e}")
            # Last resort: navigate to current URL again
            try:
                current_url = self.driver.current_url
                self.driver.get(current_url)
                time.sleep(3)
                self.logger.info("Navigated to current URL again as last resort")
            except Exception as nav_error:
                self.logger.error(f"Last resort navigation failed: {nav_error}")
                raise
    
    def scroll_to_element(self, locator):
        """Scroll to specific element."""
        try:
            element = self.wait_for_element(locator)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self.logger.info(f"Scrolled to element: {locator}")
        except Exception as e:
            self.logger.error(f"Failed to scroll to element: {locator} - {e}")
            raise
    
    def take_screenshot(self, name="screenshot"):
        """Take screenshot and attach to Allure report."""
        try:
            screenshot_path = f"screenshots/{name}_{self.driver.title}.png"
            self.driver.save_screenshot(screenshot_path)
            allure.attach.file(screenshot_path, name=name, attachment_type=allure.attachment_type.PNG)
            self.logger.info(f"Screenshot taken: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def get_current_url(self):
        """Get current page URL."""
        return self.driver.current_url
    
    def get_page_title(self):
        """Get current page title."""
        return self.driver.title
