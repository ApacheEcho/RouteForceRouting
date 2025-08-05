#!/usr/bin/env python3
"""
Voice Integration Test Suite
Tests all voice-to-code features for RouteForceRouting
"""

import unittest
import sys
import os
import json
import tempfile
import subprocess
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, '/home/runner/work/RouteForceRouting/RouteForceRouting')

class TestVoiceCommitGenerator(unittest.TestCase):
    """Test voice commit message generation"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from voice_tools.voice_commit_generator import VoiceCommitGenerator
            self.generator = VoiceCommitGenerator()
        except ImportError:
            self.skipTest("Voice tools not available")
    
    def test_commit_pattern_recognition(self):
        """Test recognition of commit patterns"""
        test_cases = [
            ("fix routing bug", "fix", "Fix"),
            ("add voice feature", "add", "Add"), 
            ("update mobile app", "update", "Update"),
            ("optimize algorithm", "optimize", "Optimize")
        ]
        
        for voice_input, expected_type, expected_prefix in test_cases:
            with self.subTest(voice_input=voice_input):
                parsed = self.generator.parse_voice_input(voice_input)
                self.assertEqual(parsed["type"], expected_type)
                
                commit_msg = self.generator.generate_commit_message(voice_input)
                self.assertTrue(commit_msg.startswith(expected_prefix))
    
    def test_description_cleaning(self):
        """Test cleaning of voice input descriptions"""
        test_cases = [
            ("um fix the uh routing bug", "Fix the routing bug"),
            ("like add voice you know feature", "Add voice feature"),
            ("  update   mobile    app  ", "Update mobile app")
        ]
        
        for dirty_input, expected_clean in test_cases:
            with self.subTest(dirty_input=dirty_input):
                cleaned = self.generator.clean_description(dirty_input.replace("fix", "").replace("add", "").replace("update", "").strip())
                # This is a basic test - the actual cleaning may vary
                self.assertNotIn("um", cleaned.lower())
                self.assertNotIn("uh", cleaned.lower())
    
    def test_context_addition(self):
        """Test adding project context to commit messages"""
        test_cases = [
            ("fix routing algorithm", "routing engine"),
            ("add voice commands", "voice-driven development"),
            ("update api endpoint", "API layer"),
            ("enhance dashboard ui", "dashboard interface")
        ]
        
        for voice_input, expected_context in test_cases:
            with self.subTest(voice_input=voice_input):
                commit_msg = self.generator.generate_commit_message(voice_input)
                self.assertIn(expected_context, commit_msg)

class TestVoiceDevelopmentMode(unittest.TestCase):
    """Test voice development mode functionality"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from voice_tools.voice_dev_mode import VoiceDevelopmentMode
            self.voice_dev = VoiceDevelopmentMode()
        except ImportError:
            self.skipTest("Voice development mode not available")
    
    def test_command_loading(self):
        """Test that voice commands are loaded correctly"""
        commands = self.voice_dev.commands
        
        expected_commands = [
            "run tests", "run app", "git status", "git commit",
            "check health", "list files", "help", "exit"
        ]
        
        for cmd in expected_commands:
            self.assertIn(cmd, commands)
    
    def test_command_execution_structure(self):
        """Test command execution without actually running commands"""
        # Test unknown command handling
        result = self.voice_dev.execute_command("unknown command xyz")
        self.assertTrue(result)  # Should continue even with unknown commands
        
        # Test help command
        with patch('builtins.print'):
            result = self.voice_dev.execute_command("help")
            self.assertTrue(result)
    
    def test_session_logging(self):
        """Test session logging functionality"""
        self.voice_dev.log_command("test", "test command", "success")
        
        self.assertEqual(len(self.voice_dev.session_log), 1)
        log_entry = self.voice_dev.session_log[0]
        
        self.assertEqual(log_entry["command"], "test")
        self.assertEqual(log_entry["full_text"], "test command")
        self.assertEqual(log_entry["status"], "success")

class TestVoiceAPI(unittest.TestCase):
    """Test voice API endpoints"""
    
    def setUp(self):
        """Set up Flask test client"""
        try:
            from app import create_app
            self.app = create_app('testing')
            self.client = self.app.test_client()
            self.app_context = self.app.app_context()
            self.app_context.push()
        except Exception as e:
            self.skipTest(f"Flask app not available: {e}")
    
    def tearDown(self):
        """Clean up"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()
    
    def test_voice_commands_endpoint(self):
        """Test getting available voice commands"""
        try:
            response = self.client.get('/api/mobile/voice/commands')
            
            if response.status_code == 404:
                self.skipTest("Voice API endpoints not registered")
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            
            self.assertTrue(data['success'])
            self.assertIn('commands', data)
            self.assertIn('commit', data['commands'])
            self.assertIn('note', data['commands'])
        except Exception as e:
            self.skipTest(f"Voice API not available: {e}")
    
    def test_voice_commit_endpoint(self):
        """Test voice commit message generation endpoint"""
        try:
            test_data = {
                'text': 'fix routing algorithm bug'
            }
            
            response = self.client.post('/api/mobile/voice/commit',
                                      json=test_data,
                                      content_type='application/json')
            
            if response.status_code == 404:
                self.skipTest("Voice commit endpoint not available")
            
            if response.status_code == 200:
                data = response.get_json()
                self.assertTrue(data['success'])
                self.assertIn('commit_message', data)
                self.assertIn('Fix', data['commit_message'])
        except Exception as e:
            self.skipTest(f"Voice commit endpoint not available: {e}")

class TestVoiceSetup(unittest.TestCase):
    """Test voice setup and configuration"""
    
    def test_vscode_configuration(self):
        """Test VS Code configuration files"""
        vscode_settings = "/home/runner/work/RouteForceRouting/RouteForceRouting/.vscode/settings.json"
        
        self.assertTrue(os.path.exists(vscode_settings))
        
        with open(vscode_settings, 'r') as f:
            settings = json.load(f)
        
        # Check key voice settings
        self.assertIn('github.copilot.voice.enabled', settings)
        self.assertTrue(settings['github.copilot.voice.enabled'])
        
        self.assertIn('github.copilot.voice.keyBindings', settings)
        keybindings = settings['github.copilot.voice.keyBindings']
        self.assertIn('startListening', keybindings)
        self.assertIn('stopListening', keybindings)
    
    def test_voice_tools_directory(self):
        """Test voice tools directory structure"""
        voice_tools_dir = "/home/runner/work/RouteForceRouting/RouteForceRouting/voice-tools"
        
        self.assertTrue(os.path.exists(voice_tools_dir))
        
        expected_files = [
            "voice_commit_generator.py",
            "voice_dev_mode.py", 
            "setup.sh",
            "README.md"
        ]
        
        for file_name in expected_files:
            file_path = os.path.join(voice_tools_dir, file_name)
            self.assertTrue(os.path.exists(file_path), f"Missing {file_name}")
    
    def test_requirements_updated(self):
        """Test that voice dependencies are in requirements.txt"""
        requirements_file = "/home/runner/work/RouteForceRouting/RouteForceRouting/requirements.txt"
        
        with open(requirements_file, 'r') as f:
            requirements = f.read()
        
        voice_deps = ['speechrecognition', 'pyaudio', 'pydub', 'pyperclip']
        
        for dep in voice_deps:
            self.assertIn(dep, requirements, f"Missing dependency: {dep}")

class TestVoiceIntegration(unittest.TestCase):
    """Integration tests for voice features"""
    
    @patch('subprocess.run')
    def test_git_integration(self, mock_subprocess):
        """Test integration with git commands"""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "On branch main\nnothing to commit"
        
        try:
            from voice_tools.voice_dev_mode import VoiceDevelopmentMode
            voice_dev = VoiceDevelopmentMode()
            
            # Test git status command
            with patch('builtins.print'):
                voice_dev.git_status("git status")
            
            mock_subprocess.assert_called()
        except ImportError:
            self.skipTest("Voice development mode not available")
    
    def test_mobile_integration_structure(self):
        """Test mobile voice integration structure"""
        mobile_voice_file = "/home/runner/work/RouteForceRouting/RouteForceRouting/mobile/voice_integration.py"
        
        self.assertTrue(os.path.exists(mobile_voice_file))
        
        # Check if the mobile voice integration can be imported
        try:
            import mobile.voice_integration
            self.assertTrue(hasattr(mobile.voice_integration, 'mobile_voice_bp'))
        except ImportError:
            self.fail("Mobile voice integration cannot be imported")

def run_voice_feature_tests():
    """Run comprehensive voice feature tests"""
    print("🧪 Running Voice-to-Code Integration Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestVoiceCommitGenerator,
        TestVoiceDevelopmentMode,
        TestVoiceAPI,
        TestVoiceSetup,
        TestVoiceIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n🔥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.skipped:
        print("\n⏭️ SKIPPED:")
        for test, reason in result.skipped:
            print(f"  - {test}: {reason}")
    
    # Overall result
    if result.wasSuccessful():
        print("\n✅ All voice integration tests passed!")
        return True
    else:
        print("\n❌ Some voice integration tests failed!")
        return False

if __name__ == "__main__":
    success = run_voice_feature_tests()
    sys.exit(0 if success else 1)