"""
ChannelSmith Alpha Demo
=======================

Demonstrates all core capabilities of the ChannelSmith packing/unpacking engine:

    1. Pack textures into a single image using the ORM template
    2. Unpack a packed texture back into individual channels
    3. Repack from ORM format to ORD format
    4. Use custom default values with a user-defined template

Run from the project root:
    python examples/alpha_demo.py

All output files are written to a temporary 'examples/output/' directory.
"""

import os
import sys
import shutil
import numpy as np
from PIL import Image

# Add project root to path so we can import channelsmith
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from channelsmith.core.packing_engine import pack_texture_from_template
from channelsmith.core.unpacking_engine import unpack_texture
from channelsmith.core.packing_template import PackingTemplate
from channelsmith.core.channel_map import ChannelMap
from channelsmith.templates.template_loader import load_template, save_template
from channelsmith.utils.image_utils import save_image, load_image


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'channelsmith', 'templates')


def setup_output_dir():
    """Create a clean output directory for demo results."""
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}\n")


def create_sample_textures():
    """
    Create sample grayscale texture maps for the demo.

    Returns a dictionary of texture type -> NumPy array (512x512, uint8).
    """
    # Ambient Occlusion: mostly white with darker edges (simulated)
    ao = np.full((512, 512), 240, dtype=np.uint8)
    ao[:20, :] = 180   # darken top edge
    ao[-20:, :] = 180  # darken bottom edge
    ao[:, :20] = 180   # darken left edge
    ao[:, -20:] = 180  # darken right edge

    # Roughness: horizontal gradient from smooth (0) to rough (255)
    roughness = np.tile(
        np.linspace(0, 255, 512, dtype=np.uint8), (512, 1)
    )

    # Metallic: mostly non-metallic with a metallic square in the center
    metallic = np.zeros((512, 512), dtype=np.uint8)
    metallic[156:356, 156:356] = 255  # metallic center patch

    # Displacement: radial pattern (higher in center)
    y, x = np.ogrid[:512, :512]
    center_y, center_x = 256, 256
    dist = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
    displacement = np.clip(255 - dist, 0, 255).astype(np.uint8)

    return {
        'ambient_occlusion': ao,
        'roughness': roughness,
        'metallic': metallic,
        'displacement': displacement,
    }


# ---------------------------------------------------------------------------
# Example 1: Pack textures with ORM template
# ---------------------------------------------------------------------------

def example_1_pack_orm(textures):
    """Pack individual texture maps into a single ORM image."""
    print("=" * 60)
    print("Example 1: Pack Textures with ORM Template")
    print("=" * 60)

    # Load the bundled ORM template from JSON
    orm_template = load_template(os.path.join(TEMPLATES_DIR, 'orm.json'))
    print(f"Loaded template: {orm_template.name} - {orm_template.description}")

    # Show channel assignments
    for key, ch in orm_template.get_used_channels().items():
        print(f"  {key} channel -> {ch.map_type} (default: {ch.default_value})")

    # Pack the textures
    orm_textures = {
        'ambient_occlusion': textures['ambient_occlusion'],
        'roughness': textures['roughness'],
        'metallic': textures['metallic'],
    }
    packed = pack_texture_from_template(orm_textures, orm_template)

    # Save result
    output_path = os.path.join(OUTPUT_DIR, 'packed_orm.png')
    save_image(packed, output_path)

    print(f"\nResult: {packed.mode} image, {packed.size[0]}x{packed.size[1]}")
    print(f"Saved to: {output_path}")

    # Also save individual source textures for reference
    for name, arr in orm_textures.items():
        ref_path = os.path.join(OUTPUT_DIR, f'source_{name}.png')
        save_image(Image.fromarray(arr, mode='L'), ref_path)

    print(f"Source textures saved to: {OUTPUT_DIR}/source_*.png\n")
    return packed, orm_template


# ---------------------------------------------------------------------------
# Example 2: Unpack existing ORM texture
# ---------------------------------------------------------------------------

def example_2_unpack_orm(packed, orm_template):
    """Unpack a packed ORM texture back into individual channels."""
    print("=" * 60)
    print("Example 2: Unpack Existing ORM Texture")
    print("=" * 60)

    # Unpack using the same template
    channels = unpack_texture(packed, orm_template)

    print(f"Extracted {len(channels)} channels:")
    for name, arr in channels.items():
        print(f"  {name}: {arr.shape[1]}x{arr.shape[0]}, "
              f"range [{arr.min()}-{arr.max()}]")

        # Save each extracted channel
        channel_path = os.path.join(OUTPUT_DIR, f'unpacked_{name}.png')
        save_image(Image.fromarray(arr, mode='L'), channel_path)

    print(f"\nExtracted channels saved to: {OUTPUT_DIR}/unpacked_*.png\n")
    return channels


# ---------------------------------------------------------------------------
# Example 3: Repack ORM to ORD
# ---------------------------------------------------------------------------

def example_3_repack_orm_to_ord(orm_channels, displacement):
    """Repack from ORM format to ORD format, swapping metallic for displacement."""
    print("=" * 60)
    print("Example 3: Repack ORM -> ORD")
    print("=" * 60)

    # Load the ORD template
    ord_template = load_template(os.path.join(TEMPLATES_DIR, 'ord.json'))
    print(f"Target template: {ord_template.name} - {ord_template.description}")

    for key, ch in ord_template.get_used_channels().items():
        print(f"  {key} channel -> {ch.map_type} (default: {ch.default_value})")

    # Build new texture dict: reuse AO and roughness, add displacement
    ord_textures = {
        'ambient_occlusion': orm_channels['ambient_occlusion'],
        'roughness': orm_channels['roughness'],
        'displacement': displacement,
    }
    print(f"\nReusing: ambient_occlusion, roughness from ORM")
    print(f"Adding:  displacement (new channel)")

    # Pack with ORD template
    packed_ord = pack_texture_from_template(ord_textures, ord_template)

    # Save result
    output_path = os.path.join(OUTPUT_DIR, 'repacked_ord.png')
    save_image(packed_ord, output_path)

    print(f"\nResult: {packed_ord.mode} image, {packed_ord.size[0]}x{packed_ord.size[1]}")
    print(f"Saved to: {output_path}\n")
    return packed_ord


# ---------------------------------------------------------------------------
# Example 4: Custom template with custom default values
# ---------------------------------------------------------------------------

def example_4_custom_defaults():
    """Create and use a custom template with specific default values."""
    print("=" * 60)
    print("Example 4: Custom Template with Custom Defaults")
    print("=" * 60)

    # Create a custom RGBA template
    custom_template = PackingTemplate(
        name='CustomPBR',
        description='Custom PBR with Height and Opacity',
        channels={
            'R': ChannelMap('roughness', 0.8),      # Rough default
            'G': ChannelMap('metallic', 0.0),        # Non-metallic default
            'B': ChannelMap('height', 0.5),          # Flat default
            'A': ChannelMap('opacity', 1.0),         # Fully opaque default
        }
    )

    print(f"Created template: {custom_template.name}")
    print(f"  Mode: {'RGBA' if custom_template.is_rgba() else 'RGB'}")
    for key, ch in custom_template.get_used_channels().items():
        print(f"  {key} -> {ch.map_type} (default: {ch.default_value})")

    # Save the custom template to JSON
    template_path = os.path.join(OUTPUT_DIR, 'custom_pbr.json')
    save_template(custom_template, template_path)
    print(f"\nTemplate saved to: {template_path}")

    # Pack with only roughness provided -- all other channels use defaults
    textures = {
        'roughness': np.full((256, 256), 100, dtype=np.uint8),
    }
    print(f"\nProviding only: roughness (value=100)")
    print(f"Missing channels will use template defaults:")
    print(f"  metallic  -> default 0.0 (black)")
    print(f"  height    -> default 0.5 (mid-gray)")
    print(f"  opacity   -> default 1.0 (white)")

    packed = pack_texture_from_template(textures, custom_template)

    # Verify default values in the packed result
    arr = np.array(packed)
    print(f"\nPacked pixel [0,0]: R={arr[0,0,0]}, G={arr[0,0,1]}, "
          f"B={arr[0,0,2]}, A={arr[0,0,3]}")
    print(f"  R (roughness):  {arr[0,0,0]} (provided)")
    print(f"  G (metallic):   {arr[0,0,1]} (default 0.0 * 255 = 0)")
    print(f"  B (height):     {arr[0,0,2]} (default 0.5 * 255 = ~127)")
    print(f"  A (opacity):    {arr[0,0,3]} (default 1.0 * 255 = 255)")

    output_path = os.path.join(OUTPUT_DIR, 'custom_packed.png')
    save_image(packed, output_path)
    print(f"\nSaved to: {output_path}")

    # Reload template and verify round-trip
    reloaded = load_template(template_path)
    print(f"\nReloaded template from JSON: {reloaded.name}")
    print(f"  Channels match: {list(reloaded.get_used_channels().keys())}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Run all demo examples."""
    print()
    print("ChannelSmith Alpha Demo")
    print("~~~~~~~~~~~~~~~~~~~~~~~")
    print("Demonstrating texture channel packing/unpacking capabilities.\n")

    setup_output_dir()
    textures = create_sample_textures()

    # Example 1: Pack with ORM
    packed_orm, orm_template = example_1_pack_orm(textures)

    # Example 2: Unpack the ORM texture
    orm_channels = example_2_unpack_orm(packed_orm, orm_template)

    # Example 3: Repack as ORD
    example_3_repack_orm_to_ord(orm_channels, textures['displacement'])

    # Example 4: Custom template with defaults
    example_4_custom_defaults()

    print("=" * 60)
    print("All examples complete!")
    print(f"Output files are in: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 60)


if __name__ == '__main__':
    main()
