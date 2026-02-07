"""
Core engine components for ChannelSmith texture packing/unpacking.

This package contains the core logic for texture channel packing and unpacking,
independent of any GUI framework.
"""

from channelsmith.core.channel_map import (
    ChannelMap,
    AMBIENT_OCCLUSION,
    ROUGHNESS,
    METALLIC,
    DISPLACEMENT,
    HEIGHT,
    OPACITY,
    ALPHA,
    PREDEFINED_CHANNELS,
)

__all__ = [
    'ChannelMap',
    'AMBIENT_OCCLUSION',
    'ROUGHNESS',
    'METALLIC',
    'DISPLACEMENT',
    'HEIGHT',
    'OPACITY',
    'ALPHA',
    'PREDEFINED_CHANNELS',
]
