# ChannelSmith Installation Guide

Welcome! This guide covers three installation methods for ChannelSmith, from easiest to most technical.

---

## Method 1: Standalone Executable (Easiest) ⭐

**Perfect for:** Game artists and non-developers
**Requirements:** Windows 10+, macOS 12+, or Linux (Ubuntu 20.04+)
**Time:** 2 minutes

### Steps

1. **Download** the latest executable from [GitHub Releases](https://github.com/yourusername/channelsmith/releases)
   - Windows: `ChannelSmith-Windows.zip`
   - macOS: `ChannelSmith-macOS.zip`
   - Linux: `ChannelSmith-Linux.tar.gz`

2. **Extract** the archive to your desired location

3. **Run** the executable
   - **Windows:** Double-click `ChannelSmith.exe`
   - **macOS:** Double-click `ChannelSmith`
   - **Linux:** `./ChannelSmith` in terminal

4. **Browser opens automatically** to http://localhost:5000

That's it! No Python installation required.

### Troubleshooting

- **Windows SmartScreen warning:** Click "More info" → "Run anyway" (safe, we're open source)
- **Port 5000 already in use:** Close other applications using that port or restart your computer
- **Browser doesn't open:** Manually visit http://localhost:5000

---

## Method 2: Installer Scripts (Recommended for Mac/Linux) 🔧

**Perfect for:** Mac/Linux users who want automatic setup
**Requirements:** Python 3.8+, basic terminal knowledge
**Time:** 5 minutes (first time), 30 seconds (subsequent runs)

### Steps

1. **Download or clone the repository:**
   ```bash
   git clone https://github.com/yourusername/channelsmith.git
   cd channelsmith
   ```

2. **Make scripts executable** (first time only):
   ```bash
   chmod +x launch_web_ui.sh launch_simple.sh install.sh
   ```

3. **Run setup wizard** (first time):
   ```bash
   ./install.sh
   ```
   This will:
   - Check Python installation
   - Create virtual environment
   - Install all dependencies
   - Run health check
   - Print success message

4. **Launch the app**:
   ```bash
   ./launch_web_ui.sh
   ```

### Subsequent Launches

After first-time setup, just run:
```bash
./launch_web_ui.sh
```

Or for quick launch:
```bash
./launch_simple.sh
```

### Manual Activation

If you prefer to activate the environment manually:
```bash
source venv/bin/activate
python -m channelsmith
```

### Troubleshooting

- **"Python 3 is not installed":** Install Python 3.8+ from https://www.python.org/ or use `brew install python3` (macOS)
- **"Permission denied":** Run `chmod +x *.sh` to make scripts executable
- **"venv not found":** Run `./install.sh` to create virtual environment
- **Flask import errors:** Run `pip install flask flask-cors`

---

## Method 3: Manual Python Installation (For Developers) 👨‍💻

**Perfect for:** Developers who want full control
**Requirements:** Python 3.8+, pip, git
**Time:** 10 minutes

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/channelsmith.git
   cd channelsmith
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Upgrade pip:**
   ```bash
   pip install --upgrade pip
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Launch the application:**
   ```bash
   python -m channelsmith
   ```

Browser opens automatically at http://localhost:5000

### Development Features

For development, you may want additional tools:
```bash
# Install with development extras
pip install -r requirements-dev.txt

# Format code
black channelsmith/

# Run linter
pylint channelsmith/

# Run tests with coverage
pytest --cov=channelsmith --cov-report=html
```

---

## System Requirements

### Windows
- Windows 10 or newer
- ~500 MB disk space (executable + temp files)
- No Python required for standalone executable

### macOS
- macOS 12 (Monterey) or newer
- ~500 MB disk space
- Intel or Apple Silicon (M1/M2/M3)
- No Python required for standalone executable

### Linux
- Ubuntu 20.04+ (or equivalent)
- ~500 MB disk space
- No Python required for standalone executable

### All Platforms (Manual Installation)
- Python 3.8 or higher
- pip (Python package manager)
- ~1.5 GB disk space (includes dependencies)

---

## Uninstalling ChannelSmith

### Standalone Executable
Simply delete the extracted folder. No registry entries or system files are modified.

### Installed from Scripts
1. Delete the entire `channelsmith` folder
2. No other files to clean up

### Manual Installation
```bash
# Remove virtual environment
rm -rf venv

# Remove repository
rm -rf channelsmith/

# (On Windows, use: rmdir /s venv & rmdir /s channelsmith)
```

---

## Upgrading ChannelSmith

### Standalone Executable
1. Download the new version from [GitHub Releases](https://github.com/yourusername/channelsmith/releases)
2. Extract to a new location (or overwrite old one)
3. Run the new executable

### From Scripts/Manual Installation
```bash
# Pull latest code
git pull origin main

# Reinstall dependencies (in case there are new ones)
pip install -r requirements.txt --upgrade

# Restart the application
python -m channelsmith
```

---

## FAQ

### Q: Is ChannelSmith safe to use?
**A:** Yes! ChannelSmith is open source and proprietary to cgCrate. It never uploads files anywhere—all processing happens locally on your computer.

### Q: Do I need Python for the standalone executable?
**A:** No! Python is bundled inside the executable. Just download, extract, and run.

### Q: Can I use ChannelSmith offline?
**A:** Yes! ChannelSmith is completely offline. It launches a local server on `localhost:5000` (just your computer).

### Q: Why does port 5000 fail sometimes?
**A:** Another application is using that port. Solutions:
- Restart your computer
- Close other applications (especially other local development servers)
- Wait a few minutes for the port to be released

### Q: How do I update to a new version?
**A:** Download the latest release and extract it. Your old version can be deleted.

### Q: Can I use this commercially?
**A:** ChannelSmith is proprietary software. Contact cgCrate for commercial licensing inquiries.

### Q: Where are my textures stored?
**A:** Nowhere! ChannelSmith doesn't save anything to disk except your downloaded results. All processing happens in memory.

### Q: Can I customize templates?
**A:** The current version includes ORM, ORD, and Free templates. Custom template UI is planned for a future release.

### Q: What file formats are supported?
**A:** PNG (recommended), JPG, BMP. Output is always PNG.

### Q: Can I use ChannelSmith on Linux?
**A:** Yes! All installation methods work on Linux. Use the Linux executable or `launch_web_ui.sh` script.

---

## Getting Help

### Resources
- **[User Guide](cs_wiki.md)** - Comprehensive guide with workflows and tips
- **[README.md](README.md)** - Project overview
- **[GitHub Issues](https://github.com/yourusername/channelsmith/issues)** - Report bugs or request features

### Common Issues

If you encounter problems, try:
1. Restart the application
2. Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
3. Check that Python 3.8+ is installed (if using scripts)
4. Ensure port 5000 is available
5. Check [GitHub Issues](https://github.com/yourusername/channelsmith/issues) for similar problems

---

**Happy texture packing!** 🎨
