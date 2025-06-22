#!/usr/bin/env python3
"""
Standardized validation module for oversight curriculum run scripts.
This module provides consistent validation across all execution scripts.
"""

import os
import sys
import platform
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

# Try to import dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class StandardValidator:
    """Standard validation class for oversight curriculum scripts"""
    
    def __init__(self, script_name: str = "unknown"):
        self.script_name = script_name
        self.script_dir = Path(__file__).parent.parent.absolute()
        self.working_dir = self.script_dir
        self.validation_results = {}
        self.errors = []
        
        # Ensure we're in the right directory
        os.chdir(self.working_dir)
        
    def log(self, message: str, level: str = "INFO", color: str = Colors.BLUE):
        """Log a message with timestamp and color"""
        timestamp = time.strftime("%H:%M:%S")
        level_colors = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "STEP": Colors.PURPLE
        }
        
        color_code = level_colors.get(level, Colors.BLUE)
        print(f"{color_code}[{level}]{Colors.NC} [{timestamp}] {self.script_name}: {message}")
        
    def print_banner(self):
        """Print the validation banner"""
        banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                OVERSIGHT CURRICULUM VALIDATION              ║
║                    Standard Validator                       ║
║                    Script: {self.script_name:<30} ║
╚══════════════════════════════════════════════════════════════╝{Colors.NC}
"""
        print(banner)
        
    def check_working_directory(self) -> bool:
        """Check and set the correct working directory"""
        self.log("Checking working directory...", "STEP")
        
        try:
            # Check if we're in the oversight_curriculum directory
            if self.working_dir.name == "oversight_curriculum":
                self.log("Already in oversight_curriculum directory", "SUCCESS")
                self.validation_results['working_directory'] = True
                return True
            else:
                # Try to find the oversight_curriculum directory
                oversight_dir = self.script_dir / "oversight_curriculum"
                if oversight_dir.exists():
                    os.chdir(oversight_dir)
                    self.working_dir = oversight_dir
                    self.log(f"Changed to oversight_curriculum directory: {self.working_dir}", "SUCCESS")
                    self.validation_results['working_directory'] = True
                    return True
                else:
                    self.log("Could not find oversight_curriculum directory", "ERROR")
                    self.validation_results['working_directory'] = False
                    self.errors.append("Could not find oversight_curriculum directory")
                    return False
        except Exception as e:
            self.log(f"Error checking working directory: {e}", "ERROR")
            self.validation_results['working_directory'] = False
            self.errors.append(f"Working directory error: {e}")
            return False
            
    def check_environment(self) -> bool:
        """Check and load environment variables"""
        self.log("Checking environment setup...", "STEP")
        
        try:
            # Check if .env file exists
            env_file = self.working_dir / ".env"
            
            if not env_file.exists():
                self.log(".env file not found", "WARNING")
                self.log("Creating .env file template...", "INFO")
                
                env_template = """# Claude API Configuration
CLAUDE_API_KEY=your-api-key-here

# Optional: Model configuration
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Optional: Logging level
LOG_LEVEL=INFO
"""
                with open(env_file, 'w') as f:
                    f.write(env_template)
                    
                self.log("Please edit .env file and add your actual API key", "ERROR")
                self.log("Then run this script again", "INFO")
                self.validation_results['environment'] = False
                self.errors.append("Missing .env file - template created")
                return False
            
            # Load .env file
            if DOTENV_AVAILABLE:
                load_dotenv(env_file)
                self.log("Loaded .env file using python-dotenv", "SUCCESS")
            else:
                # Manual loading for basic .env files
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                self.log("Loaded .env file manually", "SUCCESS")
            
            # Check if API key is set
            api_key = os.getenv("CLAUDE_API_KEY")
            if not api_key:
                self.log("CLAUDE_API_KEY not found in .env file", "ERROR")
                self.validation_results['environment'] = False
                self.errors.append("CLAUDE_API_KEY not found in .env file")
                return False
            
            # Validate API key format
            if not api_key.startswith("sk-"):
                self.log("Invalid API key format (should start with 'sk-')", "ERROR")
                self.validation_results['environment'] = False
                self.errors.append("Invalid API key format")
                return False
            
            self.log("Environment variables loaded successfully", "SUCCESS")
            self.log(f"API Key: {api_key[:10]}...{api_key[-4:]}", "INFO")
            self.validation_results['environment'] = True
            return True
            
        except Exception as e:
            self.log(f"Error checking environment: {e}", "ERROR")
            self.validation_results['environment'] = False
            self.errors.append(f"Environment error: {e}")
            return False
    
    def check_python_dependencies(self) -> bool:
        """Check Python and required dependencies"""
        self.log("Checking Python and dependencies...", "STEP")
        
        try:
            # Check Python version
            python_version = platform.python_version()
            self.log(f"Python version: {python_version}", "INFO")
            
            # Check if requirements.txt exists
            requirements_file = self.working_dir / "requirements.txt"
            if not requirements_file.exists():
                self.log("requirements.txt not found", "ERROR")
                self.validation_results['dependencies'] = False
                self.errors.append("requirements.txt not found")
                return False
            
            # Parse requirements
            required_packages = self._parse_requirements(requirements_file)
            self.log(f"Found {len(required_packages)} required packages", "INFO")
            
            # Check each package
            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package)
                    self.log(f"✅ {package}", "INFO")
                except ImportError:
                    self.log(f"❌ {package} - MISSING", "ERROR")
                    missing_packages.append(package)
            
            if missing_packages:
                self.log(f"Missing packages: {', '.join(missing_packages)}", "ERROR")
                self.log("Please run: pip install -r requirements.txt", "INFO")
                self.validation_results['dependencies'] = False
                self.errors.append(f"Missing packages: {', '.join(missing_packages)}")
                return False
            
            self.log("All dependencies satisfied", "SUCCESS")
            self.validation_results['dependencies'] = True
            return True
            
        except Exception as e:
            self.log(f"Error checking dependencies: {e}", "ERROR")
            self.validation_results['dependencies'] = False
            self.errors.append(f"Dependencies error: {e}")
            return False
    
    def _parse_requirements(self, requirements_file: Path) -> List[str]:
        """Parse requirements.txt file"""
        packages = []
        try:
            with open(requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (remove version specifiers)
                        package = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0]
                        
                        # Convert package names to import names
                        package_mapping = {
                            'charset-normalizer': 'charset_normalizer',
                            'python-dateutil': 'python_dateutil',
                            'python-dotenv': 'dotenv',
                            'markupsafe': 'markupsafe',
                            'jinja2': 'jinja2',
                            'fonttools': 'fonttools',
                            'pillow': 'PIL'
                        }
                        
                        import_name = package_mapping.get(package, package)
                        packages.append(import_name)
        except Exception as e:
            self.log(f"Error parsing requirements: {e}", "ERROR")
        return packages
    
    def check_directories(self) -> bool:
        """Check and create required directories"""
        self.log("Checking required directories...", "STEP")
        
        try:
            required_dirs = ['results', 'logs', 'temp']
            created_dirs = []
            
            for dir_name in required_dirs:
                dir_path = self.working_dir / dir_name
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(dir_name)
                    self.log(f"Created directory: {dir_name}", "INFO")
                else:
                    self.log(f"Directory exists: {dir_name}", "INFO")
            
            if created_dirs:
                self.log(f"Created directories: {', '.join(created_dirs)}", "SUCCESS")
            
            self.validation_results['directories'] = True
            return True
            
        except Exception as e:
            self.log(f"Error creating directories: {e}", "ERROR")
            self.validation_results['directories'] = False
            self.errors.append(f"Directory error: {e}")
            return False
    
    def check_files(self) -> bool:
        """Check if required files exist"""
        self.log("Checking required files...", "STEP")
        
        try:
            required_files = [
                'src/deduction_loop.py',
                'src/model.py',
                'src/metrics.py',
                'azr_loop.py'
            ]
            
            missing_files = []
            for file_path in required_files:
                full_path = self.working_dir / file_path
                if not full_path.exists():
                    missing_files.append(file_path)
                    self.log(f"❌ Missing: {file_path}", "ERROR")
                else:
                    self.log(f"✅ Found: {file_path}", "INFO")
            
            if missing_files:
                self.log(f"Missing files: {', '.join(missing_files)}", "ERROR")
                self.validation_results['files'] = False
                self.errors.append(f"Missing files: {', '.join(missing_files)}")
                return False
            
            self.log("All required files found", "SUCCESS")
            self.validation_results['files'] = True
            return True
            
        except Exception as e:
            self.log(f"Error checking files: {e}", "ERROR")
            self.validation_results['files'] = False
            self.errors.append(f"Files error: {e}")
            return False
    
    def run_quick_test(self) -> bool:
        """Run a quick test to verify basic functionality"""
        self.log("Running quick functionality test...", "STEP")
        
        try:
            # Test basic imports
            sys.path.insert(0, str(self.working_dir / "src"))
            
            # Test model import
            try:
                from model import ask
                self.log("✅ Model module imported successfully", "INFO")
            except ImportError as e:
                self.log(f"❌ Model import failed: {e}", "ERROR")
                self.validation_results['quick_test'] = False
                self.errors.append(f"Model import failed: {e}")
                return False
            
            # Test basic API call (if API key is available)
            api_key = os.getenv("CLAUDE_API_KEY")
            if api_key and api_key != "your-api-key-here":
                try:
                    # Simple test call
                    response = ask("Say 'hello'", model="claude-3-5-sonnet-20241022", max_tokens=10)
                    if response and len(response) > 0:
                        self.log("✅ API test successful", "SUCCESS")
                    else:
                        self.log("⚠️ API test returned empty response", "WARNING")
                except Exception as e:
                    self.log(f"⚠️ API test failed: {e}", "WARNING")
                    # Don't fail validation for API test, just warn
            else:
                self.log("⚠️ Skipping API test (no valid API key)", "WARNING")
            
            self.validation_results['quick_test'] = True
            return True
            
        except Exception as e:
            self.log(f"Error in quick test: {e}", "ERROR")
            self.validation_results['quick_test'] = False
            self.errors.append(f"Quick test error: {e}")
            return False
    
    def validate_all(self) -> bool:
        """Run all validation checks"""
        self.print_banner()
        
        checks = [
            self.check_working_directory,
            self.check_environment,
            self.check_python_dependencies,
            self.check_directories,
            self.check_files,
            self.run_quick_test
        ]
        
        all_passed = True
        for check in checks:
            if not check():
                all_passed = False
        
        # Print summary
        self.log("Validation Summary:", "STEP")
        for check_name, result in self.validation_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  {check_name}: {status}", "INFO")
        
        if self.errors:
            self.log("Errors encountered:", "ERROR")
            for error in self.errors:
                self.log(f"  - {error}", "ERROR")
        
        if all_passed:
            self.log("🎉 All validation checks passed!", "SUCCESS")
        else:
            self.log("❌ Some validation checks failed", "ERROR")
        
        return all_passed
    
    def get_validation_summary(self) -> Dict:
        """Get validation summary"""
        return {
            'script_name': self.script_name,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'results': self.validation_results,
            'errors': self.errors,
            'all_passed': all(self.validation_results.values()) if self.validation_results else False
        }


def validate_script(script_name: str = "unknown") -> bool:
    """Convenience function to run validation for a script"""
    validator = StandardValidator(script_name)
    return validator.validate_all()


if __name__ == "__main__":
    # Test the validator
    success = validate_script("validation_test")
    sys.exit(0 if success else 1) 