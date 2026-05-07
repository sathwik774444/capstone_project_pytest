"""
Custom pytest configuration for Selenium Grid support.
Adds command line options and fixtures for Grid execution.
"""

import pytest
import os
from selenium import webdriver
from selenium_grid_config import SeleniumGridConfig, GridBrowserManager


def pytest_addoption(parser):
    """Add custom command line options for Selenium Grid."""
    parser.addoption(
        "--selenium-grid-enabled",
        action="store_true",
        default=False,
        help="Enable Selenium Grid for distributed test execution"
    )
    parser.addoption(
        "--selenium-grid-url",
        action="store",
        default="http://localhost:4444",
        help="Selenium Grid URL (default: http://localhost:4444)"
    )
    parser.addoption(
        "--use-grid",
        action="store_true",
        default=False,
        help="Use Selenium Grid for test execution"
    )
    parser.addoption(
        "--cloud-provider",
        action="store",
        choices=["browserstack", "saucelabs", "none"],
        default="none",
        help="Cloud provider for test execution"
    )


@pytest.fixture(scope="session")
def selenium_grid_enabled(request):
    """Check if Selenium Grid is enabled."""
    return request.config.getoption("--selenium-grid-enabled") or request.config.getoption("--use-grid")


@pytest.fixture(scope="session")
def selenium_grid_url(request):
    """Get Selenium Grid URL."""
    return request.config.getoption("--selenium-grid-url")


@pytest.fixture(scope="session")
def cloud_provider(request):
    """Get cloud provider."""
    return request.config.getoption("--cloud-provider")


@pytest.fixture(scope="function")
def grid_browser(request, selenium_grid_enabled, selenium_grid_url, cloud_provider):
    """
    WebDriver fixture for Selenium Grid execution.
    Automatically switches between local and Grid execution based on configuration.
    """
    driver = None
    
    try:
        # Determine execution mode
        if cloud_provider != "none":
            # Cloud execution
            from selenium_grid_config import create_cloud_grid_driver
            driver = create_cloud_grid_driver(
                cloud_provider=cloud_provider,
                browser_name="chrome"
            )
        elif selenium_grid_enabled:
            # Selenium Grid execution
            grid_config = SeleniumGridConfig()
            grid_config.grid_url = selenium_grid_url
            grid_config.enable_grid = True
            driver = grid_config.create_grid_driver(browser_name="chrome")
        else:
            # Local execution
            from fixtures.browser_fixture import BrowserManager
            browser_manager = BrowserManager()
            driver = browser_manager.create_driver()
        
        # Set common capabilities
        driver.set_window_size(1920, 1080)
        driver.implicitly_wait(10)
        
        yield driver
        
    except Exception as e:
        print(f"Error setting up browser: {e}")
        raise e
    
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"Error quitting browser: {e}")


@pytest.fixture(scope="function")
def browser(request, grid_browser):
    """
    Main browser fixture that delegates to grid_browser.
    This maintains compatibility with existing tests.
    """
    return grid_browser


@pytest.fixture(scope="session")
def grid_config(request):
    """Get Grid configuration."""
    return {
        'enabled': request.config.getoption("--selenium-grid-enabled") or request.config.getoption("--use-grid"),
        'url': request.config.getoption("--selenium-grid-url"),
        'cloud_provider': request.config.getoption("--cloud-provider")
    }


# Hook to modify test collection for Grid execution
def pytest_collection_modifyitems(config, items):
    """Modify test collection based on execution mode."""
    grid_enabled = config.getoption("--selenium-grid-enabled") or config.getoption("--use-grid")
    cloud_provider = config.getoption("--cloud-provider")
    
    # Add markers based on execution mode
    for item in items:
        if grid_enabled or cloud_provider != "none":
            item.add_marker(pytest.mark.grid)
        
        if cloud_provider == "browserstack":
            item.add_marker(pytest.mark.browserstack)
        elif cloud_provider == "saucelabs":
            item.add_marker(pytest.mark.saucelabs)


# Hook for test reporting
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Generate enhanced reports for Grid execution."""
    outcome = yield
    report = outcome.get_result()
    
    # Add execution mode information
    grid_enabled = item.config.getoption("--selenium-grid-enabled") or item.config.getoption("--use-grid")
    cloud_provider = item.config.getoption("--cloud-provider")
    
    if grid_enabled:
        report.execution_mode = "selenium_grid"
    elif cloud_provider != "none":
        report.execution_mode = cloud_provider
    else:
        report.execution_mode = "local"


def pytest_configure(config):
    """Configure pytest for Grid execution."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "grid: Tests that run on Selenium Grid"
    )
    config.addinivalue_line(
        "markers", "browserstack: Tests that run on BrowserStack"
    )
    config.addinivalue_line(
        "markers", "saucelabs: Tests that run on Sauce Labs"
    )
    
    # Set environment variables for backward compatibility
    if config.getoption("--selenium-grid-enabled") or config.getoption("--use-grid"):
        os.environ["SELENIUM_GRID_ENABLED"] = "true"
        os.environ["SELENIUM_GRID_URL"] = config.getoption("--selenium-grid-url")
    
    if config.getoption("--cloud-provider") != "none":
        os.environ["CLOUD_PROVIDER"] = config.getoption("--cloud-provider")


def pytest_sessionstart(session):
    """Called after session has been created."""
    grid_enabled = session.config.getoption("--selenium-grid-enabled") or session.config.getoption("--use-grid")
    cloud_provider = session.config.getoption("--cloud-provider")
    
    if grid_enabled:
        print(f"\n🚀 Selenium Grid Enabled: {session.config.getoption('--selenium-grid-url')}")
    
    if cloud_provider != "none":
        print(f"☁️  Cloud Provider: {cloud_provider}")


def pytest_sessionfinish(session, exitstatus):
    """Called after session has finished."""
    grid_enabled = session.config.getoption("--selenium-grid-enabled") or session.config.getoption("--use-grid")
    cloud_provider = session.config.getoption("--cloud-provider")
    
    if grid_enabled or cloud_provider != "none":
        print(f"\n✅ Distributed test execution completed")
        print(f"   Exit status: {exitstatus}")
