# ChannelSmith Web UI - Quick Start (2 Minutes) 🚀

## Step 1: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

**Dependencies added:**
- Flask 3.0+ (web framework)
- flask-cors 4.0+ (CORS support)
- Pillow, numpy, pytest (already installed)

## Step 2: Launch Web UI (< 1 minute)

```bash
python -m channelsmith
```

**What happens:**
1. Flask server starts at `http://localhost:5000`
2. Browser opens automatically
3. You see the ChannelSmith web interface (dark theme, Tailwind CSS)

## Step 3: Try It Out (< 1 minute)

### Pack Textures
1. **Upload channels:** Drag images to the upload zones (or click)
   - Red channel (Ambient Occlusion)
   - Green channel (Roughness)
   - Blue channel (Metallic)
   - Alpha channel (optional)

2. **Click "Pack Texture"** → Download packed PNG

### Unpack Textures
1. **Switch tab** to "Unpack Texture"
2. **Upload** a packed image
3. **Click "Unpack Texture"** → Download channels as PNG

---

## Advanced Usage

### Run API Tests
```bash
pytest tests/test_api/ -v
# Expected: 22 passed in ~0.5s
```

### Run All Tests (No GUI)
```bash
pytest tests/test_core/ tests/test_api/ -q
# Expected: 229 passed
```

### Use Legacy GUI
```bash
python -m channelsmith --gui
# Opens classic tkinter interface
```

### Use Programmatically
```python
from channelsmith.api.app import create_app
app = create_app()
# Use Flask test client or production WSGI server
```

---

## File Structure

```
channelsmith/
├── api/                 ← Flask REST API (NEW)
├── frontend/            ← Web UI (NEW)
├── core/               ← Core engine (unchanged)
└── gui/                ← Legacy GUI (still works)

tests/
├── test_api/           ← API tests (NEW)
└── test_core/          ← Core tests (passing)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5000 in use | `python -m channelsmith` on different port, or kill process on 5000 |
| Module not found | `pip install -r requirements.txt` |
| Browser not opening | Manual open: http://localhost:5000 |
| Blank page | Check browser console (F12), check Flask logs |
| Drag-drop not working | Use "click to upload" instead |

---

## Next Steps

1. **Test the UI:** Follow [WEB_UI_TESTING.md](WEB_UI_TESTING.md)
2. **Read the docs:** [README.md](README.md) for full features
3. **API reference:** Check `/api/health`, `/api/templates`, `/api/pack`, `/api/unpack`
4. **Customize:** Edit `channelsmith/frontend/` for styling changes

---

## What's New?

✨ **Web UI MVP (Just Completed!)**
- Modern Flask REST API with 5 endpoints
- Tailwind CSS dark theme interface
- Vanilla JavaScript for interactivity
- 22 comprehensive API tests (all passing)
- No external tools needed (everything in browser)

🔄 **Backwards Compatible**
- Core engine unchanged (207 tests still passing)
- Legacy GUI still works (`--gui` flag)
- Programmatic API works as before

---

**Version:** 0.1.0-web-mvp
**Status:** Ready for testing 🎯
