# ChannelSmith - Context for Claude Code

**Project Name:** ChannelSmith  
**Version:** 0.1.0 (Alpha Development)  
**Language:** Python 3.8+  
**Purpose:** Texture channel packing/unpacking tool for game development

---

## 🎯 Project Overview

ChannelSmith is a desktop application that allows game developers and technical artists to:
- **Pack** multiple grayscale texture maps (Roughness, Metallic, AO, etc.) into a single RGBA image
- **Unpack** existing packed textures to extract individual channels
- **Repack** textures with different template formats (e.g., ORM → ORD)
- **Replace** individual channels without recreating entire textures

### Key Value Proposition
- Reduce texture memory footprint by ~75% (4 textures → 1)
- Enable template conversion workflows
- Intelligent default values for missing textures
- Intuitive drag-and-drop GUI

---

## 📚 Essential Documentation

**Primary Reference:** `docs/MVP_Documentation.md` - Complete MVP specification

**Quick References:**
- This file (CLAUDE.md) - Development context and conventions
- `ALPHA_TASKS.md` - Phase 1 implementation checklist
- `SETUP.md` - Development environment setup

---

## 🏗️ Architecture Overview

### Core Principles
1. **Separation of Concerns:** Packing/unpacking engine independent from GUI
2. **Extensibility:** Template system designed for easy addition of new presets
3. **Modularity:** Each component testable independently
4. **Cross-platform ready:** No OS-specific dependencies in core logic (Windows primary target)

### Component Structure

```
channelsmith/
├── core/                    # Engine layer (no GUI dependencies)
│   ├── channel_map.py       # ChannelMap class - defines texture map types
│   ├── packing_template.py  # PackingTemplate class - RGBA channel assignments
│   ├── packing_engine.py    # Core packing logic
│   ├── unpacking_engine.py  # Core unpacking/extraction logic
│   └── validator.py         # Resolution validation, error checking
├── gui/                     # GUI layer (tkinter)
│   ├── main_window.py       # Main application window
│   ├── drag_drop.py         # Drag-and-drop handlers
│   └── dialogs.py           # Notification/error dialogs
├── templates/               # JSON template definitions
│   ├── orm.json             # Occlusion-Roughness-Metallic
│   ├── ord.json             # Occlusion-Roughness-Displacement
│   └── template_loader.py   # JSON loader/serializer
└── utils/                   # Shared utilities
    ├── image_utils.py       # Image loading/saving helpers
    └── constants.py         # Application constants
```

---

## 🔧 Technical Stack

### Core Dependencies
- **Pillow (PIL) ≥10.0.0** - Image manipulation
- **NumPy ≥1.24.0** - Efficient pixel array operations
- **tkinter** - GUI framework (built-in with Python)

### Development Dependencies
- **pytest** - Testing framework
- **black** - Code formatter
- **pylint** - Linter

### Future (Post-MVP)
- **PyInstaller** - Create standalone .exe for distribution

---

## 📝 Code Conventions

### File & Naming Standards
```python
# Files
snake_case.py                    # All Python files

# Classes
class ChannelMap:                # PascalCase
class PackingEngine:

# Functions & Variables
def pack_channels():             # snake_case
texture_path = "..."
MAX_RESOLUTION = 4096            # Constants: UPPER_CASE

# Private members
def _internal_helper():          # Leading underscore
self._cache = {}
```

### Type Hints (Required)
```python
from typing import Optional, List, Dict
import numpy as np
from PIL import Image

def pack_channels(
    r_channel: np.ndarray,
    g_channel: np.ndarray,
    b_channel: np.ndarray,
    a_channel: Optional[np.ndarray] = None
) -> Image.Image:
    """Packs grayscale channels into RGBA image."""
    pass

def load_template(path: str) -> Dict[str, any]:
    """Loads template from JSON file."""
    pass
```

### Docstrings (Google Style - Required)
```python
def unpack_texture(image: Image.Image, template: PackingTemplate) -> Dict[str, np.ndarray]:
    """
    Extracts individual channels from a packed texture.
    
    Args:
        image: Packed texture image (RGB or RGBA)
        template: Template defining channel assignments
        
    Returns:
        Dictionary mapping channel names to grayscale arrays
        Example: {'R': ao_array, 'G': roughness_array, 'B': metallic_array}
        
    Raises:
        ValueError: If image channels don't match template expectations
        
    Example:
        >>> template = PackingTemplate.load("orm.json")
        >>> channels = unpack_texture(packed_image, template)
        >>> ao_data = channels['R']  # Ambient Occlusion
    """
    pass
```

### Testing (pytest)
```python
# File: tests/test_core/test_packing_engine.py

import pytest
import numpy as np
from channelsmith.core.packing_engine import pack_channels

def test_pack_orm_template():
    """Test packing with ORM template produces correct output."""
    # Arrange
    ao = np.full((1024, 1024), 255, dtype=np.uint8)      # White
    roughness = np.full((1024, 1024), 128, dtype=np.uint8)  # Gray
    metallic = np.zeros((1024, 1024), dtype=np.uint8)    # Black
    
    # Act
    result = pack_channels(ao, roughness, metallic)
    
    # Assert
    assert result.size == (1024, 1024)
    assert result.mode == "RGB"
    
def test_pack_mismatched_resolutions_raises_error():
    """Test that mismatched resolutions raise ValueError."""
    ao = np.zeros((1024, 1024), dtype=np.uint8)
    roughness = np.zeros((2048, 2048), dtype=np.uint8)  # Different size
    
    with pytest.raises(ValueError, match="resolution mismatch"):
        pack_channels(ao, roughness, None)
```

---

## 🎨 Key Design Decisions

### 1. Channel Default Values
When a channel is missing, fill with context-aware defaults:

| Channel Type | Default Value | Reasoning |
|--------------|---------------|-----------|
| `ambient_occlusion` | 1.0 (white) | No occlusion = fully lit |
| `roughness` | 0.5 (mid-gray) | Realistic average |
| `metallic` | 0.0 (black) | Non-metallic default |
| `displacement` | 0.5 (mid-gray) | Flat surface |
| `alpha` | 1.0 (white) | Fully opaque |

Implementation:
```python
class ChannelMap:
    def __init__(self, map_type: str, default_value: float):
        self.map_type = map_type
        self.default_value = default_value  # 0.0 to 1.0 range
```

### 2. RGB vs RGBA Auto-Detection
Automatically export 3 or 4 channels based on template usage:

```python
def determine_output_mode(template: PackingTemplate) -> str:
    """
    Determines if output should be RGB or RGBA.
    
    Returns 'RGB' if only R, G, B channels are used.
    Returns 'RGBA' if A channel is also used.
    """
    if 'A' in template.channels and template.channels['A'] is not None:
        return 'RGBA'
    return 'RGB'
```

### 3. Resolution Normalization (Bilinear Upscaling)
When textures have mismatched resolutions:

```python
from PIL import Image

def normalize_resolution(
    images: List[Image.Image],
    target_size: tuple[int, int]
) -> List[np.ndarray]:
    """
    Upscale all images to target resolution using bilinear interpolation.
    
    Args:
        images: List of PIL Images (potentially different sizes)
        target_size: Target (width, height) tuple
        
    Returns:
        List of normalized NumPy arrays
    """
    normalized = []
    for img in images:
        if img.size != target_size:
            img = img.resize(target_size, Image.BILINEAR)
        normalized.append(np.array(img))
    return normalized
```

### 4. Template JSON Structure
```json
{
  "name": "ORM",
  "description": "Occlusion-Roughness-Metallic (Standard PBR)",
  "channels": {
    "R": {
      "type": "ambient_occlusion",
      "default": 1.0
    },
    "G": {
      "type": "roughness",
      "default": 0.5
    },
    "B": {
      "type": "metallic",
      "default": 0.0
    }
  }
}
```

---

## 🚀 Current Phase: Alpha (No GUI)

### Phase Goal
Build and test the core packing/unpacking engine without GUI.

### Success Criteria
- ✅ Can pack textures programmatically via Python API
- ✅ Can unpack existing packed textures
- ✅ Can repack with different templates (ORM → ORD)
- ✅ All validation logic works
- ✅ Handles edge cases (mismatches, missing textures)
- ✅ Unit tests pass with >80% coverage

### Implementation Order
See `ALPHA_TASKS.md` for detailed checklist.

**Priority sequence:**
1. ChannelMap class
2. PackingTemplate class + JSON loader
3. Core packing algorithm
4. Core unpacking algorithm
5. Validation layer
6. Comprehensive tests

---

## 🧪 Testing Strategy

### Test Coverage Requirements
- **Core logic:** >90% coverage
- **GUI:** Manual testing (Alpha phase = no GUI)
- **Integration tests:** Full workflows (pack → unpack → repack)

### Test Organization
```
tests/
├── test_core/
│   ├── test_channel_map.py
│   ├── test_packing_template.py
│   ├── test_packing_engine.py
│   ├── test_unpacking_engine.py
│   └── test_validator.py
├── test_templates/
│   └── test_template_loader.py
└── test_integration/
    └── test_workflows.py
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=channelsmith --cov-report=html

# Run specific test file
pytest tests/test_core/test_packing_engine.py

# Run specific test
pytest tests/test_core/test_packing_engine.py::test_pack_orm_template
```

---

## 🔄 Git Workflow (Simplified)

### Branch Structure
```
main    # Stable releases only (Alpha, Beta, RC)
  └── dev   # Daily development work
```

### Workflow
1. Work on `dev` branch
2. When milestone reached → merge to `main` and tag
3. Experimental features → create temporary branch from `dev`

### Commit Message Format (Conventional Commits)
```
<type>(<scope>): <description>

[optional body]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Add/modify tests
- `refactor`: Code restructuring

**Examples:**
```
feat(core): add channel extraction from packed textures
fix(validator): handle edge case with 1-channel images
docs(readme): add installation instructions
test(packing): add tests for resolution mismatch handling
```

### Tagging Releases
```bash
# When Alpha is complete
git tag -a v0.1.0-alpha -m "Alpha release - core engine complete"
git push origin v0.1.0-alpha
```

---

## 🐛 Error Handling Philosophy

### Core Principles
1. **Be informative:** Tell user what went wrong
2. **Be actionable:** Suggest how to fix it
3. **Be forgiving:** Gracefully recover when possible
4. **Log everything:** For debugging and support

### Exception Strategy
```python
class ChannelSmithError(Exception):
    """Base exception for ChannelSmith errors."""
    pass

class ResolutionMismatchError(ChannelSmithError):
    """Raised when texture resolutions don't match."""
    pass

class TemplateValidationError(ChannelSmithError):
    """Raised when template JSON is invalid."""
    pass

# Usage
def pack_channels(r, g, b):
    if r.shape != g.shape:
        raise ResolutionMismatchError(
            f"Resolution mismatch: R={r.shape}, G={g.shape}. "
            f"All channels must have the same resolution."
        )
```

---

## 📦 Distribution Plan (Future - Post RC)

### PyInstaller Configuration
When ready for distribution:

```bash
# Create standalone .exe
pyinstaller --onefile \
            --windowed \
            --name ChannelSmith \
            --icon=assets/icon.ico \
            --add-data "templates;templates" \
            main.py

# Output: dist/ChannelSmith.exe
```

### File to Include
- All template JSON files
- Application icon
- README/documentation
- License file

---

## 💡 Development Tips

### Quick Start Development Loop
```bash
# 1. Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run tests
pytest

# 4. Format code
black channelsmith/

# 5. Lint
pylint channelsmith/
```

### Debugging
```python
# Use logging instead of print
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Packing channels: R={r.shape}, G={g.shape}")
logger.info("Texture packed successfully")
logger.warning("Resolution mismatch detected")
logger.error("Failed to load template")
```

### Performance Considerations
- Use NumPy operations (vectorized) instead of loops
- Avoid unnecessary image conversions
- Profile with `cProfile` for bottlenecks

```python
# Good - Vectorized
result = np.stack([r_channel, g_channel, b_channel], axis=2)

# Bad - Loop
for i in range(height):
    for j in range(width):
        result[i, j, 0] = r_channel[i, j]  # Slow!
```

---

## 🎓 Learning Resources

### Python Image Processing
- Pillow docs: https://pillow.readthedocs.io/
- NumPy basics: https://numpy.org/doc/stable/user/quickstart.html

### Testing
- pytest docs: https://docs.pytest.org/
- Coverage.py: https://coverage.readthedocs.io/

### Game Dev Context
- Polycount Channel Packing: http://wiki.polycount.com/wiki/ChannelPacking
- Unreal Engine texture docs: https://docs.unrealengine.com/

---

## 📞 Quick Reference

### Key Files to Reference
- **Architecture:** `docs/MVP_Documentation.md` - Section "Technical Architecture"
- **Workflows:** `docs/MVP_Documentation.md` - Section "Unpacking & Repacking Workflows"
- **Template System:** `docs/MVP_Documentation.md` - Section "Template System"
- **Tasks:** `ALPHA_TASKS.md` - Implementation checklist

### Common Operations
```python
# Load template
from channelsmith.templates.template_loader import load_template
template = load_template("templates/orm.json")

# Pack textures
from channelsmith.core.packing_engine import pack_texture
result = pack_texture(ao_img, roughness_img, metallic_img, template)

# Unpack textures
from channelsmith.core.unpacking_engine import unpack_texture
channels = unpack_texture(packed_img, template)
```

---

## 🎯 Remember

1. **Test-Driven Development:** Write tests first when possible
2. **Type hints everywhere:** Makes debugging easier
3. **Google-style docstrings:** Document all public functions/classes
4. **Keep engine pure:** No GUI code in core/ modules
5. **Validate early:** Check inputs before processing
6. **Log, don't print:** Use logging module for debugging

---

**Last Updated:** February 7, 2026  
**Current Phase:** Alpha Development  
**Next Milestone:** Core engine complete with tests
