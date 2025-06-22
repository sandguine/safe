# Robust Execution Guide for Oversight Curriculum

This guide ensures your oversight curriculum runs smoothly every time by addressing all critical setup requirements and providing robust execution scripts.

## 🎯 Quick Start

### Option 1: Bash Script (Recommended for Unix/Linux/macOS)
```bash
# Make executable and run
chmod +x run_robust.sh
./run_robust.sh
```

### Option 2: Python Script (Cross-platform)
```bash
python run_safe.py
```

## 📋 Prerequisites Checklist

Before running, ensure you have:

### 1. ✅ Working Directory
- Script automatically sets `PWD` to `anthropic/oversight_curriculum`
- No manual directory navigation needed

### 2. ✅ Environment Variables
- `.env` file with `CLAUDE_API_KEY=sk-your-actual-key`
- Script validates API key format and presence
- Automatic `.env` template creation if missing

### 3. ✅ Python Environment
- Python 3.7+ installed
- Virtual environment recommended (but not required)
- All dependencies from `requirements.txt` installed

### 4. ✅ Dependencies
- `python-dotenv` for environment loading
- `requests` for API calls
- `pandas` for data processing
- `matplotlib` for plotting
- All other packages in `requirements.txt`

## 🔧 Setup Steps

### Step 1: Clone and Navigate
```bash
cd /path/to/your/project
git clone <repository-url>
cd anthropic/oversight_curriculum
```

### Step 2: Set Up Environment
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure API Key
```bash
# Edit .env file
nano .env

# Add your API key:
CLAUDE_API_KEY=sk-your-actual-api-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
LOG_LEVEL=INFO
```

### Step 4: Verify Setup
```bash
python verify_setup.py
```

## 🚀 Execution Scripts

### Bash Script (`run_robust.sh`)

**Features:**
- ✅ Automatic directory navigation
- ✅ Environment variable loading and validation
- ✅ Dependency checking and installation
- ✅ Comprehensive error handling
- ✅ Colored output for better UX
- ✅ User prompts for error recovery
- ✅ Automatic cleanup

**Usage:**
```bash
# Basic execution
./run_robust.sh

# With custom parameters
CYCLES=5 PUZZLES_PER_CYCLE=3 SOLUTIONS_PER_PUZZLE=2 ./run_robust.sh
```

**What it does:**
1. **Directory Check**: Ensures you're in `oversight_curriculum`
2. **Environment Load**: Loads and validates `.env` file
3. **Dependency Check**: Verifies Python and all packages
4. **Verification**: Runs `verify_setup.py`
5. **Directory Creation**: Creates `results/`, `logs/`, `temp/`
6. **Main Execution**: Runs `azr_loop.py` with parameters
7. **Analysis**: Runs analysis on results (if available)
8. **Tests**: Runs unit tests (if available)
9. **Cleanup**: Removes temporary files and cache
10. **Summary**: Generates execution report

### Python Script (`run_safe.py`)

**Features:**
- ✅ Cross-platform compatibility (Windows, macOS, Linux)
- ✅ Same robust error handling as bash script
- ✅ Command-line argument parsing
- ✅ Dry-run mode for testing
- ✅ Detailed logging and reporting

**Usage:**
```bash
# Basic execution
python run_safe.py

# With custom parameters
python run_safe.py --cycles 5 --puzzles-per-cycle 3 --solutions-per-puzzle 2

# Dry run (see what would happen without executing)
python run_safe.py --dry-run
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. "CLAUDE_API_KEY not found"
**Solution:**
```bash
# Check if .env file exists
ls -la .env

# Create .env file if missing
echo "CLAUDE_API_KEY=sk-your-actual-key" > .env
```

#### 2. "Python 3 is not installed"
**Solution:**
```bash
# On macOS
brew install python3

# On Ubuntu/Debian
sudo apt-get install python3 python3-pip

# On Windows
# Download from python.org
```

#### 3. "Missing packages"
**Solution:**
```bash
# Install all requirements
pip install -r requirements.txt

# Or install specific missing package
pip install python-dotenv requests pandas matplotlib
```

#### 4. "Permission denied" (bash script)
**Solution:**
```bash
chmod +x run_robust.sh
```

#### 5. "Directory not found"
**Solution:**
```bash
# Ensure you're in the right location
pwd
# Should show: /path/to/anthropic/oversight_curriculum

# If not, navigate there
cd /path/to/anthropic/oversight_curriculum
```

### Verification Steps

Run these commands to verify your setup:

```bash
# 1. Check working directory
pwd
# Should end with: oversight_curriculum

# 2. Check Python version
python3 --version
# Should be 3.7 or higher

# 3. Check .env file
cat .env
# Should contain CLAUDE_API_KEY=sk-...

# 4. Check dependencies
python3 -c "import dotenv, requests, pandas, matplotlib; print('All packages available')"

# 5. Run verification
python3 verify_setup.py
```

## 📊 Output and Results

### Generated Files
After successful execution, you'll find:

```
results/
├── robust_run_YYYYMMDD_HHMMSS.csv    # Main results
├── execution_summary_YYYYMMDD_HHMMSS.txt  # Execution report
├── baseline_*.csv                     # Baseline experiment results
├── oversight_*.csv                    # Oversight experiment results
└── comparison_*.png                   # Visual comparisons

logs/
└── execution_logs.txt                 # Detailed logs

temp/
└── (temporary files, cleaned after execution)
```

### Execution Summary
The script provides a detailed summary including:
- ✅ Working directory
- ✅ Python version
- ✅ API key status (masked)
- ✅ Execution time
- ✅ Steps completed
- ✅ Generated files list
- ✅ Completion timestamp

## 🔄 Automation

### For Regular Execution
Create a simple wrapper script:

```bash
#!/bin/bash
# daily_run.sh

cd /path/to/anthropic/oversight_curriculum
./run_robust.sh

# Optional: Send results via email or upload to cloud
# mail -s "Oversight Curriculum Results" your@email.com < results/execution_summary_*.txt
```

### Cron Job (Linux/macOS)
```bash
# Add to crontab (runs daily at 9 AM)
0 9 * * * /path/to/anthropic/oversight_curriculum/daily_run.sh
```

## 🎯 Best Practices

### 1. Always Use Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Keep API Key Secure
```bash
# Never commit .env to version control
echo ".env" >> .gitignore
```

### 3. Regular Verification
```bash
# Run verification before each execution
python verify_setup.py
```

### 4. Monitor Resources
```bash
# Check disk space
df -h

# Check memory usage
free -h
```

### 5. Backup Results
```bash
# Archive results periodically
tar -czf results_backup_$(date +%Y%m%d).tar.gz results/
```

## 🆘 Emergency Recovery

If something goes wrong:

1. **Check logs**: Look at `logs/` directory
2. **Verify setup**: Run `python verify_setup.py`
3. **Clean and retry**: Remove `temp/` and `__pycache__/` directories
4. **Reset environment**: Deactivate and reactivate virtual environment
5. **Check API quota**: Verify your Claude API key has sufficient credits

## 📞 Support

If you encounter issues:

1. Check this guide first
2. Run `python verify_setup.py` for diagnostics
3. Check the logs in `logs/` directory
4. Ensure all prerequisites are met
5. Try the dry-run mode: `python run_safe.py --dry-run`

---

**Remember**: These scripts are designed to be robust and handle most common issues automatically. They will guide you through any problems and provide clear error messages to help you resolve them quickly. 