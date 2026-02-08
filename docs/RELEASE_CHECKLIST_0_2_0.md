# ChannelSmith v0.2.0 Release Checklist

**Version:** 0.2.0 - Local Distribution
**Date:** 2026-02-09
**Status:** In Progress ⚙️

---

## Pre-Release Verification

### Code Quality
- [ ] All 229 core tests passing: `pytest` (expect 229+ pass)
- [ ] No linting errors: `black channelsmith/` and `pylint channelsmith/`
- [ ] Code coverage maintained (>85%)
- [ ] No uncommitted changes: `git status` (clean)
- [ ] No warnings or deprecations in logs

### Feature Completeness

#### Phase 1: Cross-Platform Launcher Scripts ✅
- [x] `launch_web_ui.sh` created for macOS/Linux
- [x] `launch_simple.sh` created for quick launch
- [x] `install.sh` created for first-time setup
- [x] Scripts have executable markers in place
- [x] Scripts include proper error handling and colored output
- [x] Browser auto-opens on launch

#### Phase 2: Documentation & Versioning ✅
- [x] Version constant in `channelsmith/__init__.py` = "0.2.0"
- [x] `__main__.py` imports and displays version dynamically
- [x] `--version` flag works: `python -m channelsmith --version`
- [x] CHANGELOG.md created with v0.2.0 section
- [x] INSTALL.md created (3-tier installation guide)
- [x] CONTRIBUTING.md created (contribution guidelines)
- [x] README.md updated with badges, download section, documentation links
- [x] All documentation links verified and working

#### Phase 3: PyInstaller Configuration ✅
- [x] `channelsmith.spec` created with correct data files
- [x] `build_exe.bat` created for Windows builds
- [x] `build_exe.sh` created for macOS/Linux builds
- [x] Spec file includes all frontend assets
- [x] Spec file includes all template files
- [x] Spec file includes cs_wiki.md
- [x] Hidden imports configured correctly
- [x] One-file executable mode enabled

#### Phase 4: GitHub Actions CI/CD ✅
- [x] `.github/workflows/release.yml` created with 4 jobs:
  - Windows build job
  - macOS build job
  - Linux build job
  - GitHub Release creation job
- [x] Workflow triggers on version tags (v*)
- [x] Build scripts create proper archives
- [x] Release creation includes CHANGELOG content
- [x] `docs/RELEASE_PROCESS.md` created with detailed steps
- [x] This checklist (`RELEASE_CHECKLIST_0_2_0.md`) created

---

## Build Verification

### Local Build Testing

#### Windows Build
- [ ] Run `build_exe.bat` successfully
- [ ] Check `dist/ChannelSmith.exe` created
- [ ] Verify file size is ~40-50MB
- [ ] Test executable launches without errors
- [ ] Browser opens to http://localhost:5000
- [ ] Web UI loads and renders correctly

#### macOS Build
- [ ] Run `./build_exe.sh` successfully
- [ ] Check `dist/ChannelSmith` created
- [ ] Verify file size is ~40-50MB
- [ ] Test executable launches without errors
- [ ] Browser opens to http://localhost:5000
- [ ] Web UI loads and renders correctly

#### Linux Build
- [ ] Run `./build_exe.sh` successfully
- [ ] Check `dist/ChannelSmith` created
- [ ] Verify file size is ~40-50MB
- [ ] Test executable launches without errors
- [ ] Browser opens to http://localhost:5000
- [ ] Web UI loads and renders correctly

### GitHub Actions Verification

After pushing v0.2.0 tag, verify automated build:

- [ ] GitHub Actions workflow starts automatically
- [ ] All 3 build jobs run in parallel without errors
- [ ] Each job completes in <15 minutes
- [ ] Release creation job succeeds
- [ ] GitHub Release page is created with all assets

---

## Functional Testing

### Pack Workflow (All Platforms)
- [ ] Open http://localhost:5000
- [ ] Select "ORM" preset
- [ ] Upload 3 grayscale images (256x256 PNG) for R/G/B channels
- [ ] Click "Pack Texture" button
- [ ] Verify packed texture preview appears
- [ ] Download packed texture
- [ ] Verify downloaded file is valid PNG

### Unpack Workflow (All Platforms)
- [ ] Switch to "Unpack Texture" mode
- [ ] Upload previously packed texture
- [ ] Select correct preset
- [ ] Click "Unpack Texture" button
- [ ] Verify all channels appear in preview
- [ ] Download extracted channels
- [ ] Verify downloaded files are valid PNGs

### Template Switching (All Platforms)
- [ ] Test with ORM preset (Red=AO, Green=Roughness, Blue=Metallic)
- [ ] Test with ORD preset (Red=AO, Green=Roughness, Blue=Displacement)
- [ ] Test with Free preset (generic R/G/B/A)
- [ ] Verify labels update correctly for each template

### Browser Compatibility
- [ ] Test in Chrome/Edge (Windows)
- [ ] Test in Safari (macOS, if available)
- [ ] Test in Firefox (all platforms)
- [ ] Verify responsive design on mobile viewport

### Edge Cases
- [ ] Upload mismatched resolution images (should handle gracefully)
- [ ] Upload non-grayscale image to RGB channel (should convert)
- [ ] Unpack non-packed texture (should show error)
- [ ] Close info panel without error
- [ ] Rapid button clicks (should queue operations)

---

## Cross-Platform Testing

### Windows 10/11
- [ ] Download ChannelSmith-Windows.zip from release
- [ ] Extract to temp directory
- [ ] Run ChannelSmith.exe (double-click)
- [ ] Verify no Python errors or warnings
- [ ] Test both pack and unpack workflows
- [ ] Verify port 5000 availability check works

### macOS 12+
- [ ] Download ChannelSmith-macOS.tar.gz from release
- [ ] Extract: `tar xzf ChannelSmith-macOS.tar.gz`
- [ ] Run executable: `./ChannelSmith-macOS/ChannelSmith`
- [ ] Verify macOS allows running (may need Gatekeeper approval)
- [ ] Test both pack and unpack workflows
- [ ] Verify browser auto-opens correctly

### Linux (Ubuntu 20.04+)
- [ ] Download ChannelSmith-Linux.tar.gz from release
- [ ] Extract: `tar xzf ChannelSmith-Linux.tar.gz`
- [ ] Run executable: `./ChannelSmith-Linux/ChannelSmith`
- [ ] Verify executable runs without glibc warnings
- [ ] Test both pack and unpack workflows
- [ ] Verify browser auto-opens correctly

---

## Documentation Verification

- [ ] INSTALL.md covers all 3 installation methods clearly
- [ ] INSTALL.md includes troubleshooting section
- [ ] INSTALL.md has FAQ section
- [ ] CONTRIBUTING.md explains how to report bugs
- [ ] CONTRIBUTING.md explains code standards
- [ ] CHANGELOG.md has complete v0.2.0 entry
- [ ] README.md download section has correct links
- [ ] README.md badges are accurate (v0.2.0, beta status)
- [ ] All internal links in documentation work
- [ ] cs_wiki.md displays correctly in web UI info panel

---

## Deployment Checklist

### Version Management
- [ ] Update `channelsmith/__init__.py`: `__version__ = "0.2.0"`
- [ ] Update `CHANGELOG.md` with v0.2.0 section
- [ ] Verify `python -m channelsmith --version` shows 0.2.0

### Git Operations
- [ ] All changes committed on `dev` branch
- [ ] `dev` branch is up to date with `main`
- [ ] Run all tests one final time: `pytest` (expect 229+ pass)
- [ ] Merge `dev` → `main`: `git checkout main && git merge dev && git push origin main`
- [ ] Create annotated tag: `git tag -a v0.2.0 -m "Release v0.2.0 - Local Distribution"`
- [ ] Push tag: `git push origin v0.2.0`
- [ ] Verify tag pushed: `git ls-remote origin | grep v0.2.0`

### GitHub Actions Verification
- [ ] Go to GitHub Actions tab
- [ ] Verify "Build and Release" workflow is running
- [ ] Wait for all jobs to complete (10-15 minutes)
- [ ] Check that workflow completed successfully
- [ ] Verify GitHub Release page created with 3 assets

### Release Assets
- [ ] ChannelSmith-Windows.zip exists and is ~50-60MB
- [ ] ChannelSmith-macOS.tar.gz exists and is ~50-60MB
- [ ] ChannelSmith-Linux.tar.gz exists and is ~50-60MB
- [ ] All 3 archives include CHANGELOG.md and README.md
- [ ] All 3 executables are extractable without errors

---

## Post-Release Tasks

### Documentation Updates
- [ ] Update README.md with actual release download links
- [ ] Update version badge in README.md to 0.2.0
- [ ] Merge `main` back to `dev` branch
- [ ] Create "Unreleased" section in CHANGELOG.md

### Announcements
- [ ] Write release announcement (if public)
- [ ] Update project website (if applicable)
- [ ] Post to social media (if applicable)
- [ ] Send to mailing list (if applicable)

### Future Planning
- [ ] Create issues for v0.3.0 features
- [ ] Update roadmap
- [ ] Plan next milestone

---

## Sign-Off

| Item | Responsible | Status | Date |
|------|-------------|--------|------|
| Code Quality | Developer | - | - |
| Build Testing | Developer | - | - |
| Functional Testing | QA/Developer | - | - |
| Cross-Platform Testing | Tester | - | - |
| Documentation | Technical Writer | - | - |
| GitHub Release | DevOps/Maintainer | - | - |

---

## Critical Verification Steps (DO NOT SKIP)

Before marking release as complete, **MUST** verify:

1. **All tests pass:** `pytest` returns ✅ pass (expect 229+)
2. **Version displays correctly:** `python -m channelsmith --version` shows `ChannelSmith 0.2.0`
3. **Tag is created and pushed:** `git tag -a v0.2.0 && git push origin v0.2.0`
4. **GitHub Actions completes:** All 3 build jobs + release job succeed
5. **Executables download:** All 3 platform archives available in GitHub Releases
6. **Executables work:** Test each platform's executable:
   - Launches without Python errors
   - Browser opens to localhost:5000
   - Pack workflow succeeds
   - Unpack workflow succeeds
7. **Download links updated:** README.md has working direct links to executables

---

## Known Issues / Workarounds

- [ ] None known at release time

---

## Version History

- **v0.1.0** (2026-02-01) - Web UI MVP
- **v0.2.0** (2026-02-09) - Local Distribution with executables
- **v0.3.0** (TBD) - TBD

---

**Ready for Release:** When all checkmarks are filled ✅
