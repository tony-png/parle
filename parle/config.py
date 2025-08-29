import json
import os
from pathlib import Path


class Config:
    def __init__(self):
        self.config_dir = Path.home() / '.parle'
        self.config_file = self.config_dir / 'config.json'
        self.defaults = {
            'hotkey': 'ctrl+shift+r',
            'language': 'en',
            'start_on_boot': False,
            'show_notifications': True,
            'beep_on_start': True,
            'beep_on_stop': True
        }
        self.config = self.load()
    
    def load(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle missing keys
                    return {**self.defaults, **loaded}
            except:
                return self.defaults.copy()
        return self.defaults.copy()
    
    def save(self):
        """Save configuration to file"""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save()
    
    def reset(self):
        """Reset to default configuration"""
        self.config = self.defaults.copy()
        self.save()