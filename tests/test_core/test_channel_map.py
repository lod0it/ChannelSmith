"""
Tests for the ChannelMap class.

This module contains unit tests for the ChannelMap class, including:
- Creation and initialization
- Default value validation
- String representations
- Predefined channel constants
"""

import pytest
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


class TestChannelMapCreation:
    """Test ChannelMap instantiation and initialization."""

    def test_create_with_valid_values(self):
        """Test creating a ChannelMap with valid parameters."""
        channel = ChannelMap('roughness', 0.5, 'Surface Roughness')

        assert channel.map_type == 'roughness'
        assert channel.default_value == 0.5
        assert channel.description == 'Surface Roughness'

    def test_create_with_minimum_default_value(self):
        """Test creating a ChannelMap with default_value = 0.0."""
        channel = ChannelMap('metallic', 0.0)

        assert channel.default_value == 0.0

    def test_create_with_maximum_default_value(self):
        """Test creating a ChannelMap with default_value = 1.0."""
        channel = ChannelMap('ambient_occlusion', 1.0)

        assert channel.default_value == 1.0

    def test_create_without_description(self):
        """Test that description is auto-generated when not provided."""
        channel = ChannelMap('ambient_occlusion', 1.0)

        assert channel.description == 'Ambient Occlusion'

    def test_create_with_underscore_auto_description(self):
        """Test that underscores in map_type are converted to spaces in description."""
        channel = ChannelMap('custom_map_type', 0.5)

        assert channel.description == 'Custom Map Type'


class TestChannelMapValidation:
    """Test validation of ChannelMap parameters."""

    def test_default_value_below_minimum_raises_error(self):
        """Test that default_value < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="default_value must be between 0.0 and 1.0"):
            ChannelMap('roughness', -0.1)

    def test_default_value_above_maximum_raises_error(self):
        """Test that default_value > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="default_value must be between 0.0 and 1.0"):
            ChannelMap('roughness', 1.5)

    def test_default_value_far_below_minimum_raises_error(self):
        """Test that very negative default_value raises ValueError."""
        with pytest.raises(ValueError, match="default_value must be between 0.0 and 1.0"):
            ChannelMap('roughness', -10.0)

    def test_default_value_far_above_maximum_raises_error(self):
        """Test that very large default_value raises ValueError."""
        with pytest.raises(ValueError, match="default_value must be between 0.0 and 1.0"):
            ChannelMap('roughness', 100.0)


class TestChannelMapStringRepresentation:
    """Test string representations of ChannelMap."""

    def test_repr(self):
        """Test __repr__ returns valid Python representation."""
        channel = ChannelMap('metallic', 0.0)

        result = repr(channel)

        assert result == "ChannelMap(map_type='metallic', default_value=0.0)"

    def test_repr_with_description(self):
        """Test __repr__ includes map_type and default_value regardless of description."""
        channel = ChannelMap('roughness', 0.5, 'Custom Description')

        result = repr(channel)

        assert result == "ChannelMap(map_type='roughness', default_value=0.5)"

    def test_str(self):
        """Test __str__ returns human-readable format."""
        channel = ChannelMap('roughness', 0.5, 'Surface Roughness')

        result = str(channel)

        assert result == 'Surface Roughness (default: 0.5)'

    def test_str_with_auto_description(self):
        """Test __str__ uses auto-generated description."""
        channel = ChannelMap('ambient_occlusion', 1.0)

        result = str(channel)

        assert result == 'Ambient Occlusion (default: 1.0)'


class TestPredefinedChannels:
    """Test predefined channel type constants."""

    def test_ambient_occlusion_constant(self):
        """Test AMBIENT_OCCLUSION predefined constant."""
        assert AMBIENT_OCCLUSION.map_type == 'ambient_occlusion'
        assert AMBIENT_OCCLUSION.default_value == 1.0
        assert AMBIENT_OCCLUSION.description == 'Ambient Occlusion'

    def test_roughness_constant(self):
        """Test ROUGHNESS predefined constant."""
        assert ROUGHNESS.map_type == 'roughness'
        assert ROUGHNESS.default_value == 0.5
        assert ROUGHNESS.description == 'Roughness'

    def test_metallic_constant(self):
        """Test METALLIC predefined constant."""
        assert METALLIC.map_type == 'metallic'
        assert METALLIC.default_value == 0.0
        assert METALLIC.description == 'Metallic'

    def test_displacement_constant(self):
        """Test DISPLACEMENT predefined constant."""
        assert DISPLACEMENT.map_type == 'displacement'
        assert DISPLACEMENT.default_value == 0.5
        assert DISPLACEMENT.description == 'Displacement'

    def test_height_constant(self):
        """Test HEIGHT predefined constant."""
        assert HEIGHT.map_type == 'height'
        assert HEIGHT.default_value == 0.5
        assert HEIGHT.description == 'Height'

    def test_opacity_constant(self):
        """Test OPACITY predefined constant."""
        assert OPACITY.map_type == 'opacity'
        assert OPACITY.default_value == 1.0
        assert OPACITY.description == 'Opacity'

    def test_alpha_constant(self):
        """Test ALPHA predefined constant."""
        assert ALPHA.map_type == 'alpha'
        assert ALPHA.default_value == 1.0
        assert ALPHA.description == 'Alpha'


class TestPredefinedChannelsDictionary:
    """Test the PREDEFINED_CHANNELS lookup dictionary."""

    def test_dictionary_contains_all_types(self):
        """Test that PREDEFINED_CHANNELS contains all predefined types."""
        expected_types = [
            'ambient_occlusion',
            'roughness',
            'metallic',
            'displacement',
            'height',
            'opacity',
            'alpha',
        ]

        for channel_type in expected_types:
            assert channel_type in PREDEFINED_CHANNELS

    def test_dictionary_lookup_ambient_occlusion(self):
        """Test looking up ambient_occlusion from dictionary."""
        channel = PREDEFINED_CHANNELS['ambient_occlusion']

        assert channel.map_type == 'ambient_occlusion'
        assert channel.default_value == 1.0

    def test_dictionary_lookup_roughness(self):
        """Test looking up roughness from dictionary."""
        channel = PREDEFINED_CHANNELS['roughness']

        assert channel.map_type == 'roughness'
        assert channel.default_value == 0.5

    def test_dictionary_lookup_metallic(self):
        """Test looking up metallic from dictionary."""
        channel = PREDEFINED_CHANNELS['metallic']

        assert channel.map_type == 'metallic'
        assert channel.default_value == 0.0

    def test_dictionary_has_correct_count(self):
        """Test that PREDEFINED_CHANNELS has exactly 7 entries."""
        assert len(PREDEFINED_CHANNELS) == 7


class TestChannelMapEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string_map_type(self):
        """Test creating ChannelMap with empty string map_type."""
        channel = ChannelMap('', 0.5)

        assert channel.map_type == ''
        assert channel.default_value == 0.5

    def test_very_long_map_type(self):
        """Test creating ChannelMap with very long map_type."""
        long_type = 'very_long_map_type_name_that_goes_on_and_on'
        channel = ChannelMap(long_type, 0.5)

        assert channel.map_type == long_type

    def test_special_characters_in_map_type(self):
        """Test creating ChannelMap with special characters in map_type."""
        channel = ChannelMap('map-type.with!special@chars', 0.5)

        assert channel.map_type == 'map-type.with!special@chars'

    def test_float_precision_default_value(self):
        """Test that float precision is preserved in default_value."""
        channel = ChannelMap('test', 0.123456789)

        assert channel.default_value == 0.123456789
