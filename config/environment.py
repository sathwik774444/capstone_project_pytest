"""Environment configuration management module."""

import os
import yaml
from pathlib import Path


class EnvironmentConfig:
    """Centralized configuration management."""
    
    def __init__(self):
        self.config_path = Path(__file__).parent / "config.yaml"
        self.config = self._load_config()
        self.env = os.getenv("TEST_ENV", "test")
    
    def _load_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
    
    def get(self, key, default=None):
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def base_url(self):
        """Get base URL."""
        return self.get("environment.base_url")
    
    @property
    def ui_url(self):
        """Get UI URL."""
        return self.get("environment.ui_url")
    
    @property
    def api_url(self):
        """Get API URL."""
        return self.get("environment.api_url")
    
    @property
    def browser_config(self):
        """Get browser configuration."""
        return self.get("browser")
    
    @property
    def test_data(self):
        """Get test data."""
        return self.get("test_data")
    
    @property
    def api_config(self):
        """Get API configuration."""
        return self.get("api")
    
    @property
    def logging_config(self):
        """Get logging configuration."""
        return self.get("logging")
    
    @property
    def reporting_config(self):
        """Get reporting configuration."""
        return self.get("reporting")


# Global configuration instance
env_config = EnvironmentConfig()
