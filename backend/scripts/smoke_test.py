import os
import json

# Ensure required env vars before importing Settings
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret')

# Ensure project root is on sys.path so package imports work when running this script
import sys
from pathlib import Path
# Add the `backend` package folder to sys.path so imports like `from utils...` resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app as application

# Use the module-level `app` instance so routes defined at module scope (like /routes)
app = application
client = app.test_client()

res = client.get('/health')
print('/health ->', res.status_code, res.get_data(as_text=True))

res = client.get('/routes')
print('/routes ->', res.status_code)
try:
    print(json.loads(res.get_data(as_text=True)))
except Exception as e:
    print('routes response not JSON:', res.get_data(as_text=True))

print('\nRegistered URL rules:')
for rule in app.url_map.iter_rules():
    print(str(rule))
