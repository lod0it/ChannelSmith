# ChannelSmith User Guide

**Version:** 0.1.0-beta
**Last Updated:** February 8, 2026

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Workflows](#core-workflows)
3. [Advanced Features](#advanced-features)
4. [FAQ](#faq)
5. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

1. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org)
   - Ensure Python is added to PATH

2. **Clone or extract ChannelSmith**
   ```bash
   git clone <repository-url>
   cd ChannelSmith
   ```

3. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Launching ChannelSmith

```bash
python -m channelsmith
```

The GUI window should open. You'll see two main tabs: **Pack** and **Unpack**.

---

## Core Workflows

### Workflow 1: Pack Textures (Combine into One)

**Goal:** Combine multiple grayscale maps into a single RGBA texture

**Steps:**

1. **Select Template**
   - Click the **Template** dropdown at the top
   - Choose a template (typically **ORM** for most games):
     - **ORM:** Occlusion-Roughness-Metallic (R/G/B channels)
     - **ORD:** Occlusion-Roughness-Displacement (R/G/B channels)
   - Each template shows which channels it uses

2. **Load Images**
   - For each required channel, click **Select Image** or drag-and-drop a PNG/JPG/TGA file
   - Images are automatically converted to grayscale
   - Missing images use smart defaults (e.g., AO=white, Roughness=mid-gray)

3. **Preview (Optional)**
   - After loading images, the preview panel shows what channels are loaded
   - Green checkmarks indicate loaded textures
   - Gray placeholders indicate default values will be used

4. **Pack Textures**
   - Click the **Pack** button
   - The combined image appears in the preview panel
   - Status bar shows "Pack complete"

5. **Save Result**
   - Right-click the preview image OR
   - Use **File → Export as PNG**
   - Choose location and filename (e.g., `material_orm.png`)

**Example: Packing ORM Textures**

If your texture folder has:
- `material_ao.png` (white = well-lit areas)
- `material_roughness.png` (gray values)
- `material_metallic.png` (black = non-metal, white = metal)

After packing, you get a single `material_orm.png` where:
- Red channel = AO
- Green channel = Roughness
- Blue channel = Metallic

**Result:** 3 textures (typical 2-4 MB each) → 1 texture (~3-5 MB)

---

### Workflow 2: Unpack Textures (Extract Channels)

**Goal:** Extract individual channels from a packed texture

**Steps:**

1. **Select Template**
   - Choose the template used to create the packed texture
   - Must match the original template (wrong template = wrong results)

2. **Load Packed Image**
   - Click **Select Image** or drag-and-drop the packed texture
   - Preview shows the loaded image

3. **Unpack Channels**
   - Click the **Unpack** button
   - ChannelSmith extracts individual channels

4. **Save Channels**
   - Each channel shows in the results list
   - Click **Save** next to each channel to save as individual PNG
   - Or use **Save All** to batch-save all channels

**Example: Unpacking ORM**

Loaded `material_orm.png` → Unpacking → Extract:
- `material_orm_ao.png` (from red channel)
- `material_orm_roughness.png` (from green channel)
- `material_orm_metallic.png` (from blue channel)

---

### Workflow 3: Repack Textures (Change Format)

**Goal:** Convert texture from one template format to another (e.g., ORM → ORD)

**Steps:**

1. **Unpack Original**
   - Use Workflow 2 to unpack the original packed texture
   - Save the extracted channels
   - Note: AO and Roughness are shared between ORM/ORD

2. **Load New Textures**
   - If changing to ORD, ensure you have a **Displacement** map
   - Load the shared channels (AO, Roughness) from the unpacked files
   - Load new channels as needed

3. **Pack with New Template**
   - Select the new template (e.g., ORD)
   - Follow Workflow 1 to pack with the new format
   - Save the result

**Example: Converting ORM → ORD**

```
Original ORM:    material_orm.png (R=AO, G=Roughness, B=Metallic)
           ↓
         Unpack → material_ao.png, material_roughness.png, material_metallic.png
           ↓
    Discard metallic, add displacement: material_displacement.png
           ↓
         Pack as ORD (R=AO, G=Roughness, B=Displacement)
           ↓
Result ORD:      material_ord.png
```

---

## Advanced Features

### Drag-and-Drop

**Supported:** All image selectors support drag-and-drop

1. Open your file explorer
2. Drag a PNG/JPG/TGA image
3. Drop it onto the image selector in ChannelSmith
4. Image loads automatically

### Custom Templates

ChannelSmith comes with preset templates (ORM, ORD), but you can create custom ones:

1. Use the **Templates → Create Custom** menu
2. Define which channels map to R/G/B/A
3. Set default values for missing channels
4. Save with a memorable name

### Project Save/Load

Save your work as a project to revisit later:

**Save Project:**
1. After packing/unpacking, click **File → Save Project**
2. Choose location (creates `.csproj` file)
3. Includes all loaded images and settings

**Load Project:**
1. Click **File → Open Project**
2. Select a saved `.csproj` file
3. All previous images and settings restore

### Resolution Handling

**What if textures have different resolutions?**

ChannelSmith automatically:
- Finds the highest resolution
- Upscales lower resolutions to match
- Uses bilinear interpolation for smooth results

Example: 256×256 AO + 1024×1024 Roughness → All channels upscaled to 1024×1024

### Smart Defaults

If you omit a channel, ChannelSmith fills it with intelligent defaults:

| Channel | Default | Meaning |
|---------|---------|---------|
| Ambient Occlusion | White (1.0) | Fully lit (no shadow) |
| Roughness | Mid-gray (0.5) | Medium roughness |
| Metallic | Black (0.0) | Non-metallic |
| Displacement | Mid-gray (0.5) | No displacement |
| Opacity/Alpha | White (1.0) | Fully opaque |

**Use case:** If you only have a Roughness map, ChannelSmith creates a valid ORM with:
- Red = White (full AO)
- Green = Your Roughness
- Blue = Black (non-metal)

---

## FAQ

### Q: What image formats does ChannelSmith support?

**A:** Input formats: PNG, JPG/JPEG, TGA, TIFF
Output format: PNG (default, lossless)

### Q: Can I use colored (RGB) textures instead of grayscale?

**A:** Yes. ChannelSmith converts RGB to grayscale automatically using luminance: `(0.299×R + 0.587×G + 0.114×B)`

### Q: What's the maximum texture resolution?

**A:** No hard limit, but practical limit is your GPU/RAM. Common sizes: 1024×1024, 2048×2048, 4096×4096

### Q: How much space do I save?

**A:** Roughly **75% reduction**:
- 4 separate textures @ 2-4 MB each = 8-16 MB
- 1 packed RGBA = 2-4 MB
- **Result:** 4-12 MB saved per material

### Q: Can I pack 4 channels into RGBA?

**A:** Yes! Some templates support alpha channel (e.g., ORMA). Select a template with 4 channels.

### Q: What if I pack with the wrong template?

**A:** The channels will be read incorrectly in your game engine. Always verify:
- Template name matches your engine's expectation
- Channel order is correct (check template details)

### Q: Can I edit the extracted channels after unpacking?

**A:** Yes! Save the unpacked channels, edit them in Photoshop/GIMP/other tools, then repack.

### Q: My textures have different resolutions. Is that OK?

**A:** Yes, ChannelSmith handles it. It upscales all to the highest resolution automatically.

### Q: Can I batch process multiple materials?

**A:** Not in the GUI yet. For batch processing, use the Python API (see main README).

### Q: Do I need a GPU?

**A:** No. ChannelSmith runs on CPU. GPU acceleration coming in future versions.

### Q: Is my data safe? Does ChannelSmith send data anywhere?

**A:** Completely offline. All processing happens locally. No data leaves your machine.

---

## Troubleshooting

### Issue: "No template available" error

**Cause:** Templates weren't installed or not found
**Solution:**
1. Check `channelsmith/templates/` directory exists
2. Verify `orm.json` and `ord.json` files are present
3. Reinstall: `pip install -r requirements.txt`

### Issue: Image won't load / "Failed to load image"

**Cause:** Unsupported format, corrupted file, or permissions issue
**Solution:**
1. Verify file is PNG/JPG/TGA/TIFF
2. Try opening file in another program (e.g., Windows Photo Viewer)
3. Convert to PNG: `ffmpeg -i input.jpg output.png`
4. Check file permissions

### Issue: Packed texture looks wrong in engine

**Cause:** Wrong template selected
**Solution:**
1. Verify template matches engine requirement (ORM vs ORD vs custom)
2. Check channel order in template
3. Repack with correct template

### Issue: Unpacked channels are black/white/wrong colors

**Cause:** Used wrong template for unpacking
**Solution:**
1. Select correct template that was used during packing
2. Reunpack with correct template

### Issue: "Memory error" or "Out of memory"

**Cause:** Texture resolution too high
**Solution:**
1. Reduce texture resolution (4096×4096 → 2048×2048)
2. Close other applications
3. Try 32-bit version (uses less RAM)

### Issue: Progress bar stuck / Application not responding

**Cause:** Large texture processing takes time
**Solution:**
1. Wait 30+ seconds (large textures take time)
2. If still stuck, force close app (`Ctrl+Alt+Delete` → Task Manager)
3. Use smaller textures for testing

### Issue: Drag-drop doesn't work

**Cause:** tkinterdnd2 not installed or unavailable on system
**Solution:**
1. Click button to select file manually
2. To enable drag-drop: `pip install tkinterdnd2`

### Issue: "Template file not found"

**Cause:** Template path incorrect or custom template missing
**Solution:**
1. Use built-in templates (ORM, ORD) first
2. For custom templates, save to `channelsmith/templates/`

---

## Tips & Best Practices

### Quality Preservation

- Use **PNG format** for saving (lossless)
- Avoid JPG (lossy compression artifacts)
- Keep originals as backups

### Texture Naming

Use clear naming conventions:
```
material_orm_ao.png          → Ambient Occlusion
material_orm_roughness.png   → Roughness
material_orm_metallic.png    → Metallic
material_orm_packed.png      → Final packed texture
```

### Resolution Strategy

- Start with consistent resolutions (all 1024×1024)
- If mixed, let ChannelSmith upscale automatically
- Higher res = larger file size, slower processing

### Template Selection

| Engine | Template | Notes |
|--------|----------|-------|
| Unreal Engine | ORM | Standard format |
| Unity | ORM or custom | Check material specs |
| Godot | Custom | Define in material |
| Custom Engine | Custom | Define per specification |

### Workflow Efficiency

1. **First time:** Pack manually, save project
2. **Iterate:** Load project, modify individual channels, repack
3. **Final:** Export and test in engine

---

## Getting Help

### Documentation
- **README.md** - Project overview and quick start
- **SETUP.md** - Installation details
- **This guide** - User workflows and FAQ

### Reporting Issues

If you encounter bugs:
1. Note exact steps to reproduce
2. Include error message (if any)
3. Describe your system (OS, Python version)
4. Provide sample files if possible

### Feature Requests

Would you like:
- Batch processing?
- More template options?
- Color channel support?
- Video frame processing?

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0-beta | Feb 8, 2026 | GUI release with Pack/Unpack/Repack workflows |
| 0.1.0-alpha | Jan 2026 | Core engine and templates |

---

**Happy texturing! 🎨**
