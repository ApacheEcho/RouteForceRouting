#!/usr/bin/env python3
"""
Production Readiness Check for RouteForce Routing
Validates configuration and dependencies for deployment
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path


class ProductionReadinessChecker:
    """Check production readiness of RouteForceRouting application"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
        
    def check_environment_variables(self):
        """Check critical environment variables"""
        print("🔍 Checking Environment Variables...")
        
        # Critical variables for production
        required_env = {
            'FLASK_ENV': 'Should be set to "production" for deployment',
            'SECRET_KEY': 'Required for session security'
        }
        
        # Optional but recommended
        optional_env = {
            'DATABASE_URL': 'PostgreSQL database URL (Render provides this)',
            'REDIS_URL': 'Redis cache URL (optional but improves performance)',
            'SENTRY_DSN': 'Error monitoring (optional but recommended)',
            'GOOGLE_MAPS_API_KEY': 'For enhanced routing features'
        }
        
        for var, description in required_env.items():
            if not os.environ.get(var):
                self.issues.append(f"Missing required environment variable: {var} - {description}")
            else:
                self.passed.append(f"✅ {var} is configured")
                
        for var, description in optional_env.items():
            if not os.environ.get(var):
                self.warnings.append(f"Optional environment variable not set: {var} - {description}")
            else:
                self.passed.append(f"✅ {var} is configured")
    
    def check_dependencies(self):
        """Check if all required packages are installed"""
        print("🔍 Checking Dependencies...")
        
        critical_packages = [
            'flask',
            'gunicorn',
            'eventlet',
            'sentry-sdk',
            'redis',
            'requests'
        ]
        
        for package in critical_packages:
            try:
                spec = importlib.util.find_spec(package.replace('-', '_'))
                if spec is None:
                    self.issues.append(f"Missing critical package: {package}")
                else:
                    self.passed.append(f"✅ {package} is installed")
            except ImportError:
                self.issues.append(f"Cannot import package: {package}")
    
    def check_application_files(self):
        """Check if critical application files exist"""
        print("🔍 Checking Application Files...")
        
        critical_files = [
            'app.py',
            'Procfile',
            'gunicorn_config.py',
            'requirements.txt',
            'app/__init__.py'
        ]
        
        for file_path in critical_files:
            if not Path(file_path).exists():
                self.issues.append(f"Missing critical file: {file_path}")
            else:
                self.passed.append(f"✅ {file_path} exists")
    
    def check_flask_app(self):
        """Test Flask application import and basic functionality"""
        print("🔍 Checking Flask Application...")
        
        try:
            # Test basic import
            from app import create_app
            
            # Test app creation
            test_app = create_app('testing')
            
            if test_app:
                self.passed.append("✅ Flask application imports and creates successfully")
            else:
                self.issues.append("Flask application creation failed")
                
        except Exception as e:
            self.issues.append(f"Flask application import/creation error: {str(e)}")
    
    def check_gunicorn_config(self):
        """Validate gunicorn configuration"""
        print("🔍 Checking Gunicorn Configuration...")
        
        try:
            # Test importing and basic validation
            import gunicorn_config
            
            # Check essential config attributes
            required_attrs = ['bind', 'workers', 'worker_class']
            
            for attr in required_attrs:
                if hasattr(gunicorn_config, attr):
                    value = getattr(gunicorn_config, attr)
                    self.passed.append(f"✅ Gunicorn config has {attr} = {value}")
                else:
                    self.warnings.append(f"Gunicorn config missing recommended attribute: {attr}")
                    
        except ImportError as e:
            self.issues.append(f"Cannot import gunicorn_config.py - {str(e)}")
        except Exception as e:
            self.issues.append(f"Gunicorn configuration error: {str(e)}")
    
    def check_sentry_configuration(self):
        """Check Sentry error monitoring setup"""
        print("🔍 Checking Sentry Configuration...")
        
        try:
            from app.monitoring.sentry_config import SentryConfig
            
            config = SentryConfig()
            if config.is_enabled():
                self.passed.append("✅ Sentry monitoring is configured")
            else:
                self.warnings.append("Sentry monitoring not configured (optional but recommended)")
                
        except Exception as e:
            self.warnings.append(f"Sentry configuration check failed: {str(e)}")
    
    def run_all_checks(self):
        """Run all production readiness checks"""
        print("🚀 RouteForce Production Readiness Check")
        print("=" * 50)
        
        self.check_environment_variables()
        self.check_dependencies()
        self.check_application_files()
        self.check_flask_app()
        self.check_gunicorn_config()
        self.check_sentry_configuration()
        
        # Print results
        print("\n📊 Results:")
        print("=" * 50)
        
        if self.passed:
            print("✅ Passed Checks:")
            for item in self.passed:
                print(f"   {item}")
        
        if self.warnings:
            print("\n⚠️  Warnings (Non-Critical):")
            for item in self.warnings:
                print(f"   {item}")
        
        if self.issues:
            print("\n❌ Critical Issues:")
            for item in self.issues:
                print(f"   {item}")
        
        # Final assessment
        print("\n🎯 Final Assessment:")
        print("=" * 50)
        
        if not self.issues:
            print("✅ Application is READY for production deployment!")
            print("🚀 You can safely deploy to Render or other platforms.")
            
            if self.warnings:
                print("ℹ️  Consider addressing warnings for optimal performance.")
            
            return True
        else:
            print("❌ Application has CRITICAL ISSUES that must be resolved.")
            print("🔧 Please fix the issues above before deploying.")
            return False


def main():
    """Main function"""
    checker = ProductionReadinessChecker()
    is_ready = checker.run_all_checks()
    
    if is_ready:
        print("\n🎉 Ready to deploy! Run: git push origin main")
        sys.exit(0)
    else:
        print("\n🔧 Fix issues above before deploying.")
        sys.exit(1)


if __name__ == '__main__':
    main()
