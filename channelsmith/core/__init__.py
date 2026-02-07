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
from channelsmith.core.validator import (
    check_resolution_match,
    get_max_resolution,
    validate_channel_data,
    validate_images_for_packing,
    validate_arrays_for_packing,
    ResolutionMismatchError,
    InvalidChannelDataError,
)

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
    'check_resolution_match',
    'get_max_resolution',
    'validate_channel_data',
    'validate_images_for_packing',
    'validate_arrays_for_packing',
    'ResolutionMismatchError',
    'InvalidChannelDataError',
]
