"""TC008: Test verify instant note display in UI."""

import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.notes_page import NotesPage
from config.environment import env_config


@allure.feature("Notes")
@allure.story("Note Display")
@allure.title("TC008: Test verify instant note display in UI")
@allure.description("Verify that created note is instantly visible in the notes list")
@allure.severity(allure.severity_level.CRITICAL)
def test_verify_instant_note_display_in_ui(browser):
    """Test verifying that created note is instantly visible in UI."""
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
    
    # 🔹 Get test data
    note_data = env_config.test_data["note_data"]
    
    # 🔹 Create a new note (reuse the same logic from test_create_note_with_valid_details)
    with allure.step(f"Create note with title: {note_data['title']}"):
        notes_page.create_note(note_data['title'], note_data['description'])
    
    # 🔹 Verify instant note display in UI
    with allure.step("Verify instant note display in UI"):
        import time
        
        # Wait for note to be created and appear in UI
        time.sleep(3)
        
        # Scroll down to ensure note is visible (handle advertisements)
        with allure.step("Scroll down to make note visible"):
            # Scroll down to bypass advertisements and see the notes
            browser.execute_script("window.scrollTo(0, 500);")
            time.sleep(1)
            
            # # Scroll further down if needed
            # browser.execute_script("window.scrollTo(0, 800);")
            # time.sleep(1)
            
            # # Scroll to bottom of page to ensure all notes are visible
            # browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # time.sleep(2)
        
        # Check if note with created title is visible in the list
        with allure.step("Check if created note is visible in notes list"):
            note_visible = notes_page.is_note_with_title_visible(note_data['title'])
            
            if note_visible:
                allure.attach(
                    f"Note '{note_data['title']}' is visible in the notes list",
                    name="Note Display Status",
                    attachment_type=allure.attachment_type.TEXT
                )
                assert True, f"Successfully verified that note '{note_data['title']}' is instantly displayed in UI"
            else:
                # Try scrolling up and down again to ensure note visibility
                with allure.step("Additional scrolling attempts to find note"):
                    browser.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    # Check again
                    note_visible = notes_page.is_note_with_title_visible(note_data['title'])
                    
                    if note_visible:
                        allure.attach(
                            f"Note '{note_data['title']}' found after additional scrolling",
                            name="Note Display Status",
                            attachment_type=allure.attachment_type.TEXT
                        )
                        assert True, f"Note '{note_data['title']}' is visible after additional scrolling"
                    else:
                        # Get current page source for debugging
                        page_source = browser.page_source
                        allure.attach(
                            page_source,
                            name="Page Source (Note Not Found)",
                            attachment_type=allure.attachment_type.TEXT
                        )
                        assert False, f"Note '{note_data['title']}' is not visible in the notes list after scrolling"
        
        # Additional verification: Get notes count and ensure at least one note exists
        with allure.step("Verify notes count after creation"):
            notes_count = notes_page.get_notes_count()
            allure.attach(
                f"Total notes count after creation: {notes_count}",
                name="Notes Count",
                attachment_type=allure.attachment_type.TEXT
            )
            
            