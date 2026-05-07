"""Allure utilities for enhanced reporting."""

import allure
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import requests
from selenium import webdriver


class AllureReporter:
    """Enhanced Allure reporting utilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def attach_screenshot(self, driver: webdriver.Remote, name: str = "Screenshot") -> None:
        """Attach screenshot to Allure report."""
        try:
            screenshot_path = self._take_screenshot(driver, name)
            if screenshot_path and os.path.exists(screenshot_path):
                allure.attach.file(
                    screenshot_path,
                    name=name,
                    attachment_type=allure.attachment_type.PNG
                )
                self.logger.info(f"Screenshot attached to Allure: {screenshot_path}")
        except Exception as e:
            self.logger.error(f"Failed to attach screenshot: {e}")
    
    def attach_html_report(self, html_content: str, name: str = "HTML Report") -> None:
        """Attach HTML content to Allure report."""
        try:
            allure.attach(
                html_content,
                name=name,
                attachment_type=allure.attachment_type.HTML
            )
        except Exception as e:
            self.logger.error(f"Failed to attach HTML report: {e}")
    
    def attach_api_response(self, response: requests.Response, name: str = "API Response") -> None:
        """Attach API response to Allure report."""
        try:
            # Create detailed response information
            response_info = {
                "Status Code": response.status_code,
                "URL": response.url,
                "Method": response.request.method if hasattr(response.request, 'method') else 'Unknown',
                "Headers": dict(response.headers),
                "Response Time": f"{response.elapsed.total_seconds():.3f}s",
                "Content-Type": response.headers.get('content-type', 'Unknown'),
                "Content-Length": len(response.content)
            }
            
            # Attach response metadata
            allure.attach(
                json.dumps(response_info, indent=2),
                name=f"{name} - Metadata",
                attachment_type=allure.attachment_type.JSON
            )
            
            # Attach response body
            if response.text:
                try:
                    # Try to parse as JSON for pretty formatting
                    json_data = response.json()
                    allure.attach(
                        json.dumps(json_data, indent=2),
                        name=f"{name} - Body",
                        attachment_type=allure.attachment_type.JSON
                    )
                except (json.JSONDecodeError, ValueError):
                    # Attach as text if not JSON
                    allure.attach(
                        response.text,
                        name=f"{name} - Body",
                        attachment_type=allure.attachment_type.TEXT
                    )
            else:
                allure.attach(
                    "Empty response body",
                    name=f"{name} - Body",
                    attachment_type=allure.attachment_type.TEXT
                )
                
        except Exception as e:
            self.logger.error(f"Failed to attach API response: {e}")
    
    def attach_api_request(self, request: requests.PreparedRequest, name: str = "API Request") -> None:
        """Attach API request details to Allure report."""
        try:
            request_info = {
                "Method": request.method,
                "URL": request.url,
                "Headers": dict(request.headers),
                "Body": request.body.decode('utf-8') if request.body else None
            }
            
            allure.attach(
                json.dumps(request_info, indent=2),
                name=name,
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
            self.logger.error(f"Failed to attach API request: {e}")
    
    def attach_log_file(self, log_file_path: str, name: str = "Log File") -> None:
        """Attach log file to Allure report."""
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                
                allure.attach(
                    log_content,
                    name=name,
                    attachment_type=allure.attachment_type.TEXT
                )
                self.logger.info(f"Log file attached to Allure: {log_file_path}")
            else:
                self.logger.warning(f"Log file not found: {log_file_path}")
        except Exception as e:
            self.logger.error(f"Failed to attach log file: {e}")
    
    def attach_environment_info(self) -> None:
        """Attach environment information to Allure report."""
        try:
            env_info = {
                "Python Version": sys.version,
                "Platform": sys.platform,
                "Current Working Directory": os.getcwd(),
                "Environment Variables": dict(os.environ),
                "Timestamp": datetime.now().isoformat()
            }
            
            allure.attach(
                json.dumps(env_info, indent=2),
                name="Environment Information",
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
            self.logger.error(f"Failed to attach environment info: {e}")
    
    def attach_test_data(self, data: Any, name: str = "Test Data") -> None:
        """Attach test data to Allure report."""
        try:
            if isinstance(data, (dict, list)):
                allure.attach(
                    json.dumps(data, indent=2),
                    name=name,
                    attachment_type=allure.attachment_type.JSON
                )
            else:
                allure.attach(
                    str(data),
                    name=name,
                    attachment_type=allure.attachment_type.TEXT
                )
        except Exception as e:
            self.logger.error(f"Failed to attach test data: {e}")
    
    def attach_performance_metrics(self, metrics: Dict[str, Any], name: str = "Performance Metrics") -> None:
        """Attach performance metrics to Allure report."""
        try:
            allure.attach(
                json.dumps(metrics, indent=2),
                name=name,
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
            self.logger.error(f"Failed to attach performance metrics: {e}")
    
    def attach_browser_info(self, driver: webdriver.Remote, name: str = "Browser Information") -> None:
        """Attach browser information to Allure report."""
        try:
            browser_info = {
                "Browser Name": driver.name,
                "Current URL": driver.current_url,
                "Title": driver.title,
                "Window Size": driver.get_window_size(),
                "Window Position": driver.get_window_position(),
                "Cookies": len(driver.get_cookies()),
                "Local Storage": driver.execute_script("return Object.keys(localStorage);"),
                "Session Storage": driver.execute_script("return Object.keys(sessionStorage);")
            }
            
            allure.attach(
                json.dumps(browser_info, indent=2),
                name=name,
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
            self.logger.error(f"Failed to attach browser info: {e}")
    
    def attach_console_logs(self, driver: webdriver.Remote, name: str = "Console Logs") -> None:
        """Attach browser console logs to Allure report."""
        try:
            # Get console logs
            logs = driver.get_log('browser')
            if logs:
                log_entries = []
                for log in logs:
                    log_entries.append({
                        "timestamp": log['timestamp'],
                        "level": log['level'],
                        "message": log['message']
                    })
                
                allure.attach(
                    json.dumps(log_entries, indent=2),
                    name=name,
                    attachment_type=allure.attachment_type.JSON
                )
            else:
                allure.attach(
                    "No console logs available",
                    name=name,
                    attachment_type=allure.attachment_type.TEXT
                )
        except Exception as e:
            self.logger.error(f"Failed to attach console logs: {e}")
    
    def attach_network_logs(self, driver: webdriver.Remote, name: str = "Network Logs") -> None:
        """Attach network logs to Allure report (if available)."""
        try:
            # This would require additional setup for network logging
            # For now, we'll attach basic network information
            network_info = {
                "Current URL": driver.current_url,
                "Page Load Strategy": "normal",  # Default value
                "Note": "Detailed network logging requires additional setup"
            }
            
            allure.attach(
                json.dumps(network_info, indent=2),
                name=name,
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
            self.logger.error(f"Failed to attach network logs: {e}")
    
    def create_test_step(self, step_name: str, description: str = "") -> None:
        """Create a test step in Allure report."""
        try:
            with allure.step(step_name):
                if description:
                    allure.attach(
                        description,
                        name="Step Description",
                        attachment_type=allure.attachment_type.TEXT
                    )
        except Exception as e:
            self.logger.error(f"Failed to create test step: {e}")
    
    def _take_screenshot(self, driver: webdriver.Remote, name: str) -> Optional[str]:
        """Take screenshot and return file path."""
        try:
            # Create screenshots directory
            screenshots_dir = "screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)
            
            # Take screenshot
            driver.save_screenshot(filepath)
            self.logger.info(f"Screenshot saved: {filepath}")
            
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return None


# Global instance for easy access
allure_reporter = AllureReporter()


def attach_allure_screenshot(driver: webdriver.Remote, name: str = "Screenshot") -> None:
    """Convenience function to attach screenshot."""
    allure_reporter.attach_screenshot(driver, name)


def attach_allure_api_response(response: requests.Response, name: str = "API Response") -> None:
    """Convenience function to attach API response."""
    allure_reporter.attach_api_response(response, name)


def attach_allure_logs(log_file_path: str = None, name: str = "Test Logs") -> None:
    """Convenience function to attach logs."""
    if log_file_path is None:
        log_file_path = "logs/test_execution.log"
    allure_reporter.attach_log_file(log_file_path, name)


def attach_allure_test_data(data: Any, name: str = "Test Data") -> None:
    """Convenience function to attach test data."""
    allure_reporter.attach_test_data(data, name)


def attach_allure_browser_info(driver: webdriver.Remote, name: str = "Browser Information") -> None:
    """Convenience function to attach browser information."""
    allure_reporter.attach_browser_info(driver, name)


def attach_allure_console_logs(driver: webdriver.Remote, name: str = "Console Logs") -> None:
    """Convenience function to attach console logs."""
    allure_reporter.attach_console_logs(driver, name)
