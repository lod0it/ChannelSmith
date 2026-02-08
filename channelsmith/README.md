# ChannelSmith API Reference

Texture channel packing/unpacking library for game development.

## Quick Start

```python
import numpy as np
from channelsmith.templates.template_loader import load_template
from channelsmith.core.packing_engine import pack_texture_from_template
from channelsmith.core.unpacking_engine import unpack_texture
from channelsmith.utils.image_utils import save_image, load_image

# Pack textures using the ORM template
template = load_template('channelsmith/templates/orm.json')
textures = {
    'ambient_occlusion': np.full((1024, 1024), 255, dtype=np.uint8),
    'roughness': np.full((1024, 1024), 128, dtype=np.uint8),
    'metallic': np.zeros((1024, 1024), dtype=np.uint8),
}
packed = pack_texture_from_template(textures, template)
save_image(packed, 'packed_orm.png')

# Unpack back to individual channels
loaded = load_image('packed_orm.png')
channels = unpack_texture(loaded, template)
# channels = {'ambient_occlusion': array, 'roughness': array, 'metallic': array}
```

## Public API

### Packing Engine (`channelsmith.core.packing_engine`)

#### `pack_channels(r=None, g=None, b=None, a=None) -> Image`

Pack grayscale arrays into a single RGB/RGBA image.

```python
from channelsmith.core.packing_engine import pack_channels

r = np.full((512, 512), 255, dtype=np.uint8)
g = np.full((512, 512), 128, dtype=np.uint8)
b = np.zeros((512, 512), dtype=np.uint8)

packed = pack_channels(r, g, b)        # RGB
packed = pack_channels(r, g, b, a=a)   # RGBA
```

- At least one channel must be provided
- Missing RGB channels are filled with zeros
- Mismatched resolutions are automatically normalized to the maximum
- Accepts uint8, int16, float32, float64 arrays

#### `pack_texture_from_template(textures, template) -> Image`

Pack textures according to a template's channel mapping.

```python
from channelsmith.core.packing_engine import pack_texture_from_template

textures = {
    'ambient_occlusion': 'path/to/ao.png',    # file path
    'roughness': roughness_image,               # PIL Image
    'metallic': metallic_array,                 # NumPy array
}
packed = pack_texture_from_template(textures, template)
```

- Texture sources can be: file path (`str`), PIL `Image`, or NumPy `ndarray`
- Missing textures are filled with the template's default values
- Mismatched resolutions are normalized to the largest input

#### `normalize_resolution(arrays, target_size) -> list`

Resize all arrays to a target `(width, height)` using bilinear interpolation.

#### `create_default_channel(size, default_value) -> ndarray`

Create a channel array filled with a default value (0.0-1.0 range).

### Unpacking Engine (`channelsmith.core.unpacking_engine`)

#### `extract_channel(image, channel) -> ndarray`

Extract a single R/G/B/A channel from a packed image.

```python
from channelsmith.core.unpacking_engine import extract_channel

r_data = extract_channel(packed_image, 'R')
g_data = extract_channel(packed_image, 'G')
```

- Returns a 2D uint8 NumPy array
- Requesting `'A'` from an RGB image raises `ValueError`

#### `unpack_texture(image, template) -> dict`

Extract all channels defined in a template.

```python
from channelsmith.core.unpacking_engine import unpack_texture

channels = unpack_texture(packed_image, template)
ao = channels['ambient_occlusion']
roughness = channels['roughness']
```

- Returns `{texture_type_name: ndarray}` for each channel in the template
- Template with alpha requires an RGBA image

### Templates

#### Built-in Templates

| Template | File | R | G | B |
|----------|------|---|---|---|
| ORM | `channelsmith/templates/orm.json` | Ambient Occlusion (1.0) | Roughness (0.5) | Metallic (0.0) |
| ORD | `channelsmith/templates/ord.json` | Ambient Occlusion (1.0) | Roughness (0.5) | Displacement (0.5) |

#### `load_template(path) -> PackingTemplate`

```python
from channelsmith.templates.template_loader import load_template

template = load_template('channelsmith/templates/orm.json')
```

#### `save_template(template, path)`

```python
from channelsmith.templates.template_loader import save_template

save_template(my_template, 'templates/custom.json')
```

#### Creating Custom Templates

```python
from channelsmith.core.packing_template import PackingTemplate
from channelsmith.core.channel_map import ChannelMap

template = PackingTemplate(
    name='CustomPBR',
    description='My custom PBR packing',
    channels={
        'R': ChannelMap('roughness', 0.8),
        'G': ChannelMap('metallic', 0.0),
        'B': ChannelMap('height', 0.5),
        'A': ChannelMap('opacity', 1.0),  # optional alpha channel
    }
)
```

Or define as JSON:

```json
{
  "name": "CustomPBR",
  "description": "My custom PBR packing",
  "channels": {
    "R": { "type": "roughness", "default": 0.8 },
    "G": { "type": "metallic", "default": 0.0 },
    "B": { "type": "height", "default": 0.5 },
    "A": { "type": "opacity", "default": 1.0 }
  }
}
```

### Image Utilities (`channelsmith.utils.image_utils`)

| Function | Description |
|----------|-------------|
| `load_image(path)` | Load an image file (PNG, TGA, JPEG, TIFF, BMP) |
| `save_image(image, path, img_format=None)` | Save a PIL Image to disk |
| `to_grayscale(image)` | Convert a PIL Image to a 2D uint8 NumPy array |
| `from_grayscale(array)` | Convert a 2D NumPy array to a grayscale PIL Image |

### Predefined Channel Types (`channelsmith.core.channel_map`)

| Constant | Type | Default |
|----------|------|---------|
| `AMBIENT_OCCLUSION` | `ambient_occlusion` | 1.0 (white) |
| `ROUGHNESS` | `roughness` | 0.5 (mid-gray) |
| `METALLIC` | `metallic` | 0.0 (black) |
| `DISPLACEMENT` | `displacement` | 0.5 (mid-gray) |
| `HEIGHT` | `height` | 0.5 (mid-gray) |
| `OPACITY` | `opacity` | 1.0 (white) |
| `ALPHA` | `alpha` | 1.0 (white) |

## Common Workflows

### Repack ORM to ORD

```python
orm = load_template('channelsmith/templates/orm.json')
ord = load_template('channelsmith/templates/ord.json')

# Unpack the ORM texture
channels = unpack_texture(load_image('packed_orm.png'), orm)

# Build ORD textures (reuse AO + roughness, add displacement)
ord_textures = {
    'ambient_occlusion': channels['ambient_occlusion'],
    'roughness': channels['roughness'],
    'displacement': load_image('displacement.png'),
}
packed_ord = pack_texture_from_template(ord_textures, ord)
save_image(packed_ord, 'packed_ord.png')
```

### Replace a Single Channel

```python
template = load_template('channelsmith/templates/orm.json')
channels = unpack_texture(load_image('packed_orm.png'), template)

# Replace roughness with a new map
channels['roughness'] = to_grayscale(load_image('new_roughness.png'))

repacked = pack_texture_from_template(channels, template)
save_image(repacked, 'updated_orm.png')
```

## Troubleshooting

### `ValueError: Cannot extract alpha channel from 'RGB' image`

The template requires an alpha channel but the image is RGB. Either:
- Use a template without alpha (like ORM or ORD)
- Convert the image to RGBA before unpacking

### `FileNotFoundError: Image file not found`

The file path passed to `load_image()` or as a texture source doesn't exist. Check the path is correct and the file is accessible.

### `TemplateValidationError: Invalid JSON`

The template JSON file is malformed. Ensure it has `name`, `description`, and `channels` fields. Each channel needs `type` and `default` keys. Default values must be between 0.0 and 1.0.

### `InvalidChannelDataError: Channel data must be 2D array`

A NumPy array passed as a texture is not 2D. Ensure you're passing grayscale arrays with shape `(height, width)`, not RGB arrays with shape `(height, width, 3)`.

### Mismatched resolutions

Not an error -- ChannelSmith automatically upscales all channels to the largest resolution using bilinear interpolation. The output resolution will match the largest input.
