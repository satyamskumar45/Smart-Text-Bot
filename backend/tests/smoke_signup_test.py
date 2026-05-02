"""Smoke test for /auth/signup that mocks DB interactions.

Run locally after activating your backend venv and installing requirements:

$ python -m venv .venv
$ .\.venv\Scripts\Activate.ps1
$ pip install -r backend\requirements.txt
$ python backend\tests\smoke_signup_test.py

The script prints HTTP status and JSON response.
"""
import os
from datetime import datetime

# Ensure JWT secret present
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from flask import Flask

# Import the auth blueprint
from backend.routes.auth_routes import auth_bp
from backend.models.user_model import UserModel
from backend.models.refresh_token_model import RefreshTokenModel

# Mock DB interactions

def fake_find_by_email(cls, email, include_password=False):
    return None


def fake_create_user(cls, email, password_hash, name=None, role=None, is_guest=False, guest_session_id=None):
    return {
        "id": "fakeid123",
        "email": email,
        "role": role or "user",
        "created_at": datetime.utcnow(),
    }


def fake_create_token(cls, user_id, token, expires_at):
    return {"id": "rtfake", "user_id": str(user_id), "token": token}

# Patch the classmethods
UserModel.find_by_email = classmethod(fake_find_by_email)
UserModel.create_user = classmethod(fake_create_user)
RefreshTokenModel.create_token = classmethod(fake_create_token)

# Create a minimal Flask app and register blueprint
app = Flask(__name__)
app.register_blueprint(auth_bp)

# Use test client to call signup
with app.test_client() as client:
    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "Password123!", "name": "Tester"},
    )
    print("STATUS:", response.status_code)
    try:
        print("JSON:", response.get_json())
    except Exception as e:
        print("Failed to parse JSON:", e)
        print("DATA:", response.data)
