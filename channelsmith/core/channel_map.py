"""
ChannelMap class for defining texture map types and their default values.

This module provides the ChannelMap class which represents a single texture
channel type (e.g., ambient occlusion, roughness, metallic) along with its
default fill value when the texture is missing.
"""

from typing import Optional


class ChannelMap:
    """
    Represents a texture channel type with its default value.

    A ChannelMap defines a specific type of texture map (e.g., ambient occlusion,
    roughness, metallic) and its default value when the texture is missing during
    packing operations.

    Attributes:
        map_type: The type of texture map (e.g., 'ambient_occlusion', 'roughness')
        default_value: Default value for missing textures, normalized to 0.0-1.0 range
        description: Optional human-readable description of this channel type

    Example:
        >>> ao_channel = ChannelMap('ambient_occlusion', 1.0, 'Ambient Occlusion')
        >>> ao_channel.map_type
        'ambient_occlusion'
        >>> ao_channel.default_value
        1.0
    """

    def __init__(
        self,
        map_type: str,
        default_value: float,
        description: Optional[str] = None
    ):
        """
        Initialize a ChannelMap instance.

        Args:
            map_type: The type of texture map (e.g., 'ambient_occlusion', 'roughness')
            default_value: Default value for missing textures, must be in range 0.0-1.0
            description: Optional human-readable description of this channel type

        Raises:
            ValueError: If default_value is not in the range 0.0-1.0

        Example:
            >>> channel = ChannelMap('roughness', 0.5, 'Surface roughness')
            >>> channel.default_value
            0.5
        """
        # Validate default_value range
        if not 0.0 <= default_value <= 1.0:
            raise ValueError(
                f"default_value must be between 0.0 and 1.0, got {default_value}"
            )

        self.map_type = map_type
        self.default_value = default_value
        self.description = description or map_type.replace('_', ' ').title()

    def __repr__(self) -> str:
        """
        Return a string representation of the ChannelMap for debugging.

        Returns:
            A string representation showing the map type and default value

        Example:
            >>> channel = ChannelMap('metallic', 0.0)
            >>> repr(channel)
            "ChannelMap(map_type='metallic', default_value=0.0)"
        """
        return (
            f"ChannelMap(map_type='{self.map_type}', "
            f"default_value={self.default_value})"
        )

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the ChannelMap.

        Returns:
            A formatted string with description and default value

        Example:
            >>> channel = ChannelMap('roughness', 0.5, 'Surface Roughness')
            >>> str(channel)
            'Surface Roughness (default: 0.5)'
        """
        return f"{self.description} (default: {self.default_value})"


# Predefined channel types with context-aware default values
AMBIENT_OCCLUSION = ChannelMap(
    'ambient_occlusion',
    1.0,
    'Ambient Occlusion'
)

ROUGHNESS = ChannelMap(
    'roughness',
    0.5,
    'Roughness'
)

METALLIC = ChannelMap(
    'metallic',
    0.0,
    'Metallic'
)

DISPLACEMENT = ChannelMap(
    'displacement',
    0.5,
    'Displacement'
)

HEIGHT = ChannelMap(
    'height',
    0.5,
    'Height'
)

OPACITY = ChannelMap(
    'opacity',
    1.0,
    'Opacity'
)

ALPHA = ChannelMap(
    'alpha',
    1.0,
    'Alpha'
)

# Dictionary for easy lookup by type name
PREDEFINED_CHANNELS = {
    'ambient_occlusion': AMBIENT_OCCLUSION,
    'roughness': ROUGHNESS,
    'metallic': METALLIC,
    'displacement': DISPLACEMENT,
    'height': HEIGHT,
    'opacity': OPACITY,
    'alpha': ALPHA,
}
