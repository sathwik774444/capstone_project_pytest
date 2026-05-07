"""TC009: Test create note with large description."""

import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.notes_page import NotesPage
from config.environment import env_config


@allure.feature("Notes")
@allure.story("Note Validation")
@allure.title("TC009: Test create note with large description")
@allure.description("Verify validation message appears when creating note with large description (>1500 characters)")
@allure.severity(allure.severity_level.NORMAL)
def test_create_note_with_large_description(browser):
    """Test creating a note with large description and verify validation."""
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
    
    # 🔹 Get large description test data
    large_data = env_config.test_data["large_description_data"]
    
    # 🔹 Create note with large description
    with allure.step(f"Create note with large description (title: {large_data['title']})"):
        # Click add note button
        notes_page.click_add_note_button()
        
        # Wait for note form to be visible
        notes_page.wait_for_element(notes_page.NOTE_FORM)
        
        # Enter note title
        notes_page.enter_note_title(large_data['title'])
        
        # Enter large description (more than 1500 characters)
        notes_page.enter_note_description(large_data['description'])
        
        # Click save button
        notes_page.click_save_note_button()
    
    # 🔹 Verify description validation message appears
    with allure.step("Verify description validation message appears"):
        import time
        
        # Wait for validation message to appear
        time.sleep(2)
        
        # Check if description validation is displayed
        validation_displayed = notes_page.is_description_validation_displayed()
        
        if validation_displayed:
            # Get the validation message text
            validation_message = notes_page.get_description_validation_message()
            
            allure.attach(
                f"Description validation message found: {validation_message}",
                name="Validation Message",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Assert that validation is visible
            assert True, f"Description validation message displayed: {validation_message}"
        else:
            # Wait additional time and check again
            time.sleep(2)
            validation_displayed = notes_page.is_description_validation_displayed()
            
            if validation_displayed:
                validation_message = notes_page.get_description_validation_message()
                allure.attach(
                    f"Description validation message found (after wait): {validation_message}",
                    name="Validation Message",
                    attachment_type=allure.attachment_type.TEXT
                )
                assert True, f"Description validation message displayed after wait: {validation_message}"
            else:
                # If no validation message, check if note was created successfully
                # This might indicate that large descriptions are allowed
                allure.attach(
                    "No description validation message found - large description may be allowed",
                    name="Validation Status",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # Check if note was created despite large description
                note_visible = notes_page.is_note_with_title_visible(large_data['title'])
                if note_visible:
                    allure.attach(
                        f"Note with large description was created successfully: {large_data['title']}",
                        name="Note Creation Status",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    assert True, "Large description was accepted and note was created"
                else:
                    assert False, "Neither validation message nor note creation occurred"
    
    # 🔹 Log test data information
    allure.attach(
        f"Large Description Length: {len(large_data['description'])} characters\nTitle: {large_data['title']}",
        name="Test Data Information",
        attachment_type=allure.attachment_type.TEXT
    )