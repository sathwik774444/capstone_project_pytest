"""Home page object for the notes application."""

from selenium.webdriver.common.by import By
from .base_page import BasePage
import allure


class HomePage(BasePage):
    """Page object for home page after successful login."""
    
    # Locators
    HOME_LINK = (By.CSS_SELECTOR, "a[data-testid='home']")
    
    def __init__(self, driver):
        """Initialize HomePage with WebDriver instance."""
        super().__init__(driver)
    
    def is_home_page_loaded(self):
        """Check if home page is loaded successfully."""
        try:
            # Wait for any of the home page indicators to be visible
            if self.is_element_visible(self.HOME_LINK, timeout=10):
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking home page load: {e}")
            return False
    
    def get_user_email(self):
        """Get user email from profile."""
        if self.is_element_visible(self.USER_EMAIL, timeout=5):
            return self.get_text(self.USER_EMAIL)
        return None
    
    def get_welcome_message(self):
        """Get welcome message text."""
        if self.is_element_visible(self.WELCOME_MESSAGE, timeout=5):
            return self.get_text(self.WELCOME_MESSAGE)
        return None
    
    def logout(self):
        """Perform logout action."""
        with allure.step("Logout from application"):
            if self.is_element_visible(self.LOGOUT_BUTTON):
                self.click_element(self.LOGOUT_BUTTON)
                self.wait_for_page_load()
            else:
                self.logger.warning("Logout button not found")
    
    def click_add_note_button(self):
        """Click add note button."""
        with allure.step("Click add note button"):
            self.click_element(self.ADD_NOTE_BUTTON)
    
    def get_notes_count(self):
        """Get count of notes displayed."""
        try:
            if self.is_element_visible(self.NOTES_LIST, timeout=5):
                notes = self.driver.find_elements(*self.NOTE_ITEM)
                return len(notes)
            return 0
        except Exception:
            return 0
    
    def is_user_profile_visible(self):
        """Check if user profile is visible."""
        return self.is_element_visible(self.USER_PROFILE, timeout=5)
    
    def is_logout_button_visible(self):
        """Check if logout button is visible."""
        return self.is_element_visible(self.LOGOUT_BUTTON, timeout=5)
    
    def is_add_note_button_visible(self):
        """Check if add note button is visible."""
        return self.is_element_visible(self.ADD_NOTE_BUTTON, timeout=5)
    
    def is_notes_list_visible(self):
        """Check if notes list is visible."""
        return self.is_element_visible(self.NOTES_LIST, timeout=5)
    
    def get_page_title(self):
        """Get home page title."""
        return super().get_page_title()
    
    def get_current_url(self):
        """Get current page URL."""
        return super().get_current_url()
    
    def validate_home_page_elements(self):
        """Validate all key home page elements are present."""
        validation_results = {}
        
        validation_results['user_profile'] = self.is_user_profile_visible()
        validation_results['logout_button'] = self.is_logout_button_visible()
        validation_results['add_note_button'] = self.is_add_note_button_visible()
        validation_results['notes_list'] = self.is_notes_list_visible()
        
        return validation_results
    
    def wait_for_element_visible(self, locator, timeout=10):
        """Wait for specific element to be visible."""
        return self.wait_for_element(locator, timeout)
