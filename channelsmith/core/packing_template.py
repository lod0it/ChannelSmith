"""
PackingTemplate class for defining RGBA channel assignments.

This module provides the PackingTemplate class which defines how different
texture maps are assigned to the RGBA channels of a packed texture.
"""

from typing import Dict, Optional
from channelsmith.core.channel_map import ChannelMap


class PackingTemplate:
    """
    Defines how texture channels are mapped to RGBA slots in a packed texture.

    A PackingTemplate specifies which texture map types (e.g., ambient occlusion,
    roughness, metallic) are assigned to each RGBA channel in the final packed
    texture. This enables different packing configurations like ORM (Occlusion-
    Roughness-Metallic) or ORD (Occlusion-Roughness-Displacement).

    Attributes:
        name: Template name (e.g., 'ORM', 'ORD')
        description: Human-readable description of the template
        channels: Dictionary mapping RGBA keys to ChannelMap instances
                 Keys: 'R', 'G', 'B', 'A'
                 Values: ChannelMap instances or None if channel unused

    Example:
        >>> orm_template = PackingTemplate(
        ...     name='ORM',
        ...     description='Occlusion-Roughness-Metallic',
        ...     channels={
        ...         'R': ChannelMap('ambient_occlusion', 1.0),
        ...         'G': ChannelMap('roughness', 0.5),
        ...         'B': ChannelMap('metallic', 0.0)
        ...     }
        ... )
        >>> orm_template.is_rgba()
        False
        >>> orm_template.get_channel('R').map_type
        'ambient_occlusion'
    """

    def __init__(
        self,
        name: str,
        description: str,
        channels: Optional[Dict[str, Optional[ChannelMap]]] = None,
    ):
        """
        Initialize a PackingTemplate instance.

        Args:
            name: Template name (e.g., 'ORM', 'ORD')
            description: Human-readable description of the template
            channels: Dictionary mapping RGBA keys to ChannelMap instances.
                     Keys must be 'R', 'G', 'B', and/or 'A'.
                     Values can be ChannelMap instances or None for unused channels.
                     If not provided, initializes with all channels set to None.

        Raises:
            ValueError: If channels dict contains invalid keys (not R/G/B/A)

        Example:
            >>> template = PackingTemplate(
            ...     name='ORM',
            ...     description='Occlusion-Roughness-Metallic',
            ...     channels={
            ...         'R': ChannelMap('ambient_occlusion', 1.0),
            ...         'G': ChannelMap('roughness', 0.5),
            ...         'B': ChannelMap('metallic', 0.0)
            ...     }
            ... )
        """
        self.name = name
        self.description = description

        # Initialize channels dictionary with None values
        self.channels: Dict[str, Optional[ChannelMap]] = {
            "R": None,
            "G": None,
            "B": None,
            "A": None,
        }

        # Validate and update channels if provided
        if channels:
            valid_keys = {"R", "G", "B", "A"}
            invalid_keys = set(channels.keys()) - valid_keys
            if invalid_keys:
                raise ValueError(
                    f"Invalid channel keys: {invalid_keys}. "
                    f"Valid keys are: {valid_keys}"
                )
            self.channels.update(channels)

    def get_channel(self, key: str) -> Optional[ChannelMap]:
        """
        Get the ChannelMap assigned to a specific RGBA channel.

        Args:
            key: Channel key ('R', 'G', 'B', or 'A')

        Returns:
            ChannelMap instance if channel is used, None if unused

        Raises:
            KeyError: If key is not 'R', 'G', 'B', or 'A'

        Example:
            >>> template = PackingTemplate('ORM', 'Test', {
            ...     'R': ChannelMap('ambient_occlusion', 1.0)
            ... })
            >>> channel = template.get_channel('R')
            >>> channel.map_type
            'ambient_occlusion'
            >>> template.get_channel('A')  # Unused channel
            None
        """
        if key not in {"R", "G", "B", "A"}:
            raise KeyError(
                f"Invalid channel key: '{key}'. Must be 'R', 'G', 'B', or 'A'"
            )
        return self.channels[key]

    def is_channel_used(self, key: str) -> bool:
        """
        Check if a specific RGBA channel is used in this template.

        Args:
            key: Channel key ('R', 'G', 'B', or 'A')

        Returns:
            True if channel is assigned a ChannelMap, False if unused

        Raises:
            KeyError: If key is not 'R', 'G', 'B', or 'A'

        Example:
            >>> template = PackingTemplate('ORM', 'Test', {
            ...     'R': ChannelMap('ambient_occlusion', 1.0),
            ...     'G': ChannelMap('roughness', 0.5),
            ...     'B': ChannelMap('metallic', 0.0)
            ... })
            >>> template.is_channel_used('R')
            True
            >>> template.is_channel_used('A')
            False
        """
        if key not in {"R", "G", "B", "A"}:
            raise KeyError(
                f"Invalid channel key: '{key}'. Must be 'R', 'G', 'B', or 'A'"
            )
        return self.channels[key] is not None

    def is_rgba(self) -> bool:
        """
        Check if this template uses the alpha channel.

        Returns:
            True if alpha channel is used, False if only RGB channels are used

        Example:
            >>> rgb_template = PackingTemplate('ORM', 'Test', {
            ...     'R': ChannelMap('ambient_occlusion', 1.0),
            ...     'G': ChannelMap('roughness', 0.5),
            ...     'B': ChannelMap('metallic', 0.0)
            ... })
            >>> rgb_template.is_rgba()
            False
            >>>
            >>> rgba_template = PackingTemplate('ORMA', 'Test', {
            ...     'R': ChannelMap('ambient_occlusion', 1.0),
            ...     'G': ChannelMap('roughness', 0.5),
            ...     'B': ChannelMap('metallic', 0.0),
            ...     'A': ChannelMap('alpha', 1.0)
            ... })
            >>> rgba_template.is_rgba()
            True
        """
        return self.is_channel_used("A")

    def get_used_channels(self) -> Dict[str, ChannelMap]:
        """
        Get a dictionary of only the used channels.

        Returns:
            Dictionary mapping channel keys to ChannelMap instances,
            containing only channels that are actually used

        Example:
            >>> template = PackingTemplate('ORM', 'Test', {
            ...     'R': ChannelMap('ambient_occlusion', 1.0),
            ...     'G': ChannelMap('roughness', 0.5)
            ... })
            >>> used = template.get_used_channels()
            >>> list(used.keys())
            ['R', 'G']
        """
        return {
            key: channel_map
            for key, channel_map in self.channels.items()
            if channel_map is not None
        }

    def __repr__(self) -> str:
        """
        Return a string representation of the PackingTemplate for debugging.

        Returns:
            A string representation showing the template name and channel usage

        Example:
            >>> template = PackingTemplate('ORM', 'Occlusion-Roughness-Metallic')
            >>> repr(template)
            "PackingTemplate(name='ORM', channels=['R', 'G', 'B', 'A'])"
        """
        channel_keys = list(self.channels.keys())
        return f"PackingTemplate(name='{self.name}', channels={channel_keys})"

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the PackingTemplate.

        Returns:
            A formatted string with template name, description, and used channels

        Example:
            >>> template = PackingTemplate('ORM', 'Occlusion-Roughness-Metallic', {
            ...     'R': ChannelMap('ambient_occlusion', 1.0),
            ...     'G': ChannelMap('roughness', 0.5),
            ...     'B': ChannelMap('metallic', 0.0)
            ... })
            >>> print(template)
            ORM: Occlusion-Roughness-Metallic
            Channels: R (ambient_occlusion), G (roughness), B (metallic)
        """
        used_channels = self.get_used_channels()
        channel_info = ", ".join(
            f"{key} ({channel.map_type})" for key, channel in used_channels.items()
        )
        return f"{self.name}: {self.description}\nChannels: {channel_info}"
