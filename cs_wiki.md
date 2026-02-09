# ChannelSmith Wiki - Complete User Guide

Welcome to ChannelSmith! 🎨 This guide will help you master texture channel packing for your games.

---

## 🚀 Getting Started

### What is Texture Channel Packing?

Game textures often contain multiple grayscale maps stored separately:
- **Ambient Occlusion (AO)** - Shadows in crevices
- **Roughness** - How shiny/matte a surface is
- **Metallic** - How metallic a surface is
- **Displacement** - Height information

**ChannelSmith packs these into ONE RGBA image**, saving ~75% memory!

### Quick Example

Instead of loading 4 files:
```
T_example_ao.png (512KB)
T_example_roughness.png (512KB)
T_example_metallic.png (512KB)
T_example_displacement.png (512KB)
Total: 2MB
```

You get 1 packed file:
```
T_example_packed.png (512KB)
Total: 512KB ✨
```

### System Requirements

- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)
- **No installation needed!** Everything works in your browser
- **Internet connection** (for initial load only)

---

## 📦 Pack Texture Guide

**Pack** = Combine multiple grayscale textures into one RGBA image

### Step-by-Step Instructions

#### 1️⃣ **Open ChannelSmith**
- Visit http://localhost:5000 in your browser
- Look for the **"Pack Texture"** tab (it's selected by default)

#### 2️⃣ **Choose Your Preset**
The preset determines what each channel will store:

- **Free Mode** (Default) - Use ANY grayscale images, flexible packing
- **ORM** - Occlusion, Roughness, Metallic (most common for PBR)
- **ORD** - Occlusion, Roughness, Displacement (for parallax mapping)

**💡 Tip:** If you're not sure, use **Free Mode**!

#### 3️⃣ **Upload Your Channels**

For each channel you want to pack:
1. Click the upload zone OR drag & drop your image
2. See the preview appear instantly on the right
3. Repeat for other channels

**Channel Defaults (if you leave them empty):**
- **Red** → White (1.0) - Max brightness
- **Green** → Mid-Gray (0.5) - 50% brightness
- **Blue** → Black (0.0) - No brightness
- **Alpha** → White (1.0) - Fully opaque

**Example:**
- Red = Your AO texture
- Green = Your Roughness texture
- Blue = Your Metallic texture
- Alpha = (Leave empty for 1.0 default)

#### 4️⃣ **Pack It!**
- Click the big **📦 PACK** button
- Wait a moment...
- Your packed image appears on the right!

#### 5️⃣ **Download**
- Click **📥 Download Packed Image**
- Save it to your project folder
- **Done!** 🎉

### Real-World Example: ORM Preset

You have three textures for a wooden crate:
- `crate_ao.png` (dark ambient occlusion)
- `crate_roughness.png` (surface roughness)
- `crate_metallic.png` (metallic areas)

**Steps:**
1. Select **"ORM"** preset
2. Upload `crate_ao.png` to Red channel
3. Upload `crate_roughness.png` to Green channel
4. Upload `crate_metallic.png` to Blue channel
5. Click **PACK**
6. Download as `crate_orm.png`

Your game engine now uses 1 image instead of 3! ⚡

---

## 📂 Unpack Texture Guide

**Unpack** = Extract individual channels from a packed texture

### Why Unpack?

You might need to:
- Extract channels from an existing packed texture
- Convert between preset formats (ORM → ORD)
- Edit individual channels and re-pack
- Share channels with team members

### Step-by-Step Instructions

#### 1️⃣ **Switch to Unpack Tab**
- Click the **"Unpack Texture"** tab at the top

#### 2️⃣ **Upload Your Packed Texture**
- Click the upload zone or drag your packed image
- See it preview on the right

#### 3️⃣ **Select the Correct Preset**
- Choose the preset used when this texture was packed
- **This is important!** If you use the wrong preset, channels will be wrong

**Example:** If you packed with ORM, unpack with ORM ✓

#### 4️⃣ **Unpack It!**
- Click the big **📂 UNPACK** button
- Wait a moment...
- All channels appear below!

#### 5️⃣ **Download Channels**
- Click **📥** next to each channel to download it individually
- Or download them all if available
- Save to your project folder

### Alpha Channel Auto-Extraction

When you upload an **RGBA texture** (image with alpha channel), ChannelSmith automatically extracts the alpha channel even if your selected preset doesn't define it.

**Example Use Case:**
- You have a BaseColor texture with RGB in the color channels and Roughness in the alpha channel
- You select the **ORM** preset (which only defines R, G, B)
- ChannelSmith will extract:
  - R → Ambient Occlusion (from template)
  - G → Roughness (from template)
  - B → Metallic (from template)
  - A → Alpha (auto-extracted, not in template)

This means you can preview and download the alpha channel even when using RGB-only presets. Perfect for game engines that pack data this way!

**Note:** If you upload an RGB texture (no alpha), only the template-defined channels are extracted (3 channels).

### Example: Converting Formats

You have an **ORM** packed texture, but need **ORD** instead:

**Steps:**
1. Click **Unpack Texture** tab
2. Upload your ORM packed texture
3. Select **"ORM"** preset
4. Click UNPACK
5. Download all three channel images
6. Switch to **Pack Texture** tab
7. Select **"ORD"** preset
8. Upload: Red (your AO), Green (your Roughness), Blue (your Displacement)
9. Click PACK
10. Download your new ORD texture

**Done!** Format converted! 🔄

---

## 🎨 Template Presets Explained

Each preset defines what each channel stores. Choose based on your needs:

### 1. Free Mode 🎉 (Default)
```
Red Channel → Any grayscale texture
Green Channel → Any grayscale texture
Blue Channel → Any grayscale texture
Alpha Channel → Any grayscale texture (optional)
```

**Best for:**
- Experimenting with packing
- Custom texture combinations
- Quick testing
- When you want complete control

**Default values if empty:**
- Red: White (1.0)
- Green: Mid-Gray (0.5)
- Blue: Black (0.0)
- Alpha: White (1.0)

---

### 2. ORM 🔧 (Occlusion-Roughness-Metallic)
```
Red Channel → Ambient Occlusion (AO)
Green Channel → Roughness
Blue Channel → Metallic
Alpha Channel → (unused, defaults to 1.0)
```

**Best for:**
- Standard PBR (Physically Based Rendering) workflows
- Unreal Engine, Unity, Godot (most game engines)
- Most game artist pipelines

**Channel Info:**
- **Red (AO)**: Darkens crevices and corners (0 = fully dark, 1 = fully bright)
- **Green (Roughness)**: 0 = mirror-like, 0.5 = normal, 1 = rough surface
- **Blue (Metallic)**: 0 = non-metal, 1 = fully metallic

**Real example:** Metal grating
- AO: Dark in crevices between grates
- Roughness: High (rough metal)
- Metallic: 1.0 (it's metal!)

---

### 3. ORD 🗺️ (Occlusion-Roughness-Displacement)
```
Red Channel → Ambient Occlusion (AO)
Green Channel → Roughness
Blue Channel → Displacement (Height)
Alpha Channel → (unused, defaults to 1.0)
```

**Best for:**
- Parallax mapping / heightfield materials
- Terrain details
- When you need height information instead of metallic

**Channel Info:**
- **Red (AO)**: Same as ORM
- **Green (Roughness)**: Same as ORM
- **Blue (Displacement)**: Height map (0 = low, 1 = high)

**Real example:** Stone wall
- AO: Shadows in cracks
- Roughness: Rough stone
- Displacement: Height variation of stones (0.5 = flat, 1.0 = raised)

---

## ❓ Troubleshooting & FAQ

### **Q: What if I upload the wrong format?**
**A:** No worries! You can:
1. Click **Clear** button to remove the image
2. Upload the correct image
3. The preview updates instantly ✨

### **Q: Can I change my mind after packing?**
**A:** Absolutely! Just:
1. Click **Clear** to reset all channels
2. Start fresh with new images
3. Or upload your packed image to **Unpack** to extract channels again

### **Q: What image formats work?**
**A:** Most common formats:
- PNG (recommended - lossless)
- JPG (smaller file size, slight quality loss)
- TGA (good for transparency)
- BMP, WebP, and more

**💡 Tip:** Use PNG for best quality!

### **Q: The preview looks wrong?**
**A:** Make sure your images are grayscale (single channel):
- ✓ Grayscale image = each pixel has 1 value (0-255)
- ✗ RGB image = each pixel has 3 values (R, G, B)
- ✗ RGBA image = each pixel has 4 values (R, G, B, A)

**Quick fix:** Convert to grayscale in Photoshop, Gimp, or online converters

### **Q: Can I pack larger textures?**
**A:** Yes! Any size works - 512x512, 2K, 4K, 8K...

**💡 Tip:** Larger textures use more memory and load slower. Consider these sizes:
- Game assets: 512x512 - 2K
- High-detail surfaces: 2K - 4K
- Textures atlases: varies

### **Q: How do I use the packed texture in my game engine?**

#### Unreal Engine 5
1. Import packed image as texture
2. Set compression to "Mask (DXT5, BC4/5)"
3. Create material, set up PBR with custom nodes
4. Sample packed texture, extract channels with Component Mask

#### Unity
1. Import packed image as texture
2. Create material with shader supporting packed formats
3. Assign texture to material
4. Shader handles channel assignment

#### Godot
1. Import as texture
2. Create StandardMaterial3D
3. Assign packed texture to appropriate texture slots
4. Godot handles channel separation

#### Custom Engine
Use the packed texture and read channels directly:
- Red channel [0] = AO (ORM) or AO (ORD)
- Green channel [1] = Roughness
- Blue channel [2] = Metallic (ORM) or Displacement (ORD)

### **Q: What's the difference between formats?**
**ORM vs ORD:**
- Both use Red for AO, Green for Roughness
- **ORM**: Blue = Metallic (shininess)
- **ORD**: Blue = Displacement (height)

Choose based on your material type:
- Shiny metals, leather, plastic? → Use **ORM**
- Bumpy surfaces, parallax mapping? → Use **ORD**

### **Q: Can I edit a channel after unpacking?**
**A:** Yes!
1. Unpack your texture
2. Download a channel
3. Edit it in Photoshop, Gimp, Paint.net, etc.
4. Save the edited version
5. Come back to ChannelSmith and re-pack with the edited image

Perfect for fine-tuning! 🎯

### **Q: How do I know if my channels are correct?**
**A:** Look at the previews:
- Dark areas = Low values (shadows, metallic=0, rough)
- Light areas = High values (bright, metallic=1, smooth)

If it looks wrong, try a different channel assignment!

### **Q: What if I accidentally clear everything?**
**A:** No problem! Just start over. Your file isn't affected - just upload again!

### **Q: Can I batch process multiple textures?**
**A:** Currently, ChannelSmith handles one texture at a time.

**Workaround for batch processing:**
1. Pack one texture
2. Download it
3. Repeat steps 1-2 for other textures

Or use the Python API (for developers):
```python
from channelsmith.core.packing_engine import pack_texture_from_template

# Automate packing multiple textures
for texture_name in ['wood', 'metal', 'stone']:
    # Load channels, pack, save...
```

---

## 💡 Tips & Tricks

### Best Practices

1. **Always preview first**
   - Check preview cards before packing
   - Make sure channels look right
   - Preview = what you'll get!

2. **Use consistent image sizes**
   - If channels are different sizes, ChannelSmith handles it
   - But matching sizes work best: 512x512, 1024x1024, 2048x2048

3. **Keep original channel files**
   - Save your AO, Roughness, Metallic originals
   - Never know when you need to re-pack with different settings!

4. **Name your files clearly**
   - `wood_orm.png` (obvious it's ORM packed)
   - `wood_ao.png`, `wood_roughness.png` (clear what each is)
   - Helps your team understand your workflow

5. **Test in your engine immediately**
   - After packing, load in your game engine
   - Make sure channels look right in-game
   - Better to catch issues now!

### Common Workflows

**Workflow 1: Quick Testing**
1. Open ChannelSmith
2. Select **Free Mode**
3. Upload any grayscale images
4. Pack and download
5. Test in your engine

**Workflow 2: Professional ORM Pipeline**
1. Create AO, Roughness, Metallic maps in Substance Painter
2. Export as individual PNGs
3. Open ChannelSmith
4. Select **ORM** preset
5. Upload each channel to correct slot
6. Pack and download
7. Import into Unreal Engine
8. Create material with channel unpacking nodes

**Workflow 3: Texture Conversion**
1. Have ORM packed texture
2. Need ORD format instead?
3. Unpack with ORM preset
4. Download Red (AO), Green (Roughness)
5. Create new Displacement map
6. Pack with ORD preset using those 3 channels
7. Done! Format converted!

---

## 🆘 Getting Help

### Stuck?

1. **Check this guide** - Most questions answered above
2. **Try the other preset** - Sometimes it's a format mismatch
3. **Clear and start fresh** - Reset and try again with different images
4. **Check image format** - Make sure images are grayscale, not RGB

### Still Need Help?

- **GitHub Issues:** [Report bugs](https://github.com/cgCrate/ChannelSmith)
- **Community:** Ask other game devs in forums like Polycount, Game Dev Stack Exchange

---

## 📚 Learn More

### PBR Material Theory

Want to understand textures better?

- **Ambient Occlusion (AO):**
  - Shows how much light reaches different areas
  - Used for subtle shadows in crevices
  - Values: 0 (fully dark) to 1 (full brightness)

- **Roughness:**
  - Describes surface texture
  - 0 = mirror-like (reflective)
  - 0.5 = normal material
  - 1 = completely rough (non-reflective)

- **Metallic:**
  - Indicates metal vs non-metal
  - 0 = not metal (dielectric)
  - 1 = fully metallic
  - Usually binary (0 or 1, not in-between)

- **Displacement:**
  - Height information for parallax mapping
  - 0 = lowest point
  - 0.5 = middle
  - 1 = highest point

### Game Engine Docs

- **Unreal Engine:** UE Material System, PBR Documentation
- **Unity:** Standard Material, Custom Shaders
- **Godot:** StandardMaterial3D, Shader Programming

---

## 🎓 Quick Reference

### File Naming Convention

```
asset_type_orm.png          ← Packed texture (ORM)
asset_type_ord.png          ← Packed texture (ORD)
asset_type_ao.png           ← Ambient Occlusion
asset_type_roughness.png    ← Roughness
asset_type_metallic.png     ← Metallic
asset_type_displacement.png ← Displacement
```

### Channel Assignment Quick Guide

| Preset | Red | Green | Blue | Alpha |
|--------|-----|-------|------|-------|
| Free | Any | Any | Any | Any |
| ORM | AO | Roughness | Metallic | 1.0 |
| ORD | AO | Roughness | Displacement | 1.0 |

### Preset Defaults (when empty)

| Channel | Default Value | Reason |
|---------|---------------|--------|
| Red | 1.0 (White) | Maximum brightness |
| Green | 0.5 (Mid-Gray) | 50% normal |
| Blue | 0.0 (Black) | No value |
| Alpha | 1.0 (White) | Fully opaque |

---

## ✨ Final Tips

- **You can't break anything!** Try different settings, experiment
- **Unpacking is reversible** - Extract channels, edit, re-pack
- **Preview before downloading** - Make sure it looks right
- **Keep backups** - Save original channel files
- **Have fun!** Packing textures becomes second nature quickly 🚀

---

**Happy packing!** 🎨

*Last Updated: February 2026*
*Version: ChannelSmith Web MVP*
