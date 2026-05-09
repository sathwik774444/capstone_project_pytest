import time
import logging
import yaml
import os

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)

logger = logging.getLogger(__name__)


class Agentic:

    RETRYABLE_EXCEPTIONS = (
        TimeoutException,
        NoSuchElementException,
        StaleElementReferenceException,
        ElementClickInterceptedException
    )

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # SELF HEALING LOCATOR 
    # Done
    def find_element_with_healing(self, locators):

        last_exception = None

        for locator in locators:

            try:
                logger.info(f"[AGENTIC] Trying locator: {locator}")

                element = self.wait.until(
                    EC.presence_of_element_located(locator)
                )

                logger.info(f"[AGENTIC] Locator success: {locator}")

                return element

            except Exception as e:
                logger.warning(f"[AGENTIC] Locator failed: {locator}")
                last_exception = e

        raise last_exception

    # SAFE CLICK
    def intelligent_click(self, locators, retries=2):

        for attempt in range(retries + 1):

            try:

                element = self.find_element_with_healing(locators)

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    element
                )

                self.wait.until(
                    EC.element_to_be_clickable(locators[0])
                )

                element.click()

                logger.info("[AGENTIC] Normal click success")

                return True

            except self.RETRYABLE_EXCEPTIONS as e:

                logger.warning(
                    f"[AGENTIC] Click failed attempt {attempt+1}: {e}"
                )

                time.sleep(2)

                try:
                    element = self.find_element_with_healing(locators)

                    self.driver.execute_script(
                        "arguments[0].click();",
                        element
                    )

                    logger.info("[AGENTIC] JS click success")

                    return True

                except Exception as js_error:

                    logger.error(
                        f"[AGENTIC] JS click failed: {js_error}"
                    )

                    if attempt == retries:
                        raise

        return False

    # SAFE TYPE
    #used
    def intelligent_type(self, locators, text):

        element = self.find_element_with_healing(locators)

        element.clear()

        element.send_keys(text)

        logger.info(f"[AGENTIC] Typed text: {text}")

    # INTELLIGENT WAIT
    
    def wait_until_visible(self, locator):

        return self.wait.until(
            EC.visibility_of_element_located(locator)
        )
    
    def load_config(self):
        """Load configuration from config.yaml file."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"[AGENTIC] Failed to load config: {e}")
            return None
    
    #Auto-retry mechanism for flaky UI steps 
    #Done

    def retry_login(self, login_function, *args, **kwargs):
        """
        Auto-retry mechanism for flaky UI login operations.
        
        Args:
            login_function: The login function to retry
            *args: Arguments to pass to the login function
            **kwargs: Keyword arguments to pass to the login function
            
        Returns:
            bool: True if login succeeded, False otherwise
        """
        config = self.load_config()
        if not config:
            logger.error("[AGENTIC] No config found, using default retry values")
            retry_count = 3
            retry_delay = 2
        else:
            ui_retry_config = config.get('ui_retry', {})
            retry_count = ui_retry_config.get('login_retry_count', 3)
            retry_delay = ui_retry_config.get('login_retry_delay', 2)
        
        last_exception = None
        
        for attempt in range(retry_count + 1):  # +1 for initial attempt
            try:
                logger.info(f"[AGENTIC] Login attempt {attempt + 1} of {retry_count + 1}")
                
                # Call the login function
                result = login_function(*args, **kwargs)
                
                # Check if login was successful (no error message)
                if hasattr(result, '__call__'):
                    # If result is a function, call it to check success
                    success = result()
                else:
                    # If result is a boolean or other value, use it directly
                    success = result
                
                if success or success is None:  # None means no error detected
                    logger.info(f"[AGENTIC] Login successful on attempt {attempt + 1}")
                    return True
                else:
                    logger.warning(f"[AGENTIC] Login failed on attempt {attempt + 1} - error message detected")
                    raise Exception("Login failed - error message displayed")
                    
            except self.RETRYABLE_EXCEPTIONS as e:
                last_exception = e
                logger.warning(f"[AGENTIC] Login attempt {attempt + 1} failed with retryable exception: {e}")
                
                if attempt < retry_count:
                    logger.info(f"[AGENTIC] Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"[AGENTIC] All {retry_count + 1} login attempts failed")
                    
            except Exception as e:
                last_exception = e
                logger.error(f"[AGENTIC] Login attempt {attempt + 1} failed with non-retryable exception: {e}")
                # For non-retryable exceptions, don't retry
                break
        
        # If we get here, all retries failed
        logger.error(f"[AGENTIC] Login retry mechanism exhausted. Last error: {last_exception}")
        raise last_exception if last_exception else Exception("Login failed after all retry attempts")
    
    #Intelligent waiting system for login operations
    #Done
    
    def intelligent_wait_for_login_completion(self, success_indicators=None, error_indicators=None, timeout=30):
        """
        Intelligent waiting system that waits for login completion based on multiple indicators.
        
        Args:
            success_indicators: List of locators that indicate successful login
            error_indicators: List of locators that indicate login failure
            timeout: Maximum time to wait in seconds
            
        Returns:
            dict: Contains 'status' (success/error/timeout), 'indicator_found', and 'details'
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        
        # Default indicators for login success/failure
        if success_indicators is None:
            success_indicators = [
                (By.XPATH, "//div[contains(@class,'navbar')]//span[contains(text(),'Notes')]"),
                (By.XPATH, "//a[contains(@href,'/notes/app/profile')]"),
                (By.XPATH, "//button[contains(text(),'Logout')]"),
                (By.XPATH, "//div[contains(@class,'content')]//h1[contains(text(),'Notes')]")
            ]
        
        if error_indicators is None:
            error_indicators = [
                (By.CSS_SELECTOR, "div[data-testid='alert-message']"),
                (By.CSS_SELECTOR, ".alert-danger"),
                (By.CSS_SELECTOR, ".error-message"),
                (By.XPATH, "//div[contains(@class,'alert') and contains(@class,'danger')]")
            ]
        
        logger.info("[AGENTIC] Starting intelligent wait for login completion")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check for success indicators
                for i, locator in enumerate(success_indicators):
                    try:
                        element = self.driver.find_element(*locator)
                        if element.is_displayed():
                            logger.info(f"[AGENTIC] Login success detected via indicator {i+1}: {locator}")
                            return {
                                'status': 'success',
                                'indicator_found': locator,
                                'details': f"Success element found: {element.text[:50]}"
                            }
                    except:
                        continue
                
                # Check for error indicators
                for i, locator in enumerate(error_indicators):
                    try:
                        element = self.driver.find_element(*locator)
                        if element.is_displayed():
                            error_text = element.text
                            logger.warning(f"[AGENTIC] Login error detected via indicator {i+1}: {locator}")
                            return {
                                'status': 'error',
                                'indicator_found': locator,
                                'details': f"Error message: {error_text}"
                            }
                    except:
                        continue
                
                # Check URL changes as additional success indicator
                current_url = self.driver.current_url
                if 'login' not in current_url.lower() and 'notes/app' in current_url.lower():
                    logger.info(f"[AGENTIC] Login success detected via URL change: {current_url}")
                    return {
                        'status': 'success',
                        'indicator_found': 'URL_CHANGE',
                        'details': f"URL changed to: {current_url}"
                    }
                
                # Short sleep before next check
                time.sleep(0.5)
                
            except Exception as e:
                logger.debug(f"[AGENTIC] Wait check interrupted: {e}")
                time.sleep(0.5)
                continue
        
        # Timeout reached
        logger.error(f"[AGENTIC] Login completion wait timed out after {timeout} seconds")
        return {
            'status': 'timeout',
            'indicator_found': None,
            'details': f"No success or error indicators found within {timeout} seconds"
        }
    
    def adaptive_wait_for_element(self, locator, base_timeout=10, max_timeout=30, backoff_factor=1.5):
        """
        Adaptive waiting that increases timeout based on previous failures.
        
        Args:
            locator: Element locator tuple
            base_timeout: Initial timeout in seconds
            max_timeout: Maximum timeout in seconds
            backoff_factor: Multiplier for timeout increase
            
        Returns:
            WebElement: The found element or raises exception
        """
        current_timeout = base_timeout
        attempt = 1
        
        while current_timeout <= max_timeout:
            try:
                logger.info(f"[AGENTIC] Adaptive wait attempt {attempt} with timeout {current_timeout}s")
                wait = WebDriverWait(self.driver, current_timeout)
                element = wait.until(EC.presence_of_element_located(locator))
                logger.info(f"[AGENTIC] Element found on attempt {attempt}")
                return element
                
            except TimeoutException:
                logger.warning(f"[AGENTIC] Adaptive wait attempt {attempt} failed, increasing timeout")
                current_timeout = min(current_timeout * backoff_factor, max_timeout)
                attempt += 1
                time.sleep(1)  # Brief pause between attempts
        
        raise TimeoutException(f"Element not found after {attempt-1} adaptive attempts")
    
    def smart_wait_for_page_stability(self, stability_duration=2, max_wait=15):
        """
        Waits for page to become stable (no DOM changes for specified duration).
        
        Args:
            stability_duration: Seconds of no changes required for stability
            max_wait: Maximum time to wait for stability
            
        Returns:
            bool: True if page became stable, False if timed out
        """
        logger.info(f"[AGENTIC] Waiting for page stability for {stability_duration}s")
        start_time = time.time()
        last_dom_hash = None
        stable_start_time = None
        
        while time.time() - start_time < max_wait:
            try:
                # Get current DOM state
                current_dom = self.driver.page_source
                current_hash = hash(current_dom)
                
                if current_hash == last_dom_hash:
                    # DOM hasn't changed
                    if stable_start_time is None:
                        stable_start_time = time.time()
                        logger.debug("[AGENTIC] DOM stability started")
                    elif time.time() - stable_start_time >= stability_duration:
                        logger.info("[AGENTIC] Page stability achieved")
                        return True
                else:
                    # DOM changed, reset stability timer
                    last_dom_hash = current_hash
                    stable_start_time = None
                    logger.debug("[AGENTIC] DOM changed, resetting stability timer")
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.debug(f"[AGENTIC] Stability check interrupted: {e}")
                time.sleep(0.5)
        
        logger.warning(f"[AGENTIC] Page stability not achieved within {max_wait}s")
        return False
    
    def wait_with_progress_tracking(self, locator, timeout=30, check_interval=0.5):
        """
        Waits for element with progress tracking and detailed logging.
        
        Args:
            locator: Element locator tuple
            timeout: Maximum wait time in seconds
            check_interval: Time between checks in seconds
            
        Returns:
            WebElement: The found element
        """
        logger.info(f"[AGENTIC] Starting progress-tracked wait for {locator}")
        start_time = time.time()
        elapsed = 0
        
        while elapsed < timeout:
            try:
                element = self.driver.find_element(*locator)
                if element.is_displayed():
                    logger.info(f"[AGENTIC] Element found after {elapsed:.1f}s")
                    return element
                    
            except:
                pass
            
            elapsed = time.time() - start_time
            if int(elapsed) % 5 == 0 and elapsed > 0:  # Log every 5 seconds
                logger.info(f"[AGENTIC] Still waiting for element... {elapsed:.1f}s elapsed")
            
            time.sleep(check_interval)
        
        raise TimeoutException(f"Element {locator} not found after {timeout}s")
    
    #Decision-based rerun logic for login operations
    #Done
    
    def analyze_login_failure(self, exception, attempt_count, context=None):
        """
        Analyze login failure and provide intelligent decision on next steps.
        
        Args:
            exception: The exception that occurred
            attempt_count: Current attempt number (1-based)
            context: Additional context about the failure
            
        Returns:
            dict: Decision containing action, reason, and adjustments
        """
        from selenium.webdriver.common.by import By
        
        failure_analysis = {
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'attempt_count': attempt_count,
            'recommended_action': None,
            'reason': None,
            'adjustments': {}
        }
        
        # Analyze specific exception types
        if isinstance(exception, TimeoutException):
            if 'element not found' in str(exception).lower():
                failure_analysis.update({
                    'recommended_action': 'retry_with_longer_timeout',
                    'reason': 'Element loading timeout - likely slow network or heavy page',
                    'adjustments': {
                        'increase_timeout_factor': 1.5,
                        'add_stability_wait': True,
                        'use_alternative_locators': True
                    }
                })
            else:
                failure_analysis.update({
                    'recommended_action': 'retry_with_page_refresh',
                    'reason': 'General timeout - page might be stuck',
                    'adjustments': {
                        'refresh_page': True,
                        'extended_wait': True
                    }
                })
                
        elif isinstance(exception, NoSuchElementException):
            failure_analysis.update({
                'recommended_action': 'retry_with_healing',
                'reason': 'Element not found - possible DOM change or timing issue',
                'adjustments': {
                    'use_self_healing': True,
                    'wait_for_stability': True
                }
            })
            
        elif isinstance(exception, StaleElementReferenceException):
            failure_analysis.update({
                'recommended_action': 'retry_with_element_refresh',
                'reason': 'Stale element reference - DOM was updated',
                'adjustments': {
                    'refresh_element_reference': True,
                    'wait_for_dom_stability': True,
                    'shorter_actions': True
                }
            })
            
        elif isinstance(exception, ElementClickInterceptedException):
            failure_analysis.update({
                'recommended_action': 'retry_with_alternative_click',
                'reason': 'Element click intercepted - overlay or loading issue',
                'adjustments': {
                    'use_javascript_click': True,
                    'wait_for_overlay_disappear': True,
                    'scroll_to_element': True
                }
            })
        
        # Analyze attempt count for escalation
        if attempt_count >= 3:
            failure_analysis.update({
                'recommended_action': 'escalate_strategy',
                'reason': 'Multiple failures detected - using aggressive recovery',
                'adjustments': {
                    'full_page_refresh': True,
                    'maximum_timeout': True,
                    'fallback_locators': True,
                    'debug_mode': True
                }
            })
        
        # Check for specific error messages on page
        try:
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='alert-message'], .alert-danger, .error-message")
            if error_elements:
                error_text = error_elements[0].text.lower()
                if 'invalid' in error_text or 'incorrect' in error_text:
                    failure_analysis.update({
                        'recommended_action': 'abort_retry',
                        'reason': 'Credential validation error - retrying will not help',
                        'adjustments': {'should_abort': True}
                    })
                elif 'server' in error_text or 'network' in error_text:
                    failure_analysis.update({
                        'recommended_action': 'retry_with_delay',
                        'reason': 'Server/network error - temporary issue expected',
                        'adjustments': {
                            'increase_delay': True,
                            'exponential_backoff': True
                        }
                    })
        except:
            pass
        
        logger.info(f"[AGENTIC] Failure analysis: {failure_analysis['recommended_action']} - {failure_analysis['reason']}")
        return failure_analysis
    
    def execute_decision_based_retry(self, login_function, username, password, max_attempts=5):
        """
        Execute login with decision-based retry logic.
        
        Args:
            login_function: The login function to execute
            username: Login username
            password: Login password
            max_attempts: Maximum number of attempts
            
        Returns:
            dict: Result containing success status and execution details
        """
        config = self.load_config()
        base_retry_count = config.get('ui_retry', {}).get('login_retry_count', 3) if config else 3
        base_retry_delay = config.get('ui_retry', {}).get('login_retry_delay', 2) if config else 2
        
        execution_log = []
        last_exception = None
        current_adjustments = {}
        
        for attempt in range(1, max_attempts + 1):
            attempt_start = time.time()
            
            try:
                logger.info(f"[AGENTIC] Decision-based login attempt {attempt}/{max_attempts}")
                
                # Apply any adjustments from previous failure analysis
                if current_adjustments.get('refresh_page', False):
                    logger.info("[AGENTIC] Applying adjustment: Refreshing page")
                    self.driver.refresh()
                    time.sleep(2)
                
                if current_adjustments.get('wait_for_stability', False):
                    logger.info("[AGENTIC] Applying adjustment: Waiting for page stability")
                    self.smart_wait_for_page_stability(stability_duration=3, max_wait=10)
                
                # Execute login with current adjustments
                result = login_function(username, password)
                
                # Success - return result
                execution_time = time.time() - attempt_start
                execution_log.append({
                    'attempt': attempt,
                    'status': 'success',
                    'execution_time': execution_time,
                    'adjustments_applied': current_adjustments.copy()
                })
                
                logger.info(f"[AGENTIC] Login successful on attempt {attempt} after {execution_time:.2f}s")
                
                return {
                    'success': True,
                    'attempt': attempt,
                    'execution_time': execution_time,
                    'execution_log': execution_log,
                    'final_adjustments': current_adjustments
                }
                
            except Exception as e:
                last_exception = e
                execution_time = time.time() - attempt_start
                
                # Analyze the failure
                failure_analysis = self.analyze_login_failure(e, attempt, {
                    'execution_time': execution_time,
                    'previous_adjustments': current_adjustments
                })
                
                execution_log.append({
                    'attempt': attempt,
                    'status': 'failed',
                    'exception': str(e),
                    'execution_time': execution_time,
                    'failure_analysis': failure_analysis,
                    'adjustments_applied': current_adjustments.copy()
                })
                
                # Check if we should abort
                if failure_analysis['adjustments'].get('should_abort', False):
                    logger.warning(f"[AGENTIC] Aborting retry based on failure analysis: {failure_analysis['reason']}")
                    break
                
                # Prepare adjustments for next attempt
                current_adjustments = failure_analysis['adjustments']
                
                # Calculate delay for next attempt
                if attempt < max_attempts:
                    delay = base_retry_delay
                    if current_adjustments.get('increase_delay', False):
                        delay *= 2
                    if current_adjustments.get('exponential_backoff', False):
                        delay = delay * (2 ** (attempt - 1))
                    
                    delay = min(delay, 10)  # Cap at 10 seconds
                    
                    logger.info(f"[AGENTIC] Waiting {delay}s before next attempt (reason: {failure_analysis['reason']})")
                    time.sleep(delay)
        
        # All attempts failed
        logger.error(f"[AGENTIC] All {max_attempts} decision-based login attempts failed")
        
        return {
            'success': False,
            'attempts_made': attempt,
            'last_exception': str(last_exception),
            'execution_log': execution_log,
            'final_adjustments': current_adjustments
        }
    
    def apply_intelligent_adjustments(self, adjustments):
        """
        Apply intelligent adjustments based on failure analysis.
        
        Args:
            adjustments: Dictionary of adjustments to apply
        """
        if adjustments.get('use_alternative_locators', False):
            logger.info("[AGENTIC] Will use alternative locators in next attempt")
        
        if adjustments.get('use_javascript_click', False):
            logger.info("[AGENTIC] Will use JavaScript click in next attempt")
        
        if adjustments.get('wait_for_overlay_disappear', False):
            logger.info("[AGENTIC] Will wait for overlays to disappear")
            # Wait for any loading overlays to disappear
            try:
                from selenium.webdriver.common.by import By
                overlays = self.driver.find_elements(By.CSS_SELECTOR, ".loading, .overlay, .spinner")
                if overlays:
                    logger.info(f"[AGENTIC] Found {len(overlays)} overlay elements, waiting for them to disappear")
                    time.sleep(3)
            except:
                pass
        
        if adjustments.get('debug_mode', False):
            logger.info("[AGENTIC] Debug mode activated - capturing additional diagnostics")
            try:
                logger.info(f"[AGENTIC] Current URL: {self.driver.current_url}")
                logger.info(f"[AGENTIC] Page title: {self.driver.title}")
                # Capture screenshot for debugging
                self.driver.save_screenshot(f"debug_login_attempt_{int(time.time())}.png")
            except:
                pass