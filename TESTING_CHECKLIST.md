# ChannelSmith Web UI - Testing Checklist ✅

Quick checklist for verifying the new web UI works correctly.

---

## 🟢 Pre-Test Setup

### Install & Launch (< 2 minutes)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch web UI
python -m channelsmith

# 3. Browser opens automatically at http://localhost:5000
```

### Check Terminal Output
Look for these messages:
```
Starting ChannelSmith Web UI v0.1.0
Starting Flask development server...
ChannelSmith Web UI: http://localhost:5000
Press Ctrl+C to stop
```

---

## 🟢 Step 1: Verify Web UI Loads

- [ ] Browser opens automatically
- [ ] URL shows `http://localhost:5000`
- [ ] Page title is "ChannelSmith - Texture Channel Packer"
- [ ] Dark theme visible (#1e1e1e background, teal header)
- [ ] Two tabs visible: "Pack Channels" and "Unpack Texture"

---

## 🟢 Step 2: Test Pack Workflow

### 2.1 Interface Check
- [ ] "Pack Channels" tab is active
- [ ] Template dropdown shows "ORM" (default)
- [ ] 4 upload zones visible:
  - [ ] Red Channel (Ambient Occlusion)
  - [ ] Green Channel (Roughness)
  - [ ] Blue Channel (Metallic)
  - [ ] Alpha Channel (Optional)
- [ ] Preview section shows 4 canvas areas
- [ ] "Pack Texture" button visible and clickable

### 2.2 Upload Test
- [ ] Click Red Channel upload zone
- [ ] Select an image file from your computer
- [ ] Preview updates showing the uploaded image
- [ ] Repeat for Green and Blue channels
- [ ] Leave Alpha empty (to test defaults)

### 2.3 Pack Test
- [ ] Click "Pack Texture" button
- [ ] See "Packing texture..." message
- [ ] Success notification appears
- [ ] Packed result displays in preview area
- [ ] "📥 Download Packed Image" button appears

### 2.4 Download Test
- [ ] Click "📥 Download Packed Image"
- [ ] File downloads as `channelsmith_packed_orm.png`
- [ ] File opens in image viewer (RGB format)

---

## 🟢 Step 3: Test Unpack Workflow

### 3.1 Switch Tab
- [ ] Click "Unpack Texture" tab
- [ ] Interface changes to unpack view
- [ ] Template dropdown shows "ORM"
- [ ] Upload zone for packed image

### 3.2 Upload Packed Image
- [ ] Click upload zone
- [ ] Select the `channelsmith_packed_orm.png` file from Step 2.4
- [ ] File loads successfully

### 3.3 Unpack Test
- [ ] Click "Unpack Texture" button
- [ ] See "Unpacking texture..." message
- [ ] Success notification appears
- [ ] 3 channel cards appear:
  - [ ] Ambient Occlusion
  - [ ] Roughness
  - [ ] Metallic

### 3.4 Download Channels
- [ ] Each channel shows a preview image
- [ ] Each channel has a "📥 Download" button
- [ ] Click download on one channel
- [ ] File downloads as `channelsmith_ambient_occlusion_orm.png`

---

## 🟢 Step 4: Test Edge Cases

### 4.1 Test with Missing Channels
1. [ ] Go back to Pack tab
2. [ ] Upload ONLY Red channel
3. [ ] Leave Green, Blue, Alpha empty
4. [ ] Click "Pack Texture"
5. [ ] **Expected:** Succeeds with default values (not error)
6. [ ] Green channel shows mid-gray (0.5)
7. [ ] Blue channel shows black (0.0)

### 4.2 Test Different Image Sizes
1. [ ] Upload Red: 256×256 image
2. [ ] Upload Green: 512×512 image
3. [ ] Upload Blue: 1024×1024 image
4. [ ] Pack texture
5. [ ] **Expected:** Normalizes to 1024×1024

### 4.3 Test Template Switch
1. [ ] Change template to "ORD"
2. [ ] Upload 3 images
3. [ ] Pack
4. [ ] Unpack with "ORD" template
5. [ ] **Expected:** Blue channel shows "Displacement" (not "Metallic")

---

## 🟢 Step 5: Test Error Handling

### 5.1 Invalid File
- [ ] Try uploading a `.txt` file to Red channel
- [ ] **Expected:** Error message appears (user-friendly)
- [ ] Upload zone doesn't break

### 5.2 Try Invalid Template
- Use browser dev tools to send invalid template
- [ ] **Expected:** API returns 400 error with message

### 5.3 Large Image
- [ ] Upload 4K image (4096×4096)
- [ ] Processing should complete in < 5 seconds
- [ ] **Expected:** Success

---

## 🟢 Step 6: Test Browser Features

### 6.1 Drag-Drop
- [ ] Try dragging an image file to upload zone
- [ ] **Expected:** Zone highlights, file uploads

### 6.2 Notifications
- [ ] Success messages appear after operations
- [ ] Auto-dismiss after 3-5 seconds
- [ ] Error messages stay until dismissed

### 6.3 Responsive Design
- [ ] Press F12 (Developer Tools)
- [ ] Click responsive design mode (Ctrl+Shift+M)
- [ ] Test at different screen widths:
  - [ ] Mobile (375px)
  - [ ] Tablet (768px)
  - [ ] Desktop (1920px)

### 6.4 Console Check
- [ ] Press F12 (Developer Tools)
- [ ] Click "Console" tab
- [ ] **Expected:** No red error messages
- [ ] Network tab shows successful API calls

---

## 🟢 Step 7: Run Automated Tests

### 7.1 API Tests
```bash
pytest tests/test_api/ -v
```

**Expected Output:**
```
test_health_check_returns_ok PASSED
test_get_templates_returns_list PASSED
test_pack_with_orm_template PASSED
test_unpack_orm_template PASSED
...
======================== 22 passed in 0.49s =========================
```

- [ ] All 22 tests pass
- [ ] No failures or errors
- [ ] Execution time < 1 second

### 7.2 Core Tests
```bash
pytest tests/test_core/ -q
```

**Expected Output:**
```
207 passed in 1.09s
```

- [ ] All 207 tests still pass
- [ ] No regressions
- [ ] Same count as before refactor

### 7.3 All Tests
```bash
pytest tests/test_api/ tests/test_core/ -q
```

**Expected Output:**
```
229 passed in ~2s
```

- [ ] 229 total tests passing
- [ ] 22 API + 207 Core
- [ ] Zero failures

---

## 🟢 Step 8: API Testing (Advanced)

### 8.1 Health Check
```bash
curl http://localhost:5000/api/health
```

**Expected Response:**
```json
{"status":"ok","version":"0.1.0-web"}
```

- [ ] Status code: 200
- [ ] JSON response valid

### 8.2 Get Templates
```bash
curl http://localhost:5000/api/templates
```

**Expected Response:**
```json
{"templates":["ORD","ORM"],"custom":[]}
```

- [ ] Lists both ORM and ORD
- [ ] Valid JSON

### 8.3 Check Logs
Terminal should show:
```
127.0.0.1 - - [Date Time] "GET /api/health HTTP/1.1" 200 -
127.0.0.1 - - [Date Time] "GET /api/templates HTTP/1.1" 200 -
```

- [ ] No ERROR messages
- [ ] All requests return 200 status

---

## 🟢 Step 9: Test Legacy GUI (Backward Compatibility)

### 9.1 Launch Legacy GUI
```bash
python -m channelsmith --gui
```

- [ ] Tkinter window opens
- [ ] Pack tab visible
- [ ] Unpack tab visible
- [ ] All buttons work (no crashes)

### 9.2 Test Basic Operation
- [ ] Load an image
- [ ] Pack operation works
- [ ] Save result
- [ ] **Expected:** No errors, backward compatible

---

## 🟢 Final Checks

### Performance
- [ ] Web UI loads in < 2 seconds
- [ ] Pack operation completes in < 5 seconds
- [ ] Unpack operation completes in < 5 seconds
- [ ] Large images (4K) handled gracefully

### Browser Compatibility
Test on available browsers:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (if available)
- [ ] Edge (if available)

### Documentation
- [ ] README.md updated
- [ ] WEB_UI_TESTING.md available
- [ ] QUICKSTART.md available
- [ ] REFACTOR_SUMMARY.md available

---

## ✅ Success Criteria - All Passed?

- [ ] Web UI loads and displays correctly
- [ ] Pack workflow works end-to-end
- [ ] Unpack workflow works end-to-end
- [ ] 22 API tests passing
- [ ] 207 core tests passing (zero regressions)
- [ ] Error handling works
- [ ] Browser console clean (no errors)
- [ ] API endpoints respond correctly
- [ ] Legacy GUI still works
- [ ] Documentation complete

---

## 🎯 Summary

If all checkboxes are marked ✅, then:

✨ **The Web UI MVP is working perfectly!**

### What You've Verified
- ✅ Flask REST API fully functional (5 endpoints)
- ✅ Web UI renders and responds correctly
- ✅ Pack/Unpack workflows complete
- ✅ All tests passing (229 total)
- ✅ Zero regressions in core engine
- ✅ Error handling works
- ✅ Backward compatible with legacy GUI

### Next Steps
1. Share feedback on user experience
2. Test with real texture files
3. Plan advanced features (batch, custom templates UI)
4. Consider performance optimizations
5. Plan public release

---

**Status:** ✅ Ready for Production
**Date:** February 8, 2026
**Version:** 0.1.0-web-mvp
