# ChannelSmith

**Texture Channel Packing/Unpacking Tool for Game Development**

![Status](https://img.shields.io/badge/status-alpha-orange)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-proprietary-red)

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

### Usage (Alpha - Programmatic API)

Currently in Alpha phase with no GUI. Use the Python API:

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
    'R': ao_map,
    'G': roughness_map,
    'B': metallic_map
}

packed = pack_texture_from_template(textures, template)

# Save result
save_image(packed, "output/material_orm.png", "PNG")
```

**GUI coming in Beta phase!**

---

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Development environment setup
- **[CLAUDE.md](CLAUDE.md)** - Architecture and development guidelines
- **[ALPHA_TASKS.md](ALPHA_TASKS.md)** - Alpha phase implementation roadmap
- **[docs/MVP_Documentation.md](docs/MVP_Documentation.md)** - Complete MVP specification

---

## 🏗️ Project Structure

```
ChannelSmith/
├── channelsmith/           # Main package
│   ├── core/              # Packing/unpacking engine
│   ├── gui/               # GUI layer (Beta+)
│   ├── templates/         # Template JSON files and loader
│   └── utils/             # Utilities
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Usage examples
└── requirements.txt       # Python dependencies
```

---

## 🛠️ Development Status

### Current Phase: Alpha

**Goal:** Core packing/unpacking engine functional and tested (no GUI)

**Progress:**
- [ ] ChannelMap class
- [ ] PackingTemplate class
- [ ] Template JSON loader
- [ ] Packing engine
- [ ] Unpacking engine
- [ ] Validation layer
- [ ] Comprehensive tests

See [ALPHA_TASKS.md](ALPHA_TASKS.md) for detailed checklist.

### Roadmap

- **Alpha (Current):** Core engine - 2-3 weeks
- **Beta:** Simple GUI with drag-and-drop - 2-3 weeks
- **RC:** Bug fixes, installer, documentation - 1-2 weeks
- **v1.0:** Public release

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

---

## 🎓 For Developers

### First Time Setup

1. Read [SETUP.md](SETUP.md) for environment setup
2. Read [CLAUDE.md](CLAUDE.md) for architecture overview
3. Check [ALPHA_TASKS.md](ALPHA_TASKS.md) for current tasks
4. Review [docs/MVP_Documentation.md](docs/MVP_Documentation.md) for full specs

### Development Workflow

1. Activate virtual environment: `source venv/bin/activate`
2. Create feature: Work on `dev` branch
3. Write tests first (TDD approach)
4. Format code: `black channelsmith/`
5. Run tests: `pytest`
6. Commit: `git commit -m "feat(core): description"`

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

## 📞 Contact

For inquiries about ChannelSmith, please contact [your email/contact info].

---

**Status:** In Development  
**Version:** 0.1.0-alpha  
**Last Updated:** February 7, 2026
