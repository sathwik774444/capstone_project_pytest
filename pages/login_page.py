"""Login page object for the notes application."""

from selenium.webdriver.common.by import By
from .base_page import BasePage
from utils.agentic import Agentic
import allure


class LoginPage(BasePage):
    """Page object for login page."""
    
    # Primary Locators
    BASE_LOGIN_BUTTON = (By.CSS_SELECTOR, "a[href='/notes/app/login']")
    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[data-testid='login-submit']")
    LOGIN_FORM = (By.TAG_NAME, "form")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "div[data-testid='alert-message']")
    EMAIL_VALIDATION = (By.CSS_SELECTOR, "div.invalid-feedback")
    
    # Self-Healing Alternative Locators
    EMAIL_INPUT_HEALING = [
        (By.ID, "email"),
        (By.NAME, "email"),
        (By.CSS_SELECTOR, "input[data-testid='login-email']")
    ]
    
    PASSWORD_INPUT_HEALING = [
        (By.ID, "password"),
        (By.NAME, "password"),
        (By.CSS_SELECTOR, "input[data-testid='login-password']")
    ]
    
    LOGIN_BUTTON_HEALING = [
        (By.CSS_SELECTOR, "button[data-testid='login-submit']"),
        (By.XPATH, "//button[contains(text(),'Login')]")
    ]
    
    def __init__(self, driver):
        """Initialize LoginPage with WebDriver instance."""
        super().__init__(driver)
        self.agentic = Agentic(driver)
    
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
        """Perform login with given credentials using intelligent waiting system."""
        with allure.step(f"Login with username: {username}"):
            # Wait for login form to be ready using adaptive wait
            self.wait_for_login_page_load()
            
            # Wait for page stability before entering credentials
            self.agentic.smart_wait_for_page_stability(stability_duration=1, max_wait=10)
            
            # Enter email with progress tracking
            with allure.step("Enter email with intelligent wait"):
                self.agentic.wait_with_progress_tracking(self.EMAIL_INPUT, timeout=15)
                self.enter_email(username)
            
            # Enter password with progress tracking
            with allure.step("Enter password with intelligent wait"):
                self.agentic.wait_with_progress_tracking(self.PASSWORD_INPUT, timeout=15)
                self.enter_password(password)
            
            # Click login button with fallback
            self.click_login_button()
            
            # Use intelligent wait for login completion
            with allure.step("Wait for login completion with intelligent indicators"):
                result = self.agentic.intelligent_wait_for_login_completion(timeout=30)
                
                # Log the result for debugging
                self.logger.info(f"Login completion result: {result['status']} - {result['details']}")
                
                # Attach result to Allure report
                allure.attach(
                    f"Login Status: {result['status']}\nIndicator: {result['indicator_found']}\nDetails: {result['details']}",
                    name="Intelligent Login Completion Result",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # Wait for page stability after login
                if result['status'] == 'success':
                    self.agentic.smart_wait_for_page_stability(stability_duration=2, max_wait=15)
    
    def login_with_retry(self, username, password):
        """
        Perform login with auto-retry mechanism for flaky UI.
        Uses configuration from config.yaml for retry count and delay.
        """
        with allure.step(f"Login with retry mechanism for username: {username}"):
            try:
                # Use the agentic retry mechanism
                return self.agentic.retry_login(self._perform_login, username, password)
            except Exception as e:
                self.logger.error(f"Login with retry failed: {e}")
                raise
    
    def login_with_decision_based_retry(self, username, password, max_attempts=5):
        """
        Perform login with decision-based retry logic that analyzes failures and adjusts strategy.
        
        Args:
            username: Login username
            password: Login password
            max_attempts: Maximum number of retry attempts
            
        Returns:
            dict: Login result with detailed execution information
        """
        with allure.step(f"Decision-based retry login for username: {username}"):
            try:
                # Use the decision-based retry mechanism
                result = self.agentic.execute_decision_based_retry(
                    self._perform_login_with_adjustments, 
                    username, 
                    password, 
                    max_attempts
                )
                
                # Log the result
                if result['success']:
                    self.logger.info(f"Decision-based login successful on attempt {result['attempt']}")
                    allure.attach(
                        f"Login successful!\nAttempt: {result['attempt']}\nTime: {result['execution_time']:.2f}s\nAdjustments: {result['final_adjustments']}",
                        name="Decision-Based Login Success",
                        attachment_type=allure.attachment_type.TEXT
                    )
                else:
                    self.logger.error(f"Decision-based login failed after {result['attempts_made']} attempts")
                    allure.attach(
                        f"Login failed!\nAttempts: {result['attempts_made']}\nLast error: {result['last_exception']}\nExecution log: {result['execution_log']}",
                        name="Decision-Based Login Failure",
                        attachment_type=allure.attachment_type.TEXT
                    )
                
                return result
                
            except Exception as e:
                self.logger.error(f"Decision-based login failed with exception: {e}")
                raise
    
    def _perform_login_with_adjustments(self, username, password):
        """
        Internal method that performs login with intelligent adjustments.
        This method is called by the decision-based retry system.
        """
        # Apply any intelligent adjustments before login
        adjustments = getattr(self, '_current_adjustments', {})
        if adjustments:
            self.agentic.apply_intelligent_adjustments(adjustments)
        
        # Perform the actual login using the enhanced login method
        self.login(username, password)
        
        # Check if login was successful
        return not self.is_error_message_displayed()
    
    def _perform_login(self, username, password):
        """
        Internal method to perform the actual login operation.
        Returns True if successful, False if error message is displayed.
        """
        try:
            # Use the existing login method to perform the login operation
            self.login(username, password)
            
            # Check if login was successful (no error message)
            if not self.is_error_message_displayed():
                self.logger.info("Login completed successfully - no error message detected")
                return True
            else:
                self.logger.warning("Login failed - error message detected")
                return False
                
        except Exception as e:
            self.logger.error(f"Login operation failed: {e}")
            raise
    
    def enter_email(self, email):
        """Enter email in email input field with self-healing capability."""
        with allure.step(f"Enter email: {email}"):
            try:
                # Attempt with primary locator first
                self.type_text(self.EMAIL_INPUT, email)
                self.logger.info(f"Email entered successfully using primary locator: {self.EMAIL_INPUT}")
            except Exception as primary_error:
                self.logger.warning(f"Primary email locator failed: {primary_error}")
                try:
                    # Fallback to self-healing locators
                    self.agentic.intelligent_type(self.EMAIL_INPUT_HEALING, email)
                    self.logger.info("Email entered successfully using self-healing locators")
                except Exception as healing_error:
                    self.logger.error(f"All email locators failed - Primary: {primary_error}, Healing: {healing_error}")
                    raise Exception(f"Unable to enter email using any locator strategy. Primary error: {primary_error}, Healing error: {healing_error}")
    
    def enter_password(self, password):
        """Enter password in password input field with self-healing capability."""
        with allure.step("Enter password"):
            try:
                # Attempt with primary locator first
                self.type_text(self.PASSWORD_INPUT, password)
                self.logger.info(f"Password entered successfully using primary locator: {self.PASSWORD_INPUT}")
            except Exception as primary_error:
                self.logger.warning(f"Primary password locator failed: {primary_error}")
                try:
                    # Fallback to self-healing locators
                    self.agentic.intelligent_type(self.PASSWORD_INPUT_HEALING, password)
                    self.logger.info("Password entered successfully using self-healing locators")
                except Exception as healing_error:
                    self.logger.error(f"All password locators failed - Primary: {primary_error}, Healing: {healing_error}")
                    raise Exception(f"Unable to enter password using any locator strategy. Primary error: {primary_error}, Healing error: {healing_error}")
    
    def click_login_button(self):
        """Click login button with self-healing capability."""
        with allure.step("Click login button"):
            try:
                # Attempt with primary locator first
                element = self.wait_for_element_clickable(self.LOGIN_BUTTON, timeout=10)
                element.click()
                self.logger.info(f"Login button clicked successfully using primary locator: {self.LOGIN_BUTTON}")
            except Exception as primary_error:
                self.logger.warning(f"Primary login button locator failed: {primary_error}")
                try:
                    # Fallback to self-healing locators
                    success = self.agentic.intelligent_click(self.LOGIN_BUTTON_HEALING, retries=2)
                    if success:
                        self.logger.info("Login button clicked successfully using self-healing locators")
                    else:
                        raise Exception("Self-healing click returned False")
                except Exception as healing_error:
                    self.logger.error(f"All login button locators failed - Primary: {primary_error}, Healing: {healing_error}")
                    raise Exception(f"Unable to click login button using any locator strategy. Primary error: {primary_error}, Healing error: {healing_error}")
    
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
    
    def incorrect_login_with_retry(self, username, password):
        """
        Perform incorrect login with auto-retry mechanism for flaky UI.
        Returns True if error message appears after successful retry.
        """
        with allure.step(f"Incorrect login with retry mechanism for username: {username}"):
            try:
                # Use the agentic retry mechanism
                return self.agentic.retry_login(self._perform_incorrect_login, username, password)
            except Exception as e:
                self.logger.error(f"Incorrect login with retry failed: {e}")
                raise
    
    def _perform_incorrect_login(self, username, password):
        """
        Internal method to perform the actual incorrect login operation.
        Returns True if error message is displayed (expected for invalid credentials).
        """
        try:
            # Use the existing incorrect_login method to perform the login operation
            has_error = self.incorrect_login(username, password)
            
            if has_error:
                self.logger.info("Incorrect login test passed - error message detected as expected")
                return True
            else:
                self.logger.warning("Incorrect login test failed - no error message detected")
                return False
                
        except Exception as e:
            self.logger.error(f"Incorrect login operation failed: {e}")
            raise
    
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
        """Wait for login page to fully load with intelligent waiting system."""
        with allure.step("Wait for login page to load with intelligent waiting"):
            try:
                # Wait for page stability first
                self.agentic.smart_wait_for_page_stability(stability_duration=1, max_wait=10)
                
                # Use adaptive wait for primary locators
                self.agentic.adaptive_wait_for_element(self.LOGIN_FORM, base_timeout=5, max_timeout=15)
                self.agentic.adaptive_wait_for_element(self.EMAIL_INPUT, base_timeout=5, max_timeout=15)
                self.agentic.adaptive_wait_for_element(self.PASSWORD_INPUT, base_timeout=5, max_timeout=15)
                self.agentic.adaptive_wait_for_element(self.LOGIN_BUTTON, base_timeout=5, max_timeout=15)
                
                self.logger.info("Login page loaded successfully using adaptive waiting")
                
                # Additional stability check
                if self.agentic.smart_wait_for_page_stability(stability_duration=1, max_wait=5):
                    self.logger.info("Login page stability confirmed")
                
            except Exception as primary_error:
                self.logger.warning(f"Primary intelligent page load wait failed: {primary_error}")
                try:
                    # Fallback to self-healing with intelligent waiting
                    self.agentic.adaptive_wait_for_element(self.LOGIN_FORM, base_timeout=3, max_timeout=10)
                    self.agentic.wait_with_progress_tracking(self.EMAIL_INPUT_HEALING[0], timeout=10)
                    self.agentic.wait_with_progress_tracking(self.PASSWORD_INPUT_HEALING[0], timeout=10)
                    self.agentic.wait_with_progress_tracking(self.LOGIN_BUTTON_HEALING[0], timeout=10)
                    
                    # Final stability check
                    self.agentic.smart_wait_for_page_stability(stability_duration=1, max_wait=5)
                    
                    self.logger.info("Login page loaded successfully using intelligent self-healing")
                except Exception as healing_error:
                    self.logger.error(f"Login page load failed with all intelligent strategies - Primary: {primary_error}, Healing: {healing_error}")
                    raise Exception(f"Unable to wait for login page load using any intelligent locator strategy. Primary error: {primary_error}, Healing error: {healing_error}")
    
    def get_page_title(self):
        """Get login page title."""
        return super().get_page_title()
    
    def is_login_page_loaded(self):
        """Check if login page is loaded successfully with self-healing capability."""
        try:
            # Try primary locators first
            if (self.is_element_visible(self.EMAIL_INPUT) and 
                self.is_element_visible(self.PASSWORD_INPUT) and 
                self.is_element_visible(self.LOGIN_BUTTON)):
                self.logger.info("Login page verified using primary locators")
                return True
        except Exception as primary_error:
            self.logger.warning(f"Primary page load verification failed: {primary_error}")
        
        try:
            # Fallback to self-healing locators
            if (self.agentic.wait_until_visible(self.EMAIL_INPUT_HEALING[0]) and
                self.agentic.wait_until_visible(self.PASSWORD_INPUT_HEALING[0]) and
                self.agentic.wait_until_visible(self.LOGIN_BUTTON_HEALING[0])):
                self.logger.info("Login page verified using self-healing locators")
                return True
        except Exception as healing_error:
            self.logger.error(f"Page load verification failed with all strategies - Primary: {primary_error}, Healing: {healing_error}")
        
        return False
