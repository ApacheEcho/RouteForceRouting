"""
Voice API Blueprint
Provides endpoints for voice-to-code functionality
"""

import os
import subprocess
from datetime import datetime
from typing import Optional, List, Dict, Any

from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename

from app.auth_decorators import require_auth
from app.utils.response_helpers import success_response, error_response

voice_bp = Blueprint("voice", __name__)


@voice_bp.route("/commit", methods=["POST"])
@require_auth
def voice_commit():
    """
    Handle voice-dictated commit messages
    """
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("No data provided")
        
        commit_message = data.get("message", "").strip()
        files = data.get("files", [])
        author = data.get("author", "Voice User")
        
        if not commit_message:
            raise BadRequest("Commit message is required")
        
        # Validate commit message format
        if len(commit_message) > 500:
            raise BadRequest("Commit message too long (max 500 characters)")
        
        # Process commit through git (in production, this would be more sophisticated)
        result = {
            "commit_id": f"voice-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "message": commit_message,
            "files": files,
            "author": author,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "queued"  # In real implementation, this would track actual git status
        }
        
        # Log the voice commit for tracking
        current_app.logger.info(f"Voice commit: {commit_message} by {author}")
        
        return success_response(
            data=result,
            message="Voice commit processed successfully"
        )
        
    except BadRequest as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        current_app.logger.error(f"Voice commit error: {str(e)}")
        return error_response(
            message="Failed to process voice commit", 
            status_code=500
        )


@voice_bp.route("/code-generation", methods=["POST"])
@require_auth
def generate_code_from_voice():
    """
    Generate code from voice input description
    """
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("No data provided")
        
        description = data.get("description", "").strip()
        language = data.get("language", "javascript")
        function_name = data.get("function_name", "")
        component_name = data.get("component_name", "")
        
        if not description:
            raise BadRequest("Code description is required")
        
        # Generate code based on description and language
        generated_code = _generate_code(
            description=description,
            language=language,
            function_name=function_name,
            component_name=component_name
        )
        
        result = {
            "code": generated_code,
            "language": language,
            "description": description,
            "generated_at": datetime.utcnow().isoformat(),
            "metadata": {
                "lines": len(generated_code.split('\n')),
                "characters": len(generated_code),
                "function_name": function_name,
                "component_name": component_name
            }
        }
        
        return success_response(
            data=result,
            message="Code generated successfully from voice input"
        )
        
    except BadRequest as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        current_app.logger.error(f"Code generation error: {str(e)}")
        return error_response(
            message="Failed to generate code from voice input", 
            status_code=500
        )


@voice_bp.route("/notes", methods=["POST"])
@require_auth
def save_voice_note():
    """
    Save voice note for later processing
    """
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("No data provided")
        
        transcript = data.get("transcript", "").strip()
        category = data.get("category", "general")
        tags = data.get("tags", [])
        priority = data.get("priority", "normal")
        
        if not transcript:
            raise BadRequest("Transcript is required")
        
        # Process and save note
        note_id = f"note-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Extract automatic tags from content
        auto_tags = _extract_auto_tags(transcript)
        all_tags = list(set(tags + auto_tags))
        
        result = {
            "note_id": note_id,
            "transcript": transcript,
            "category": category,
            "tags": all_tags,
            "priority": priority,
            "created_at": datetime.utcnow().isoformat(),
            "processed": True
        }
        
        current_app.logger.info(f"Voice note saved: {note_id}")
        
        return success_response(
            data=result,
            message="Voice note saved successfully"
        )
        
    except BadRequest as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        current_app.logger.error(f"Voice note error: {str(e)}")
        return error_response(
            message="Failed to save voice note", 
            status_code=500
        )


@voice_bp.route("/audio/upload", methods=["POST"])
@require_auth
def upload_voice_audio():
    """
    Handle audio file upload for offline voice processing
    """
    try:
        if 'audio' not in request.files:
            raise BadRequest("No audio file provided")
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            raise BadRequest("No audio file selected")
        
        # Validate file type
        allowed_extensions = {'wav', 'mp3', 'ogg', 'webm', 'm4a'}
        filename = secure_filename(audio_file.filename)
        
        if '.' not in filename or \
           filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            raise BadRequest("Invalid audio file format")
        
        # In production, you would:
        # 1. Save file to cloud storage
        # 2. Queue for speech-to-text processing
        # 3. Process through AI/ML pipeline
        
        audio_id = f"audio-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        result = {
            "audio_id": audio_id,
            "filename": filename,
            "size": len(audio_file.read()),
            "uploaded_at": datetime.utcnow().isoformat(),
            "status": "uploaded",
            "processing_status": "queued"
        }
        
        current_app.logger.info(f"Voice audio uploaded: {audio_id}")
        
        return success_response(
            data=result,
            message="Audio file uploaded successfully"
        )
        
    except BadRequest as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        current_app.logger.error(f"Audio upload error: {str(e)}")
        return error_response(
            message="Failed to upload audio file", 
            status_code=500
        )


@voice_bp.route("/settings", methods=["GET", "POST"])
@require_auth
def voice_settings():
    """
    Get or update voice settings for the user
    """
    if request.method == "GET":
        # Get current voice settings
        settings = {
            "language": "en-US",
            "auto_save": True,
            "push_to_talk": False,
            "noise_reduction": True,
            "commit_templates": [
                "fix: {description}",
                "feat: {description}",
                "refactor: {description}",
                "docs: {description}"
            ],
            "voice_shortcuts": {
                "quick_commit": "commit all changes",
                "new_function": "create function",
                "new_component": "create react component",
                "add_todo": "add todo note"
            }
        }
        
        return success_response(
            data=settings,
            message="Voice settings retrieved successfully"
        )
    
    else:  # POST
        try:
            data = request.get_json()
            
            # Update settings (in production, save to user preferences)
            updated_settings = {
                "language": data.get("language", "en-US"),
                "auto_save": data.get("auto_save", True),
                "push_to_talk": data.get("push_to_talk", False),
                "noise_reduction": data.get("noise_reduction", True),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            return success_response(
                data=updated_settings,
                message="Voice settings updated successfully"
            )
            
        except Exception as e:
            current_app.logger.error(f"Settings update error: {str(e)}")
            return error_response(
                message="Failed to update voice settings", 
                status_code=500
            )


def _generate_code(description: str, language: str, function_name: str = "", component_name: str = "") -> str:
    """
    Generate code based on voice description
    """
    if language == "javascript" or language == "jsx":
        if "function" in description.lower():
            name = function_name or "newFunction"
            return f"""function {name}() {{
    // {description}
    
}}"""
        elif "component" in description.lower() and language == "jsx":
            name = component_name or "NewComponent"
            return f"""import React from 'react';

interface {name}Props {{
  // Define props here
}}

export const {name}: React.FC<{name}Props> = () => {{
  // {description}
  
  return (
    <div>
      <h1>{name}</h1>
    </div>
  );
}};

export default {name};"""
    
    elif language == "python":
        if "function" in description.lower():
            name = function_name or "new_function"
            return f"""def {name}():
    \"\"\"
    {description}
    \"\"\"
    pass"""
        elif "class" in description.lower():
            name = component_name or "NewClass"
            return f"""class {name}:
    \"\"\"
    {description}
    \"\"\"
    
    def __init__(self):
        pass"""
    
    # Fallback
    return f"# {description}\n# Generated from voice input"


def _extract_auto_tags(text: str) -> List[str]:
    """
    Extract automatic tags from voice note content
    """
    tags = []
    text_lower = text.lower()
    
    # Common programming tags
    if any(word in text_lower for word in ['bug', 'fix', 'error', 'issue']):
        tags.append('#bug')
    if any(word in text_lower for word in ['feature', 'add', 'new', 'implement']):
        tags.append('#feature')
    if any(word in text_lower for word in ['refactor', 'improve', 'optimize']):
        tags.append('#refactor')
    if any(word in text_lower for word in ['urgent', 'asap', 'critical']):
        tags.append('#urgent')
    if any(word in text_lower for word in ['api', 'endpoint', 'service']):
        tags.append('#api')
    if any(word in text_lower for word in ['ui', 'interface', 'design']):
        tags.append('#ui')
    if any(word in text_lower for word in ['test', 'testing', 'spec']):
        tags.append('#testing')
    if any(word in text_lower for word in ['doc', 'documentation', 'readme']):
        tags.append('#docs')
    
    return tags