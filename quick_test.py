#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=== Quick Status Check ===")
print(f"API Key loaded: {'Yes' if os.getenv('CLAUDE_API_KEY') else 'No'}")

if os.getenv('CLAUDE_API_KEY'):
    key = os.getenv('CLAUDE_API_KEY')
    print(f"Key format: {key[:10]}...{key[-4:]}")
    print(f"Key length: {len(key)} characters")
else:
    print("No API key found in .env file")

# Test model import
try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    import model
    print("✅ Model imported successfully")
    
    # Test API call
    try:
        response = model.ask("Say 'hello'")
        print(f"✅ API call successful: {response}")
    except Exception as e:
        print(f"❌ API call failed: {e}")
        
except Exception as e:
    print(f"❌ Model import failed: {e}") 