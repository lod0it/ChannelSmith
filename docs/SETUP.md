# ChannelSmith - Development Environment Setup

This guide will help you set up your development environment for ChannelSmith.

---

## 📋 Prerequisites

### Required Software
- **Python 3.8 or higher** ([Download](https://www.python.org/downloads/))
  - ⚠️ During installation on Windows, check "Add Python to PATH"
- **Git** ([Download](https://git-scm.com/downloads))
- **Code Editor** - Recommended: VS Code, PyCharm, or any editor with Python support

### Verify Installation
Open terminal/command prompt and run:

```bash
python --version
# Should show: Python 3.8.x or higher

pip --version
# Should show pip version

git --version
# Should show git version
```

---

## 🚀 Initial Setup

### 1. Create Project Directory

```bash
# Create project folder
mkdir ChannelSmith
cd ChannelSmith

# Initialize Git repository
git init
git checkout -b dev  # Create and switch to dev branch
```

### 2. Create Virtual Environment

A virtual environment keeps project dependencies isolated.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when activated.

### 3. Create Project Structure

```bash
# Create directory structure
mkdir -p channelsmith/{core,gui,templates,utils}
mkdir -p tests/{test_core,test_templates,test_integration}
mkdir docs

# Create __init__.py files (makes directories Python packages)
# Windows
type nul > channelsmith/__init__.py
type nul > channelsmith/core/__init__.py
type nul > channelsmith/gui/__init__.py
type nul > channelsmith/templates/__init__.py
type nul > channelsmith/utils/__init__.py

# macOS/Linux
touch channelsmith/__init__.py
touch channelsmith/core/__init__.py
touch channelsmith/gui/__init__.py
touch channelsmith/templates/__init__.py
touch channelsmith/utils/__init__.py
```

Your structure should look like:
```
ChannelSmith/
├── channelsmith/
│   ├── __init__.py
│   ├── core/
│   │   └── __init__.py
│   ├── gui/
│   │   └── __init__.py
│   ├── templates/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── test_core/
│   ├── test_templates/
│   └── test_integration/
├── docs/
└── venv/
```

### 4. Place Setup Files

Copy these files to the root of your project:
- `CLAUDE.md` (this file you already have)
- `SETUP.md` (this file)
- `ALPHA_TASKS.md`
- `requirements.txt`
- `.gitignore`
- `README.md`
- `docs/MVP_Documentation.md`

### 5. Install Dependencies

```bash
# Make sure virtual environment is activated (you see (venv) in prompt)
pip install -r requirements.txt
```

This installs:
- Pillow (image processing)
- NumPy (array operations)
- pytest (testing)
- black (code formatter)
- pylint (linter)

### 6. Verify Installation

```bash
# Test that packages are installed
python -c "import PIL; import numpy; import pytest; print('All packages imported successfully!')"
```

---

## 🛠️ Development Tools Setup

### VS Code (Recommended)

1. **Install VS Code:** https://code.visualstudio.com/

2. **Install Python Extension:**
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
   - Search "Python" by Microsoft
   - Click Install

3. **Select Python Interpreter:**
   - Press Ctrl+Shift+P / Cmd+Shift+P
   - Type "Python: Select Interpreter"
   - Choose the one from your `venv` folder

4. **Recommended Extensions:**
   - Python (Microsoft)
   - Pylance (Microsoft)
   - Python Test Explorer
   - GitLens

5. **Settings (Optional):**
   Create `.vscode/settings.json`:
   ```json
   {
     "python.formatting.provider": "black",
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true,
     "python.testing.pytestEnabled": true,
     "editor.formatOnSave": true
   }
   ```

### PyCharm

1. **Open Project:** File → Open → Select ChannelSmith folder
2. **Configure Interpreter:** File → Settings → Project → Python Interpreter → Add → Existing environment → Select venv
3. **Enable pytest:** Settings → Tools → Python Integrated Tools → Default test runner → pytest

---

## 🧪 Testing Your Setup

### Run a Quick Test

Create a test file to verify everything works:

**File:** `tests/test_setup.py`
```python
"""Test to verify development environment is set up correctly."""

import numpy as np
from PIL import Image


def test_numpy_works():
    """Test that NumPy is working."""
    array = np.array([1, 2, 3])
    assert array.sum() == 6


def test_pillow_works():
    """Test that Pillow is working."""
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    assert img.size == (100, 100)
    assert img.mode == 'RGB'


def test_imports():
    """Test that project structure is importable."""
    # This will fail until you create the modules, but that's expected
    # Uncomment these as you create the files:
    # from channelsmith.core import channel_map
    # from channelsmith.templates import template_loader
    pass
```

**Run the test:**
```bash
pytest tests/test_setup.py -v
```

You should see:
```
tests/test_setup.py::test_numpy_works PASSED
tests/test_setup.py::test_pillow_works PASSED
tests/test_setup.py::test_imports PASSED
```

---

## 🎨 Code Quality Tools

### Black (Code Formatter)

Format your code automatically:

```bash
# Format all Python files
black channelsmith/

# Check what would be changed without modifying
black --check channelsmith/

# Format a specific file
black channelsmith/core/channel_map.py
```

### Pylint (Linter)

Check code quality:

```bash
# Lint the entire package
pylint channelsmith/

# Lint a specific file
pylint channelsmith/core/channel_map.py

# Get score
pylint channelsmith/ --score=y
```

---

## 📦 Git Configuration

### Create .gitignore

Already provided in `.gitignore` file.

### First Commit

```bash
# Check what files will be committed
git status

# Add all files
git add .

# Create first commit
git commit -m "feat(setup): initial project structure"

# Create main branch and switch back to dev
git branch main
git checkout dev
```

---

## 🔄 Daily Development Workflow

### 1. Start Working

```bash
# Navigate to project
cd ChannelSmith

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Make sure you're on dev branch
git checkout dev

# Pull latest changes (if working with team)
git pull origin dev
```

### 2. Write Code

- Create/edit files in `channelsmith/`
- Write tests in `tests/`
- Run tests frequently: `pytest`

### 3. Before Committing

```bash
# Format code
black channelsmith/

# Run tests
pytest

# Check lint (optional, don't stress over perfect scores initially)
pylint channelsmith/

# Check what changed
git status
git diff
```

### 4. Commit Changes

```bash
# Add files
git add .

# Commit with conventional message
git commit -m "feat(core): add ChannelMap class"

# Push to remote (if you set up GitHub/GitLab)
git push origin dev
```

### 5. End of Day

```bash
# Deactivate virtual environment
deactivate
```

---

## 🐛 Troubleshooting

### "python not found" or "pip not found"

**Windows:**
- Reinstall Python and check "Add Python to PATH"
- Or manually add to PATH: System Properties → Environment Variables → PATH → Add Python installation folder

**macOS/Linux:**
- Use `python3` and `pip3` instead of `python` and `pip`
- Or create alias: `alias python=python3` in `~/.bashrc` or `~/.zshrc`

### Virtual Environment Not Activating

**Windows:**
```bash
# If activation fails, try:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then activate again
```

**macOS/Linux:**
```bash
# Make sure you're in the project directory
cd ChannelSmith
source venv/bin/activate
```

### Pillow Installation Fails on Windows

Install Microsoft C++ Build Tools:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

Or use pre-compiled wheels:
```bash
pip install --upgrade pip
pip install Pillow
```

### Tests Not Found by pytest

Make sure:
1. Virtual environment is activated
2. pytest is installed: `pip list | grep pytest`
3. You're in the project root directory
4. Test files start with `test_`

```bash
# Run from project root
cd ChannelSmith
pytest
```

### Import Errors

Make sure `__init__.py` files exist in all package directories:
```
channelsmith/__init__.py
channelsmith/core/__init__.py
channelsmith/gui/__init__.py
channelsmith/templates/__init__.py
channelsmith/utils/__init__.py
```

---

## 📚 Next Steps

Once setup is complete:

1. ✅ Read `CLAUDE.md` - Understand project context
2. ✅ Read `docs/MVP_Documentation.md` - Understand full specification
3. ✅ Check `ALPHA_TASKS.md` - See implementation roadmap
4. 🚀 Start coding! Begin with `channelsmith/core/channel_map.py`

---

## 🆘 Getting Help

### Resources
- **Python Docs:** https://docs.python.org/3/
- **Pillow Docs:** https://pillow.readthedocs.io/
- **NumPy Docs:** https://numpy.org/doc/
- **pytest Docs:** https://docs.pytest.org/

### When Working with Claude Code
- Ensure all context files (CLAUDE.md, MVP_Documentation.md) are in the project
- Reference specific sections: "See CLAUDE.md section on Testing Strategy"
- Provide error messages in full for debugging

---

**Setup Complete! 🎉**

You're ready to start development. Good luck with ChannelSmith!
