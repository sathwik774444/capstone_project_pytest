"""Login page object for the notes application."""

from selenium.webdriver.common.by import By
from .base_page import BasePage
import allure


class LoginPage(BasePage):
    """Page object for login page."""
    
    # Locators
    BASE_LOGIN_BUTTON = (By.CSS_SELECTOR, "a[href='/notes/app/login']")
    EMAIL_INPUT = (By.ID, "email")
    # EMAIL_INPUT = (By.CSS_SELECTOR, "input[data-testid='login-email']")
    PASSWORD_INPUT = (By.ID, "password")
    # PASSWORD_INPUT = (By.CSS_SELECTOR, "input[data-testid='login-password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[data-testid='login-submit']")
    LOGIN_FORM = (By.TAG_NAME, "form")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "div[data-testid='alert-message']")
    # ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")
    EMAIL_VALIDATION = (By.CSS_SELECTOR, "div.invalid-feedback")
    
    def __init__(self, driver):
        """Initialize LoginPage with WebDriver instance."""
        super().__init__(driver)
    
    def navigate_to_login(self):
        """Navigate to login page."""
        base_url = "https://practice.expandtesting.com/notes/app"
        with allure.step("Navigate to base app page"):
            try:
                self.navigate_to(base_url)
                self.wait_for_page_load()
                
                # Wait a moment for page to stabilize
                import time
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Failed to navigate to base page: {e}")
                # Try direct navigation to login page
                try:
                    login_url = "https://practice.expandtesting.com/notes/app/login"
                    self.driver.get(login_url)
                    self.logger.info("Navigated directly to login page due to base page failure")
                    return
                except Exception as direct_error:
                    self.logger.error(f"Direct navigation also failed: {direct_error}")
                    raise
        
        with allure.step("Click login button to navigate to login page"):
            try:
                self.click_base_login_button()
                # Wait shorter time for page load to avoid timeout
                time.sleep(2)
            except Exception as e:
                self.logger.warning(f"Failed to click login button: {e}, trying direct navigation")
                # Fallback to direct navigation
                try:
                    login_url = "https://practice.expandtesting.com/notes/app/login"
                    self.driver.get(login_url)
                    self.logger.info("Used direct navigation as fallback")
                except Exception as fallback_error:
                    self.logger.error(f"Fallback navigation failed: {fallback_error}")
                    raise
    
    def click_base_login_button(self):
        """Click base login button with fallback."""
        try:
            # Try regular click first with shorter timeout
            element = self.wait_for_element_clickable(self.BASE_LOGIN_BUTTON, timeout=10)
            element.click()
            self.logger.info("Successfully clicked base login button with regular click")
        except Exception as e:
            if "timeout" in str(e).lower() and "renderer" in str(e).lower():
                self.logger.warning(f"Chrome renderer timeout detected: {e}, handling timeout")
                self.handle_renderer_timeout()
                # Retry after handling timeout
                try:
                    element = self.wait_for_element_clickable(self.BASE_LOGIN_BUTTON, timeout=5)
                    element.click()
                    self.logger.info("Successfully clicked base login button after timeout handling")
                    return
                except Exception as retry_error:
                    self.logger.error(f"Retry also failed: {retry_error}")
            
            self.logger.warning(f"Regular click failed: {e}, trying JavaScript click")
            try:
                # If regular click fails, try JavaScript click with element finding
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                short_wait = WebDriverWait(self.driver, 5)
                element = short_wait.until(EC.element_to_be_clickable(self.BASE_LOGIN_BUTTON))
                self.driver.execute_script("arguments[0].click();", element)
                self.logger.info("Successfully clicked base login button with JavaScript click")
            except Exception as js_error:
                self.logger.error(f"JavaScript click also failed: {js_error}")
                # Last resort: try direct navigation to login page
                try:
                    login_url = "https://practice.expandtesting.com/notes/app/login"
                    self.driver.get(login_url)
                    self.logger.info("Navigated directly to login page as last resort")
                except Exception as nav_error:
                    self.logger.error(f"Direct navigation also failed: {nav_error}")
                    raise
    
    def login(self, username, password):
        """Perform login with given credentials."""
        with allure.step(f"Login with username: {username}"):
            # Wait for login form to be ready
            self.wait_for_login_page_load()
            
            # Enter email
            self.enter_email(username)
            
            # Enter password
            self.enter_password(password)
            
            # Click login button with fallback
            self.click_login_button()
            
            # Wait for page to process
            self.wait_for_page_load()
    
    def enter_email(self, email):
        """Enter email in email input field."""
        with allure.step(f"Enter email: {email}"):
            self.type_text(self.EMAIL_INPUT, email)
    
    def enter_password(self, password):
        """Enter password in password input field."""
        with allure.step("Enter password"):
            self.type_text(self.PASSWORD_INPUT, password)
    
    def click_login_button(self):
        """Click login button."""
        with allure.step("Click login button"):
            # Try regular click first with shorter timeout
            try:
                element = self.wait_for_element_clickable(self.LOGIN_BUTTON, timeout=10)
                element.click()
                self.logger.info("Successfully clicked login button with regular click")
            except Exception as e:
                if "timeout" in str(e).lower() and "renderer" in str(e).lower():
                    self.logger.warning(f"Chrome renderer timeout detected: {e}, handling timeout")
                    self.handle_renderer_timeout()
                    # Retry after handling timeout
                    try:
                        element = self.wait_for_element_clickable(self.LOGIN_BUTTON, timeout=5)
                        element.click()
                        self.logger.info("Successfully clicked login button after timeout handling")
                        return
                    except Exception as retry_error:
                        self.logger.error(f"Retry also failed: {retry_error}")
                
                self.logger.warning(f"Regular login click failed: {e}, trying JavaScript click")
                try:
                    # If regular click fails, try JavaScript click with shorter wait
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    short_wait = WebDriverWait(self.driver, 5)
                    element = short_wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON))
                    self.driver.execute_script("arguments[0].click();", element)
                    self.logger.info("Successfully clicked login button with JavaScript click")
                except Exception as js_error:
                    self.logger.error(f"JavaScript login click also failed: {js_error}")
                    # Try form submission as last resort
                    try:
                        # Try to find form with shorter timeout
                        from selenium.webdriver.support.ui import WebDriverWait
                        from selenium.webdriver.support import expected_conditions as EC
                        short_wait = WebDriverWait(self.driver, 3)
                        form = short_wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
                        self.driver.execute_script("arguments[0].submit();", form)
                        self.logger.info("Submitted login form as last resort")
                    except Exception as form_error:
                        self.logger.error(f"Form submission also failed: {form_error}")
                        # Final fallback: try pressing Enter on password field
                        try:
                            password_field = self.driver.find_element(*self.PASSWORD_INPUT)
                            password_field.send_keys("\n")
                            self.logger.info("Pressed Enter on password field as final fallback")
                        except Exception as enter_error:
                            self.logger.error(f"Enter key fallback also failed: {enter_error}")
                            raise
    
    def wait_for_login_completion(self):
        """Wait for login completion (either success or error)."""
        with allure.step("Wait for login completion"):
            # Wait a moment for the page to process
            import time
            time.sleep(2)



    def incorrect_login(self, username, password):
        """Perform login with given credentials and return True if error message appears."""
        with allure.step(f"Login with username: {username}"):
            # Wait for login form to be ready
            self.wait_for_login_page_load()
            
            # Enter email
            self.enter_email(username)
            
            # Enter password
            self.enter_password(password)
            
            # Click login button with fallback
            self.click_login_button()
            
            # Wait for page to process and check for error message
            return self.wait_for_error_message()
    
    def wait_for_error_message(self):
        """Wait for error message to appear and return True if displayed."""
        try:
            # Wait for error message to be visible
            if self.is_element_visible(self.ERROR_MESSAGE, timeout=10):
                self.logger.info("Error message detected after login attempt")
                return True
            else:
                self.logger.info("No error message detected after login attempt")
                return False
        except Exception as e:
            self.logger.error(f"Error waiting for error message: {e}")
            return False
    


    def get_error_message(self):
        """Get error message text."""
        if self.is_element_visible(self.ERROR_MESSAGE, timeout=5):
            return self.get_text(self.ERROR_MESSAGE)
        return None
    
    def is_error_message_displayed(self):
        """Check if error message is displayed."""
        return self.is_element_visible(self.ERROR_MESSAGE, timeout=5)
    
    def get_email_validation_message(self):
        """Get email validation message text."""
        if self.is_element_visible(self.EMAIL_VALIDATION, timeout=5):
            return self.get_text(self.EMAIL_VALIDATION)
        return None
    
    def get_password_validation_message(self):
        """Get password validation message text."""
        if self.is_element_visible(self.EMAIL_VALIDATION, timeout=5):
            return self.get_text(self.EMAIL_VALIDATION)
        return None
    
    def is_email_validation_displayed(self):
        """Check if email validation message is displayed."""
        return self.is_element_visible(self.EMAIL_VALIDATION, timeout=5)
    
    def is_password_validation_displayed(self):
        """Check if password validation message is displayed."""
        return self.is_element_visible(self.EMAIL_VALIDATION, timeout=5)
    
    def email_validation(self):
        """Check email field validation and return True if validation message is displayed."""
        try:
            if self.is_email_validation_displayed():
                self.logger.info("Email validation message detected")
                return True
            else:
                self.logger.info("No email validation message detected")
                return False
        except Exception as e:
            self.logger.error(f"Error checking email validation: {e}")
            return False
    
    def password_validation(self):
        """Check password field validation and return True if validation message is displayed."""
        try:
            if self.is_password_validation_displayed():
                self.logger.info("Password validation message detected")
                return True
            else:
                self.logger.info("No password validation message detected")
                return False
        except Exception as e:
            self.logger.error(f"Error checking password validation: {e}")
            return False
    


    def is_login_form_displayed(self):
        """Check if login form is displayed."""
        return self.is_element_visible(self.LOGIN_FORM)
    
    def is_login_button_enabled(self):
        """Check if login button is enabled."""
        try:
            button = self.wait_for_element(self.LOGIN_BUTTON)
            return button.is_enabled()
        except Exception:
            return False
    
    def click_register_link(self):
        """Click register link."""
        with allure.step("Click register link"):
            self.click_element(self.REGISTER_LINK)
    
    
    def wait_for_login_page_load(self):
        """Wait for login page to fully load."""
        with allure.step("Wait for login page to load"):
            self.wait_for_element(self.LOGIN_FORM)
            self.wait_for_element(self.EMAIL_INPUT)
            self.wait_for_element(self.PASSWORD_INPUT)
            self.wait_for_element(self.LOGIN_BUTTON)
    
    def get_page_title(self):
        """Get login page title."""
        return super().get_page_title()
    
    def is_login_page_loaded(self):
        """Check if login page is loaded successfully."""
        try:
            return (self.is_element_visible(self.EMAIL_INPUT) and 
                   self.is_element_visible(self.PASSWORD_INPUT) and 
                   self.is_element_visible(self.LOGIN_BUTTON))
        except Exception:
            return False
