# GUI Structure & Architecture

**Purpose:** Simple, maintainable tkinter GUI for pack/unpack workflows

---

## Directory Layout

```
channelsmith/gui/
├── __init__.py
├── app.py                 # Main app entry, ties components
├── main_window.py         # Root window, menu bar, tabs
├── template_selector.py   # Template dropdown
├── image_selector.py      # Single channel image picker
├── packer_panel.py        # Pack workflow (3 images → 1 result)
├── unpacker_panel.py      # Unpack workflow (1 image → 3 channels)
├── preview_panel.py       # Canvas for image preview
├── progress.py            # Progress bar during operations
├── dialogs.py             # Error/success/file dialogs
├── file_manager.py        # Save/load projects
└── drag_drop.py           # Drag-drop handler

tests/test_gui/
├── test_components.py     # Unit tests for widgets
├── test_workflows.py      # Integration tests
└── fixtures.py            # Test data (sample images)
```

---

## Component Hierarchy

```
MainWindow (tk.Tk)
├── Menu Bar
│   ├── File (Open, Save, Exit)
│   └── Help (About, Docs)
│
├── Notebook (ttk.Notebook)
│   ├── Tab "Pack"
│   │   └── PackerPanel
│   │       ├── TemplateSelector
│   │       ├── ImageSelector (R/G/B) × 3
│   │       ├── PreviewPanel (packed result)
│   │       └── Buttons (Pack, Save Output)
│   │
│   └── Tab "Unpack"
│       └── UnpackerPanel
│           ├── ImageSelector (packed image)
│           ├── TemplateSelector
│           ├── PreviewPanel (input)
│           ├── PreviewPanel (R/G/B results) × 3
│           └── Button (Unpack)
│
└── Status Bar
    └── Label (status text)
```

---

## Core Patterns

### Widget Pattern
All custom widgets follow this pattern:

```python
class MyWidget(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build_ui()

    def _build_ui(self):
        """Create child widgets"""
        pass

    def get_value(self):
        """Return current state"""
        return self._state
```

**Use:**
```python
root = tk.Tk()
widget = MyWidget(root)
widget.pack()
value = widget.get_value()
```

### Validation Pattern
All user inputs validated before calling core API:

```python
def pack_textures(self):
    if not self.image_r.get_image():
        show_error("Missing Image", "Please select R channel")
        return

    # Call core API
    result = pack_texture(...)
    show_success("Done", "Textures packed")
```

### Async Pattern (later)
For long operations, use threading:

```python
def on_pack_clicked(self):
    self.progress.start("Packing...")
    thread = Thread(target=self._do_pack)
    thread.daemon = True
    thread.start()

def _do_pack(self):
    result = pack_texture(...)
    self.progress.stop()
    self.preview.show_image(result)
```

---

## Design Decisions

**Single-threaded now** - Operations fast enough (< 1 sec), no need for threading yet

**No custom styling** - Use tkinter defaults, easy to iterate

**Constants at top of files:**
```python
# geometry
PREVIEW_SIZE = 300
PANEL_WIDTH = 400

# colors
BG_COLOR = "#f0f0f0"
ERROR_COLOR = "#ff6666"
```

**Business logic in separate layer** - All GUI code in `gui/`, all pack/unpack calls to `core/`

---

## File I/O & State

**Save Project:**
```json
{
  "template": "ORM",
  "channels": {
    "R": "/path/to/ao.png",
    "G": "/path/to/roughness.png",
    "B": "/path/to/metallic.png"
  },
  "last_output": "/path/to/packed.png"
}
```

**Load Project:**
- Restore file paths
- Restore template selection
- Load and display preview images

---

## Error Handling

**GUI-level validation:**
1. Check file exists before processing
2. Check file is readable image format
3. Check image dimensions reasonable (not 1px or 8192px)

**Core-level errors:**
- Catch exceptions from `core/`
- Display user-friendly messages
- Log full traceback to file

**Dialog Pattern:**
```python
from channelsmith.gui.dialogs import show_error, show_success

try:
    result = pack_texture(...)
    show_success("Success", "Saved to...")
except Exception as e:
    show_error("Pack Failed", str(e))
    logger.exception("Pack failed")
```

---

## Testing Strategy

**Unit Tests** (B14)
- Mock tkinter objects
- Test widget methods: `get_value()`, `set_value()`
- Test validation logic

**Integration Tests** (B15)
- Create temporary test images
- Simulate user clicks (call methods directly, not events)
- Verify core API called correctly
- Check output files created

**No GUI Rendering Tests**
- Don't try to render windows in tests
- Test business logic only

---

## Common Changes for Non-Developers

### Change button label
```python
# In packer_panel.py
self.pack_btn = tk.Button(self, text="PACK NOW")  # Change text
```

### Change panel size
```python
# In __init__
self.geometry("1400x900")  # width x height
```

### Change colors
```python
# At top of file
BUTTON_COLOR = "#4CAF50"
self.pack_btn = tk.Button(self, bg=BUTTON_COLOR)
```

### Add new dialog
```python
# In dialogs.py
def ask_custom(title, message):
    return simpledialog.askstring(title, message)
```

### Add new button to menu
```python
# In main_window.py, _create_menu()
file_menu.add_command(label="New Project", command=self.new_project)
```

---

## Performance Notes

**Images under 2048x2048:** Instant (< 100ms)
**Images 2048x4096:** Fast (< 500ms)
**Images 4096x4096+:** Slow (> 1s) - consider progress bar

**Memory:** Each image ~10-40MB in memory (uncompressed). OK for single texture.

---

## Future: Threading

When operations get slow:

```python
from threading import Thread
import queue

class PackerPanel(tk.Frame):
    def __init__(self, parent):
        ...
        self.result_queue = queue.Queue()

    def on_pack_clicked(self):
        self.progress.start("Packing...")
        thread = Thread(target=self._pack_thread)
        thread.daemon = True
        thread.start()
        self._check_result()

    def _pack_thread(self):
        result = pack_texture(...)
        self.result_queue.put(result)

    def _check_result(self):
        try:
            result = self.result_queue.get_nowait()
            self.preview.show_image(result)
            self.progress.stop()
        except queue.Empty:
            self.after(100, self._check_result)  # Poll every 100ms
```

---

## Logging

All GUI operations logged:

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Packing with template: {template_name}")
logger.error(f"Pack failed: {error}")
```

Log file: `channelsmith.log` in working directory
