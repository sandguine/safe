# Setup Guide for Claude API

## Quick Fix Steps

### 1. Set Your API Key

**Option A: Set environment variable (recommended)**
```bash
# On macOS/Linux:
export CLAUDE_API_KEY="sk-your-actual-api-key-here"

# On Windows:
set CLAUDE_API_KEY=sk-your-actual-api-key-here
```

**Option B: Create a .env file**
```bash
# Create .env file in project root
echo "CLAUDE_API_KEY=sk-your-actual-api-key-here" > .env
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Test the Setup
```bash
python verify_setup.py
```

## What Was Wrong

The main issues in your original `model.py` were:

1. **API Key Validation**: No check if the API key was set
2. **Response Parsing**: Wrong path to extract the response text
   - ❌ `data["content"]` 
   - ✅ `data["content"][0]["text"]`

## Fixed Issues

✅ **Added API key validation** - Now checks if `CLAUDE_API_KEY` is set
✅ **Fixed response parsing** - Correctly extracts text from Claude's response
✅ **Better error handling** - More informative error messages

## Verification Steps

Run `python verify_setup.py` to check:
1. ✅ API key is set and valid format
2. ✅ Dependencies are installed
3. ✅ Model module can be imported
4. ✅ API request works

## Next Steps

Once the verification passes, you can proceed with implementing:
1. The main deduction loop (port from AZR)
2. The referee system
3. Metrics collection
4. Comparison framework 