#!/usr/bin/env python3
"""
Test runner script for Notes Application Test Automation Framework.

This script provides convenient ways to run different types of tests
with various configurations and reporting options.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=False, text=True)
    
    if result.returncode == 0:
        print(f"\n✅ {description} completed successfully!")
    else:
        print(f"\n❌ {description} failed with return code: {result.returncode}")
    
    return result.returncode


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Notes Application Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                    # Run all tests
  python run_tests.py --ui                     # Run UI tests only
  python run_tests.py --api                    # Run API tests only
  python run_tests.py --e2e                    # Run E2E tests only
  python run_tests.py --smoke                  # Run smoke tests
  python run_tests.py --parallel 4             # Run with 4 parallel workers
  python run_tests.py --report allure          # Generate Allure report
  python run_tests.py --headless               # Run in headless mode
        """
    )
    
    # Test selection options
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--ui", action="store_true", help="Run UI tests only")
    parser.add_argument("--api", action="store_true", help="Run API tests only")
    parser.add_argument("--e2e", action="store_true", help="Run E2E hybrid tests only")
    parser.add_argument("--login", action="store_true", help="Run login tests only")
    parser.add_argument("--notes", action="store_true", help="Run notes tests only")
    
    # Marker-based options
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests")
    parser.add_argument("--regression", action="store_true", help="Run regression tests")
    parser.add_argument("--critical", action="store_true", help="Run critical tests only")
    
    # Execution options
    parser.add_argument("--parallel", type=int, metavar="N", help="Run tests with N parallel workers")
    parser.add_argument("--headless", action="store_true", help="Run tests in headless mode")
    parser.add_argument("--debug", action="store_true", help="Run tests in debug mode")
    
    # Reporting options
    parser.add_argument("--report", choices=["html", "allure", "both"], default="html", 
                       help="Generate test report (default: html)")
    parser.add_argument("--serve", action="store_true", help="Serve Allure report after tests")
    
    # Configuration options
    parser.add_argument("--env", default="test", help="Test environment (default: test)")
    parser.add_argument("--browser", default="chrome", help="Browser to use (default: chrome)")
    
    # File/Path options
    parser.add_argument("--file", help="Run specific test file")
    parser.add_argument("--function", help="Run specific test function")
    
    args = parser.parse_args()
    
    # Ensure we're in the project directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Create necessary directories
    os.makedirs("allure-results", exist_ok=True)
    os.makedirs("allure-report", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    # Build pytest command
    pytest_cmd = "pytest"
    
    # Add test selection
    if args.file:
        pytest_cmd += f" {args.file}"
    elif args.function:
        pytest_cmd += f" -k {args.function}"
    elif args.ui:
        pytest_cmd += " -m ui"
    elif args.api:
        pytest_cmd += " -m api"
    elif args.e2e:
        pytest_cmd += " -m e2e"
    elif args.login:
        pytest_cmd += " tests/test_login.py"
    elif args.notes:
        pytest_cmd += " tests/test_notes_ui.py tests/test_notes_api.py"
    elif args.smoke:
        pytest_cmd += " -m smoke"
    elif args.regression:
        pytest_cmd += " -m regression"
    elif args.critical:
        pytest_cmd += " -m critical"
    elif not args.all:
        pytest_cmd += " tests/"
    
    # Add execution options
    if args.parallel:
        pytest_cmd += f" -n {args.parallel}"
    
    if args.debug:
        pytest_cmd += " -s -v --pdb"
    else:
        pytest_cmd += " -v"
    
    # Add reporting options
    if args.report in ["html", "both"]:
        pytest_cmd += " --html=reports/report.html --self-contained-html"
    
    if args.report in ["allure", "both"]:
        pytest_cmd += " --alluredir=allure-results"
    
    # Add environment and browser options
    pytest_cmd += f" --env={args.env}"
    
    # Set environment variables for headless mode
    if args.headless:
        os.environ["HEADLESS"] = "true"
    
    # Run the tests
    return_code = run_command(pytest_cmd, "Test Execution")
    
    # Generate additional reports if requested
    if args.report in ["allure", "both"] and return_code == 0:
        print("\n" + "="*60)
        print("Generating Allure Report...")
        print("="*60)
        
        # Generate Allure report
        allure_generate_cmd = "allure generate allure-results -o allure-report --clean"
        subprocess.run(allure_generate_cmd, shell=True)
        
        if args.serve:
            print("\n" + "="*60)
            print("Starting Allure Report Server...")
            print("="*60)
            print("Allure report will be available at: http://localhost:4040")
            print("Press Ctrl+C to stop the server")
            
            serve_cmd = "allure serve allure-results"
            subprocess.run(serve_cmd, shell=True)
        else:
            print(f"\n📊 Allure report generated successfully!")
            print(f"Open the report: file://{script_dir}/allure-report/index.html")
    
    elif args.report == "html" and return_code == 0:
        print(f"\n📊 HTML report generated successfully!")
        print(f"Open the report: file://{script_dir}/reports/report.html")
    
    # Exit with the same code as the test execution
    sys.exit(return_code)


if __name__ == "__main__":
    main()
