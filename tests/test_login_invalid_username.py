"""TC002: Test login with invalid username."""

import pytest
import allure
from pages.login_page import LoginPage
from config.environment import env_config


@allure.feature("Login")
@allure.story("User Authentication")
@allure.title("TC002: Test login with invalid username")
@allure.description("Verify login fails with invalid username and valid password")
@allure.severity(allure.severity_level.NORMAL)
def test_login_invalid_username(browser):
    """Test login failure with invalid username."""
    login_page = LoginPage(browser)
    
    # Navigate to login page
    login_page.navigate_to_login()
    
    # Get test data
    invalid_user = env_config.test_data["invalid_user"]
    valid_user = env_config.test_data["valid_user"]

    with allure.step("Attempt login with invalid username"):
        login_page.incorrect_login(invalid_user["username"], valid_user["password"])
    
    
    # Verify login failure
    with allure.step("Verify login failure"):
        # Check if still on login page
        assert login_page.is_login_form_displayed(), "User should remain on login page"
        
        # Check if error message is displayed
        assert login_page.is_error_message_displayed(), "Error message should be displayed"
        
        # Get error message
        error_msg = login_page.get_error_message()
        assert error_msg, "Error message should not be empty"
        
        # Verify error message content
        assert any(keyword in error_msg.lower() for keyword in ["invalid", "failed", "incorrect", "error"]), \
            f"Error message should indicate failure: {error_msg}"
    
    allure.attach(
        f"Error Message: {error_msg}\nCurrent URL: {browser.current_url}",
        name="Login Failure Details",
        attachment_type=allure.attachment_type.TEXT
    )
