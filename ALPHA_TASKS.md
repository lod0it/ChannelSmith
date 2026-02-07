# ChannelSmith - Alpha Phase Tasks

**Phase:** Alpha (No GUI)  
**Goal:** Core packing/unpacking engine functional and tested  
**Duration:** 2-3 weeks  

---

## 🎯 Success Criteria

- [ ] Can pack textures programmatically via Python API
- [ ] Can unpack existing packed textures and extract channels
- [ ] Can repack with different templates (ORM → ORD)
- [ ] All validation logic works correctly
- [ ] Produces correct output for ORM and ORD templates
- [ ] Handles edge cases (mismatches, missing textures)
- [ ] Test coverage >80%
- [ ] All tests passing

---

## 📝 Implementation Checklist

### Phase 1.1: Foundation (Week 1)

#### Task 1: ChannelMap Class
**File:** `channelsmith/core/channel_map.py`

- [ ] Create `ChannelMap` class
- [ ] Add attributes: `map_type`, `default_value`, `description`
- [ ] Implement `__init__` method with type hints
- [ ] Implement `__repr__` for debugging
- [ ] Add validation (default_value must be 0.0-1.0)
- [ ] Write docstrings (Google style)

**Predefined channel types to support:**
- [ ] `ambient_occlusion` (default: 1.0)
- [ ] `roughness` (default: 0.5)
- [ ] `metallic` (default: 0.0)
- [ ] `displacement` (default: 0.5)
- [ ] `height` (default: 0.5)
- [ ] `opacity` (default: 1.0)
- [ ] `alpha` (default: 1.0)

**Tests:**
- [ ] Test ChannelMap creation
- [ ] Test default value validation
- [ ] Test string representation

**Estimated time:** 2-3 hours

---

#### Task 2: PackingTemplate Class
**File:** `channelsmith/core/packing_template.py`

- [ ] Create `PackingTemplate` class
- [ ] Add attributes: `name`, `description`, `channels` (dict)
- [ ] Implement `__init__` method
- [ ] Implement method to get channel by key (R/G/B/A)
- [ ] Implement method to check if channel is used
- [ ] Implement `is_rgba()` method (checks if alpha channel used)
- [ ] Write docstrings

**Tests:**
- [ ] Test template creation
- [ ] Test channel retrieval
- [ ] Test RGBA detection
- [ ] Test empty template handling

**Estimated time:** 2-3 hours

---

#### Task 3: Template JSON Loader
**File:** `channelsmith/templates/template_loader.py`

- [ ] Implement `load_template(path: str) -> PackingTemplate`
- [ ] Implement `save_template(template: PackingTemplate, path: str)`
- [ ] Add JSON validation
- [ ] Handle file not found errors
- [ ] Handle malformed JSON errors
- [ ] Write docstrings

**Create predefined templates:**

**File:** `channelsmith/templates/orm.json`
- [ ] Create ORM template JSON (Occlusion-Roughness-Metallic)

**File:** `channelsmith/templates/ord.json`
- [ ] Create ORD template JSON (Occlusion-Roughness-Displacement)

**Tests:**
- [ ] Test loading valid template
- [ ] Test loading invalid JSON (should raise error)
- [ ] Test loading non-existent file (should raise error)
- [ ] Test saving template
- [ ] Test round-trip (save then load)

**Estimated time:** 3-4 hours

---

### Phase 1.2: Core Engine (Week 1-2)

#### Task 4: Image Utilities
**File:** `channelsmith/utils/image_utils.py`

- [ ] Implement `load_image(path: str) -> Image.Image`
- [ ] Implement `save_image(image: Image.Image, path: str, format: str)`
- [ ] Implement `to_grayscale(image: Image.Image) -> np.ndarray`
- [ ] Implement `from_grayscale(array: np.ndarray) -> Image.Image`
- [ ] Add error handling for corrupted images
- [ ] Write docstrings

**Tests:**
- [ ] Test loading supported formats (PNG, TGA, JPEG, TIFF)
- [ ] Test loading corrupted image (should raise error)
- [ ] Test grayscale conversion
- [ ] Test round-trip conversions

**Estimated time:** 2-3 hours

---

#### Task 5: Validation Layer
**File:** `channelsmith/core/validator.py`

- [ ] Implement `check_resolution_match(images: List[Image.Image]) -> bool`
- [ ] Implement `get_max_resolution(images: List[Image.Image]) -> Tuple[int, int]`
- [ ] Implement `validate_channel_data(data: np.ndarray)`
- [ ] Create custom exceptions:
  - [ ] `ResolutionMismatchError`
  - [ ] `InvalidChannelDataError`
  - [ ] `TemplateValidationError`
- [ ] Write docstrings

**Tests:**
- [ ] Test matching resolutions
- [ ] Test mismatched resolutions
- [ ] Test max resolution detection
- [ ] Test invalid channel data

**Estimated time:** 2-3 hours

---

#### Task 6: Packing Engine
**File:** `channelsmith/core/packing_engine.py`

- [ ] Implement `normalize_resolution(arrays: List[np.ndarray], target_size: Tuple) -> List[np.ndarray]`
  - [ ] Use Pillow's BILINEAR resampling
  
- [ ] Implement `pack_channels(r, g, b, a=None) -> Image.Image`
  - [ ] Validate input arrays
  - [ ] Check resolution match
  - [ ] Stack channels using NumPy
  - [ ] Create PIL Image from array
  - [ ] Return RGB or RGBA based on alpha presence

- [ ] Implement `pack_texture_from_template(textures: Dict, template: PackingTemplate) -> Image.Image`
  - [ ] Load textures for each channel
  - [ ] Apply default values for missing channels
  - [ ] Call pack_channels
  - [ ] Return packed image

- [ ] Write comprehensive docstrings

**Tests:**
- [ ] Test packing 3 channels (RGB output)
- [ ] Test packing 4 channels (RGBA output)
- [ ] Test with mismatched resolutions (should normalize)
- [ ] Test with missing channels (should use defaults)
- [ ] Test ORM template packing
- [ ] Test ORD template packing
- [ ] Test edge cases (1-channel, empty channels)

**Estimated time:** 4-6 hours

---

#### Task 7: Unpacking Engine
**File:** `channelsmith/core/unpacking_engine.py`

- [ ] Implement `extract_channel(image: Image.Image, channel: str) -> np.ndarray`
  - [ ] Convert image to NumPy array
  - [ ] Extract R/G/B/A channel using array slicing
  - [ ] Return grayscale array

- [ ] Implement `unpack_texture(image: Image.Image, template: PackingTemplate) -> Dict[str, np.ndarray]`
  - [ ] Validate image matches template expectations
  - [ ] Extract each channel defined in template
  - [ ] Return dictionary mapping channel names to arrays

- [ ] Write comprehensive docstrings

**Tests:**
- [ ] Test extracting R channel
- [ ] Test extracting G channel
- [ ] Test extracting B channel
- [ ] Test extracting A channel (if present)
- [ ] Test unpacking with ORM template
- [ ] Test unpacking with ORD template
- [ ] Test unpacking RGB image (no alpha)
- [ ] Test unpacking RGBA image

**Estimated time:** 3-4 hours

---

### Phase 1.3: Integration & Testing (Week 2-3)

#### Task 8: Integration Tests
**File:** `tests/test_integration/test_workflows.py`

**Workflow 1: Pack Textures**
- [ ] Test loading 3 separate grayscale images
- [ ] Test packing with ORM template
- [ ] Test output is valid RGB image
- [ ] Test output resolution is correct

**Workflow 2: Unpack Textures**
- [ ] Test loading packed ORM texture
- [ ] Test unpacking with ORM template
- [ ] Test extracted channels match original data

**Workflow 3: Repack (ORM → ORD)**
- [ ] Test unpacking ORM texture
- [ ] Test loading new displacement map
- [ ] Test packing with ORD template
- [ ] Test output is valid

**Workflow 4: Selective Channel Update**
- [ ] Test unpacking existing texture
- [ ] Test replacing one channel
- [ ] Test repacking with same template
- [ ] Test output has updated channel

**Workflow 5: Resolution Mismatch Handling**
- [ ] Test packing with mismatched resolutions
- [ ] Test automatic upscaling occurs
- [ ] Test output resolution is maximum of inputs

**Estimated time:** 4-6 hours

---

#### Task 9: Edge Cases & Error Handling
**File:** `tests/test_core/test_edge_cases.py`

- [ ] Test packing with all channels missing (should use defaults)
- [ ] Test packing single channel
- [ ] Test packing with very small images (1x1)
- [ ] Test packing with maximum size (4096x4096)
- [ ] Test invalid template (malformed JSON)
- [ ] Test corrupted image loading
- [ ] Test unsupported image format
- [ ] Test grayscale input when color expected

**Estimated time:** 3-4 hours

---

#### Task 10: Documentation & Examples
**File:** `examples/alpha_demo.py`

Create a demonstration script showing all capabilities:

- [ ] Example 1: Pack textures with ORM template
- [ ] Example 2: Unpack existing ORM texture
- [ ] Example 3: Repack ORM to ORD
- [ ] Example 4: Use custom default values
- [ ] Add comments explaining each step
- [ ] Add print statements showing progress

**File:** `channelsmith/README.md`

- [ ] Add usage examples
- [ ] Document all public APIs
- [ ] Add troubleshooting section

**Estimated time:** 2-3 hours

---

#### Task 11: Code Quality Pass

- [ ] Run black on entire codebase: `black channelsmith/`
- [ ] Run pylint: `pylint channelsmith/`
- [ ] Fix any critical issues
- [ ] Ensure all functions have docstrings
- [ ] Ensure all functions have type hints
- [ ] Remove any debug print statements
- [ ] Add logging instead of prints

**Estimated time:** 2-3 hours

---

#### Task 12: Final Testing & Validation

- [ ] Run full test suite: `pytest`
- [ ] Check test coverage: `pytest --cov=channelsmith --cov-report=html`
- [ ] Ensure coverage >80%
- [ ] Fix any failing tests
- [ ] Test on fresh Python environment
- [ ] Verify all dependencies in requirements.txt

**Estimated time:** 2-3 hours

---

## 📊 Progress Tracking

### Completion Status

| Task | Status | Time Spent | Notes |
|------|--------|------------|-------|
| 1. ChannelMap | ⬜ Not Started | - | - |
| 2. PackingTemplate | ⬜ Not Started | - | - |
| 3. Template Loader | ⬜ Not Started | - | - |
| 4. Image Utils | ⬜ Not Started | - | - |
| 5. Validator | ⬜ Not Started | - | - |
| 6. Packing Engine | ⬜ Not Started | - | - |
| 7. Unpacking Engine | ⬜ Not Started | - | - |
| 8. Integration Tests | ⬜ Not Started | - | - |
| 9. Edge Cases | ⬜ Not Started | - | - |
| 10. Documentation | ⬜ Not Started | - | - |
| 11. Code Quality | ⬜ Not Started | - | - |
| 12. Final Testing | ⬜ Not Started | - | - |

**Legend:**
- ⬜ Not Started
- 🟡 In Progress
- ✅ Complete
- ❌ Blocked

---

## 🎓 Implementation Tips

### Starting Order
Follow this sequence for optimal dependency management:

1. **Foundation** (Tasks 1-3): These have no dependencies
2. **Utilities** (Task 4): Needed by both engines
3. **Validation** (Task 5): Needed by engines
4. **Engines** (Tasks 6-7): Core functionality
5. **Testing** (Tasks 8-9): Verify everything works
6. **Polish** (Tasks 10-12): Make it production-ready

### When Stuck
1. Check `CLAUDE.md` for architecture details
2. Check `docs/MVP_Documentation.md` for specifications
3. Look at test examples for expected behavior
4. Write the test first (TDD approach)

### Git Commits
Commit after each task completion:
```bash
git add .
git commit -m "feat(core): implement ChannelMap class with tests"
```

---

## 🚀 Ready for Beta?

Before moving to Beta (GUI phase), ensure:

- [ ] All tasks above completed
- [ ] All tests passing
- [ ] Code coverage >80%
- [ ] Can pack/unpack via Python API
- [ ] Can convert between templates
- [ ] Documentation complete
- [ ] Code reviewed and cleaned

**When ready:**
```bash
# Merge to main
git checkout main
git merge dev
git tag -a v0.1.0-alpha -m "Alpha complete - core engine functional"
git push origin main --tags

# Continue on dev for Beta
git checkout dev
```

---

**Alpha Phase Complete! 🎉**

Next: Beta Phase - GUI Implementation
