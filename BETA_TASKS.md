# ChannelSmith - Beta Phase Tasks

**Phase:** Beta (GUI Implementation)
**Goal:** Functional tkinter GUI for pack/unpack workflows
**Scope:** Simple, iterable, no fancy features

---

## Task Structure

Each task is **completely independent**. Run them in any order after prerequisites.

**Prerequisites:** Alpha phase complete (core engine working)

---

## B1: Main Window Setup
**File:** `channelsmith/gui/main_window.py`
**Depends:** None

- [ ] Create `MainWindow` class (tk.Tk)
- [ ] Set window size 1200x800
- [ ] Create menu bar (File, Help)
- [ ] File menu: Open Project, Save Project, Exit
- [ ] Help menu: About, Docs link
- [ ] Add status bar at bottom
- [ ] Add main content area (tk.Frame)
- [ ] Test window opens and closes cleanly

---

## B2: Template Selector
**File:** `channelsmith/gui/template_selector.py`
**Depends:** None (load templates from disk)

- [ ] Create `TemplateSelector` frame widget
- [ ] Add label "Template"
- [ ] Add dropdown (ttk.Combobox) with ORM, ORD
- [ ] Add "Load Custom" button
- [ ] Store selected template name
- [ ] Method: `get_selected_template() -> str`
- [ ] Test dropdown works, custom load opens file dialog

---

## B3: Image Selector
**File:** `channelsmith/gui/image_selector.py`
**Depends:** None

- [ ] Create `ImageSelector` frame widget
- [ ] Add label for channel (e.g., "Roughness")
- [ ] Add button "Choose Image"
- [ ] Add label showing selected file path
- [ ] Add button "Preview" (shows image)
- [ ] Store PIL Image object
- [ ] Method: `get_image() -> Optional[PIL.Image.Image]`
- [ ] Method: `get_file_path() -> str`
- [ ] Test file selection works

---

## B4: Preview Panel
**File:** `channelsmith/gui/preview_panel.py`
**Depends:** None

- [ ] Create `PreviewPanel` frame with tk.Canvas
- [ ] Add label "Preview"
- [ ] Canvas size 300x300
- [ ] Method: `show_image(image: PIL.Image.Image)`
- [ ] Resize image to fit canvas (maintain aspect ratio)
- [ ] Convert PIL Image to PhotoImage for display
- [ ] Handle missing image gracefully (gray placeholder)
- [ ] Test image displays correctly

---

## B5: Packer Panel
**File:** `channelsmith/gui/packer_panel.py`
**Depends:** B2 (TemplateSelector), B3 (ImageSelector)

- [ ] Create `PackerPanel` frame
- [ ] Add TemplateSelector
- [ ] Add 3 x ImageSelector (for R/G/B channels)
- [ ] Add "Pack" button
- [ ] Add "Save Output" button (disabled until pack done)
- [ ] Method: `pack_textures() -> PIL.Image.Image` (calls core API)
- [ ] Show result in preview
- [ ] Test pack button works

---

## B6: Unpacker Panel
**File:** `channelsmith/gui/unpacker_panel.py`
**Depends:** B2 (TemplateSelector), B4 (PreviewPanel)

- [ ] Create `UnpackerPanel` frame
- [ ] Add "Select Packed Image" button
- [ ] Show selected image in preview
- [ ] Add TemplateSelector
- [ ] Add "Unpack" button
- [ ] Show 3 x extracted channels in previews
- [ ] Method: `unpack_texture(image, template) -> Dict`
- [ ] Test unpack button works

---

## B7: Layout Integration
**File:** `channelsmith/gui/main_window.py` (update)
**Depends:** B1, B5, B6

- [ ] Add notebook (ttk.Notebook) with 2 tabs
- [ ] Tab 1: "Pack" → PackerPanel
- [ ] Tab 2: "Unpack" → UnpackerPanel
- [ ] Test tabs switch correctly
- [ ] Test both panels visible

---

## B8: Error Handling & Dialogs
**File:** `channelsmith/gui/dialogs.py` (new)
**Depends:** None

- [ ] Function: `show_error(title: str, message: str)`
- [ ] Function: `show_success(title: str, message: str)`
- [ ] Function: `ask_file(title: str, file_types: list) -> str`
- [ ] Function: `ask_directory(title: str) -> str`
- [ ] Test dialogs appear and return correctly

---

## B9: Drag-Drop Support
**File:** `channelsmith/gui/drag_drop.py` (new)
**Depends:** B3 (ImageSelector)

- [ ] Add drag-drop binding to ImageSelector
- [ ] Accept .png, .tga, .jpg, .tiff files
- [ ] Extract file path from drop event
- [ ] Load and display image
- [ ] Test drag-drop works

---

## B10: Progress Indicator
**File:** `channelsmith/gui/progress.py` (new)
**Depends:** None

- [ ] Create `ProgressBar` widget
- [ ] Show during pack/unpack operations
- [ ] Add animated progress (indeterminate)
- [ ] Add status text
- [ ] Method: `start(message: str)`
- [ ] Method: `stop()`
- [ ] Test progress shows/hides

---

## B11: File Operations
**File:** `channelsmith/gui/file_manager.py` (new)
**Depends:** B5, B6

- [ ] Method: `save_image(image: PIL.Image.Image, default_name: str) -> str`
- [ ] Method: `load_project(path: str) -> Dict` (load saved state)
- [ ] Method: `save_project(state: Dict, path: str)` (save settings)
- [ ] Test save/load works

---

## B12: Main App Entry Point
**File:** `channelsmith/gui/app.py` (new)
**Depends:** All above

- [ ] Create `ChannelSmithApp` class
- [ ] Initialize MainWindow
- [ ] Bind quit handlers
- [ ] Test app launches cleanly

---

## B13: Entry Point Script
**File:** `main_gui.py` (root level)
**Depends:** B12

- [ ] Create simple entry point script
- [ ] `if __name__ == "__main__": ChannelSmithApp().run()`
- [ ] Test `python main_gui.py` works

---

## Testing Tasks

### B14: GUI Unit Tests
**File:** `tests/test_gui/test_components.py`

- [ ] Test TemplateSelector loads templates
- [ ] Test ImageSelector loads images
- [ ] Test PreviewPanel displays images
- [ ] Test dialog functions work

---

### B15: Integration Tests
**File:** `tests/test_gui/test_workflows.py`

- [ ] Test full pack workflow (select images, click pack, save)
- [ ] Test full unpack workflow (select image, click unpack)
- [ ] Test error handling (invalid files, missing images)
- [ ] Test drag-drop flow

---

## Documentation

### B16: GUI Development Guide
**File:** `docs/GUI_DEVELOPMENT.md`

For non-developers to iterate:
- Component overview + where each lives
- How to change button labels/colors
- How to resize panels
- Common tkinter patterns
- How to add new dialogs

---

## Implementation Notes

**Keep It Simple:**
- No animations, no fancy styling
- Use default tkinter theme
- Single-threaded (no async needed yet)
- Blocking operations OK for now

**Easy to Iterate:**
- Each panel is standalone widget
- Each panel has clean API (`get_image()`, `pack_textures()`)
- All dialogs in one file
- Colors/sizes as constants at top of file

**Testing:**
- No need to actually display GUI in tests
- Mock tk objects if needed
- Test business logic, not tkinter rendering

---

## Checklist: Ready for Release?

- [ ] All tasks B1-B13 complete
- [ ] GUI tests passing (B14-B15)
- [ ] Can pack textures via GUI
- [ ] Can unpack textures via GUI
- [ ] Can save/load projects
- [ ] Error messages helpful
- [ ] No GUI code in `channelsmith/core/`
- [ ] Documentation complete (B16)
