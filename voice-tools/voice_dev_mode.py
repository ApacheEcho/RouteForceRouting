#!/usr/bin/env python3
"""
Voice Development Mode
Provides voice-activated development tools for RouteForceRouting project.
Supports voice commands for common development tasks while commuting or away from keyboard.
"""

import speech_recognition as sr
import subprocess
import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable

class VoiceDevelopmentMode:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.commands = self.load_voice_commands()
        self.session_log = []
        self.is_listening = False
        
    def load_voice_commands(self) -> Dict[str, Callable]:
        """Load available voice commands and their handlers"""
        return {
            "run tests": self.run_tests,
            "run app": self.run_application,
            "git status": self.git_status,
            "git commit": self.voice_commit,
            "check health": self.health_check,
            "list files": self.list_files,
            "show logs": self.show_logs,
            "create note": self.create_voice_note,
            "start recording": self.start_session_recording,
            "stop recording": self.stop_session_recording,
            "help": self.show_help,
            "exit": self.exit_voice_mode,
            "status": self.project_status
        }
    
    def listen_for_command(self, timeout: int = 15) -> Optional[str]:
        """Listen for voice commands"""
        try:
            print("🎤 Listening for voice command...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            print("🔄 Processing command...")
            command_text = self.recognizer.recognize_google(audio)
            print(f"📝 Command heard: '{command_text}'")
            return command_text.lower()
            
        except sr.WaitTimeoutError:
            print("⏰ No command detected")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand the command")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
    
    def execute_command(self, command_text: str) -> bool:
        """Execute the recognized voice command"""
        if not command_text:
            return True
            
        # Find matching command
        for cmd_key, cmd_handler in self.commands.items():
            if cmd_key in command_text:
                try:
                    print(f"🚀 Executing: {cmd_key}")
                    result = cmd_handler(command_text)
                    self.log_command(cmd_key, command_text, "success")
                    return result != False  # Continue unless explicitly told to stop
                except Exception as e:
                    print(f"❌ Error executing {cmd_key}: {e}")
                    self.log_command(cmd_key, command_text, f"error: {e}")
                    return True
        
        print(f"❓ Unknown command: '{command_text}'")
        print("💡 Say 'help' for available commands")
        self.log_command("unknown", command_text, "unknown")
        return True
    
    def log_command(self, command: str, full_text: str, status: str):
        """Log command execution for session review"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "full_text": full_text,
            "status": status
        }
        self.session_log.append(log_entry)
    
    # Command handlers
    def run_tests(self, command_text: str):
        """Run the test suite"""
        print("🧪 Running tests...")
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", ".", "-v", "--tb=short"],
                cwd="/home/runner/work/RouteForceRouting/RouteForceRouting",
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print("✅ Tests passed!")
                print(f"Output: {result.stdout[-500:]}")  # Last 500 chars
            else:
                print("❌ Tests failed!")
                print(f"Error: {result.stderr[-500:]}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Test execution timed out")
        except Exception as e:
            print(f"❌ Error running tests: {e}")
    
    def run_application(self, command_text: str):
        """Start the Flask application"""
        print("🚀 Starting RouteForce application...")
        print("💡 Application will run in background. Say 'show logs' to see output.")
        
        try:
            # Start app in background
            subprocess.Popen(
                ["python", "app.py"],
                cwd="/home/runner/work/RouteForceRouting/RouteForceRouting",
                env={**os.environ, "FLASK_ENV": "development"}
            )
            print("✅ Application started on http://localhost:8000")
            
        except Exception as e:
            print(f"❌ Error starting application: {e}")
    
    def git_status(self, command_text: str):
        """Show git status"""
        print("📊 Git status:")
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd="/home/runner/work/RouteForceRouting/RouteForceRouting",
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                print(f"Changes detected:\n{result.stdout}")
            else:
                print("✅ Working directory clean")
                
        except Exception as e:
            print(f"❌ Error checking git status: {e}")
    
    def voice_commit(self, command_text: str):
        """Create a commit using voice input"""
        print("💬 Starting voice commit process...")
        
        try:
            # Import and use the voice commit generator
            sys.path.append("/home/runner/work/RouteForceRouting/RouteForceRouting/voice-tools")
            from voice_commit_generator import VoiceCommitGenerator
            
            generator = VoiceCommitGenerator()
            print("🎤 Speak your commit message:")
            
            voice_text = generator.listen_for_voice(timeout=15)
            if voice_text:
                commit_message = generator.generate_commit_message(voice_text)
                print(f"📋 Generated: {commit_message}")
                
                # Auto-commit if requested
                if "auto commit" in command_text or "commit now" in command_text:
                    try:
                        subprocess.run(
                            ["git", "add", "."],
                            cwd="/home/runner/work/RouteForceRouting/RouteForceRouting",
                            check=True
                        )
                        subprocess.run(
                            ["git", "commit", "-m", commit_message],
                            cwd="/home/runner/work/RouteForceRouting/RouteForceRouting",
                            check=True
                        )
                        print("✅ Changes committed successfully!")
                    except subprocess.CalledProcessError as e:
                        print(f"❌ Commit failed: {e}")
                else:
                    print(f"💡 To commit: git commit -m \"{commit_message}\"")
            else:
                print("❌ No commit message captured")
                
        except ImportError:
            print("❌ Voice commit generator not available")
        except Exception as e:
            print(f"❌ Error in voice commit: {e}")
    
    def health_check(self, command_text: str):
        """Check application health"""
        print("🏥 Checking application health...")
        
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Application healthy")
                print(f"CPU: {data.get('system', {}).get('cpu_percent', 'unknown')}%")
                print(f"Memory: {data.get('system', {}).get('memory_percent', 'unknown')}%")
            else:
                print(f"⚠️ Application responded with status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Application not running or not accessible")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
    
    def list_files(self, command_text: str):
        """List project files"""
        print("📁 Project files:")
        
        try:
            if "changed" in command_text or "modified" in command_text:
                # Show git changes
                result = subprocess.run(
                    ["git", "diff", "--name-only"],
                    cwd="/home/runner/work/RouteForceRouting/RouteForceRouting",
                    capture_output=True,
                    text=True
                )
                files = result.stdout.strip().split('\n') if result.stdout.strip() else []
                print("Modified files:")
                for file in files:
                    if file:
                        print(f"  📝 {file}")
            else:
                # Show recent files
                result = subprocess.run(
                    ["find", ".", "-name", "*.py", "-mtime", "-1", "-type", "f"],
                    cwd="/home/runner/work/RouteForceRouting/RouteForceRouting",
                    capture_output=True,
                    text=True
                )
                files = result.stdout.strip().split('\n')[:10]  # Limit to 10 files
                print("Recent Python files:")
                for file in files:
                    if file and file != ".":
                        print(f"  🐍 {file}")
                        
        except Exception as e:
            print(f"❌ Error listing files: {e}")
    
    def show_logs(self, command_text: str):
        """Show application logs"""
        print("📋 Recent logs:")
        
        try:
            # Check for common log locations
            log_files = [
                "/tmp/routeforce.log",
                "app.log",
                "flask.log"
            ]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        recent_lines = lines[-10:]  # Last 10 lines
                        print(f"📄 {log_file}:")
                        for line in recent_lines:
                            print(f"  {line.strip()}")
                    return
            
            print("📋 No log files found. Showing git log instead:")
            result = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                cwd="/home/runner/work/RouteForceRouting/RouteForceRouting",
                capture_output=True,
                text=True
            )
            print(result.stdout)
            
        except Exception as e:
            print(f"❌ Error showing logs: {e}")
    
    def create_voice_note(self, command_text: str):
        """Create a voice note for later development"""
        print("📝 Creating voice note...")
        print("🎤 Speak your development note:")
        
        try:
            voice_text = self.listen_for_command(timeout=20)
            if voice_text:
                note_file = f"voice-tools/voice_notes_{datetime.now().strftime('%Y%m%d')}.md"
                
                with open(note_file, 'a') as f:
                    f.write(f"\n## {datetime.now().strftime('%H:%M:%S')} - Voice Note\n")
                    f.write(f"{voice_text}\n")
                    f.write("---\n")
                
                print(f"✅ Note saved to {note_file}")
            else:
                print("❌ No note captured")
                
        except Exception as e:
            print(f"❌ Error creating note: {e}")
    
    def start_session_recording(self, command_text: str):
        """Start recording development session"""
        self.is_listening = True
        print("🔴 Session recording started")
        print("💡 All commands will be logged for review")
    
    def stop_session_recording(self, command_text: str):
        """Stop recording and save session"""
        self.is_listening = False
        
        session_file = f"voice-tools/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(session_file, 'w') as f:
                json.dump(self.session_log, f, indent=2)
            
            print(f"⏹️ Session recording stopped")
            print(f"📋 Session saved to {session_file}")
            print(f"📊 Commands executed: {len(self.session_log)}")
            
        except Exception as e:
            print(f"❌ Error saving session: {e}")
    
    def project_status(self, command_text: str):
        """Show overall project status"""
        print("📊 RouteForce Project Status:")
        
        try:
            # Git info
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd="/home/runner/work/RouteForceRouting/RouteForceRouting",
                capture_output=True,
                text=True
            )
            current_branch = result.stdout.strip()
            print(f"🌿 Current branch: {current_branch}")
            
            # File count
            result = subprocess.run(
                ["find", ".", "-name", "*.py", "-type", "f"],
                cwd="/home/runner/work/RouteForceRouting/RouteForceRouting",
                capture_output=True,
                text=True
            )
            py_files = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            print(f"🐍 Python files: {py_files}")
            
            # Recent activity
            result = subprocess.run(
                ["git", "log", "--since=1.day", "--oneline"],
                cwd="/home/runner/work/RouteForceRouting/RouteForceRouting",
                capture_output=True,
                text=True
            )
            recent_commits = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            print(f"📈 Recent commits (24h): {recent_commits}")
            
        except Exception as e:
            print(f"❌ Error getting project status: {e}")
    
    def show_help(self, command_text: str):
        """Show available voice commands"""
        print("🎯 Available Voice Commands:")
        print("=" * 40)
        for cmd in self.commands.keys():
            print(f"  🎤 '{cmd}'")
        
        print("\n💡 Usage Tips:")
        print("  - Speak clearly and wait for the listening prompt")
        print("  - Commands are case-insensitive")
        print("  - Say 'exit' to quit voice mode")
        print("  - Say 'help' anytime to see this list")
    
    def exit_voice_mode(self, command_text: str):
        """Exit voice development mode"""
        print("👋 Exiting voice development mode")
        if self.session_log:
            print(f"📊 Session summary: {len(self.session_log)} commands executed")
        return False  # Signal to exit main loop

def main():
    """Main voice development mode loop"""
    print("🎯 RouteForce Voice Development Mode")
    print("=" * 40)
    print("🎤 Voice-activated development tools for coding on the go")
    print("💡 Say 'help' for available commands")
    print("🔄 Say 'exit' to quit")
    print()
    
    voice_dev = VoiceDevelopmentMode()
    
    try:
        while True:
            print(f"\n{'🔴' if voice_dev.is_listening else '⚪'} Ready for voice command...")
            
            command_text = voice_dev.listen_for_command()
            
            if command_text:
                should_continue = voice_dev.execute_command(command_text)
                if not should_continue:
                    break
            
            # Small delay to prevent overwhelming the system
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Voice development mode terminated")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    finally:
        # Save session if any commands were executed
        if voice_dev.session_log:
            try:
                session_file = f"voice-tools/emergency_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(session_file, 'w') as f:
                    json.dump(voice_dev.session_log, f, indent=2)
                print(f"💾 Session automatically saved to {session_file}")
            except Exception:
                pass

if __name__ == "__main__":
    main()