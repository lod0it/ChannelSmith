# Changelog

All notable changes to ChannelSmith are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Batch processing mode
- Custom template UI editor
- Advanced preview filters

---

## [0.3.0] - 2026-02-09

### Added
- **Alpha channel support** for texture packing and unpacking
  - Pack textures with optional alpha channel (RGBA output)
  - Unpack textures preserving alpha channel when present
  - Smart defaults handling (RGBA output only if alpha provided)
  - Backward compatible: RGB-only packing still works as before
- **Alpha channel auto-extraction** from RGBA textures
  - Automatically extracts alpha from RGBA images during unpacking
  - Non-breaking: RGB images remain unchanged (3 channels)
  - Enables unpacking of game textures with embedded alpha (BaseColor + alpha)
- **Unpack Texture UI redesign** - 2x2 grid layout
  - All 4 channels (R, G, B, A) displayed in organized grid
  - Individual download buttons for each channel
  - Enhanced preview with zoom functionality
  - Alpha channel shows only when unpacking RGBA images
- **Manual update notification system**
  - GitHub Releases integration for version checking
  - Display latest release notes in Info panel
  - One-click download links for Windows/macOS/Linux binaries
  - Checks performed manually (no automatic telemetry)

### Removed
- **Legacy tkinter GUI** - Completely removed in favor of Web UI
  - Removed entire `channelsmith/gui/` module (~2,500 LOC)
  - Removed `--gui` command-line flag
  - Removed 212 GUI tests (were already skipped in CI)
  - Reduced codebase by ~3,000 lines
  - **BREAKING CHANGE:** --gui flag no longer supported

### Fixed
- Alpha channel handling in pack/unpack templates
  - ORM, ORD, and Free templates now support optional alpha channel
  - Fixed pack logic to output RGBA when user provides alpha input
  - Fixed unpack logic to skip alpha extraction when template doesn't define it

### Technical Details
- All 358 tests passing ✓
- No breaking changes to core API (texture packing/unpacking)
- Complete pack→unpack cycle with alpha verified working
- Web UI fully functional with alpha channel workflows

---

## [0.2.0] - 2026-02-09

### Added
- **Cross-platform launcher scripts** for macOS and Linux
  - `launch_web_ui.sh` - Full-featured launcher with venv setup and dependency installation
  - `launch_simple.sh` - Quick launcher for experienced users
  - `install.sh` - One-time setup wizard with health checks
- **PyInstaller support** for creating standalone executables
  - `channelsmith.spec` - Build configuration for all platforms
  - `build_exe.bat` and `build_exe.sh` - Build scripts for Windows, macOS, and Linux
- **GitHub Actions CI/CD** for automated executable builds
  - Automated builds triggered on version tags
  - Multi-platform builds (Windows, macOS, Linux)
  - Automatic GitHub Release creation with assets
- **Versioning system**
  - Version constant in `channelsmith/__init__.py`
  - Dynamic version display in CLI
  - Semantic versioning (v0.2.0)
- **Documentation**
  - `CHANGELOG.md` - Complete version history
  - `INSTALL.md` - Comprehensive installation guide (3 tiers)
  - `CONTRIBUTING.md` - Contribution guidelines and code standards
- **Platform-specific installation methods**
  - Standalone executables for Windows, macOS, Linux
  - Installer scripts for Mac/Linux users
  - Traditional Python installation for developers

### Changed
- Updated `README.md` with Mac/Linux launch instructions
- Reorganized project for local distribution (Automatic1111 model)
- Made `channelsmith/__init__.py` the source of truth for version info

### Technical Details
- All 229 core tests passing ✓
- Web UI MVP fully functional
- No breaking changes to existing APIs
- Backward compatible with v0.1.0

---

## [0.1.0] - 2026-02-01

### Added
- **Web UI MVP** - Flask REST API with Tailwind CSS frontend
  - Modern dark theme with orange accents
  - Drag-and-drop texture upload
  - Live preview with Base64 encoding
  - Pack and unpack workflows
  - Dynamic channel labels based on template
  - Zoomed preview modal for better visibility
- **REST API endpoints**
  - `POST /api/pack` - Pack multiple textures into one
  - `POST /api/unpack` - Unpack texture into individual channels
  - `GET /api/templates` - List available templates
  - `GET /api/templates/<name>` - Get template details
  - `GET /api/health` - Health check endpoint
- **Template system**
  - ORM (Ambient Occlusion, Roughness, Metallic) preset
  - ORD (Ambient Occlusion, Roughness, Displacement) preset
  - Free mode for flexible grayscale texture packing
  - Smart defaults for missing channels
- **Frontend features**
  - Toggle switch for Pack/Unpack modes
  - Info panel with embedded user documentation (cs_wiki.md)
  - Download buttons for results
  - Responsive design supporting desktop and mobile
  - Optimized canvas size (240x240px)
- **Documentation**
  - User guide (cs_wiki.md) - 5000+ words for game artists
  - Setup guide (SETUP.md)
  - Web UI testing guide (WEB_UI_TESTING.md)
  - Development guidelines (CLAUDE.md)
- **Testing**
  - 229 core tests passing
  - 22 API endpoint tests
  - >85% code coverage

### Technical Details
- Built with Flask 3.0+ and Vanilla JavaScript
- Pillow for image processing
- NumPy for channel manipulation
- Supports Python 3.8+
- Cross-platform compatible (Windows, macOS, Linux)

---

## [0.0.1] - Alpha

### Initial Release
- Core packing/unpacking engine
- Template system foundation
- Legacy tkinter GUI
- Basic documentation

---

[Unreleased]: https://github.com/yourusername/channelsmith/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/yourusername/channelsmith/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/yourusername/channelsmith/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/channelsmith/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/yourusername/channelsmith/releases/tag/v0.0.1
