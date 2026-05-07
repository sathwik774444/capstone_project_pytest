"""TC006: Test create note with valid details."""

import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.notes_page import NotesPage
from config.environment import env_config


@allure.feature("Notes")
@allure.story("Note Creation")
@allure.title("TC006: Test create note with valid details")
@allure.description("Verify user can create a note with valid title and description")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_note_with_valid_details(browser):
    """Test creating a note with valid title and description."""
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
    
    # 🔹 Get initial notes count
    initial_notes_count = notes_page.get_notes_count()
    
    # Create a new note
    with allure.step(f"Create note with title: {note_data['title']}"):
        notes_page.create_note(note_data['title'], note_data['description'])
    
    # Verify note creation success
    with allure.step("Verify note creation success"):
        # Wait for note to be created
        import time
        time.sleep(2)
        
        # Check if note with created title is visible
        assert notes_page.is_note_with_title_visible(note_data['title']), f"Note with title '{note_data['title']}' should be visible"
    
    # Log test results
    final_notes_count = notes_page.get_notes_count()
    allure.attach(
        f"Note Created Successfully!\nTitle: {note_data['title']}\nDescription: {note_data['description']}\nTotal Notes: {final_notes_count}",
        name="Note Creation Details",
        attachment_type=allure.attachment_type.TEXT
    )