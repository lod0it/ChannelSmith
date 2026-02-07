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
from channelsmith.core.packing_template import PackingTemplate

__all__ = [
    'ChannelMap',
    'PackingTemplate',
    'AMBIENT_OCCLUSION',
    'ROUGHNESS',
    'METALLIC',
    'DISPLACEMENT',
    'HEIGHT',
    'OPACITY',
    'ALPHA',
    'PREDEFINED_CHANNELS',
]
