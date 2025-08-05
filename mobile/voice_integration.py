"""
Mobile Voice Integration API
Provides voice recording and processing capabilities for mobile development
"""

from flask import Blueprint, request, jsonify, current_app
import os
import tempfile
import base64
from datetime import datetime
import json

# Optional voice recognition import
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    # Note: Logging is deferred until Flask app context is available

mobile_voice_bp = Blueprint('mobile_voice', __name__)

@mobile_voice_bp.route('/voice/upload', methods=['POST'])
def upload_voice_recording():
    """
    Accept voice recording from mobile app and convert to text for development tasks
    """
    if not VOICE_AVAILABLE:
        return jsonify({
            'error': 'Voice recognition not available',
            'message': 'Install speech recognition: pip install speechrecognition pyaudio'
        }), 503

    try:
        data = request.get_json()
        
        if not data or 'audio_data' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Decode base64 audio data
        audio_data = base64.b64decode(data['audio_data'])
        
        # Create temporary file for audio processing
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name
        
        try:
            # Process audio with speech recognition
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(temp_audio_path) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
            
            # Process based on recording type
            recording_type = data.get('type', 'general')
            result = process_voice_command(text, recording_type)
            
            # Log the voice interaction
            log_voice_interaction(text, recording_type, result)
            
            return jsonify({
                'success': True,
                'text': text,
                'processed_result': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except sr.UnknownValueError:
            return jsonify({'error': 'Could not understand audio'}), 400
        except sr.RequestError as e:
            return jsonify({'error': f'Speech recognition error: {str(e)}'}), 500
        finally:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
                
    except Exception as e:
        current_app.logger.error(f"Voice upload error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_voice_bp.route('/voice/commit', methods=['POST'])
def voice_commit_message():
    """
    Generate commit message from voice input
    """
    try:
        data = request.get_json()
        voice_text = data.get('text', '')
        
        if not voice_text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Import voice commit generator
        import sys
        sys.path.append('voice-tools')
        from voice_commit_generator import VoiceCommitGenerator
        
        generator = VoiceCommitGenerator()
        commit_message = generator.generate_commit_message(voice_text)
        
        return jsonify({
            'success': True,
            'original_text': voice_text,
            'commit_message': commit_message,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Voice commit error: {str(e)}")
        return jsonify({'error': 'Failed to generate commit message'}), 500

@mobile_voice_bp.route('/voice/note', methods=['POST'])
def create_voice_note():
    """
    Create development note from voice input
    """
    try:
        data = request.get_json()
        voice_text = data.get('text', '')
        category = data.get('category', 'general')
        
        if not voice_text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Create note file
        note_date = datetime.now().strftime('%Y%m%d')
        note_file = f"voice-tools/mobile_notes_{note_date}.md"
        
        note_entry = f"""
## {datetime.now().strftime('%H:%M:%S')} - {category.title()} Note (Mobile)
{voice_text}

**Captured via:** Mobile Voice API  
**Category:** {category}  
**Timestamp:** {datetime.now().isoformat()}

---
"""
        
        with open(note_file, 'a', encoding='utf-8') as f:
            f.write(note_entry)
        
        return jsonify({
            'success': True,
            'note_saved': True,
            'file': note_file,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Voice note error: {str(e)}")
        return jsonify({'error': 'Failed to create note'}), 500

@mobile_voice_bp.route('/voice/commands', methods=['GET'])
def get_voice_commands():
    """
    Get available voice commands for mobile app
    """
    commands = {
        'commit': {
            'description': 'Generate commit message from voice',
            'examples': [
                'fix routing bug',
                'add voice feature',
                'update mobile app'
            ],
            'available': VOICE_AVAILABLE
        },
        'note': {
            'description': 'Create development note',
            'categories': ['bug', 'feature', 'idea', 'todo', 'general'],
            'examples': [
                'Remember to optimize the routing algorithm',
                'Bug in mobile voice upload needs fixing',
                'Idea for better user interface'
            ],
            'available': True  # Notes don't require voice recognition
        },
        'task': {
            'description': 'Create development task',
            'examples': [
                'Need to add unit tests for voice features',
                'Implement voice commands in dashboard',
                'Review mobile voice integration'
            ],
            'available': True  # Tasks don't require voice recognition
        }
    }
    
    return jsonify({
        'success': True,
        'commands': commands,
        'voice_enabled': VOICE_AVAILABLE,
        'setup_required': not VOICE_AVAILABLE,
        'setup_instructions': "Install voice dependencies: pip install speechrecognition pyaudio" if not VOICE_AVAILABLE else None
    })

@mobile_voice_bp.route('/voice/history', methods=['GET'])
def get_voice_history():
    """
    Get recent voice interactions
    """
    try:
        history_file = 'voice-tools/mobile_voice_history.json'
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Return last 20 entries
        recent_history = history[-20:] if len(history) > 20 else history
        
        return jsonify({
            'success': True,
            'history': recent_history,
            'total_count': len(history)
        })
        
    except Exception as e:
        current_app.logger.error(f"Voice history error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve history'}), 500

def process_voice_command(text: str, command_type: str) -> dict:
    """
    Process voice command based on type
    """
    text_lower = text.lower()
    
    if command_type == 'commit':
        # Import and use voice commit generator
        import sys
        sys.path.append('voice-tools')
        from voice_commit_generator import VoiceCommitGenerator
        
        generator = VoiceCommitGenerator()
        commit_message = generator.generate_commit_message(text)
        
        return {
            'type': 'commit',
            'generated_message': commit_message,
            'suggested_action': f'git commit -m "{commit_message}"'
        }
    
    elif command_type == 'task':
        # Extract task priority and category
        priority = 'normal'
        if any(word in text_lower for word in ['urgent', 'critical', 'important']):
            priority = 'high'
        elif any(word in text_lower for word in ['minor', 'low', 'small']):
            priority = 'low'
        
        category = 'general'
        if any(word in text_lower for word in ['bug', 'fix', 'error']):
            category = 'bug'
        elif any(word in text_lower for word in ['feature', 'add', 'new']):
            category = 'feature'
        elif any(word in text_lower for word in ['test', 'testing']):
            category = 'testing'
        
        return {
            'type': 'task',
            'priority': priority,
            'category': category,
            'description': text,
            'suggested_action': f'Create {priority} priority {category} task'
        }
    
    elif command_type == 'note':
        # Categorize the note
        category = 'general'
        if any(word in text_lower for word in ['idea', 'think', 'consider']):
            category = 'idea'
        elif any(word in text_lower for word in ['bug', 'issue', 'problem']):
            category = 'bug'
        elif any(word in text_lower for word in ['todo', 'need', 'should']):
            category = 'todo'
        
        return {
            'type': 'note',
            'category': category,
            'content': text,
            'suggested_action': f'Note saved in {category} category'
        }
    
    else:
        return {
            'type': 'general',
            'content': text,
            'suggested_action': 'Voice input processed'
        }

def log_voice_interaction(text: str, interaction_type: str, result: dict):
    """
    Log voice interaction for analytics and improvement
    """
    try:
        history_file = 'voice-tools/mobile_voice_history.json'
        
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'text': text,
            'type': interaction_type,
            'result': result,
            'source': 'mobile_api'
        }
        
        # Load existing history
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(interaction)
        
        # Keep only last 100 interactions
        if len(history) > 100:
            history = history[-100:]
        
        # Save updated history
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        current_app.logger.error(f"Failed to log voice interaction: {str(e)}")

# Register blueprint
def register_mobile_voice_routes(app):
    """Register mobile voice routes with the Flask app"""
    app.register_blueprint(mobile_voice_bp, url_prefix='/api/mobile/voice')