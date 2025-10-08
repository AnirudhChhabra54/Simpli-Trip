# VSCode Setup Guide for SimpliTrip

This guide helps you fix Pylance import errors and configure VSCode properly for the SimpliTrip project.

## ✅ Issues Fixed

1. ✅ **Kaggle API configured** - Credentials stored in `~/.kaggle/kaggle.json`
2. ✅ **VSCode Python interpreter configured** - Points to backend virtual environment
3. ✅ **All Python packages installed** - setuptools, pandas, kaggle, and all ML libraries
4. ✅ **Pylance import errors resolved** - VSCode settings configured

---

## 🔧 Configuration Details

### 1. VSCode Settings (`.vscode/settings.json`)

The following settings have been configured:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
    "python.analysis.extraPaths": ["${workspaceFolder}/backend"],
    "python.autoComplete.extraPaths": ["${workspaceFolder}/backend"]
}
```

**What this does:**
- Points VSCode to use the Python interpreter in `backend/venv/`
- Adds the backend directory to Python's module search path
- Enables autocomplete for all backend modules

### 2. Kaggle API Configuration

**Location:** `~/.kaggle/kaggle.json`

**Permissions:** `600` (read/write for owner only)

**Credentials:**
- Username: `deathwalker5454`
- API Key: Configured ✅

---

## 🚀 How to Use

### Step 1: Select Python Interpreter in VSCode

1. Open VSCode Command Palette: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type: `Python: Select Interpreter`
3. Choose: `./backend/venv/bin/python`

### Step 2: Reload VSCode Window

1. Open Command Palette: `Cmd+Shift+P`
2. Type: `Developer: Reload Window`
3. Press Enter

### Step 3: Verify Imports

Open any Python file in the backend (e.g., `backend/main.py`) and check that:
- ✅ No red squiggly lines under imports
- ✅ Autocomplete works for imported modules
- ✅ Hover tooltips show correct documentation

---

## 🧪 Testing the Setup

### Test 1: Verify Python Interpreter

```bash
cd simplitrip/backend
source venv/bin/activate
python --version
# Should show: Python 3.11.x or similar
```

### Test 2: Test Imports

```bash
cd simplitrip/backend
source venv/bin/activate
python -c "import setuptools, pandas, kaggle; print('✅ All imports successful!')"
```

**Expected Output:**
```
✅ All imports successful!
```

### Test 3: Test Kaggle API

```bash
cd simplitrip/backend
source venv/bin/activate
python -c "from kaggle.api.kaggle_api_extended import KaggleApi; api = KaggleApi(); api.authenticate(); print('✅ Kaggle API authenticated!')"
```

---

## 🐛 Troubleshooting

### Issue: Pylance still shows import errors

**Solution 1: Reload VSCode**
```
Cmd+Shift+P → "Developer: Reload Window"
```

**Solution 2: Clear Python Language Server Cache**
```
Cmd+Shift+P → "Python: Clear Cache and Reload Window"
```

**Solution 3: Manually select interpreter**
```
Cmd+Shift+P → "Python: Select Interpreter" → Choose backend/venv/bin/python
```

### Issue: "Module not found" errors

**Solution: Reinstall packages**
```bash
cd simplitrip/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Kaggle API authentication fails

**Solution: Check credentials file**
```bash
cat ~/.kaggle/kaggle.json
# Should show your username and key

# Fix permissions if needed
chmod 600 ~/.kaggle/kaggle.json
```

### Issue: Virtual environment not found

**Solution: Recreate virtual environment**
```bash
cd simplitrip/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📦 Installed Packages

The following packages are installed in the virtual environment:

### Core Framework
- fastapi==0.109.0
- uvicorn[standard]==0.27.0
- pydantic==2.5.3

### Machine Learning
- scikit-learn==1.4.0
- xgboost==2.0.3
- pandas==2.2.0
- numpy==1.26.3

### Deep Learning & LLM
- torch==2.2.0
- transformers==4.37.2
- accelerate==0.26.1

### Data Processing
- kaggle==1.6.6
- openpyxl==3.1.2

### Database
- sqlalchemy==2.0.25
- redis==5.0.1

### Utilities
- python-dotenv==1.0.0
- pyyaml==6.0.1
- tqdm==4.66.1

---

## 🎯 Quick Commands

### Activate Virtual Environment
```bash
cd simplitrip/backend
source venv/bin/activate
```

### Start Backend Server
```bash
cd simplitrip/backend
source venv/bin/activate
python main.py
```

### Run Tests
```bash
cd simplitrip/backend
source venv/bin/activate
pytest tests/
```

### Download Kaggle Datasets
```bash
cd simplitrip/backend
source venv/bin/activate
python scripts/download_datasets.py
```

---

## ✨ VSCode Extensions Recommended

Install these extensions for the best development experience:

1. **Python** (ms-python.python)
   - Python language support with IntelliSense

2. **Pylance** (ms-python.vscode-pylance)
   - Fast, feature-rich language support for Python

3. **Black Formatter** (ms-python.black-formatter)
   - Code formatting with Black

4. **Python Debugger** (ms-python.debugpy)
   - Debugging support

5. **autoDocstring** (njpwerner.autodocstring)
   - Generate Python docstrings automatically

---

## 📝 Notes

- The virtual environment is located at `simplitrip/backend/venv/`
- All Python dependencies are isolated within this virtual environment
- VSCode is configured to use this virtual environment automatically
- Kaggle API credentials are stored securely in `~/.kaggle/kaggle.json`

---

## ✅ Verification Checklist

- [x] Virtual environment created at `backend/venv/`
- [x] All packages installed from `requirements.txt`
- [x] VSCode settings configured in `.vscode/settings.json`
- [x] Kaggle API credentials configured
- [x] Python imports working (setuptools, pandas, kaggle)
- [x] Pylance import errors resolved

---

## 🆘 Need Help?

If you're still experiencing issues:

1. Check the terminal output for specific error messages
2. Verify Python version: `python --version` (should be 3.11+)
3. Verify pip version: `pip --version`
4. Check virtual environment activation: `which python` (should point to venv)
5. Review VSCode Python extension logs: Output → Python

---

**Last Updated:** January 2025
**Status:** ✅ All configurations complete and tested
