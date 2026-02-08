# Beta Phase Quick Start

**For:** Getting started with GUI implementation

---

## What Changed?

Alpha phase (core engine) is **complete**. Now implementing tkinter GUI.

---

## New Files Created

**Task checklist:**
- `BETA_TASKS.md` - 16 independent tasks (B1-B16)

**Documentation:**
- `docs/GUI_STRUCTURE.md` - Component architecture
- `docs/GUI_COMPONENTS.md` - tkinter reference for non-devs
- `docs/BETA_QUICKSTART.md` - This file

---

## Project Structure

```
channelsmith/gui/        ← All GUI code goes here (NEW)
├── __init__.py
├── app.py               ← Main app entry
├── main_window.py       ← Root window
├── template_selector.py ← Template dropdown
├── image_selector.py    ← Image picker widget
├── packer_panel.py      ← Pack tab
├── unpacker_panel.py    ← Unpack tab
├── preview_panel.py     ← Image preview
├── progress.py          ← Progress bar
├── dialogs.py           ← Error/success dialogs
├── file_manager.py      ← Save/load projects
└── drag_drop.py         ← Drag-drop support

tests/test_gui/          ← GUI tests (NEW)
├── test_components.py
└── test_workflows.py

main_gui.py              ← Entry point script (NEW)
```

---

## How to Use This

### If You're a Developer

1. Read `BETA_TASKS.md` - each task is completely independent
2. Pick any task B1-B13 (skip B14-B16 for now)
3. See task file (e.g., `channelsmith/gui/app.py`) specified in checklist
4. Implement + test
5. Run: `python main_gui.py` to test

**Dependencies:**
- B1 (MainWindow) should be first
- B2, B3 (selectors) can be done anytime
- B5 (PackerPanel) depends on B2, B3
- B6 (UnpackerPanel) depends on B2, B3
- B7 (Layout) depends on B5, B6

### If You're Non-Technical

You can iterate on GUI without coding:

1. **Change button labels:** Edit `text="Pack"` in widget creation
2. **Change colors:** Edit `bg="#RRGGBB"` or use names like `"red"`
3. **Change sizes:** Edit `width=300` or `geometry("1200x800")`
4. **Move buttons around:** Change `pack()` to `pack(side="left")`

See `docs/GUI_COMPONENTS.md` for all options.

---

## Quick Dev Commands

```bash
# Run the GUI app
python main_gui.py

# Run GUI tests
pytest tests/test_gui/ -v

# Run all tests (core + GUI)
pytest

# Format code
black channelsmith/ tests/

# Check for errors
pylint channelsmith/gui/
```

---

## Task Categories

### Foundation (Do First)
- **B1:** MainWindow - root window setup
- **B2:** TemplateSelector - dropdown for ORM/ORD
- **B3:** ImageSelector - single image picker widget

### Components (Do Anytime)
- **B4:** PreviewPanel - display images on canvas
- **B8:** ErrorHandling - dialogs for errors/success
- **B10:** ProgressBar - show progress during operations

### Workflows (After Foundation)
- **B5:** PackerPanel - combine B2 + B3 to pack textures
- **B6:** UnpackerPanel - combine B2 + B3 to unpack
- **B7:** Layout - put both panels in tabs

### Features
- **B9:** DragDrop - drop images onto selectors
- **B11:** FileOps - save/load projects
- **B12:** MainApp - tie everything together
- **B13:** EntryPoint - make it runnable

### Testing & Docs
- **B14:** UnitTests - test individual widgets
- **B15:** IntegrationTests - test full workflows
- **B16:** DevGuide - documentation for iterating

---

## Core Files You'll Use

### From Alpha Phase (Already Done)
- `channelsmith/core/packing_engine.py` - `pack_texture(images, template)`
- `channelsmith/core/unpacking_engine.py` - `unpack_texture(image, template)`
- `channelsmith/templates/template_loader.py` - `load_template(path)`

**How to use:**
```python
from channelsmith.templates.template_loader import load_template
from channelsmith.core.packing_engine import pack_texture

template = load_template("templates/orm.json")
result_image = pack_texture(
    [ao_array, roughness_array, metallic_array],
    template
)
```

### GUI Patterns You'll Write

All widgets follow this pattern:
```python
import tkinter as tk

class MyWidget(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build_ui()

    def _build_ui(self):
        """Create child widgets"""
        label = tk.Label(self, text="My Widget")
        label.pack()

    def get_value(self):
        """Return current state"""
        return None
```

---

## Testing Without GUI

You don't need to display windows to test:

```python
# Test that widget loads
def test_image_selector():
    root = tk.Tk()
    selector = ImageSelector(root)

    # Test method works (don't test rendering)
    assert selector.get_image() is None

root.destroy()
```

---

## Getting Help

**For tkinter questions:** See `docs/GUI_COMPONENTS.md`

**For architecture questions:** See `docs/GUI_STRUCTURE.md`

**For task details:** See `BETA_TASKS.md`

**For code issues:** Check `CLAUDE.md` (project rules)

---

## When to Use /clear

Since you use /clear frequently, each task is **completely independent**:

- No state carries between sessions
- All imports explicit in each file
- All setup in `__init__()` methods
- No global variables

**Before /clear:**
- Commit your work: `git add . && git commit -m "..."`
- You'll see your changes when resuming

**After /clear:**
- Read task description in `BETA_TASKS.md`
- Everything you need is in code files and docs
- No context needed from previous session

---

## Definition of Done

Each task is done when:

1. ✓ File created with classes/functions in checklist
2. ✓ All methods have type hints + docstrings
3. ✓ Code formatted with `black`
4. ✓ No pylint errors (high priority)
5. ✓ Tests written and passing
6. ✓ Can import without errors: `from channelsmith.gui.* import *`

---

## Next: Pick a Task

See `BETA_TASKS.md`, pick B1 (MainWindow) and start coding! 🚀
