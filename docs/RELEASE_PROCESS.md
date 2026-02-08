# ChannelSmith Release Process

This document describes the step-by-step process for releasing a new version of ChannelSmith. **Only maintainers should perform releases.**

---

## Pre-Release Checklist

Before starting the release process, ensure:

- [ ] All features are complete and merged to `dev` branch
- [ ] All tests pass: `pytest` (expect 229+ tests passing)
- [ ] No uncommitted changes: `git status` (should be clean)
- [ ] Linting passes: `black channelsmith/` and `pylint channelsmith/`
- [ ] Documentation is up-to-date
- [ ] All pull requests are reviewed and merged

---

## Step 1: Update Version Number

1. **Edit `channelsmith/__init__.py`:**
   ```python
   __version__ = "0.2.0"  # Update to new version
   ```

2. **Verify version is imported correctly:**
   ```bash
   python -m channelsmith --version
   # Expected output: ChannelSmith 0.2.0
   ```

---

## Step 2: Update CHANGELOG.md

1. **Add a new section at the top for your version:**
   ```markdown
   ## [0.2.0] - 2026-02-09

   ### Added
   - List new features here

   ### Changed
   - List changes here

   ### Fixed
   - List bug fixes here
   ```

2. **Update comparison links at bottom:**
   ```markdown
   [0.2.0]: https://github.com/yourusername/channelsmith/compare/v0.1.0...v0.2.0
   ```

3. **Save and verify formatting is correct**

---

## Step 3: Commit Changes

1. **Stage version and changelog files:**
   ```bash
   git add channelsmith/__init__.py CHANGELOG.md
   ```

2. **Create a commit:**
   ```bash
   git commit -m "chore: release v0.2.0"
   ```

3. **Verify commit:**
   ```bash
   git log --oneline -1
   # Expected: chore: release v0.2.0
   ```

---

## Step 4: Merge to Main Branch

1. **Switch to main branch:**
   ```bash
   git checkout main
   ```

2. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

3. **Merge dev branch:**
   ```bash
   git merge dev
   ```

4. **Push to remote:**
   ```bash
   git push origin main
   ```

---

## Step 5: Create Git Tag

The git tag is crucial—it triggers GitHub Actions to build executables.

1. **Create annotated tag:**
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0 - Local Distribution"
   ```

2. **Verify tag was created:**
   ```bash
   git tag -l
   git show v0.2.0
   ```

3. **Push tag to remote:**
   ```bash
   git push origin v0.2.0
   ```

---

## Step 6: Monitor GitHub Actions Build

1. **Go to GitHub repository** → **Actions** tab
2. **You should see "Build and Release" workflow running**
3. **Wait for all three jobs to complete:**
   - ✅ Build Windows Executable
   - ✅ Build macOS Executable
   - ✅ Build Linux Executable
   - ✅ Create GitHub Release

**Typical build time:** 10-15 minutes

### If build fails:
1. Check the workflow logs for error details
2. Fix the issue in code
3. Create a new patch version (e.g., v0.2.1)
4. Repeat from Step 1

---

## Step 7: Verify GitHub Release

1. **Go to GitHub** → **Releases** tab
2. **You should see the new release created:**
   - Tag: v0.2.0
   - Release title: (auto-generated from tag)
   - Assets: 3 files
     - ChannelSmith-Windows.zip
     - ChannelSmith-macOS.tar.gz
     - ChannelSmith-Linux.tar.gz

3. **Release notes should be auto-populated from CHANGELOG.md**

---

## Step 8: Test Downloaded Executables

Download and test each executable on its native platform:

### Windows
```bash
# 1. Download ChannelSmith-Windows.zip
# 2. Extract to temp directory
# 3. Run ChannelSmith.exe
# 4. Verify:
#    - Browser opens to http://localhost:5000
#    - Web UI loads correctly
#    - Pack workflow works (upload, pack, download)
#    - Unpack workflow works (upload, unpack, download)
```

### macOS
```bash
# 1. Download ChannelSmith-macOS.tar.gz
# 2. Extract: tar xzf ChannelSmith-macOS.tar.gz
# 3. Run: ./ChannelSmith-macOS/ChannelSmith
# 4. Verify same as Windows
```

### Linux
```bash
# 1. Download ChannelSmith-Linux.tar.gz
# 2. Extract: tar xzf ChannelSmith-Linux.tar.gz
# 3. Run: ./ChannelSmith-Linux/ChannelSmith
# 4. Verify same as Windows
```

---

## Step 9: Update README.md Download Links

1. **Edit README.md** - Update the download section with actual release links:
   ```markdown
   | Platform | Download |
   |----------|----------|
   | Windows 10+ | [ChannelSmith-Windows.zip](https://github.com/yourusername/channelsmith/releases/download/v0.2.0/ChannelSmith-Windows.zip) |
   | macOS 12+ | [ChannelSmith-macOS.tar.gz](https://github.com/yourusername/channelsmith/releases/download/v0.2.0/ChannelSmith-macOS.tar.gz) |
   | Linux | [ChannelSmith-Linux.tar.gz](https://github.com/yourusername/channelsmith/releases/download/v0.2.0/ChannelSmith-Linux.tar.gz) |
   ```

2. **Also update version badge:**
   ```markdown
   ![Version](https://img.shields.io/badge/version-0.2.0-blue)
   ```

3. **Commit and push:**
   ```bash
   git add README.md
   git commit -m "docs: update download links for v0.2.0"
   git push origin main
   ```

---

## Step 10: Announce Release

Choose your announcement method:

### Option A: GitHub Release Page
1. Go to **Releases** tab
2. Click the newly created release
3. Click **Edit** (if needed)
4. Add release highlights at the top

### Option B: Social Media / Mailing List
Post announcement with:
- Version number (v0.2.0)
- Key improvements
- Download links (from GitHub Releases)
- Known issues (if any)

### Option C: Project Website
Update project website with new version info

---

## Common Issues and Solutions

### GitHub Actions Workflow Not Triggering

**Problem:** Tag is pushed but workflow doesn't start

**Solutions:**
1. Verify tag name matches pattern: `v*` (e.g., v0.2.0)
2. Check that workflow file exists: `.github/workflows/release.yml`
3. Verify GitHub repository has Actions enabled
4. Try pushing tag again: `git push origin v0.2.0 --force`

### Build Fails on One Platform

**Problem:** Linux build succeeds but Windows fails

**Solutions:**
1. Check workflow logs for specific error
2. Test build locally on that platform
3. Fix code/spec file
4. Create new tag for patch version: v0.2.1
5. Repeat release process

### Executable Size Unexpectedly Large

**Problem:** .exe is 100MB+ when should be ~50MB

**Solutions:**
1. Check that `excludedimports` in `.spec` includes unnecessary libraries
2. Verify `--onefile` is enabled (combines into single exe)
3. Consider using UPX compression (already enabled in spec)
4. Remove debug symbols

### Port 5000 Conflict in Testing

**Problem:** Can't test executable because port 5000 in use

**Solutions:**
1. Stop other applications using port 5000
2. Kill the process: `lsof -i :5000 | kill -9 <PID>`
3. Use different port in testing (temporarily)
4. Restart computer

---

## Rollback a Release

If a release has critical issues:

1. **Create a new patch version** (don't delete old tag):
   ```bash
   git checkout main
   git pull origin main
   # Fix the issue
   git add <files>
   git commit -m "fix: critical issue in v0.2.0"
   git tag -a v0.2.1 -m "Release v0.2.1 - Hotfix"
   git push origin main v0.2.1
   ```

2. **Delete broken release** (optional):
   ```bash
   git push origin --delete v0.2.0  # Delete tag
   # Also delete from GitHub Releases UI
   ```

3. **Update INSTALL.md and README.md** to point to new version

---

## Version Numbering

ChannelSmith uses [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0) - Breaking changes
- **MINOR** (0.X.0) - New features (backward compatible)
- **PATCH** (0.0.X) - Bug fixes

Examples:
- v0.1.0 - Web UI MVP (initial release)
- v0.2.0 - Local distribution (new feature)
- v0.2.1 - Bug fix for v0.2.0
- v1.0.0 - Production release (major milestone)

---

## Next Release Cycle

After release is complete:

1. **Merge main back to dev:**
   ```bash
   git checkout dev
   git merge main
   git push origin dev
   ```

2. **Create section in CHANGELOG.md for next version:**
   ```markdown
   ## [Unreleased]

   ### Planned
   - Feature 1
   - Feature 2
   ```

3. **Update version to next development version** (optional):
   ```
   __version__ = "0.3.0-dev"
   ```

4. **Continue development on dev branch**

---

## Release Checklist Template

Use this checklist for each release:

```markdown
## Release v0.2.0

- [ ] Update version in channelsmith/__init__.py
- [ ] Update CHANGELOG.md
- [ ] Run pytest (all passing)
- [ ] Run black and pylint
- [ ] Merge dev to main
- [ ] Create git tag: git tag -a v0.2.0
- [ ] Push tag: git push origin v0.2.0
- [ ] Monitor GitHub Actions workflow
- [ ] Download and test all 3 executables
- [ ] Update README.md with download links
- [ ] Verify GitHub Release page
- [ ] Announce release
- [ ] Merge main back to dev
```

---

**For questions, see [CONTRIBUTING.md](../CONTRIBUTING.md) or check GitHub Issues.**
