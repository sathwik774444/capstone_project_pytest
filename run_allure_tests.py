#!/usr/bin/env python3
"""Enhanced test runner with comprehensive Allure integration."""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from datetime import datetime
import json


class AllureTestRunner:
    """Enhanced test runner with Allure reporting."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.allure_results_dir = self.project_root / "allure-results"
        self.allure_report_dir = self.project_root / "allure-report"
        self.screenshots_dir = self.project_root / "screenshots"
        self.logs_dir = self.project_root / "logs"
        self.reports_dir = self.project_root / "reports"
        
    def setup_directories(self):
        """Create necessary directories."""
        directories = [
            self.allure_results_dir,
            self.allure_report_dir,
            self.screenshots_dir,
            self.logs_dir,
            self.reports_dir,
            self.project_root / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"✅ Directory ready: {directory}")
    
    def cleanup_previous_results(self):
        """Clean up previous test results and reports."""
        print("🧹 Cleaning up previous results...")
        
        # Clean allure-results
        if self.allure_results_dir.exists():
            shutil.rmtree(self.allure_results_dir)
            self.allure_results_dir.mkdir(exist_ok=True)
        
        # Clean old screenshots (keep last 50)
        if self.screenshots_dir.exists():
            screenshots = list(self.screenshots_dir.glob("*.png"))
            screenshots.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for old_screenshot in screenshots[50:]:
                old_screenshot.unlink()
        
        # Clean old logs (keep last 10)
        if self.logs_dir.exists():
            logs = list(self.logs_dir.glob("*.log"))
            logs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for old_log in logs[10:]:
                old_log.unlink()
        
        print("✅ Cleanup completed")
    
    def generate_environment_info(self):
        """Generate enhanced environment information."""
        env_info = {
            "Test.Execution.Time": datetime.now().isoformat(),
            "Test.Runner": "Enhanced Allure Test Runner",
            "Python.Version": sys.version,
            "Platform": sys.platform,
            "Working.Directory": os.getcwd(),
            "Project.Root": str(self.project_root),
            "Test.Framework": "pytest",
            "Allure.Results.Directory": str(self.allure_results_dir),
            "Screenshots.Directory": str(self.screenshots_dir),
            "Logs.Directory": str(self.logs_dir)
        }
        
        # Write to environment.properties
        env_file = self.allure_results_dir / "environment.properties"
        with open(env_file, 'w') as f:
            f.write("# Enhanced Environment Information\n")
            f.write(f"# Generated at: {datetime.now().isoformat()}\n\n")
            for key, value in env_info.items():
                f.write(f"{key}={value}\n")
        
        print("✅ Environment information generated")
    
    def run_tests(self, test_path=None, markers=None, parallel=False, browser=None):
        """Run pytest with enhanced configuration."""
        print("🚀 Starting test execution...")
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            "-c", "pytest_enhanced.ini"
        ]
        
        # Add test path
        if test_path:
            cmd.append(test_path)
        else:
            cmd.append("tests/")
        
        # Add markers
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
        
        # Add browser configuration
        if browser:
            cmd.extend(["--browser", browser])
        
        # Add parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add additional options
        cmd.extend([
            "--alluredir", str(self.allure_results_dir),
            "--html", str(self.reports_dir / "pytest_report.html"),
            "--self-contained-html",
            "--tb=short",
            "--verbose"
        ])
        
        print(f"📋 Command: {' '.join(cmd)}")
        
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
                print("💡 Download from: https://docs.qameta.io/allure/#_installing_a_commandline")
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
    
    def create_test_summary(self):
        """Create test execution summary."""
        summary = {
            "execution_time": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "allure_results": str(self.allure_results_dir),
            "allure_report": str(self.allure_report_dir),
            "screenshots": str(self.screenshots_dir),
            "logs": str(self.logs_dir)
        }
        
        # Count test results
        if self.allure_results_dir.exists():
            test_files = list(self.allure_results_dir.glob("*-result.json"))
            summary["total_tests"] = len(test_files)
        
        # Save summary
        summary_file = self.reports_dir / "test_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📋 Test summary saved: {summary_file}")
    
    def run_complete_suite(self, **kwargs):
        """Run complete test suite with Allure reporting."""
        print("🎯 Starting complete test suite execution...")
        
        # Setup
        self.setup_directories()
        self.cleanup_previous_results()
        self.generate_environment_info()
        
        # Run tests
        success = self.run_tests(**kwargs)
        
        # Generate reports
        self.generate_allure_report()
        self.create_test_summary()
        
        if success:
            print("✅ Test suite completed successfully!")
        else:
            print("❌ Test suite failed!")
        
        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Enhanced Allure Test Runner")
    
    parser.add_argument(
        "--test-path", 
        help="Specific test path to run",
        default=None
    )
    
    parser.add_argument(
        "--markers", 
        nargs="+",
        help="Test markers to run",
        default=None
    )
    
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
    
    runner = AllureTestRunner()
    
    if args.clean_only:
        runner.cleanup_previous_results()
        return
    
    # Run tests
    success = runner.run_complete_suite(
        test_path=args.test_path,
        markers=args.markers,
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
