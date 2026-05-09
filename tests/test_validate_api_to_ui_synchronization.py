"""TC017: Validate API to UI synchronization for note deletion."""

import pytest
import allure
import requests
import json
import time

from selenium.webdriver.common.by import By

from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.notes_page import NotesPage
from config.environment import env_config


@allure.feature("API-UI Integration")
@allure.story("Note Deletion Synchronization")
@allure.title("TC017: Validate API to UI synchronization for note deletion")
@allure.severity(allure.severity_level.CRITICAL)
def test_validate_api_to_ui_synchronization(browser):

    # ==========================================
    # CONFIGURATION
    # ==========================================

    api_config = env_config.api_config
    api_url = env_config.api_url

    timeout = api_config.get("timeout", 30)

    valid_user = env_config.test_data["valid_user"]
    note_data = env_config.test_data["note_data_e2e"]

    login_endpoint = f"{api_url}/users/login"
    notes_endpoint = f"{api_url}/notes"

    auth_token = None
    created_note_id = None

    # ==========================================
    # STEP 1 - LOGIN VIA API
    # ==========================================

    with allure.step("Login via API"):

        login_response = requests.post(
            login_endpoint,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={
                "email": valid_user["username"],
                "password": valid_user["password"]
            }
        )

        print("LOGIN STATUS:", login_response.status_code)
        print("LOGIN RESPONSE:", login_response.text)

        allure.attach(
            login_response.text,
            name="Login API Response",
            attachment_type=allure.attachment_type.TEXT
        )

        assert login_response.status_code == 200, \
            f"Login failed: {login_response.status_code}"

        login_data = login_response.json()

        auth_token = login_data["data"]["token"]

        assert auth_token is not None, \
            "Authentication token not found"

    # ==========================================
    # STEP 2 - CREATE NOTE VIA API
    # ==========================================

    with allure.step("Create note via API"):

        create_response = requests.post(
            notes_endpoint,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-auth-token": auth_token
            },
            json={
                "title": note_data["title"],
                "description": note_data["description"],
                "category": "Home"
            }
        )

        print("CREATE STATUS:", create_response.status_code)
        print("CREATE RESPONSE:", create_response.text)

        allure.attach(
            create_response.text,
            name="Create Note Response",
            attachment_type=allure.attachment_type.TEXT
        )

        assert create_response.status_code in [200, 201], \
            f"Failed to create note: {create_response.status_code}"

        create_data = create_response.json()

        created_note_id = create_data["data"]["id"]

        assert created_note_id is not None, \
            "Created note ID not found"

    # ==========================================
    # STEP 3 - DELETE NOTE VIA API
    # ==========================================

    with allure.step("Delete note via API"):

        delete_endpoint = f"{notes_endpoint}/{created_note_id}"

        delete_response = requests.delete(
            delete_endpoint,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-auth-token": auth_token
            }
        )

        print("DELETE STATUS:", delete_response.status_code)
        print("DELETE RESPONSE:", delete_response.text)

        allure.attach(
            delete_response.text,
            name="Delete Note Response",
            attachment_type=allure.attachment_type.TEXT
        )

        assert delete_response.status_code in [200, 202, 204], \
            f"Delete failed: {delete_response.status_code}"

    # ==========================================
    # STEP 4 - LOGIN TO UI
    # ==========================================

    login_page = LoginPage(browser)
    home_page = HomePage(browser)
    notes_page = NotesPage(browser)

    with allure.step("Login to UI"):

        login_page.navigate_to_login()

        login_page.login(
            valid_user["username"],
            valid_user["password"]
        )

        assert home_page.is_home_page_loaded(), \
            "Home page not loaded"

    # ==========================================
    # STEP 5 - REFRESH NOTES PAGE
    # ==========================================

    with allure.step("Refresh notes page"):

        notes_page.wait_for_notes_page_load()

        browser.refresh()

        time.sleep(3)

    # ==========================================
    # STEP 6 - VALIDATE NOTE NOT VISIBLE
    # ==========================================

    with allure.step("Validate deleted note not visible in UI"):

        note_elements = browser.find_elements(
            By.CSS_SELECTOR,
            ".note-item, .note, [class*='note'], [class*='card']"
        )

        ui_notes = []

        for element in note_elements:

            try:

                note_text = element.text.strip()

                if note_text:
                    ui_notes.append(note_text)

            except Exception:
                continue

        allure.attach(
            json.dumps(ui_notes, indent=2),
            name="Available Notes In UI",
            attachment_type=allure.attachment_type.JSON
        )

        deleted_note_found = any(
            note_data["title"] in note
            for note in ui_notes
        )

        assert not deleted_note_found, \
            f"Deleted note '{note_data['title']}' still visible in UI"

    # ==========================================
    # STEP 7 - VALIDATE DOM HEALTH
    # ==========================================

    with allure.step("Validate DOM health"):

        dom_healthy = True

        try:

            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            time.sleep(1)

            browser.execute_script(
                "window.scrollTo(0, 0);"
            )

            time.sleep(1)

        except Exception as e:

            dom_healthy = False

            allure.attach(
                str(e),
                name="DOM Error",
                attachment_type=allure.attachment_type.TEXT
            )

        assert dom_healthy, \
            "DOM issues detected after deletion"

    # ==========================================
    # TEST SUMMARY
    # ==========================================

    with allure.step("Execution Summary"):

        allure.attach(
            f"""
            Note ID: {created_note_id}
            Note Title: {note_data['title']}
            Delete Status Code: {delete_response.status_code}
            Deleted Note Visible In UI: {deleted_note_found}
            UI Notes Count: {len(ui_notes)}
            """,
            name="Execution Summary",
            attachment_type=allure.attachment_type.TEXT
        )
