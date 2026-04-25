#!/usr/bin/env python3
"""
Debug Script - Checks all components of the translation system
Run this before starting the Flask server to identify issues
"""

import os
import sys
from pathlib import Path

print("\n" + "="*70)
print("  TRANSLATION SYSTEM DEBUG SCRIPT")
print("="*70)

# 1. Check Python version
print("\n[1] Python Version")
print(f"    Python: {sys.version}")
python_ok = sys.version_info >= (3, 7)
print(f"    Status: {'✓ OK' if python_ok else '✗ FAIL'}")

# 2. Check working directory
print("\n[2] Working Directory")
backend_dir = Path(__file__).parent
print(f"    Current: {backend_dir}")
print(f"    Status: ✓ OK")

# 3. Check .env file
print("\n[3] Environment File (.env)")
env_path = backend_dir.parent / ".env"
env_exists = env_path.exists()
print(f"    Path: {env_path}")
print(f"    Exists: {'✓ Yes' if env_exists else '✗ No'}")

if env_exists:
    with open(env_path, 'r') as f:
        env_content = f.read()
    print(f"    Content preview:")
    for line in env_content.split('\n')[:3]:
        if line.strip():
            print(f"      {line}")
else:
    print(f"    ✗ ERROR: .env file not found!")

# 4. Check required packages
print("\n[4] Required Packages")
required_packages = {
    'flask': 'Flask',
    'flask_cors': 'flask-cors',
    'groq': 'groq',
    'dotenv': 'python-dotenv',
}

all_packages_ok = True
for import_name, package_name in required_packages.items():
    try:
        __import__(import_name)
        print(f"    {package_name}: ✓ Installed")
    except ImportError:
        print(f"    {package_name}: ✗ NOT INSTALLED")
        all_packages_ok = False

# 5. Load environment variables
print("\n[5] Environment Variables")
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)
    print(f"    dotenv.load_dotenv(): ✓ Success")
except Exception as e:
    print(f"    dotenv.load_dotenv(): ✗ Error - {e}")

# 6. Check GROQ_API_KEY
print("\n[6] GROQ_API_KEY")
api_key = os.getenv("GROQ_API_KEY")

if api_key:
    # Check for quotes
    if api_key.startswith('"') or api_key.startswith("'"):
        print(f"    Status: ⚠ WARNING - Key has quotes!")
        print(f"    Value: {api_key[:30]}...")
        api_key_clean = api_key.strip('"\'')
        print(f"    After strip: {api_key_clean[:30]}...")
    else:
        print(f"    Status: ✓ Loaded (no quotes)")
        print(f"    Length: {len(api_key)} characters")
        print(f"    Preview: {api_key[:10]}...{api_key[-10:]}")
else:
    print(f"    Status: ✗ NOT FOUND")
    print(f"    Current environment vars: {list(os.environ.keys())[:5]}...")

# 7. Test Groq client initialization
print("\n[7] Groq Client Initialization")
try:
    from groq import Groq
    
    # Get the API key (strip quotes if present)
    test_key = os.getenv("GROQ_API_KEY")
    if test_key:
        test_key = test_key.strip('"\'')
    
    if not test_key:
        print(f"    Status: ✗ No API key to initialize")
    else:
        try:
            client = Groq(api_key=test_key)
            print(f"    Status: ✓ Groq client created successfully")
            
            # Try to list models (simple API call)
            print(f"    Attempting to list available models...")
            try:
                models = client.models.list()
                print(f"    Status: ✓ API is accessible")
                print(f"    Available models: {len(list(models.data))} models found")
            except Exception as e:
                print(f"    Status: ⚠ API test failed: {e}")
                
        except Exception as e:
            print(f"    Status: ✗ Error: {e}")
            
except ImportError:
    print(f"    Status: ✗ Groq package not installed")

# 8. Check services module
print("\n[8] Services Module")
try:
    services_path = backend_dir / "services" / "groq_service.py"
    if services_path.exists():
        print(f"    groq_service.py: ✓ Found")
        
        # Try to import
        try:
            sys.path.insert(0, str(backend_dir))
            import services.groq_service
            print(f"    Import groq_service: ✓ Success")
            
            # Check functions
            if hasattr(services.groq_service, 'complete'):
                print(f"    complete() function: ✓ Found")
            else:
                print(f"    complete() function: ✗ Not found")
                
            if hasattr(services.groq_service, 'translate_text'):
                print(f"    translate_text() function: ✓ Found")
            else:
                print(f"    translate_text() function: ✗ Not found")
                
        except Exception as e:
            print(f"    Import error: ✗ {e}")
    else:
        print(f"    groq_service.py: ✗ Not found at {services_path}")
        
except Exception as e:
    print(f"    Error: {e}")

# 9. Check routes module
print("\n[9] Routes Module")
try:
    routes_path = backend_dir / "routes" / "translate_routes.py"
    if routes_path.exists():
        print(f"    translate_routes.py: ✓ Found")
        
        try:
            from routes import translate_routes
            print(f"    Import translate_routes: ✓ Success")
            
            if hasattr(translate_routes, 'translate_bp'):
                print(f"    translate_bp blueprint: ✓ Found")
            else:
                print(f"    translate_bp blueprint: ✗ Not found")
                
        except Exception as e:
            print(f"    Import error: ✗ {e}")
    else:
        print(f"    translate_routes.py: ✗ Not found")
        
except Exception as e:
    print(f"    Error: {e}")

# 10. Check Flask app
print("\n[10] Flask Application")
try:
    app_path = backend_dir / "app.py"
    if app_path.exists():
        print(f"    app.py: ✓ Found")
        
        try:
            from app import app
            print(f"    Import app: ✓ Success")
            
            # Check if blueprints are registered
            print(f"    Registered blueprints: {list(app.blueprints.keys())}")
            
            if 'translate' in app.blueprints:
                print(f"    translate blueprint: ✓ Registered")
            else:
                print(f"    translate blueprint: ✗ NOT registered")
                
        except Exception as e:
            print(f"    Import error: ✗ {e}")
    else:
        print(f"    app.py: ✗ Not found")
        
except Exception as e:
    print(f"    Error: {e}")

# Final summary
print("\n" + "="*70)
print("  SUMMARY")
print("="*70)

if env_exists and api_key and all_packages_ok:
    print("\n✓ All components appear to be properly configured!")
    print("\nYou can now run: python app.py")
    print("Then test with: python test_translation.py")
else:
    print("\n✗ Some components need attention. Review the issues above.")
    
    if not env_exists:
        print("   - Create .env file with GROQ_API_KEY")
    if not api_key:
        print("   - Set GROQ_API_KEY in .env")
    if not all_packages_ok:
        print("   - Run: pip install -r requirements.txt")

print("\n")
