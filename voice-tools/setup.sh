#!/bin/bash

# Voice-to-Code Setup Script for RouteForceRouting
# This script sets up voice-driven development tools

echo "🎯 RouteForce Voice-to-Code Setup"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the RouteForceRouting root directory"
    exit 1
fi

echo "📋 Setting up voice-driven development tools..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p voice-tools
mkdir -p .vscode
mkdir -p logs

# Install voice dependencies
echo "📦 Installing voice dependencies..."
pip install speechrecognition pyaudio pydub pyperclip requests

# Install system dependencies for audio processing
echo "🔧 Setting up system audio dependencies..."
if command -v apt-get &> /dev/null; then
    echo "Detected Ubuntu/Debian system"
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev python3-pyaudio flac
elif command -v brew &> /dev/null; then
    echo "Detected macOS system"
    brew install portaudio flac
elif command -v dnf &> /dev/null; then
    echo "Detected Fedora system"
    sudo dnf install -y portaudio-devel flac
else
    echo "⚠️  Unknown system. Please install portaudio and flac manually."
fi

# Make voice tools executable
echo "🔑 Setting permissions..."
chmod +x voice-tools/voice_commit_generator.py
chmod +x voice-tools/voice_dev_mode.py

# Test microphone access
echo "🎤 Testing microphone access..."
python3 -c "
import speech_recognition as sr
try:
    r = sr.Recognizer()
    mic = sr.Microphone()
    print('✅ Microphone access successful')
except Exception as e:
    print(f'❌ Microphone access failed: {e}')
    print('💡 Try: sudo usermod -a -G audio \$USER')
"

# Create voice command shortcuts
echo "⚡ Creating voice command shortcuts..."

# Git hook for voice commits
cat > .git/hooks/prepare-commit-msg << 'EOF'
#!/bin/sh
# Voice commit hook - allows using voice for commit messages

if [ "$2" = "" ]; then
    echo "🎤 Voice commit mode available!"
    echo "💡 Run: python voice-tools/voice_commit_generator.py"
fi
EOF

chmod +x .git/hooks/prepare-commit-msg

# Create voice development aliases
cat > voice-tools/aliases.sh << 'EOF'
#!/bin/bash
# Voice development aliases for RouteForceRouting

# Voice commit shortcut
alias voice-commit="python voice-tools/voice_commit_generator.py"

# Voice development mode
alias voice-dev="python voice-tools/voice_dev_mode.py"

# Quick voice note
alias voice-note="python voice-tools/voice_dev_mode.py --command 'create note'"

# Voice status check
alias voice-status="python voice-tools/voice_dev_mode.py --command 'status'"

echo "🎯 Voice development aliases loaded!"
echo "Available commands:"
echo "  voice-commit  - Generate commit messages with voice"
echo "  voice-dev     - Enter voice development mode"
echo "  voice-note    - Create quick voice note"
echo "  voice-status  - Check project status with voice"
EOF

chmod +x voice-tools/aliases.sh

# VS Code configuration message
echo "💡 VS Code Configuration:"
echo "   - Install GitHub Copilot Voice extension"
echo "   - Workspace settings configured in .vscode/settings.json"
echo "   - Press Ctrl+Alt+V to start voice input in VS Code"

# Create quick test script
cat > voice-tools/test_voice.py << 'EOF'
#!/usr/bin/env python3
"""Quick test script for voice functionality"""

import speech_recognition as sr

def test_microphone():
    """Test microphone and speech recognition"""
    print("🧪 Testing voice functionality...")
    
    try:
        r = sr.Recognizer()
        mic = sr.Microphone()
        
        print("🎤 Microphone detected!")
        print("📝 Say something (5 second test)...")
        
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        
        print("🔄 Processing audio...")
        text = r.recognize_google(audio)
        print(f"✅ Success! Heard: '{text}'")
        
    except sr.WaitTimeoutError:
        print("⏰ No audio detected in timeout period")
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
    except sr.RequestError as e:
        print(f"❌ Error with speech service: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_microphone()
EOF

chmod +x voice-tools/test_voice.py

echo ""
echo "✅ Voice-to-Code setup complete!"
echo ""
echo "🚀 Quick Start:"
echo "   1. Test voice: python voice-tools/test_voice.py"
echo "   2. Voice commit: python voice-tools/voice_commit_generator.py"
echo "   3. Voice dev mode: python voice-tools/voice_dev_mode.py"
echo "   4. Load aliases: source voice-tools/aliases.sh"
echo ""
echo "📚 Documentation:"
echo "   - See voice-tools/README.md for detailed usage"
echo "   - VS Code: Install GitHub Copilot Voice extension"
echo "   - Mobile: Use /api/mobile/voice endpoints"
echo ""
echo "🎯 Happy voice-driven development!"