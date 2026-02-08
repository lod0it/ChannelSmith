# Contributing to ChannelSmith

Thank you for your interest in contributing to ChannelSmith! This document provides guidelines for reporting issues, requesting features, and contributing code.

---

## Code of Conduct

Be respectful, inclusive, and professional in all interactions. We're all here to make ChannelSmith better.

---

## Reporting Bugs

### Before Submitting

1. **Check existing issues** - Your bug might already be reported
2. **Read the FAQ** in [INSTALL.md](INSTALL.md) - Your question might be answered there
3. **Test in latest version** - The bug might be fixed already
4. **Try the troubleshooting steps** in the [User Guide](cs_wiki.md)

### Submitting a Bug Report

1. Go to [GitHub Issues](https://github.com/yourusername/channelsmith/issues)
2. Click **New Issue**
3. Title: Clear, specific description (e.g., "Pack button crashes with JPEG input")
4. Description:
   ```
   **Describe the bug**
   Clear description of what isn't working

   **Steps to reproduce**
   1. Open ChannelSmith
   2. Click Pack Texture
   3. Upload image.jpg
   4. Click Pack button
   5. Error occurs

   **Expected behavior**
   Texture should pack successfully

   **Environment**
   - OS: Windows 11
   - ChannelSmith version: 0.2.0
   - Python version: 3.11 (if applicable)

   **Screenshots**
   If helpful, attach screenshots of the error
   ```

---

## Requesting Features

1. Go to [GitHub Issues](https://github.com/yourusername/channelsmith/issues)
2. Click **New Issue**
3. Title: "Feature Request: [Brief description]"
4. Description:
   ```
   **Problem it solves**
   Describe the current limitation or workflow pain point

   **Proposed solution**
   Describe your ideal feature

   **Alternatives considered**
   Other approaches you've thought about

   **Additional context**
   Any relevant examples or references
   ```

---

## Code Contributions

### Setup for Development

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/channelsmith.git
   cd channelsmith
   ```

3. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Setup development environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Make your changes** following the code standards below

### Code Standards

ChannelSmith follows strict code standards to maintain quality and consistency.

#### File Naming
- **Files:** `snake_case` (e.g., `packing_engine.py`)
- **Classes:** `PascalCase` (e.g., `ChannelSmithApp`)
- **Functions:** `snake_case` (e.g., `pack_texture()`)
- **Constants:** `UPPER_CASE` (e.g., `MAX_TEXTURE_SIZE`)

#### Type Hints (REQUIRED)
Every function must have type hints:
```python
def pack_texture(images: List[PIL.Image], template: Template) -> PIL.Image:
    """Pack multiple textures using a template.

    Args:
        images: List of PIL Image objects to pack
        template: Template configuration

    Returns:
        Packed PIL Image object
    """
```

#### Docstrings (Google Style, REQUIRED)
All public APIs must have docstrings:
```python
def pack_texture_from_template(
    textures: Dict[str, PIL.Image],
    template: Template
) -> PIL.Image:
    """Pack individual texture channels into a single RGBA image.

    This function combines multiple grayscale texture maps into a single
    packed texture following the specified template layout.

    Args:
        textures: Dictionary mapping channel names to PIL Image objects.
            Expected keys: 'ambient_occlusion', 'roughness', 'metallic', etc.
            All images must be same size and L mode (grayscale).
        template: Template object defining channel assignments and defaults.

    Returns:
        PIL.Image: RGBA image with channels packed according to template.

    Raises:
        ValueError: If images are mismatched sizes or modes.
        KeyError: If required channels are missing.

    Example:
        >>> ao = load_image('ao.png')
        >>> roughness = load_image('roughness.png')
        >>> metallic = load_image('metallic.png')
        >>> template = load_template('orm.json')
        >>> packed = pack_texture_from_template({
        ...     'ambient_occlusion': ao,
        ...     'roughness': roughness,
        ...     'metallic': metallic
        ... }, template)
        >>> packed.save('packed.png')
    """
```

#### Formatting (black)
Use `black` for consistent formatting:
```bash
black channelsmith/
```

#### Linting (pylint)
Run pylint to catch issues:
```bash
pylint channelsmith/
```

#### No Print Statements
Use logging only in core/:
```python
import logging
logger = logging.getLogger(__name__)

# Good
logger.info("Packing texture with template: %s", template.name)

# Bad
print(f"Packing texture with template: {template.name}")
```

#### No sys.exit in Widgets
GUI/API code should never call `sys.exit()`. Return exit codes instead:
```python
# Good - returns exit code
def launch_gui() -> int:
    try:
        app = ChannelSmithApp()
        app.mainloop()
        return 0
    except Exception as e:
        logger.exception("Error: %s", e)
        return 1

# Bad - exits directly
def launch_gui():
    app = ChannelSmithApp()
    app.mainloop()
    sys.exit(0)
```

### Testing

ChannelSmith requires >90% code coverage.

#### Write Tests First (TDD)
Use test-driven development:
1. Write failing test
2. Write code to pass test
3. Refactor
4. Commit

#### Test Structure
- **Core logic:** `tests/test_core/`
- **API endpoints:** `tests/test_api/`
- **GUI:** `tests/test_gui/`

#### Running Tests
```bash
# All tests
pytest

# With coverage report
pytest --cov=channelsmith --cov-report=html

# Specific test file
pytest tests/test_core/test_packing_engine.py

# Verbose output
pytest -v
```

#### Test Example
```python
import pytest
from PIL import Image
from channelsmith.core.packing_engine import pack_texture_from_template
from channelsmith.templates.template_loader import load_template

def test_pack_orm_texture():
    """Test packing with ORM template."""
    # Arrange
    template = load_template("channelsmith/templates/orm.json")
    test_image = Image.new('L', (256, 256), 128)
    textures = {
        'ambient_occlusion': test_image,
        'roughness': test_image,
        'metallic': test_image,
    }

    # Act
    result = pack_texture_from_template(textures, template)

    # Assert
    assert result is not None
    assert result.size == (256, 256)
    assert result.mode == 'RGBA'
```

### Commit Messages

Follow the format: `<type>(<scope>): <description>`

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `test` - Tests
- `refactor` - Code refactoring
- `perf` - Performance improvement
- `chore` - Build, dependency updates

**Examples:**
```
feat(api): add template details endpoint
fix(core): handle mismatched texture sizes
docs(readme): update installation instructions
test(packing): add edge case tests for alpha channel
refactor(ui): simplify form validation logic
```

### Submitting a Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub
   - Title: Clear, specific description
   - Description:
     ```
     ## Summary
     Brief description of changes

     ## Type of Change
     - [ ] Bug fix
     - [ ] New feature
     - [ ] Breaking change
     - [ ] Documentation update

     ## Changes
     - Bullet point 1
     - Bullet point 2

     ## Testing
     Describe how you tested this change

     ## Checklist
     - [ ] Code follows style guidelines
     - [ ] Comments added for complex logic
     - [ ] Documentation updated
     - [ ] Tests added/updated
     - [ ] All tests pass (pytest)
     - [ ] No new warnings (pylint, black)
     ```

3. **Wait for review**
   - Maintainers will review within 1-2 weeks
   - Be responsive to feedback
   - Update PR as needed

### Code Review Expectations

When your PR is reviewed:

- **Be open to feedback** - Reviews improve code quality
- **Respond to comments** - Either explain your approach or update code
- **Keep commits atomic** - Each commit should be a logical unit
- **Don't be discouraged** - Review comments aren't personal criticism

---

## Project Structure

Understand the architecture before contributing:

```
channelsmith/
├── core/                   # Packing/unpacking engine (no GUI deps)
│   ├── packing_engine.py  # Main logic
│   └── ...
├── api/                    # Flask REST API
│   ├── app.py             # Flask app factory
│   ├── routes.py          # API endpoints
│   └── ...
├── frontend/               # Web UI (HTML/CSS/JS)
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── gui/                    # Legacy tkinter GUI (deprecated)
├── templates/              # Template JSON files
└── utils/                  # Shared utilities
```

**Key principles:**
- `core/` is GUI-agnostic (no tkinter, Flask, or web imports)
- Logging only in `core/`
- No `sys.exit()` in widgets or API routes
- All business logic in `core/`, UI is thin wrapper

---

## Release Process (For Maintainers)

Only maintainers can create releases:

1. Update version in `channelsmith/__init__.py`
2. Update `CHANGELOG.md`
3. Run `pytest` (all tests must pass)
4. Merge to `main`
5. Create git tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
6. Push tag: `git push origin v0.2.0`
7. GitHub Actions builds executables automatically
8. Create GitHub Release with changelog

See [docs/RELEASE_PROCESS.md](docs/RELEASE_PROCESS.md) for detailed steps.

---

## Questions?

- **GitHub Issues** for bugs and features
- **Discussions** (coming soon) for general questions
- **Email** [contact info] for private inquiries

---

**Thank you for contributing to ChannelSmith!** 🙏
