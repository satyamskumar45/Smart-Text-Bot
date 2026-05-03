import os
import sys
from pathlib import Path
import json

# Setup paths and env
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret')

from app import app

client = app.test_client()

payload = {
    "email": "noone@example.test",
    "password": "wrong-password"
}

res = client.post('/auth/login', json=payload)
print('status:', res.status_code)
try:
    print(json.dumps(res.get_json(), indent=2))
except Exception:
    print('raw:', res.get_data(as_text=True))
