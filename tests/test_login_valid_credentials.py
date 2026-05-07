"""TC001: Test login with valid credentials."""

import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from config.environment import env_config


@allure.feature("Login")
@allure.story("User Authentication")
@allure.title("TC001: Test login with valid credentials")
@allure.description("Verify user can login successfully with valid credentials")
@allure.severity(allure.severity_level.CRITICAL)
def test_login_valid_credentials(browser):
    """Test successful login with valid credentials using stable locators."""
    # 🔹 Initialize pages
    login_page = LoginPage(browser)
    home_page = HomePage(browser)
    
    # 🔹 Navigate to login page
    login_page.navigate_to_login()
    
    # 🔹 Get test data
    valid_user = env_config.test_data["valid_user"]
    
    # 🔹 Perform login
    with allure.step("Perform login with valid credentials"):
        login_page.login(valid_user["username"], valid_user["password"])
    
    # 🔹 Skip explicit wait and validate home page directly (faster)
    with allure.step("Validate login success"):
        assert home_page.is_home_page_loaded(), "Login failed or home page not loaded"
        
        # Debug information
        print("Current URL:", browser.current_url)
        
        allure.attach(
            f"Login successful! Current URL: {browser.current_url}\nHome page validated: {home_page.is_home_page_loaded()}",
            name="Login Success Verification",
            attachment_type=allure.attachment_type.TEXT
        )
    
    
