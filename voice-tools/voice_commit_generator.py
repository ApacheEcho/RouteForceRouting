#!/usr/bin/env python3
"""
Voice-to-Commit Message Generator
Captures voice input and generates meaningful commit messages for the RouteForceRouting project.
"""

import re
import sys
import os
import json
from datetime import datetime
from typing import Optional, Dict, List

# Optional voice recognition import
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("⚠️  Voice recognition not available. Install with: pip install speechrecognition pyaudio")

# Optional clipboard support
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

class VoiceCommitGenerator:
    def __init__(self):
        if VOICE_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        else:
            self.recognizer = None
            self.microphone = None
        self.commit_patterns = self.load_commit_patterns()
        
    def load_commit_patterns(self) -> Dict[str, str]:
        """Load commit message patterns for different types of changes"""
        return {
            "fix": "Fix {description}",
            "add": "Add {description}",
            "update": "Update {description}", 
            "remove": "Remove {description}",
            "refactor": "Refactor {description}",
            "improve": "Improve {description}",
            "optimize": "Optimize {description}",
            "enhance": "Enhance {description}",
            "implement": "Implement {description}",
            "create": "Create {description}",
            "voice": "Add voice support for {description}",
            "api": "Update API for {description}",
            "dashboard": "Enhance dashboard with {description}",
            "mobile": "Improve mobile app {description}",
            "routing": "Optimize routing {description}",
            "analytics": "Update analytics {description}",
            "test": "Add tests for {description}",
            "docs": "Update documentation for {description}"
        }
    
    def listen_for_voice(self, timeout: int = 10) -> Optional[str]:
        """Capture voice input and convert to text"""
        if not VOICE_AVAILABLE:
            print("❌ Voice recognition not available. Install with: pip install speechrecognition pyaudio")
            return None
            
        try:
            print("🎤 Listening for commit message (speak now)...")
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
            
            print("🔄 Processing voice input...")
            # Use Google's speech recognition
            text = self.recognizer.recognize_google(audio)
            print(f"📝 Heard: '{text}'")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("⏰ No voice input detected within timeout period")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Error with speech recognition service: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def parse_voice_input(self, voice_text: str) -> Dict[str, str]:
        """Parse voice input to extract commit type and description"""
        voice_text = voice_text.strip()
        
        # Check for commit type patterns
        for pattern_key, pattern_template in self.commit_patterns.items():
            if pattern_key in voice_text:
                # Extract description after the pattern key
                description = voice_text.replace(pattern_key, "").strip()
                # Clean up common speech artifacts
                description = self.clean_description(description)
                return {
                    "type": pattern_key,
                    "description": description,
                    "template": pattern_template
                }
        
        # Default to general commit if no specific pattern found
        description = self.clean_description(voice_text)
        return {
            "type": "update",
            "description": description,
            "template": self.commit_patterns["update"]
        }
    
    def clean_description(self, description: str) -> str:
        """Clean and format the description text"""
        # Remove common speech artifacts
        description = re.sub(r'\b(um|uh|like|you know)\b', '', description, flags=re.IGNORECASE)
        # Remove extra whitespace
        description = ' '.join(description.split())
        # Capitalize first letter
        if description:
            description = description[0].upper() + description[1:]
        return description
    
    def generate_commit_message(self, voice_text: str) -> str:
        """Generate a formatted commit message from voice input"""
        parsed = self.parse_voice_input(voice_text)
        
        if not parsed["description"]:
            return "Update code changes"
        
        # Format the commit message
        commit_message = parsed["template"].format(description=parsed["description"])
        
        # Add context for RouteForce project if needed
        if any(keyword in parsed["description"].lower() for keyword in 
               ["route", "routing", "optimization", "algorithm", "path", "distance"]):
            commit_message += " in routing engine"
        elif any(keyword in parsed["description"].lower() for keyword in 
                 ["voice", "speech", "audio", "microphone"]):
            commit_message += " for voice-driven development"
        elif any(keyword in parsed["description"].lower() for keyword in 
                 ["api", "endpoint", "service"]):
            commit_message += " in API layer"
        elif any(keyword in parsed["description"].lower() for keyword in 
                 ["dashboard", "ui", "interface"]):
            commit_message += " in dashboard interface"
        
        return commit_message
    
    def save_commit_history(self, voice_text: str, commit_message: str):
        """Save commit history for learning and improvement"""
        history_file = "voice-tools/commit_history.json"
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "voice_input": voice_text,
            "generated_commit": commit_message
        }
        
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []
            
            history.append(history_entry)
            
            # Keep only last 50 entries
            if len(history) > 50:
                history = history[-50:]
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save commit history: {e}")

def main():
    """Main function to run voice commit generator"""
    print("🎯 RouteForce Voice Commit Generator")
    print("=" * 40)
    
    if not VOICE_AVAILABLE:
        print("⚠️  Voice recognition not available")
        print("💡 Install with: pip install speechrecognition pyaudio")
        print("📝 Falling back to text input mode")
        print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Usage: python voice_commit_generator.py [options]

Options:
  --help          Show this help message
  --test          Test microphone and speech recognition
  --interactive   Run in interactive mode (default)
  --timeout N     Set listening timeout in seconds (default: 10)
  --text          Use text input instead of voice

Voice Commands:
  "fix [description]"       -> Fix [description]
  "add [description]"       -> Add [description]
  "update [description]"    -> Update [description]
  "voice [description]"     -> Add voice support for [description]
  
Examples:
  Say: "fix routing algorithm bug"
  Output: "Fix routing algorithm bug in routing engine"
  
  Say: "add voice commands to dashboard"
  Output: "Add voice support for commands to dashboard"
        """)
        return
    
    generator = VoiceCommitGenerator()
    
    # Test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if not VOICE_AVAILABLE:
            print("❌ Cannot test voice - speech recognition not available")
            return
            
        print("🧪 Testing microphone and speech recognition...")
        voice_text = generator.listen_for_voice(timeout=5)
        if voice_text:
            print(f"✅ Test successful! Heard: '{voice_text}'")
        else:
            print("❌ Test failed - no voice input detected")
        return
    
    # Text input mode
    use_text_input = not VOICE_AVAILABLE or (len(sys.argv) > 1 and "--text" in sys.argv)
    
    # Get timeout from arguments
    timeout = 10
    if "--timeout" in sys.argv:
        try:
            timeout_index = sys.argv.index("--timeout")
            timeout = int(sys.argv[timeout_index + 1])
        except (IndexError, ValueError):
            print("Warning: Invalid timeout value, using default 10 seconds")
    
    # Interactive mode
    try:
        while True:
            if use_text_input:
                print(f"\n📝 Text Input Mode")
                print("Type your commit description (or 'quit' to exit):")
                
                user_input = input("💬 Commit description: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if user_input:
                    commit_message = generator.generate_commit_message(user_input)
                    print(f"\n📋 Generated commit message:")
                    print(f"    {commit_message}")
                    
                    # Save to history
                    generator.save_commit_history(user_input, commit_message)
                    
                    # Option to use the commit message
                    response = input("\n🔄 Use this commit message? (y/n/e=edit): ").strip().lower()
                    if response == 'y':
                        # Copy to clipboard if available
                        if CLIPBOARD_AVAILABLE:
                            try:
                                pyperclip.copy(commit_message)
                                print("✅ Commit message copied to clipboard!")
                            except Exception:
                                pass
                        else:
                            print("💡 Install pyperclip for clipboard support: pip install pyperclip")
                        
                        print(f"🚀 Run: git commit -m \"{commit_message}\"")
                        break
                    elif response == 'e':
                        edited_message = input("Edit commit message: ").strip()
                        if edited_message:
                            print(f"🚀 Run: git commit -m \"{edited_message}\"")
                            break
                else:
                    print("Please enter a commit description")
                    
            else:
                print(f"\n🎤 Ready to generate commit message (timeout: {timeout}s)")
                print("Press Ctrl+C to exit, or speak your commit description...")
                
                voice_text = generator.listen_for_voice(timeout=timeout)
                
                if voice_text:
                    commit_message = generator.generate_commit_message(voice_text)
                    print(f"\n📋 Generated commit message:")
                    print(f"    {commit_message}")
                    
                    # Save to history
                    generator.save_commit_history(voice_text, commit_message)
                    
                    # Option to use the commit message
                    try:
                        response = input("\n🔄 Use this commit message? (y/n/e=edit): ").strip().lower()
                        if response == 'y':
                            # Copy to clipboard if available
                            if CLIPBOARD_AVAILABLE:
                                try:
                                    pyperclip.copy(commit_message)
                                    print("✅ Commit message copied to clipboard!")
                                except Exception:
                                    pass
                            else:
                                print("💡 Install pyperclip for clipboard support: pip install pyperclip")
                            
                            print(f"🚀 Run: git commit -m \"{commit_message}\"")
                            break
                        elif response == 'e':
                            edited_message = input("Edit commit message: ").strip()
                            if edited_message:
                                print(f"🚀 Run: git commit -m \"{edited_message}\"")
                                break
                        # Continue loop for 'n' or invalid response
                        
                    except KeyboardInterrupt:
                        print("\n👋 Goodbye!")
                        break
                else:
                    print("🔄 Try again or press Ctrl+C to exit")
                
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()