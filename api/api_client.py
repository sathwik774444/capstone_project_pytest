"""API client for Notes application API testing."""

import requests
import logging
import time
import allure
from typing import Dict, List, Optional, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.environment import env_config


class APIClient:
    """Centralized API client for Notes application."""
    
    def __init__(self):
        self.base_url = env_config.api_url
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        self.auth_token = None
        self.user_id = None
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=env_config.get("api.retry_count", 3),
            backoff_factor=env_config.get("api.retry_delay", 1),
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _log_request(self, method: str, url: str, **kwargs):
        """Log request details."""
        self.logger.info(f"API Request: {method} {url}")
        if kwargs.get('data'):
            self.logger.debug(f"Request data: {kwargs['data']}")
        if kwargs.get('params'):
            self.logger.debug(f"Request params: {kwargs['params']}")
    
    def _log_response(self, response: requests.Response):
        """Log response details."""
        self.logger.info(f"API Response: {response.status_code} {response.reason}")
        self.logger.debug(f"Response headers: {dict(response.headers)}")
        
        # Log response body for non-binary responses
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                self.logger.debug(f"Response body: {response.json()}")
            except:
                self.logger.debug(f"Response body: {response.text}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling and logging."""
        url = f"{self.base_url}{endpoint}"
        timeout = kwargs.pop('timeout', env_config.get("api.timeout", 30))
        
        # Add authentication token if available
        if self.auth_token:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.auth_token}'
            kwargs['headers'] = headers
        
        self._log_request(method, url, **kwargs)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=timeout,
                **kwargs
            )
            
            self._log_response(response)
            
            # Attach to Allure report
            allure.attach(
                f"Request: {method} {url}\nHeaders: {kwargs.get('headers', {})}\nData: {kwargs.get('data', 'None')}",
                name=f"API Request - {method} {endpoint}",
                attachment_type=allure.attachment_type.TEXT
            )
            
            allure.attach(
                f"Status: {response.status_code}\nHeaders: {dict(response.headers)}\nBody: {response.text}",
                name=f"API Response - {response.status_code}",
                attachment_type=allure.attachment_type.TEXT
            )
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            allure.attach(
                str(e),
                name="API Request Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and get auth token."""
        endpoint = "/users/login"
        data = {
            "email": email,
            "password": password
        }
        
        response = self._make_request("POST", endpoint, json=data)
        
        if response.status_code == 200:
            auth_data = response.json()
            self.auth_token = auth_data.get('token')
            self.user_id = auth_data.get('user', {}).get('id')
            self.logger.info(f"Login successful for user: {email}")
            return auth_data
        else:
            self.logger.error(f"Login failed: {response.status_code}")
            raise Exception(f"Login failed: {response.status_code} - {response.text}")
    
    def logout(self) -> bool:
        """Logout user and clear auth token."""
        if not self.auth_token:
            return True
        
        try:
            endpoint = "/users/logout"
            response = self._make_request("POST", endpoint)
            
            self.auth_token = None
            self.user_id = None
            
            if response.status_code in [200, 204]:
                self.logger.info("Logout successful")
                return True
            else:
                self.logger.warning(f"Logout failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            self.auth_token = None
            self.user_id = None
            return False
    
    def get_notes(self, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Get all notes for authenticated user."""
        endpoint = "/notes"
        response = self._make_request("GET", endpoint, params=params)
        
        if response.status_code == 200:
            notes = response.json()
            self.logger.info(f"Retrieved {len(notes)} notes")
            return notes
        else:
            self.logger.error(f"Failed to get notes: {response.status_code}")
            raise Exception(f"Failed to get notes: {response.status_code} - {response.text}")
    
    def get_note_by_id(self, note_id: str) -> Dict[str, Any]:
        """Get specific note by ID."""
        endpoint = f"/notes/{note_id}"
        response = self._make_request("GET", endpoint)
        
        if response.status_code == 200:
            note = response.json()
            self.logger.info(f"Retrieved note: {note_id}")
            return note
        elif response.status_code == 404:
            self.logger.warning(f"Note not found: {note_id}")
            return {}
        else:
            self.logger.error(f"Failed to get note: {response.status_code}")
            raise Exception(f"Failed to get note: {response.status_code} - {response.text}")
    
    def create_note(self, title: str, description: str, category: str = None, tags: List[str] = None) -> Dict[str, Any]:
        """Create a new note."""
        endpoint = "/notes"
        data = {
            "title": title,
            "description": description
        }
        
        if category:
            data["category"] = category
        
        if tags:
            data["tags"] = tags
        
        response = self._make_request("POST", endpoint, json=data)
        
        if response.status_code == 201:
            note = response.json()
            self.logger.info(f"Created note: {note.get('id')} - {title}")
            return note
        else:
            self.logger.error(f"Failed to create note: {response.status_code}")
            raise Exception(f"Failed to create note: {response.status_code} - {response.text}")
    
    def update_note(self, note_id: str, title: str = None, description: str = None, category: str = None, tags: List[str] = None) -> Dict[str, Any]:
        """Update existing note."""
        endpoint = f"/notes/{note_id}"
        data = {}
        
        if title is not None:
            data["title"] = title
        
        if description is not None:
            data["description"] = description
        
        if category is not None:
            data["category"] = category
        
        if tags is not None:
            data["tags"] = tags
        
        response = self._make_request("PUT", endpoint, json=data)
        
        if response.status_code == 200:
            note = response.json()
            self.logger.info(f"Updated note: {note_id}")
            return note
        else:
            self.logger.error(f"Failed to update note: {response.status_code}")
            raise Exception(f"Failed to update note: {response.status_code} - {response.text}")
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note."""
        endpoint = f"/notes/{note_id}"
        response = self._make_request("DELETE", endpoint)
        
        if response.status_code in [200, 204]:
            self.logger.info(f"Deleted note: {note_id}")
            return True
        elif response.status_code == 404:
            self.logger.warning(f"Note not found for deletion: {note_id}")
            return False
        else:
            self.logger.error(f"Failed to delete note: {response.status_code}")
            raise Exception(f"Failed to delete note: {response.status_code} - {response.text}")
    
    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Search notes by query with fallback handling."""
        try:
            endpoint = "/notes/search"
            params = {"q": query}

            response = self._make_request("GET", endpoint, params=params)

            if response.status_code == 200:
                notes = response.json()
                self.logger.info(f"Found {len(notes)} notes for query: {query}")
                return notes
            elif response.status_code == 404:
                # Search endpoint not available, fallback to client-side filtering
                self.logger.warning(f"Search endpoint not available, falling back to client-side search: {query}")
                all_notes = self.get_notes()
                filtered_notes = [
                    note for note in all_notes 
                    if query.lower() in note.get('title', '').lower() 
                    or query.lower() in note.get('description', '').lower()
                ]
                self.logger.info(f"Found {len(filtered_notes)} notes using client-side search: {query}")
                return filtered_notes
            else:
                self.logger.error(f"Failed to search notes: {response.status_code}")
                return []

        except Exception as e:
            self.logger.warning(f"Search endpoint unavailable, trying client-side search: {e}")
            try:
                # Fallback to client-side search
                all_notes = self.get_notes()
                filtered_notes = [
                    note for note in all_notes 
                    if query.lower() in note.get('title', '').lower() 
                    or query.lower() in note.get('description', '').lower()
                ]
                self.logger.info(f"Found {len(filtered_notes)} notes using client-side search fallback: {query}")
                return filtered_notes
            except Exception as fallback_error:
                self.logger.error(f"Both API and client-side search failed: {fallback_error}")
                return []
    
    def get_note_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Get note by title from all notes."""
        notes = self.get_notes()
        for note in notes:
            if note.get('title') == title:
                return note
        return None
    
    def note_exists(self, title: str) -> bool:
        """Check if note with given title exists."""
        return self.get_note_by_title(title) is not None
    
    def wait_for_note_to_exist(self, title: str, timeout: int = 30, interval: int = 2) -> bool:
        """Wait for note to appear in API."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.note_exists(title):
                self.logger.info(f"Note found in API: {title}")
                return True
            time.sleep(interval)
        
        self.logger.error(f"Note not found in API within timeout: {title}")
        return False
    
    def wait_for_note_to_disappear(self, note_id: str, timeout: int = 30, interval: int = 2) -> bool:
        """Wait for note to disappear from API."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                note = self.get_note_by_id(note_id)
                if not note:
                    self.logger.info(f"Note disappeared from API: {note_id}")
                    return True
            except:
                # Note doesn't exist anymore
                self.logger.info(f"Note disappeared from API: {note_id}")
                return True
            time.sleep(interval)
        
        self.logger.error(f"Note still exists in API after timeout: {note_id}")
        return False
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get current user profile."""
        endpoint = "/users/profile"
        response = self._make_request("GET", endpoint)
        
        if response.status_code == 200:
            profile = response.json()
            self.logger.info("Retrieved user profile")
            return profile
        else:
            self.logger.error(f"Failed to get user profile: {response.status_code}")
            raise Exception(f"Failed to get user profile: {response.status_code} - {response.text}")
    
    def validate_response_time(self, response: requests.Response, max_time_ms: int = 2000) -> bool:
        """Validate API response time."""
        response_time_ms = response.elapsed.total_seconds() * 1000
        
        if response_time_ms <= max_time_ms:
            self.logger.info(f"Response time OK: {response_time_ms:.2f}ms")
            return True
        else:
            self.logger.warning(f"Response time too slow: {response_time_ms:.2f}ms (max: {max_time_ms}ms)")
            return False
    
    def health_check(self) -> bool:
        """Perform API health check."""
        try:
            endpoint = "/health"
            response = self._make_request("GET", endpoint)
            
            if response.status_code == 200:
                self.logger.info("API health check passed")
                return True
            else:
                self.logger.warning(f"API health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"API health check error: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure logout."""
        self.logout()
