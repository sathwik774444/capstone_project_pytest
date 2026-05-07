#!/usr/bin/env python3
"""
Parallel test runner for distributed test execution.
Supports local parallel execution with pytest-xdist and Selenium Grid.
"""

import os
import sys
import argparse
import subprocess
import logging
from datetime import datetime
from pathlib import Path


class ParallelTestRunner:
    """Advanced parallel test runner with multiple execution modes."""
    
    def __init__(self):
        self.setup_logging()
        self.project_root = Path(__file__).parent
        self.test_results_dir = self.project_root / "test_results"
        self.test_results_dir.mkdir(exist_ok=True)
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/parallel_test_runner.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_local_parallel(self, num_workers=None, test_pattern=None, browser="chrome"):
        """
        Run tests in parallel using pytest-xdist locally.
        
        Args:
            num_workers: Number of parallel workers (auto-detect if None)
            test_pattern: Test pattern to run (e.g., "tests/test_login_*.py")
            browser: Browser to use for testing
        """
        self.logger.info("Starting local parallel test execution...")
        
        # Auto-detect number of workers if not specified
        if num_workers is None:
            import multiprocessing
            num_workers = multiprocessing.cpu_count()
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            "-n", str(num_workers),  # Number of parallel workers
            "--dist=loadscope",  # Distribute tests by scope
            "--tb=short",  # Short traceback format
            "--maxfail=5",  # Stop after 5 failures
            "-v",  # Verbose output
        ]
        
        # Add browser selection
        cmd.extend(["--browser", browser])
        
        # Add test pattern if specified
        if test_pattern:
            cmd.append(test_pattern)
        else:
            cmd.append("tests/")
        
        # Add reporting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = self.test_results_dir / f"parallel_report_{timestamp}.html"
        cmd.extend([
            "--html", str(html_report),
            "--self-contained-html",
            "--alluredir", f"allure-results/parallel_{timestamp}"
        ])
        
        # Add parallel-specific configuration
        cmd.extend([
            "-p", "conftest_parallel",
            "--disable-warnings"
        ])
        
        self.logger.info(f"Running command: {' '.join(cmd)}")
        
        try:
            # Execute tests
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            # Log results
            self.logger.info("Test execution completed")
            self.logger.info(f"Return code: {result.returncode}")
            
            if result.stdout:
                self.logger.info(f"STDOUT:\n{result.stdout}")
            
            if result.stderr:
                self.logger.warning(f"STDERR:\n{result.stderr}")
            
            # Generate summary report
            self.generate_summary_report(result, num_workers, "local_parallel", html_report)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error running local parallel tests: {e}")
            return False
    
    def run_grid_parallel(self, num_workers=None, test_pattern=None, grid_url=None, browser="chrome"):
        """
        Run tests in parallel using Selenium Grid.
        
        Args:
            num_workers: Number of parallel workers
            test_pattern: Test pattern to run
            grid_url: Selenium Grid URL
            browser: Browser to use for testing
        """
        self.logger.info("Starting Selenium Grid parallel test execution...")
        
        # Setup Grid configuration
        if grid_url:
            os.environ["SELENIUM_GRID_URL"] = grid_url
            os.environ["SELENIUM_GRID_ENABLED"] = "true"
        
        # Import and check Grid status
        try:
            from selenium_grid_config import SeleniumGridConfig
            grid_config = SeleniumGridConfig()
            
            if not grid_config.wait_for_grid_ready(timeout=30):
                self.logger.error("Selenium Grid is not ready")
                return False
                
        except ImportError:
            self.logger.error("Selenium Grid configuration not found")
            return False
        
        # Auto-detect workers if not specified
        if num_workers is None:
            num_workers = 4  # Default for Grid execution
        
        # Build pytest command for Grid execution
        cmd = [
            sys.executable, "-m", "pytest",
            "-n", str(num_workers),
            "--dist=loadscope",
            "--tb=short",
            "--maxfail=10",  # Higher threshold for Grid
            "-v",
        ]
        
        # Add Grid-specific options
        cmd.extend([
            "--browser", browser,
            "--use-grid",  # Custom flag to enable Grid
        ])
        
        # Add test pattern
        if test_pattern:
            cmd.append(test_pattern)
        else:
            cmd.append("tests/")
        
        # Add reporting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = self.test_results_dir / f"grid_report_{timestamp}.html"
        cmd.extend([
            "--html", str(html_report),
            "--self-contained-html",
            "--alluredir", f"allure-results/grid_{timestamp}"
        ])
        
        # Add parallel and Grid configuration
        cmd.extend([
            "-p", "conftest_parallel",
            "-p", "selenium_grid_config",
            "--disable-warnings"
        ])
        
        self.logger.info(f"Running Grid command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            self.logger.info("Grid test execution completed")
            self.logger.info(f"Return code: {result.returncode}")
            
            if result.stdout:
                self.logger.info(f"STDOUT:\n{result.stdout}")
            
            if result.stderr:
                self.logger.warning(f"STDERR:\n{result.stderr}")
            
            # Generate summary report
            self.generate_summary_report(result, num_workers, "selenium_grid", html_report)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error running Grid parallel tests: {e}")
            return False
    
    def run_cloud_parallel(self, cloud_provider, num_workers=2, test_pattern=None, browser="chrome"):
        """
        Run tests in parallel using cloud-based Grid services.
        
        Args:
            cloud_provider: 'browserstack' or 'saucelabs'
            num_workers: Number of parallel workers
            test_pattern: Test pattern to run
            browser: Browser to use for testing
        """
        self.logger.info(f"Starting {cloud_provider} cloud parallel test execution...")
        
        # Check for cloud credentials
        if cloud_provider == "browserstack":
            if not os.getenv("BROWSERSTACK_USERNAME") or not os.getenv("BROWSERSTACK_ACCESS_KEY"):
                self.logger.error("BrowserStack credentials not found in environment variables")
                return False
        elif cloud_provider == "saucelabs":
            if not os.getenv("SAUCE_USERNAME") or not os.getenv("SAUCE_ACCESS_KEY"):
                self.logger.error("Sauce Labs credentials not found in environment variables")
                return False
        
        # Build pytest command for cloud execution
        cmd = [
            sys.executable, "-m", "pytest",
            "-n", str(num_workers),
            "--dist=loadscope",
            "--tb=short",
            "--maxfail=5",
            "-v",
        ]
        
        # Add cloud-specific options
        cmd.extend([
            "--browser", browser,
            f"--cloud-provider={cloud_provider}",
        ])
        
        # Add test pattern
        if test_pattern:
            cmd.append(test_pattern)
        else:
            cmd.append("tests/")
        
        # Add reporting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = self.test_results_dir / f"{cloud_provider}_report_{timestamp}.html"
        cmd.extend([
            "--html", str(html_report),
            "--self-contained-html",
            "--alluredir", f"allure-results/{cloud_provider}_{timestamp}"
        ])
        
        # Add parallel and cloud configuration
        cmd.extend([
            "-p", "conftest_parallel",
            "-p", "selenium_grid_config",
            "--disable-warnings"
        ])
        
        self.logger.info(f"Running {cloud_provider} command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            self.logger.info(f"{cloud_provider} test execution completed")
            self.logger.info(f"Return code: {result.returncode}")
            
            if result.stdout:
                self.logger.info(f"STDOUT:\n{result.stdout}")
            
            if result.stderr:
                self.logger.warning(f"STDERR:\n{result.stderr}")
            
            # Generate summary report
            self.generate_summary_report(result, num_workers, cloud_provider, html_report)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error running {cloud_provider} parallel tests: {e}")
            return False
    
    def generate_summary_report(self, result, num_workers, execution_type, html_report):
        """Generate a summary report for the test execution."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        summary = f"""
# Parallel Test Execution Summary

**Execution Type:** {execution_type}
**Timestamp:** {timestamp}
**Number of Workers:** {num_workers}
**Return Code:** {result.returncode}
**HTML Report:** {html_report}

## Output:
```
{result.stdout}
```

## Errors (if any):
```
{result.stderr}
```

---
Generated by Parallel Test Runner
        """
        
        summary_file = self.test_results_dir / f"summary_{execution_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        self.logger.info(f"Summary report generated: {summary_file}")
    
    def setup_environment(self):
        """Setup the test environment."""
        # Create necessary directories
        directories = ["logs", "screenshots", "allure-results", "test_results"]
        for directory in directories:
            (self.project_root / directory).mkdir(exist_ok=True)
        
        self.logger.info("Environment setup completed")


def main():
    """Main entry point for parallel test runner."""
    parser = argparse.ArgumentParser(description="Parallel Test Runner for Selenium Tests")
    
    # Execution mode
    parser.add_argument(
        "--mode", 
        choices=["local", "grid", "browserstack", "saucelabs"],
        default="local",
        help="Execution mode"
    )
    
    # Worker configuration
    parser.add_argument(
        "--workers", "-w",
        type=int,
        help="Number of parallel workers (auto-detect if not specified)"
    )
    
    # Test configuration
    parser.add_argument(
        "--tests", "-t",
        help="Test pattern to run (e.g., tests/test_login_*.py)"
    )
    
    parser.add_argument(
        "--browser", "-b",
        choices=["chrome", "firefox"],
        default="chrome",
        help="Browser to use for testing"
    )
    
    # Grid configuration
    parser.add_argument(
        "--grid-url",
        help="Selenium Grid URL (for grid mode)"
    )
    
    # Setup options
    parser.add_argument(
        "--setup-grid",
        action="store_true",
        help="Setup local Selenium Grid using Docker"
    )
    
    parser.add_argument(
        "--cleanup-grid",
        action="store_true",
        help="Cleanup local Selenium Grid"
    )
    
    args = parser.parse_args()
    
    runner = ParallelTestRunner()
    runner.setup_environment()
    
    # Handle Grid setup/cleanup
    if args.setup_grid:
        from selenium_grid_config import setup_local_grid
        success = setup_local_grid()
        sys.exit(0 if success else 1)
    
    if args.cleanup_grid:
        from selenium_grid_config import cleanup_local_grid
        success = cleanup_local_grid()
        sys.exit(0 if success else 1)
    
    # Run tests based on mode
    success = False
    
    if args.mode == "local":
        success = runner.run_local_parallel(
            num_workers=args.workers,
            test_pattern=args.tests,
            browser=args.browser
        )
    
    elif args.mode == "grid":
        success = runner.run_grid_parallel(
            num_workers=args.workers,
            test_pattern=args.tests,
            grid_url=args.grid_url,
            browser=args.browser
        )
    
    elif args.mode == "browserstack":
        success = runner.run_cloud_parallel(
            cloud_provider="browserstack",
            num_workers=args.workers or 2,
            test_pattern=args.tests,
            browser=args.browser
        )
    
    elif args.mode == "saucelabs":
        success = runner.run_cloud_parallel(
            cloud_provider="saucelabs",
            num_workers=args.workers or 2,
            test_pattern=args.tests,
            browser=args.browser
        )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
