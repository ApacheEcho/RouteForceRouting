"""
Tests for Voice-to-Code Integration API
"""

import io
import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
from app import create_app
from app.api.voice import voice_bp


@pytest.fixture
def app():
    """Create test Flask application"""
    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret-key"
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json",
    }


class TestVoiceCommit:
    """Test voice commit functionality"""

    @patch("app.auth_decorators.verify_jwt_in_request")
    @patch("app.auth_decorators.get_jwt_identity")
    def test_voice_commit_success(
        self, mock_jwt_identity, mock_verify_jwt, client, auth_headers
    ):
        """Test successful voice commit"""
        mock_jwt_identity.return_value = "test@example.com"
        mock_verify_jwt.return_value = True

        with patch("app.auth_decorators.users_db") as mock_users_db:
            mock_users_db.get.return_value = {
                "email": "test@example.com",
                "role": "developer",
                "id": "test-user-id",
            }

            payload = {
                "message": "Fix navigation bug in header component",
                "files": ["src/components/Header.tsx"],
                "author": "Test User",
            }

            response = client.post(
                "/api/voice/commit",
                data=json.dumps(payload),
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert "commit_id" in data["data"]
            assert data["data"]["message"] == payload["message"]

    @patch("app.auth_decorators.verify_jwt_in_request")
    @patch("app.auth_decorators.get_jwt_identity")
    def test_voice_commit_empty_message(
        self, mock_jwt_identity, mock_verify_jwt, client, auth_headers
    ):
        """Test voice commit with empty message"""
        mock_jwt_identity.return_value = "test@example.com"
        mock_verify_jwt.return_value = True

        with patch("app.auth_decorators.users_db") as mock_users_db:
            mock_users_db.get.return_value = {
                "email": "test@example.com",
                "role": "developer",
            }

            payload = {"message": "", "files": [], "author": "Test User"}

            response = client.post(
                "/api/voice/commit",
                data=json.dumps(payload),
                headers=auth_headers,
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert data["success"] is False
            assert "Commit message is required" in data["error"]


class TestVoiceCodeGeneration:
    """Test voice code generation functionality"""

    @patch("app.auth_decorators.verify_jwt_in_request")
    @patch("app.auth_decorators.get_jwt_identity")
    def test_generate_javascript_function(
        self, mock_jwt_identity, mock_verify_jwt, client, auth_headers
    ):
        """Test generating JavaScript function from voice"""
        mock_jwt_identity.return_value = "test@example.com"
        mock_verify_jwt.return_value = True

        with patch("app.auth_decorators.users_db") as mock_users_db:
            mock_users_db.get.return_value = {
                "email": "test@example.com",
                "role": "developer",
            }

            payload = {
                "description": "Create a function that calculates the total price",
                "language": "javascript",
                "function_name": "calculateTotal",
            }

            response = client.post(
                "/api/voice/code-generation",
                data=json.dumps(payload),
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert "calculateTotal" in data["data"]["code"]
            assert data["data"]["language"] == "javascript"

    @patch("app.auth_decorators.verify_jwt_in_request")
    @patch("app.auth_decorators.get_jwt_identity")
    def test_generate_react_component(
        self, mock_jwt_identity, mock_verify_jwt, client, auth_headers
    ):
        """Test generating React component from voice"""
        mock_jwt_identity.return_value = "test@example.com"
        mock_verify_jwt.return_value = True

        with patch("app.auth_decorators.users_db") as mock_users_db:
            mock_users_db.get.return_value = {
                "email": "test@example.com",
                "role": "developer",
            }

            payload = {
                "description": "Create a React component for user profile",
                "language": "jsx",
                "component_name": "UserProfile",
            }

            response = client.post(
                "/api/voice/code-generation",
                data=json.dumps(payload),
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert "UserProfile" in data["data"]["code"]
            assert "React.FC" in data["data"]["code"]


class TestVoiceNotes:
    """Test voice notes functionality"""

    @patch("app.auth_decorators.verify_jwt_in_request")
    @patch("app.auth_decorators.get_jwt_identity")
    def test_save_voice_note(
        self, mock_jwt_identity, mock_verify_jwt, client, auth_headers
    ):
        """Test saving voice note"""
        mock_jwt_identity.return_value = "test@example.com"
        mock_verify_jwt.return_value = True

        with patch("app.auth_decorators.users_db") as mock_users_db:
            mock_users_db.get.return_value = {
                "email": "test@example.com",
                "role": "developer",
            }

            payload = {
                "transcript": "Need to fix the authentication bug in the API",
                "category": "bug",
                "tags": ["#urgent", "#api"],
                "priority": "high",
            }

            response = client.post(
                "/api/voice/notes",
                data=json.dumps(payload),
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert "note_id" in data["data"]
            assert data["data"]["transcript"] == payload["transcript"]
            assert "#bug" in data["data"]["tags"]  # Auto-extracted tag

    @patch("app.auth_decorators.verify_jwt_in_request")
    @patch("app.auth_decorators.get_jwt_identity")
    def test_auto_tag_extraction(
        self, mock_jwt_identity, mock_verify_jwt, client, auth_headers
    ):
        """Test automatic tag extraction from voice notes"""
        mock_jwt_identity.return_value = "test@example.com"
        mock_verify_jwt.return_value = True

        with patch("app.auth_decorators.users_db") as mock_users_db:
            mock_users_db.get.return_value = {
                "email": "test@example.com",
                "role": "developer",
            }

            payload = {
                "transcript": "Add new feature for API endpoint documentation",
                "category": "feature",
            }

            response = client.post(
                "/api/voice/notes",
                data=json.dumps(payload),
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert "#feature" in data["data"]["tags"]
            assert "#api" in data["data"]["tags"]
            assert "#docs" in data["data"]["tags"]


class TestVoiceAudioUpload:
    """Test voice audio upload functionality"""

    @patch("app.auth_decorators.verify_jwt_in_request")
    @patch("app.auth_decorators.get_jwt_identity")
    def test_upload_audio_file(
        self, mock_jwt_identity, mock_verify_jwt, client, auth_headers
    ):
        """Test uploading audio file"""
        mock_jwt_identity.return_value = "test@example.com"
        mock_verify_jwt.return_value = True

        with patch("app.auth_decorators.users_db") as mock_users_db:
            mock_users_db.get.return_value = {
                "email": "test@example.com",
                "role": "developer",
            }

            # Create mock audio file
            audio_data = b"fake audio data"
            audio_file = (io.BytesIO(audio_data), "voice_note.wav")

            response = client.post(
                "/api/voice/audio/upload",
                data={"audio": audio_file},
                headers={"Authorization": "Bearer test-token"},
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert "audio_id" in data["data"]
            assert data["data"]["filename"] == "voice_note.wav"

    def test_upload_no_audio_file(self, client, auth_headers):
        """Test upload without audio file"""
        response = client.post("/api/voice/audio/upload", headers=auth_headers)

        assert response.status_code == 400


class TestVoiceSettings:
    """Test voice settings functionality"""

    @patch("app.auth_decorators.verify_jwt_in_request")
    @patch("app.auth_decorators.get_jwt_identity")
    def test_get_voice_settings(
        self, mock_jwt_identity, mock_verify_jwt, client, auth_headers
    ):
        """Test getting voice settings"""
        mock_jwt_identity.return_value = "test@example.com"
        mock_verify_jwt.return_value = True

        with patch("app.auth_decorators.users_db") as mock_users_db:
            mock_users_db.get.return_value = {
                "email": "test@example.com",
                "role": "developer",
            }

            response = client.get("/api/voice/settings", headers=auth_headers)

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert "language" in data["data"]
            assert "auto_save" in data["data"]
            assert "commit_templates" in data["data"]

    @patch("app.auth_decorators.verify_jwt_in_request")
    @patch("app.auth_decorators.get_jwt_identity")
    def test_update_voice_settings(
        self, mock_jwt_identity, mock_verify_jwt, client, auth_headers
    ):
        """Test updating voice settings"""
        mock_jwt_identity.return_value = "test@example.com"
        mock_verify_jwt.return_value = True

        with patch("app.auth_decorators.users_db") as mock_users_db:
            mock_users_db.get.return_value = {
                "email": "test@example.com",
                "role": "developer",
            }

            payload = {
                "language": "en-GB",
                "auto_save": False,
                "push_to_talk": True,
                "noise_reduction": False,
            }

            response = client.post(
                "/api/voice/settings",
                data=json.dumps(payload),
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert data["data"]["language"] == "en-GB"
            assert data["data"]["push_to_talk"] is True


if __name__ == "__main__":
    pytest.main([__file__])
