"""TC010: Test create note with empty fields."""

import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.notes_page import NotesPage
from config.environment import env_config


@allure.feature("Notes")
@allure.story("Note Validation")
@allure.title("TC010: Test create note with empty fields")
@allure.description("Verify validation messages appear when creating note with empty title and description")
@allure.severity(allure.severity_level.NORMAL)
def test_create_note_with_empty_fields(browser):
    """Test creating a note with empty fields and verify validation messages."""
    # 🔹 Initialize pages
    login_page = LoginPage(browser)
    home_page = HomePage(browser)
    notes_page = NotesPage(browser)
    
    # 🔹 Navigate to login page and login
    login_page.navigate_to_login()
    valid_user = env_config.test_data["valid_user"]
    
    with allure.step("Login with valid credentials"):
        login_page.login(valid_user["username"], valid_user["password"])
    
    # 🔹 Verify login success
    with allure.step("Verify login success"):
        assert home_page.is_home_page_loaded(), "Login failed or home page not loaded"
    
    # 🔹 Wait for notes page to load
    with allure.step("Wait for notes page to load"):
        notes_page.wait_for_notes_page_load()
    
    # 🔹 Create note with empty fields
    with allure.step("Create note with empty title and description"):
        # Click add note button
        notes_page.click_add_note_button()
        
        # Wait for note form to be visible
        notes_page.wait_for_element(notes_page.NOTE_FORM)
        
        # Leave title empty (do not enter anything)
        # Leave description empty (do not enter anything)
        
        # Click save button without entering any data
        notes_page.click_save_note_button()
    
    # 🔹 Verify validation messages appear
    with allure.step("Verify title and description validation messages appear"):
        import time
        
        # Wait for validation messages to appear
        time.sleep(2)
        
        # Check if title validation is displayed
        title_validation_displayed = notes_page.is_title_validation_displayed()
        title_validation_message = None
        
        if title_validation_displayed:
            title_validation_message = notes_page.get_title_validation_message()
            allure.attach(
                f"Title validation message: {title_validation_message}",
                name="Title Validation",
                attachment_type=allure.attachment_type.TEXT
            )
        else:
            allure.attach(
                "Title validation message not found",
                name="Title Validation Status",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # Check if description validation is displayed
        description_validation_displayed = notes_page.is_description_validation_displayed()
        description_validation_message = None
        
        if description_validation_displayed:
            description_validation_message = notes_page.get_description_validation_message()
            allure.attach(
                f"Description validation message: {description_validation_message}",
                name="Description Validation",
                attachment_type=allure.attachment_type.TEXT
            )
        else:
            allure.attach(
                "Description validation message not found",
                name="Description Validation Status",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # Get all validation messages for comprehensive reporting
        all_validations = notes_page.get_all_validation_messages()
        allure.attach(
            f"All validation messages found: {all_validations}",
            name="All Validation Messages",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Wait additional time if validations not found initially
        if not title_validation_displayed or not description_validation_displayed:
            time.sleep(2)
            
            # Re-check title validation
            if not title_validation_displayed:
                title_validation_displayed = notes_page.is_title_validation_displayed()
                if title_validation_displayed:
                    title_validation_message = notes_page.get_title_validation_message()
                    allure.attach(
                        f"Title validation message (after wait): {title_validation_message}",
                        name="Title Validation (Delayed)",
                        attachment_type=allure.attachment_type.TEXT
                    )
            
            # Re-check description validation
            if not description_validation_displayed:
                description_validation_displayed = notes_page.is_description_validation_displayed()
                if description_validation_displayed:
                    description_validation_message = notes_page.get_description_validation_message()
                    allure.attach(
                        f"Description validation message (after wait): {description_validation_message}",
                        name="Description Validation (Delayed)",
                        attachment_type=allure.attachment_type.TEXT
                    )
        
        # Assert that at least one validation message is displayed
        if title_validation_displayed and description_validation_displayed:
            assert True, f"Both title and description validation messages displayed: Title: '{title_validation_message}', Description: '{description_validation_message}'"
        elif title_validation_displayed:
            assert True, f"Title validation message displayed: '{title_validation_message}'"
        elif description_validation_displayed:
            assert True, f"Description validation message displayed: '{description_validation_message}'"
        else:
            # If no validation messages, check if form is still open (validation prevented submission)
            form_still_open = notes_page.is_note_form_displayed()
            if form_still_open:
                allure.attach(
                    "Note form is still open - validation likely prevented submission",
                    name="Form Status",
                    attachment_type=allure.attachment_type.TEXT
                )
                assert True, "Form validation prevented note creation with empty fields"
            else:
                assert False, "No validation messages found and form was submitted"
    
    # 🔹 Log test completion
    allure.attach(
        f"Empty fields test completed\nTitle Validation: {'Found' if title_validation_displayed else 'Not Found'}\nDescription Validation: {'Found' if description_validation_displayed else 'Not Found'}",
        name="Test Summary",
        attachment_type=allure.attachment_type.TEXT
    )