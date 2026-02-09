# ChannelSmith

**Texture Channel Packing/Unpacking Tool for Game Development**

![Status](https://img.shields.io/badge/status-beta-brightgreen)
![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)
![License](https://img.shields.io/badge/license-proprietary-red)
![Tests](https://img.shields.io/badge/tests-229%20passing-brightgreen)

---

## 📖 What is ChannelSmith?

ChannelSmith is a desktop application that allows game developers and technical artists to efficiently manage texture channel packing. It reduces texture memory usage by combining multiple grayscale maps (Roughness, Metallic, Ambient Occlusion, etc.) into a single RGBA image.

### Key Features

✅ **Pack** multiple grayscale textures into one RGBA image  
✅ **Unpack** existing packed textures to extract individual channels  
✅ **Repack** textures with different template formats (e.g., ORM → ORD)  
✅ **Replace** individual channels without recreating entire textures  
✅ **Smart defaults** for missing texture channels  
✅ **Template system** with predefined and custom packing configurations  

### Benefits

- 📉 **Reduce memory usage by ~75%** (4 textures → 1)
- ⚡ **Faster loading times** in game engines
- 🔄 **Flexible workflows** for different engine requirements
- 🎯 **Industry-standard templates** (ORM, ORD)

---

## 📥 Download & Run

### Standalone Executable (Easiest)
No Python required! Download the latest release:

| Platform | Download |
|----------|----------|
| Windows 10+ | [ChannelSmith-Windows.zip](https://github.com/yourusername/channelsmith/releases) |
| macOS 12+ | [ChannelSmith-macOS.zip](https://github.com/yourusername/channelsmith/releases) |
| Linux | [ChannelSmith-Linux.tar.gz](https://github.com/yourusername/channelsmith/releases) |

Extract and double-click to run. Browser opens automatically.

[See full installation guide →](INSTALL.md)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd ChannelSmith
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Usage - Web UI (Recommended) 🌐

ChannelSmith features a modern **web-based interface** with Flask backend and Tailwind CSS styling!

#### Windows
Double-click `launch_web_ui.bat` or run:
```bash
python -m channelsmith
```

#### macOS / Linux
Make scripts executable (first time only):
```bash
chmod +x launch_web_ui.sh launch_simple.sh install.sh
```

Then run the launcher:
```bash
./launch_web_ui.sh
```

Or for setup first time:
```bash
./install.sh
```

The browser opens automatically at **http://localhost:5000**

#### Web UI Features

- 🎨 **Modern Dark Theme** - Professional Tailwind CSS design
- 🖱️ **Drag-and-Drop** - Upload images by dragging to zones
- 👁️ **Live Preview** - See channels in real-time as you upload
- 📥 **Download Results** - Get packed or unpacked images instantly
- ⚡ **Responsive Design** - Works on desktop, tablet, mobile
- 🚀 **No External Tools** - Everything in your browser

#### Web UI Workflow

**Pack Textures:**
1. Open http://localhost:5000 (auto-opens in browser)
2. Stay on **"Pack Channels"** tab
3. Select template (**ORM**, **ORD**, etc.)
4. Drag or click to upload Red, Green, Blue channels
5. (Alpha channel optional)
6. Click **"Pack Texture"**
7. Download packed PNG immediately

**Unpack Textures:**
1. Switch to **"Unpack Texture"** tab
2. Upload your packed texture
3. Select correct template
4. Click **"Unpack Texture"**
5. Download extracted channels as individual PNG files

#### Legacy GUI (Deprecated but Functional)

If you prefer the classic tkinter interface:

```bash
python -m channelsmith --gui
```

See [USER_GUIDE.md](docs/USER_GUIDE.md) for detailed instructions.

#### Complete Testing Guide

See **[WEB_UI_TESTING.md](docs/WEB_UI_TESTING.md)** for:
- Automated API tests (22 tests, all passing)
- Manual testing workflows
- Edge case testing
- Browser compatibility
- Performance benchmarks

### Programmatic API (Python)

For automation or scripting:

```python
from channelsmith.core.packing_engine import pack_texture_from_template
from channelsmith.templates.template_loader import load_template
from channelsmith.utils.image_utils import load_image, save_image

# Load template
template = load_template("channelsmith/templates/orm.json")

# Load individual texture maps
ao_map = load_image("textures/ao.png")
roughness_map = load_image("textures/roughness.png")
metallic_map = load_image("textures/metallic.png")

# Pack into single texture
textures = {
    'ambient_occlusion': ao_map,
    'roughness': roughness_map,
    'metallic': metallic_map
}

packed = pack_texture_from_template(textures, template)

# Save result
save_image(packed, "output/material_orm.png")
```

---

## 📚 Documentation

### Installation & Getting Started
- **[INSTALL.md](INSTALL.md)** ⭐ **START HERE** - Complete installation guide (3 methods)
- **[SETUP.md](docs/SETUP.md)** - Environment setup for developers
- **[cs_wiki.md](cs_wiki.md)** - User guide with workflows and FAQs (also in-app)

### Testing & Development
- **[WEB_UI_TESTING.md](docs/WEB_UI_TESTING.md)** - Web UI testing guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute and code standards

### Release Information
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes
- **[docs/RELEASE_PROCESS.md](docs/RELEASE_PROCESS.md)** - Release workflow (maintainers)

---

## 🏗️ Project Structure

```
ChannelSmith/
├── channelsmith/               # Main package
│   ├── core/                  # Packing/unpacking engine
│   ├── api/                   # Flask REST API (NEW)
│   │   ├── app.py            # Flask app factory
│   │   ├── routes.py         # API endpoints (pack, unpack, templates)
│   │   └── utils.py          # Image utilities & validation
│   ├── frontend/              # Web UI (NEW)
│   │   ├── index.html        # Single-page app
│   │   ├── styles.css        # Tailwind CSS styling
│   │   └── app.js            # Vanilla JavaScript logic
│   ├── gui/                   # GUI layer (Legacy, still functional)
│   ├── templates/             # Template JSON files & loader
│   └── utils/                 # Utilities
├── tests/
│   ├── test_api/             # API endpoint tests (NEW)
│   ├── test_core/            # Core engine tests
│   ├── test_gui/             # GUI tests
│   └── ...
├── docs/                      # Documentation
├── WEB_UI_TESTING.md          # Web UI testing guide (NEW)
├── SETUP.md                   # Installation guide
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🛠️ Development Status

### Current Phase: Post-Beta with Web MVP ✨

**Goal:** Deliver production-ready web UI with full pack/unpack workflows

**Progress:**
- ✅ Core packing/unpacking engine (Alpha - Complete)
- ✅ Template system with ORM/ORD templates
- ✅ **Web UI MVP** - Flask REST API + Tailwind CSS frontend (NEW)
- ✅ Full pack/unpack workflows
- ✅ Drag-and-drop support
- ✅ Live preview with Base64 encoding
- ✅ Browser auto-launch
- ✅ API tests (22 comprehensive tests, all passing)
- ✅ Core tests (207 tests, all passing, no regressions)
- ✅ Legacy tkinter GUI still functional
- 🔄 Advanced features (batch processing, custom templates UI)

**Test Coverage:**
- Core Engine: 207 tests ✓
- REST API: 22 tests ✓
- Total: 229 tests passing

### Roadmap

- **Alpha:** Core engine ✅
- **Beta:** Tkinter GUI ✅
- **Web MVP:** Flask + Tailwind web UI ✅
- **RC:** Bug fixes, performance optimization, advanced features
- **v1.0:** Production release

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=channelsmith --cov-report=html

# Run specific test file
pytest tests/test_core/test_packing_engine.py
```

---

## 🤝 Contributing

This is currently a private project. Contribution guidelines will be added upon public release.

### Code Standards

- **File naming:** snake_case
- **Type hints:** Required on all functions
- **Docstrings:** Google style, required on all public APIs
- **Testing:** pytest, >80% coverage target
- **Formatting:** black
- **Linting:** pylint

---

## 📄 License

Proprietary - All rights reserved.  
This software is intended for commercial distribution.

---

**Status:** Web MVP Complete - Post-Beta
**Version:** 0.1.0-web-mvp
**Last Updated:** February 9, 2026
