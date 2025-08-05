#!/usr/bin/env python3
"""
Test script to validate CodeQL analysis setup.
This script contains some intentional security issues that CodeQL should detect.
"""

import os
import subprocess
import tempfile

def test_codeql_analysis():
    """Test that CodeQL can identify common security issues."""
    
    # This should trigger CodeQL's command injection detection
    def potential_command_injection(user_input):
        # Intentionally vulnerable code - CodeQL should flag this
        os.system(f"echo {user_input}")  # nosec - for testing
        
    # This should trigger CodeQL's path traversal detection  
    def potential_path_traversal(filename):
        # Intentionally vulnerable code - CodeQL should flag this
        with open(f"/tmp/{filename}", 'r') as f:  # nosec - for testing
            return f.read()
    
    # This should trigger CodeQL's hardcoded credentials detection
    def hardcoded_secret():
        # Intentionally vulnerable code - CodeQL should flag this
        api_key = "sk-1234567890abcdef"  # nosec - for testing
        return api_key
    
    print("CodeQL test file created - this contains intentional security issues for testing")
    print("CodeQL should detect:")
    print("1. Command injection in potential_command_injection()")
    print("2. Path traversal in potential_path_traversal()")  
    print("3. Hardcoded credentials in hardcoded_secret()")

if __name__ == "__main__":
    test_codeql_analysis()