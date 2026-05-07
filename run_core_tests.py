#!/usr/bin/env python3
"""Run only core tests (exclude demo tests) for accurate Allure reporting."""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from datetime import datetime
import json


class CoreTestRunner:
    """Run only core tests excluding demo tests."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.allure_results_dir = self.project_root / "allure-results"
        self.allure_report_dir = self.project_root / "allure-report"
        
    def setup_directories(self):
        """Create necessary directories."""
        directories = [
            self.allure_results_dir,
            self.allure_report_dir,
            Path("screenshots"),
            Path("logs"),
            Path("reports")
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"✅ Directory ready: {directory}")
    
    def cleanup_previous_results(self):
        """Clean up previous test results and reports."""
        print("🧹 Cleaning up previous results...")
        
        if self.allure_results_dir.exists():
            shutil.rmtree(self.allure_results_dir)
            self.allure_results_dir.mkdir(exist_ok=True)
        
        print("✅ Cleanup completed")
    
    def run_core_tests(self, parallel=False, browser=None):
        """Run only core tests (excluding demo tests)."""
        print("🚀 Starting core test execution...")
        
        # Build pytest command - exclude demo tests
        cmd = [
            sys.executable, "-m", "pytest",
            "-c", "pytest_enhanced.ini",
            "--ignore=tests/test_allure_integration_demo.py",  # Exclude demo tests
            "tests/",
            "--alluredir", str(self.allure_results_dir),
            "--html", str(self.project_root / "reports" / "pytest_report.html"),
            "--self-contained-html",
            "--tb=short",
            "--verbose"
        ]
        
        # Add browser configuration
        if browser:
            cmd.extend(["--browser", browser])
        
        # Add parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        print(f"📋 Command: {' '.join(cmd)}")
        print(f"🎯 Running core tests only (excluding 3 demo tests)")
        
        # Run tests
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            # Print output
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def generate_allure_report(self):
        """Generate Allure HTML report."""
        print("📊 Generating Allure report...")
        
        try:
            # Check if allure command is available
            result = subprocess.run(["allure", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ Allure command not found. Please install Allure Commandline.")
                return False
            
            # Generate report
            cmd = [
                "allure", "generate",
                str(self.allure_results_dir),
                "-o", str(self.allure_report_dir),
                "--clean"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Allure report generated: {self.allure_report_dir}")
                print(f"🌐 Open report: file://{self.allure_report_dir / 'index.html'}")
                return True
            else:
                print(f"❌ Error generating Allure report: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error generating Allure report: {e}")
            return False
    
    def serve_allure_report(self, port=8080):
        """Serve Allure report locally."""
        print(f"🌐 Serving Allure report on port {port}...")
        
        try:
            cmd = [
                "allure", "serve",
                str(self.allure_results_dir),
                "--port", str(port)
            ]
            
            print(f"📱 Open browser: http://localhost:{port}")
            subprocess.run(cmd, cwd=self.project_root)
            
        except KeyboardInterrupt:
            print("\n🛑 Allure server stopped")
        except Exception as e:
            print(f"❌ Error serving Allure report: {e}")
    
    def run_core_suite(self, **kwargs):
        """Run complete core test suite with Allure reporting."""
        print("🎯 Starting CORE test suite execution (17 tests expected)...")
        
        # Setup
        self.setup_directories()
        self.cleanup_previous_results()
        
        # Run tests
        success = self.run_core_tests(**kwargs)
        
        # Generate reports
        self.generate_allure_report()
        
        if success:
            print("✅ Core test suite completed successfully!")
            print("📊 Expected 17 tests in Allure report")
        else:
            print("❌ Core test suite failed!")
        
        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Core Test Runner (17 tests)")
    
    parser.add_argument(
        "--parallel", 
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--browser", 
        help="Browser to use for UI tests",
        default=None
    )
    
    parser.add_argument(
        "--serve", 
        action="store_true",
        help="Serve Allure report after execution"
    )
    
    parser.add_argument(
        "--port", 
        type=int,
        help="Port for Allure server",
        default=8080
    )
    
    parser.add_argument(
        "--clean-only", 
        action="store_true",
        help="Only clean up previous results"
    )
    
    args = parser.parse_args()
    
    runner = CoreTestRunner()
    
    if args.clean_only:
        runner.cleanup_previous_results()
        return
    
    # Run tests
    success = runner.run_core_suite(
        parallel=args.parallel,
        browser=args.browser
    )
    
    # Serve report if requested
    if args.serve:
        runner.serve_allure_report(args.port)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
