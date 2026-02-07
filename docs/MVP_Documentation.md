# Texture Packing Tool - MVP Documentation

**Version:** 1.0  
**Date:** February 7, 2026  
**Project Type:** Python 3 Desktop Application  
**Target Platform:** Windows (cross-platform ready)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [MVP Scope Definition](#mvp-scope-definition)
3. [Technical Architecture](#technical-architecture)
4. [External Dependencies](#external-dependencies)
5. [Core Components](#core-components)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Template System](#template-system)
8. [Validation & Error Handling](#validation--error-handling)
9. [Future Enhancements](#future-enhancements)

---

## Project Overview

### Purpose
Develop a texture packing tool that handles channel-packed textures in optimal formats. Channel packing is a technique used in game development to reduce memory usage by merging grayscale or color maps into a single RGBA image—one map per channel—rather than using each map as a separate texture.

### Target Users
- Initially: Internal team
- Future: Commercial release (conditional on market validation)
- User expertise: Junior to senior technical artists

### Key Value Proposition
- **Memory Optimization:** Reduce texture memory footprint by 75% (4 textures → 1)
- **Workflow Efficiency:** Intuitive GUI with drag-and-drop functionality
- **Flexibility:** Predefined templates + custom packing configurations
- **Quality Control:** Intelligent validation and default value management

---

## MVP Scope Definition

### ✅ Included in MVP

#### Core Functionality
- **Channel packing engine** (separate from GUI for modularity)
- **Input formats:** PNG, TGA, JPEG, TIFF
- **Output formats:** PNG, TGA, JPEG, TIFF
- **Maximum resolution:** 4K (4096x4096)
- **Bit depth:** 8-bit per channel
- **Upscaling algorithm:** Bilinear interpolation

#### User Interface
- Simple GUI with drag-and-drop support
- Predefined packing templates (ORM, ORD)
- Custom template creation via channel assignment
- Template export/import as JSON
- Resolution mismatch detection and notification
- Visual feedback (resolution display, status indicators)

#### Smart Features
- **Automatic RGB/RGBA detection:** Export 3 or 4 channels based on template usage
- **Intelligent default values:** Context-aware fill for missing textures
- **Resolution validation:** User-prompted resolution handling with upscaling option

#### Export Capabilities
- User-specified output path
- Automatic file naming conventions
- Format selection

### ❌ Excluded from MVP (Future Features)

- Advanced upscaling algorithms (Bicubic/Lanczos)
- Advanced mode with exposed parameters
- CLI batch processing version
- macOS/Linux support (though architecture is cross-platform ready)
- Unreal Engine 5 editor integration
- 16-bit/HDR support
- Additional formats (EXR, DDS)
- Compression optimization hints
- Multi-threaded processing

---

## Technical Architecture

### Architecture Principles

1. **Separation of Concerns:** Core packing engine independent from GUI
2. **Extensibility:** Template system designed for easy addition of new presets
3. **Modularity:** Each component can be tested and developed independently
4. **Cross-platform readiness:** No OS-specific dependencies in core logic

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                   GUI Layer                         │
│  (tkinter - Windows primary, cross-platform ready)  │
└───────────────────┬─────────────────────────────────┘
                    │
                    ├─> User Input Handler
                    ├─> Drag & Drop Manager
                    ├─> Template Selector
                    └─> Status/Notification Display
                    │
┌───────────────────▼─────────────────────────────────┐
│              Validation Layer                       │
│  - Resolution Checker                               │
│  - Channel Completeness Validator                   │
│  - Format Compatibility Checker                     │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│           Template Management System                │
│  - ChannelMap (defines channel properties)          │
│  - PackingTemplate (RGBA channel assignments)       │
│  - Template Loader/Serializer (JSON)                │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│          Texture Packing Engine (Core)              │
│  - Image Loading (multi-format)                     │
│  - Resolution Normalization (upscaling)             │
│  - Channel Extraction & Packing                     │
│  - Default Value Application                        │
│  - Export (RGB/RGBA auto-detection)                 │
└─────────────────────────────────────────────────────┘
```

---

## External Dependencies

### Required Python Libraries

| Library | Version | Purpose | Installation |
|---------|---------|---------|--------------|
| **Pillow (PIL)** | ≥10.0.0 | Image loading, manipulation, export | `pip install Pillow` |
| **NumPy** | ≥1.24.0 | Efficient pixel array operations | `pip install numpy` |
| **tkinter** | Built-in | GUI framework (included with Python) | N/A |

### Optional/Development Dependencies

| Library | Purpose | Installation |
|---------|---------|--------------|
| **pytest** | Unit testing | `pip install pytest` |
| **black** | Code formatting | `pip install black` |
| **pylint** | Code linting | `pip install pylint` |

### Python Version
- **Required:** Python 3.8+
- **Recommended:** Python 3.11+ (better performance)

### System Requirements
- **OS:** Windows 10/11 (64-bit)
- **RAM:** Minimum 4GB (8GB recommended for 4K textures)
- **Disk Space:** 100MB for application + workspace for textures

---

## Core Components

### 1. ChannelMap Class

Defines the properties and behavior of individual texture map types.

```python
class ChannelMap:
    """
    Represents a single texture map type with metadata.
    
    Attributes:
        map_type (str): Type identifier (e.g., 'roughness', 'metallic')
        default_value (float): Default fill value (0.0 to 1.0)
        description (str): Human-readable description
    """
```

#### Predefined Channel Types

| Type | Default Value | Reasoning |
|------|---------------|-----------|
| `ambient_occlusion` | 1.0 (white) | No occlusion = fully lit |
| `roughness` | 0.5 (mid-gray) | Realistic average |
| `metallic` | 0.0 (black) | Non-metallic default |
| `displacement` | 0.5 (mid-gray) | Flat surface baseline |
| `height` | 0.5 (mid-gray) | Flat surface baseline |
| `opacity` | 1.0 (white) | Fully opaque |
| `alpha` | 1.0 (white) | Fully opaque |

### 2. PackingTemplate Class

Defines how texture maps are assigned to RGBA channels.

```python
class PackingTemplate:
    """
    Represents a complete packing configuration.
    
    Attributes:
        name (str): Template identifier
        channels (dict): Mapping of RGBA channels to ChannelMaps
        description (str): Template description
    """
```

#### Template Structure (JSON)

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

### 3. Texture Packing Engine

Core processing logic (pseudocode flow):

```
1. Load input textures for each channel
2. Validate resolutions → Detect mismatches
3. If mismatch detected:
   a. Notify user
   b. Prompt: Reimport OR Upscale
   c. If upscale: Apply Bilinear to lower-res textures
4. Extract channel data from each texture:
   - Grayscale maps → single channel value
   - Color maps → specified channel (R/G/B)
5. Create blank RGBA canvas (max resolution)
6. For each RGBA channel:
   - If texture provided → Copy channel data
   - If texture missing → Fill with ChannelMap default value
7. Detect channel usage:
   - If only RGB used → Export as RGB (3 channels)
   - If RGBA used → Export as RGBA (4 channels)
8. Save to specified output path and format
```

### 4. Validation Layer

#### Resolution Mismatch Handling

```
Input: Multiple textures with varying resolutions

Process:
1. Scan all loaded textures
2. Extract resolutions (width x height)
3. Compare resolutions:
   - All match? → Proceed
   - Mismatch detected? → Trigger notification

Notification Flow:
┌─────────────────────────────────────────┐
│  ⚠️ Resolution Mismatch Detected        │
├─────────────────────────────────────────┤
│  Roughness: 2048x2048                   │
│  Metallic:  4096x4096                   │
│  AO:        1024x1024                   │
├─────────────────────────────────────────┤
│  [Reimport with Uniform Resolution]     │
│  [Upscale to 4096x4096 (Bilinear)]      │
└─────────────────────────────────────────┘
```

#### Missing Texture Handling

```
Input: Template requires 3 channels, user loaded 2

Process:
1. Identify missing channels
2. Lookup ChannelMap type for missing slot
3. Prompt user:

┌─────────────────────────────────────────┐
│  ⚠️ Missing Texture: Metallic (B)       │
├─────────────────────────────────────────┤
│  The template requires a Metallic map   │
│  for the Blue channel.                  │
├─────────────────────────────────────────┤
│  [Load Texture]                         │
│  [Use Default (0.0 - Non-metallic)]     │
└─────────────────────────────────────────┘

If "Use Default" selected:
4. Fill channel with ChannelMap.default_value
5. Continue packing
```

---

## Implementation Roadmap

### Phase 1: Alpha (No GUI)

**Goal:** Core packing engine functional and tested

**Duration:** 2-3 weeks

**Deliverables:**
1. ✅ ChannelMap class implementation
2. ✅ PackingTemplate class implementation
3. ✅ Template JSON loader/serializer
4. ✅ Core texture packing algorithm
5. ✅ Resolution normalization (Bilinear upscaling)
6. ✅ Default value application logic
7. ✅ RGB/RGBA auto-detection
8. ✅ Unit tests for all components
9. ✅ Command-line test harness (temporary, for testing)

**Success Criteria:**
- Can pack textures programmatically via Python API
- All validation logic works correctly
- Produces correct output for ORM and ORD templates
- Handles edge cases (mismatches, missing textures)

**Testing Focus:**
- Various resolution combinations
- All channel type defaults
- Format conversions (PNG → TGA, etc.)
- Memory usage profiling (4K textures)

---

### Phase 2: Beta (Simple GUI Implementation)

**Goal:** User-facing GUI with core workflows

**Duration:** 2-3 weeks

**Deliverables:**
1. ✅ tkinter GUI framework setup
2. ✅ Drag-and-drop texture loading
3. ✅ Template selector dropdown
4. ✅ RGBA channel assignment interface
5. ✅ Custom template creation UI
6. ✅ Template JSON export/import buttons
7. ✅ Output path selection
8. ✅ Format selector
9. ✅ "Pack" button with status feedback
10. ✅ Resolution display for loaded textures
11. ✅ Visual mismatch warnings (color-coded button)
12. ✅ Notification dialogs for errors/warnings

**UI Mockup:**

```
┌────────────────────────────────────────────────────────┐
│  Texture Packing Tool                          [_][□][X]│
├────────────────────────────────────────────────────────┤
│                                                         │
│  Template: [ORM ▼]         [Load Template] [Save As]   │
│                                                         │
│  ┌─ Channel Assignment ─────────────────────────────┐  │
│  │                                                   │  │
│  │  R: [Occlusion ▼]  [roughness_4k.png  ] [🗑️] 4K  │  │
│  │  G: [Roughness ▼]  [Drop or Browse...] [🗑️]      │  │
│  │  B: [Metallic  ▼]  [metallic_2k.png  ] [🗑️] 2K ⚠️│  │
│  │  A: [—None—    ▼]  [                 ]            │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Output Format: [PNG ▼]   Path: [C:\textures\...] [📁] │
│                                                         │
│  [          Pack Texture          ]                     │
│     (Button color: Green/Yellow/Red based on status)    │
│                                                         │
│  Status: Ready to pack | ⚠️ Resolution mismatch detected│
└────────────────────────────────────────────────────────┘
```

**Success Criteria:**
- All core workflows accessible via GUI
- User can create and pack custom templates
- Export/import templates successfully
- Drag-and-drop works reliably
- Error messages are clear and actionable

---

### Phase 3: RC (Release Candidate - Bug-Free & Feature-Complete)

**Goal:** Production-ready MVP

**Duration:** 1-2 weeks

**Deliverables:**
1. ✅ Complete bug fixing pass
2. ✅ Performance optimization (4K texture handling)
3. ✅ User documentation (README, quick start guide)
4. ✅ Error handling robustness
5. ✅ Input validation (file types, corrupted images)
6. ✅ Edge case handling
7. ✅ Installer/packaging (Windows .exe)
8. ✅ Internal user testing
9. ✅ Feedback incorporation

**Testing Checklist:**
- [ ] All supported formats (PNG, TGA, JPEG, TIFF) load correctly
- [ ] All export formats work
- [ ] Custom templates save/load correctly
- [ ] Mismatch handling works in all scenarios
- [ ] Default values apply correctly for all channel types
- [ ] Memory doesn't leak during repeated packing
- [ ] GUI remains responsive during packing
- [ ] Application doesn't crash on invalid input
- [ ] Works on clean Windows 10/11 machines

**Success Criteria:**
- Zero critical bugs
- All MVP features implemented and working
- Documentation complete
- Ready for internal deployment

---

## Template System

### Predefined Templates

#### 1. ORM (Occlusion-Roughness-Metallic)

**Use Case:** Standard PBR workflow (most common)

**Channel Mapping:**
- **R:** Ambient Occlusion (default: 1.0)
- **G:** Roughness (default: 0.5)
- **B:** Metallic (default: 0.0)
- **A:** Unused (exports as RGB)

**Target Engines:** Unreal Engine, Unity (Standard/URP/HDRP)

---

#### 2. ORD (Occlusion-Roughness-Displacement)

**Use Case:** Materials with height/displacement

**Channel Mapping:**
- **R:** Ambient Occlusion (default: 1.0)
- **G:** Roughness (default: 0.5)
- **B:** Displacement/Height (default: 0.5)
- **A:** Unused (exports as RGB)

**Target Engines:** Unreal Engine with displacement, Substance workflows

---

### Adding New Templates

Templates are easily extensible. To add a new template:

1. Create JSON file in `templates/` directory
2. Application auto-loads on startup
3. Appears in template dropdown

**Example: RMA Template**

```json
{
  "name": "RMA",
  "description": "Roughness-Metallic-AO (Alternative order)",
  "channels": {
    "R": {
      "type": "roughness",
      "default": 0.5
    },
    "G": {
      "type": "metallic",
      "default": 0.0
    },
    "B": {
      "type": "ambient_occlusion",
      "default": 1.0
    }
  }
}
```

---

## Validation & Error Handling

### Error Categories

#### 1. User Input Errors
- **Invalid file format:** "Unsupported file type. Please use PNG, TGA, JPEG, or TIFF."
- **Corrupted image:** "Unable to load [filename]. File may be corrupted."
- **Missing output path:** "Please specify an output path."

#### 2. Resolution Issues
- **Mismatch detected:** Prompt with options (see Validation Layer)
- **Exceeds max resolution:** "Texture resolution exceeds 4K maximum."

#### 3. Template Issues
- **Invalid JSON:** "Template file is corrupted or invalid."
- **Missing required fields:** "Template missing required field: [field_name]"

#### 4. System Errors
- **Out of memory:** "Insufficient memory to process 4K textures. Close other applications."
- **Write permission denied:** "Cannot save to [path]. Check folder permissions."

### Error Handling Philosophy

- **Be informative:** Tell user what went wrong
- **Be actionable:** Suggest how to fix it
- **Be forgiving:** Don't crash, gracefully recover when possible
- **Be transparent:** Log errors for debugging (future support)

---

## Future Enhancements

### Post-MVP Roadmap (Prioritized)

#### High Priority
1. **Advanced Mode GUI**
   - Selectable upscaling algorithms (Nearest/Bilinear/Bicubic/Lanczos)
   - Compression quality slider
   - Dithering options
   - Custom default value overrides

2. **Unreal Engine Integration**
   - Python plugin for UE5 editor
   - Direct texture import with packing
   - Preset compression settings application
   - Material instance auto-setup

3. **Additional Templates**
   - RMA (Roughness-Metallic-AO)
   - ARM (AO-Roughness-Metallic)
   - Packed Normal+Height
   - Custom user-shared template library

#### Medium Priority
4. **CLI Version** (if batch processing proves valuable)
   - Batch process entire folders
   - Pipeline integration
   - Scripting support

5. **macOS/Linux Support**
   - Cross-platform GUI testing
   - Platform-specific installers

6. **16-bit/HDR Support**
   - 16-bit per channel option
   - EXR format support
   - HDR displacement maps

#### Low Priority
7. **Advanced Export Options**
   - DDS with BC compression
   - Custom compression algorithms
   - Multi-resolution export (mipmaps)

8. **Quality of Life**
   - Recent files list
   - Favorites/pinned templates
   - Texture preview thumbnails
   - Before/after comparison view

---

## Development Guidelines

### Code Style
- **PEP 8 compliance** (enforced via Black formatter)
- **Type hints** for all function signatures (Python 3.8+ style)
- **Docstrings** for all classes and public methods (Google style)

### Git Workflow
- **Branch naming:** `feature/`, `bugfix/`, `release/`
- **Commits:** Atomic, descriptive messages
- **Pull requests:** Required for main branch

### Testing Strategy
- **Unit tests:** All core components (pytest)
- **Integration tests:** Full packing workflows
- **Manual testing:** GUI interactions, edge cases
- **Performance tests:** 4K texture processing benchmarks

### Documentation
- **Code comments:** For complex logic only
- **README.md:** Installation, quick start, basic usage
- **Wiki:** Detailed technical documentation
- **User guide:** Step-by-step workflows with screenshots

---

## Appendix

### Upscaling Algorithms Comparison

| Algorithm | Speed | Quality | Artifacts | Best For |
|-----------|-------|---------|-----------|----------|
| **Nearest Neighbor** | ⚡⚡⚡ | ⭐ | Pixelation | Pixel art, hard edges |
| **Bilinear** (MVP) | ⚡⚡ | ⭐⭐⭐ | Slight blur | Technical maps (R/M/AO) |
| **Bicubic** | ⚡ | ⭐⭐⭐⭐ | Minor ringing | Albedo, color maps |
| **Lanczos** | ⚡ | ⭐⭐⭐⭐⭐ | Potential ringing | High-quality upscaling |

**MVP Choice:** Bilinear offers the best balance for technical texture maps.

### Glossary

- **Channel Packing:** Combining multiple grayscale textures into RGBA channels of a single image
- **PBR:** Physically Based Rendering - modern material workflow
- **ORM:** Occlusion-Roughness-Metallic packed texture
- **AO:** Ambient Occlusion - shadows in surface crevices
- **Displacement/Height:** Map controlling surface geometry detail
- **Bit Depth:** Bits per color channel (8-bit = 256 values, 16-bit = 65,536 values)

---

**Document Version:** 1.0  
**Last Updated:** February 7, 2026  
**Author:** Claude & Development Team  
**Status:** MVP Definition - Ready for Implementation
