# ChannelSmith - Claude Code Context

**Project:** ChannelSmith v0.1.0 (Alpha)
**Purpose:** Texture channel packing/unpacking tool for game dev
**Stack:** Python 3.8+, Pillow, NumPy, tkinter

## Project Overview

Texture packing/unpacking tool that allows:
- Pack multiple grayscale maps (R/M/AO) into single RGBA
- Unpack/extract individual channels
- Repack with different templates (ORM → ORD)
- Intelligent defaults for missing channels

**Value:** Reduce texture memory ~75% (4 textures → 1)

## Architecture

**Core Principles:** Separation of concerns, engine independent from GUI, template-based extensibility

```
channelsmith/
├── core/          # Engine (no GUI deps): channel_map, packing_template, packing_engine, unpacking_engine, validator
├── gui/           # tkinter UI: main_window, drag_drop, dialogs
├── templates/     # JSON definitions: orm.json, ord.json, template_loader.py
└── utils/         # Helpers: image_utils, constants
```

## Dependencies

**Core:** Pillow ≥10.0.0, NumPy ≥1.24.0, tkinter
**Dev:** pytest, black, pylint
**Future:** PyInstaller for .exe distribution

## Code Conventions

**Naming:** snake_case files/functions, PascalCase classes, UPPER_CASE constants
**Required:** Type hints on all functions, Google-style docstrings
**Testing:** pytest, >90% coverage for core logic

## Key Design Decisions

**Channel Defaults:**
- ambient_occlusion: 1.0 (white, fully lit)
- roughness: 0.5 (mid-gray)
- metallic: 0.0 (black, non-metallic)
- displacement: 0.5 (flat)
- alpha: 1.0 (opaque)

**RGB vs RGBA:** Auto-detect based on template (export RGB if only R/G/B used, RGBA if A channel used)

**Resolution Mismatch:** Bilinear upscaling to max resolution

**Template JSON Structure:**
```json
{
  "name": "ORM",
  "description": "Occlusion-Roughness-Metallic",
  "channels": {
    "R": {"type": "ambient_occlusion", "default": 1.0},
    "G": {"type": "roughness", "default": 0.5},
    "B": {"type": "metallic", "default": 0.0}
  }
}
```

## Current Phase: Alpha (No GUI)

**Goal:** Core packing/unpacking engine with comprehensive tests
**Status:** See ALPHA_TASKS.md for checklist
**Success:** Pack/unpack/repack via Python API, >80% test coverage

**Implementation Order:**
1. ChannelMap class
2. PackingTemplate + JSON loader
3. Packing engine
4. Unpacking engine
5. Validation layer
6. Comprehensive tests

## Testing

**Coverage:** >90% core, >80% overall
**Organization:** tests/test_core/, tests/test_templates/, tests/test_integration/
**Commands:** `pytest` (all), `pytest --cov=channelsmith --cov-report=html` (coverage)

## Git Workflow

**Branches:** `main` (stable releases), `dev` (daily work)
**Commits:** Conventional format: `<type>(<scope>): <description>`
**Types:** feat, fix, docs, test, refactor
**Example:** `feat(core): implement unpacking engine with template support`

## Error Handling

**Philosophy:** Be informative, actionable, forgiving, log everything

**Custom Exceptions:**
- ChannelSmithError (base)
- ResolutionMismatchError
- TemplateValidationError

## Development

**Quick commands:**
```bash
pytest                    # Run tests
black channelsmith/       # Format
pylint channelsmith/      # Lint
```

**Performance:** Use NumPy vectorized ops, avoid loops, use logging not print

**Key References:**
- docs/MVP_Documentation.md - Full spec
- ALPHA_TASKS.md - Implementation checklist
- SETUP.md - Environment setup

## Common Operations

```python
# Load template
from channelsmith.templates.template_loader import load_template
template = load_template("templates/orm.json")

# Pack
from channelsmith.core.packing_engine import pack_texture
result = pack_texture(ao_img, roughness_img, metallic_img, template)

# Unpack
from channelsmith.core.unpacking_engine import unpack_texture
channels = unpack_texture(packed_img, template)
```

## Core Tenets

1. Test-driven development
2. Type hints everywhere
3. Engine pure (no GUI in core/)
4. Validate early
5. Use logging

---
Last Updated: 2026-02-07 | Phase: Alpha | Next: Core engine complete
