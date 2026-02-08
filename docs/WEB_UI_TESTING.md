# ChannelSmith Web UI - Testing Guide

Complete guide to testing the new Flask-based web UI for ChannelSmith.

## Quick Start (2 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Web UI
```bash
python -m channelsmith
```

The app will automatically open in your browser at **http://localhost:5000**

### 3. Test Pack Workflow
- **Upload Red Channel (AO):** Drag or click to select an image
- **Upload Green Channel (Roughness):** Optional (uses default 0.5 mid-gray if omitted)
- **Upload Blue Channel (Metallic):** Optional (uses default 0.0 black if omitted)
- **Click "Pack Texture"** → Download packed PNG

### 4. Test Unpack Workflow
- **Switch to "Unpack Texture" tab**
- **Upload Packed Image:** Upload a packed PNG
- **Select Template:** Choose ORM or ORD
- **Click "Unpack Texture"** → See extracted channels
- **Download Channels:** Click "Download" on any channel

---

## Automated Testing (API Tests)

### Run All API Tests
```bash
pytest tests/test_api/ -v
```

Expected output: **22 passed**

### Run Specific Test Category

**Health & Templates:**
```bash
pytest tests/test_api/test_routes.py::TestHealthEndpoint -v
pytest tests/test_api/test_routes.py::TestTemplatesEndpoint -v
```

**Pack Endpoint:**
```bash
pytest tests/test_api/test_routes.py::TestPackEndpoint -v
```

**Unpack Endpoint:**
```bash
pytest tests/test_api/test_routes.py::TestUnpackEndpoint -v
```

**Integration (Pack → Unpack Roundtrip):**
```bash
pytest tests/test_api/test_routes.py::TestIntegration -v
```

### Test Coverage
```bash
pytest tests/test_api/ --cov=channelsmith.api --cov-report=html
# Opens htmlcov/index.html in your browser
```

---

## Manual Testing Workflows

### Workflow 1: Pack with All Channels (ORM)

**Setup:**
1. Open http://localhost:5000
2. Ensure "Pack Channels" tab is active
3. Template: **ORM**

**Test Steps:**
1. **Red Channel (AO):** Upload a grayscale image (any size)
   - Expected: Preview shows uploaded image
2. **Green Channel (Roughness):** Upload second image
   - Expected: Preview updates
3. **Blue Channel (Metallic):** Upload third image
   - Expected: Preview shows all three channels
4. **Alpha Channel:** Leave empty
   - Expected: Uses default white (1.0)
5. **Click "Pack Texture"**
   - Expected: Preview shows packed result
6. **Click "📥 Download Packed Image"**
   - Expected: Downloads `channelsmith_packed_orm.png`

**Verification:**
- Open downloaded file in image editor
- Should be RGB image (3 channels) not RGBA
- Red channel = original AO image
- Green channel = original Roughness image
- Blue channel = original Metallic image

---

### Workflow 2: Pack with Partial Channels (Using Defaults)

**Setup:**
1. Template: **ORM**

**Test Steps:**
1. **Red Channel (AO):** Upload one image
2. **Leave Green and Blue empty** (will use defaults)
3. **Click "Pack Texture"**

**Verification:**
- Should succeed (not fail)
- Green channel should be mid-gray (128/255 = 0.5)
- Blue channel should be black (0/255 = 0.0)
- Red channel matches uploaded image

---

### Workflow 3: Unpack with ORM Template

**Setup:**
1. Switch to **"Unpack Texture"** tab
2. Template: **ORM**

**Test Steps:**
1. **Upload Packed Image:** Use previously downloaded `channelsmith_packed_orm.png`
2. **Click "Unpack Texture"**
   - Expected: Shows 3 channel cards (AO, Roughness, Metallic)
3. **Verify Channels:**
   - "Ambient Occlusion" = original red channel
   - "Roughness" = original green channel
   - "Metallic" = original blue channel
4. **Download Channels:**
   - Click "📥 Download" on each channel
   - Files: `channelsmith_ambient_occlusion_orm.png`, etc.

---

### Workflow 4: Pack → Unpack Roundtrip

**Complete workflow from start to finish:**

**Pack Phase:**
1. Upload 3 channel images in Pack tab
2. Click "Pack Texture"
3. Download packed result

**Unpack Phase:**
1. Upload packed result in Unpack tab
2. Click "Unpack Texture"
3. Download extracted channels

**Verification:**
- Extracted channels match original uploads
- Pixel values preserved within normal PNG tolerance

---

### Workflow 5: Test ORD Template

**Setup:**
1. Template: **ORD** (Occlusion-Roughness-Displacement)

**Test Steps:**
1. **Red Channel (AO):** Upload image
2. **Green Channel (Roughness):** Upload image
3. **Blue Channel (Displacement):** Upload image (replaces Metallic from ORM)
4. **Pack & Unpack**

**Verification:**
- Unpack shows: Ambient Occlusion, Roughness, **Displacement** (not Metallic)

---

## Edge Case Testing

### Test 1: Different Image Sizes
**Setup:** Upload channels with different resolutions
- Red: 256×256
- Green: 512×512
- Blue: 1024×1024

**Expected:** Normalizes to 1024×1024 (largest size)

**How to test:**
```bash
pytest tests/test_api/test_routes.py::TestIntegration::test_pack_with_different_sizes -v
```

---

### Test 2: Invalid File Format
**Setup:** Try uploading non-image file

**Expected:** Error message "Invalid {color} channel image"

**Browser Test:**
1. Try uploading a `.txt` file
2. Should show error notification

---

### Test 3: No Channels Provided
**Setup:** Click Pack without uploading any channels

**Expected:** Uses all default values, produces valid output

**Verification:**
- Pack succeeds with 1024×1024 image
- All channels = template defaults

**Automated Test:**
```bash
pytest tests/test_api/test_routes.py::TestPackEndpoint::test_pack_without_channels_uses_defaults -v
```

---

### Test 4: RGBA Image Unpack
**Setup:** Upload RGBA image (with alpha channel)

**Expected:** Unpacks all 4 channels successfully

**Automated Test:**
```bash
pytest tests/test_api/test_routes.py::TestUnpackEndpoint::test_unpack_rgba_image -v
```

---

## Browser Compatibility Testing

Test the UI on different browsers:

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome 120+ | ✓ | Primary target, full support |
| Firefox 121+ | ✓ | Full support |
| Safari 17+ | ✓ | Full support |
| Edge 120+ | ✓ | Full support |

**Quick test per browser:**
1. Drag-drop file to upload zone
2. Verify preview updates
3. Click buttons and verify responses
4. Check console for JavaScript errors (F12)

---

## Performance Testing

### Test Large Images
```bash
# Upload a 4K image (4096×4096)
# Expected: Processes in <5 seconds
```

**Automated:**
```bash
pytest tests/test_api/test_routes.py::TestIntegration -v
# Includes 4K test
```

---

## API Endpoint Testing

### Health Check
```bash
curl http://localhost:5000/api/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "version": "0.1.0-web"
}
```

### Get Templates
```bash
curl http://localhost:5000/api/templates
```

**Expected Response:**
```json
{
  "templates": ["ORD", "ORM"],
  "custom": []
}
```

### Pack Texture (using curl)
```bash
curl -X POST http://localhost:5000/api/pack \
  -F "template=ORM" \
  -F "red_channel=@/path/to/ao.png" \
  -F "green_channel=@/path/to/roughness.png" \
  -F "blue_channel=@/path/to/metallic.png" \
  -o packed.png
```

### Unpack Texture (using curl)
```bash
curl -X POST http://localhost:5000/api/unpack \
  -F "template=ORM" \
  -F "image=@packed.png" \
  | jq . # Pretty-print JSON
```

---

## Debugging

### Enable Flask Debug Mode
Edit `channelsmith/api/app.py`:
```python
app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
```

Then restart: `python -m channelsmith`

### Check Browser Console (F12)
- JavaScript errors
- Network requests (Network tab)
- API responses

### Check Terminal Output
- Flask logs show request/response info
- Python exceptions appear in terminal

### View Logs
```bash
# Flask logs to stderr (shown in terminal)
# Check for ERROR or EXCEPTION lines
```

---

## Test Report Template

Use this to document manual tests:

```
## Test Run - [Date]

### Environment
- Browser: [Chrome/Firefox/Safari/Edge] [version]
- OS: [Windows/Mac/Linux]
- Python: [version]
- Flask: [version]

### Pack Workflow
- [ ] Upload red channel: PASS/FAIL
- [ ] Upload green channel: PASS/FAIL
- [ ] Upload blue channel: PASS/FAIL
- [ ] Pack button works: PASS/FAIL
- [ ] Download works: PASS/FAIL

### Unpack Workflow
- [ ] Upload packed image: PASS/FAIL
- [ ] Select template: PASS/FAIL
- [ ] Unpack button works: PASS/FAIL
- [ ] Channels display: PASS/FAIL
- [ ] Download works: PASS/FAIL

### Notes
- [Any issues or observations]
```

---

## Continuous Testing

### Watch Tests While Developing
```bash
# Requires pytest-watch
pip install pytest-watch

# Auto-run API tests on file changes
ptw tests/test_api/
```

### Run All Tests (Before Commit)
```bash
pytest tests/ -v
# Core: 207 tests (should pass)
# API: 22 tests (should pass)
# Total: ~229 passing
```

---

## Troubleshooting

### "Port 5000 already in use"
```bash
# Kill process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Or use different port (edit __main__.py)
app.run(host='127.0.0.1', port=5001)
```

### "Module not found: channelsmith"
```bash
# Install in development mode
pip install -e .
```

### "Flask module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend not loading (blank page)
1. Check browser console (F12) for errors
2. Verify frontend files exist:
   ```bash
   ls -la channelsmith/frontend/
   ```
3. Check Flask logs for 404 errors

### Drag-drop not working
- Browser might block file operations in some cases
- Use "Click to upload" instead
- Or test in a different browser

---

## Success Criteria ✓

All tests passing:
- [ ] `pytest tests/test_api/ -v` → 22 passed
- [ ] Manual Pack workflow → Files download correctly
- [ ] Manual Unpack workflow → Channels extract correctly
- [ ] Roundtrip test → Packed → Unpacked → Matches original
- [ ] Different sizes → Normalizes correctly
- [ ] Error handling → Shows user-friendly messages
- [ ] Browser compatibility → Works on Chrome, Firefox, Safari, Edge

---

## Next Steps

After testing and validation:
1. Create GitHub release
2. Update documentation
3. Announce new web UI
4. Gather user feedback
5. Plan Phase 2 features (batch processing, templates editor, etc.)
