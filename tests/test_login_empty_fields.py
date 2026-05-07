"""TC004: Test login with empty username and password fields."""

import pytest
import allure
from pages.login_page import LoginPage


@allure.feature("Login")
@allure.story("User Authentication")
@allure.title("TC004: Test login with empty username and password fields")
@allure.description("Verify login fails with empty username and password fields")
@allure.severity(allure.severity_level.NORMAL)
def test_login_empty_fields(browser):
    """Test login failure with empty fields."""
    login_page = LoginPage(browser)
    
    # Navigate to login page
    login_page.navigate_to_login()
    
    with allure.step("Attempt login with empty username and password"):
        login_page.login("", "")
    
    # Wait for login to complete
    login_page.wait_for_login_completion()
    
    # Verify login failure
    with allure.step("Verify login failure"):
        # Check if still on login page
        assert login_page.is_login_form_displayed(), "User should remain on login page"
        
        # Check if error message is displayed
        assert login_page.is_email_validation_displayed(), "Error message should be displayed"
        
        # Get error message
        error_msg = login_page.get_email_validation_message()
        assert error_msg, "Error message should not be empty"
        
        # Verify error message content
        assert any(keyword in error_msg.lower() for keyword in ["required", "empty", "invalid", "error"]), \
            f"Error message should indicate required fields: {error_msg}"
    
    allure.attach(
        f"Error Message: {error_msg}\nCurrent URL: {browser.current_url}",
        name="Login Failure Details",
        attachment_type=allure.attachment_type.TEXT
    )
