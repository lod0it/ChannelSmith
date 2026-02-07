"""
Tests for the PackingTemplate class.

This module contains unit tests for the PackingTemplate class, including:
- Template creation and initialization
- Channel retrieval and validation
- RGBA detection
- Used channel filtering
- String representations
"""

import pytest
from channelsmith.core.channel_map import ChannelMap
from channelsmith.core.packing_template import PackingTemplate


class TestPackingTemplateCreation:
    """Test PackingTemplate instantiation and initialization."""

    def test_create_with_all_parameters(self):
        """Test creating a PackingTemplate with all parameters."""
        channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'G': ChannelMap('roughness', 0.5),
            'B': ChannelMap('metallic', 0.0)
        }
        template = PackingTemplate('ORM', 'Occlusion-Roughness-Metallic', channels)

        assert template.name == 'ORM'
        assert template.description == 'Occlusion-Roughness-Metallic'
        assert template.channels['R'].map_type == 'ambient_occlusion'
        assert template.channels['G'].map_type == 'roughness'
        assert template.channels['B'].map_type == 'metallic'
        assert template.channels['A'] is None

    def test_create_without_channels(self):
        """Test creating a PackingTemplate without channels dict."""
        template = PackingTemplate('Empty', 'Empty template')

        assert template.name == 'Empty'
        assert template.description == 'Empty template'
        assert template.channels['R'] is None
        assert template.channels['G'] is None
        assert template.channels['B'] is None
        assert template.channels['A'] is None

    def test_create_with_rgba_channels(self):
        """Test creating a PackingTemplate with all RGBA channels."""
        channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'G': ChannelMap('roughness', 0.5),
            'B': ChannelMap('metallic', 0.0),
            'A': ChannelMap('alpha', 1.0)
        }
        template = PackingTemplate('ORMA', 'ORM with Alpha', channels)

        assert template.channels['A'].map_type == 'alpha'

    def test_create_with_partial_channels(self):
        """Test creating a PackingTemplate with only some channels defined."""
        channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'B': ChannelMap('metallic', 0.0)
        }
        template = PackingTemplate('Partial', 'Partial template', channels)

        assert template.channels['R'].map_type == 'ambient_occlusion'
        assert template.channels['G'] is None
        assert template.channels['B'].map_type == 'metallic'
        assert template.channels['A'] is None

    def test_create_with_none_channels(self):
        """Test creating a PackingTemplate with explicit None channels."""
        channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'G': None,
            'B': ChannelMap('metallic', 0.0),
            'A': None
        }
        template = PackingTemplate('Mixed', 'Mixed template', channels)

        assert template.channels['R'] is not None
        assert template.channels['G'] is None
        assert template.channels['B'] is not None
        assert template.channels['A'] is None


class TestPackingTemplateValidation:
    """Test validation of PackingTemplate parameters."""

    def test_invalid_channel_key_raises_error(self):
        """Test that invalid channel keys raise ValueError."""
        invalid_channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'X': ChannelMap('invalid', 0.5)  # Invalid key
        }

        with pytest.raises(ValueError, match="Invalid channel keys"):
            PackingTemplate('Invalid', 'Invalid template', invalid_channels)

    def test_multiple_invalid_keys_raises_error(self):
        """Test that multiple invalid keys are reported."""
        invalid_channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'X': ChannelMap('invalid', 0.5),
            'Y': ChannelMap('invalid2', 0.5)
        }

        with pytest.raises(ValueError, match="Invalid channel keys"):
            PackingTemplate('Invalid', 'Invalid template', invalid_channels)

    def test_lowercase_channel_key_raises_error(self):
        """Test that lowercase channel keys raise ValueError."""
        invalid_channels = {
            'r': ChannelMap('ambient_occlusion', 1.0)  # Lowercase
        }

        with pytest.raises(ValueError, match="Invalid channel keys"):
            PackingTemplate('Invalid', 'Invalid template', invalid_channels)


class TestChannelRetrieval:
    """Test getting channels from PackingTemplate."""

    def test_get_channel_r(self):
        """Test getting R channel."""
        channels = {'R': ChannelMap('ambient_occlusion', 1.0)}
        template = PackingTemplate('Test', 'Test template', channels)

        channel = template.get_channel('R')

        assert channel is not None
        assert channel.map_type == 'ambient_occlusion'

    def test_get_channel_g(self):
        """Test getting G channel."""
        channels = {'G': ChannelMap('roughness', 0.5)}
        template = PackingTemplate('Test', 'Test template', channels)

        channel = template.get_channel('G')

        assert channel is not None
        assert channel.map_type == 'roughness'

    def test_get_channel_b(self):
        """Test getting B channel."""
        channels = {'B': ChannelMap('metallic', 0.0)}
        template = PackingTemplate('Test', 'Test template', channels)

        channel = template.get_channel('B')

        assert channel is not None
        assert channel.map_type == 'metallic'

    def test_get_channel_a(self):
        """Test getting A channel."""
        channels = {'A': ChannelMap('alpha', 1.0)}
        template = PackingTemplate('Test', 'Test template', channels)

        channel = template.get_channel('A')

        assert channel is not None
        assert channel.map_type == 'alpha'

    def test_get_unused_channel_returns_none(self):
        """Test that getting an unused channel returns None."""
        channels = {'R': ChannelMap('ambient_occlusion', 1.0)}
        template = PackingTemplate('Test', 'Test template', channels)

        channel = template.get_channel('A')

        assert channel is None

    def test_get_channel_invalid_key_raises_error(self):
        """Test that invalid key raises KeyError."""
        template = PackingTemplate('Test', 'Test template')

        with pytest.raises(KeyError, match="Invalid channel key"):
            template.get_channel('X')

    def test_get_channel_lowercase_key_raises_error(self):
        """Test that lowercase key raises KeyError."""
        template = PackingTemplate('Test', 'Test template')

        with pytest.raises(KeyError, match="Invalid channel key"):
            template.get_channel('r')


class TestChannelUsageCheck:
    """Test checking if channels are used."""

    def test_is_channel_used_returns_true_for_used_channel(self):
        """Test is_channel_used returns True for used channels."""
        channels = {'R': ChannelMap('ambient_occlusion', 1.0)}
        template = PackingTemplate('Test', 'Test template', channels)

        assert template.is_channel_used('R') is True

    def test_is_channel_used_returns_false_for_unused_channel(self):
        """Test is_channel_used returns False for unused channels."""
        channels = {'R': ChannelMap('ambient_occlusion', 1.0)}
        template = PackingTemplate('Test', 'Test template', channels)

        assert template.is_channel_used('A') is False

    def test_is_channel_used_with_all_channels(self):
        """Test is_channel_used with all RGBA channels."""
        channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'G': ChannelMap('roughness', 0.5),
            'B': ChannelMap('metallic', 0.0),
            'A': ChannelMap('alpha', 1.0)
        }
        template = PackingTemplate('Test', 'Test template', channels)

        assert template.is_channel_used('R') is True
        assert template.is_channel_used('G') is True
        assert template.is_channel_used('B') is True
        assert template.is_channel_used('A') is True

    def test_is_channel_used_invalid_key_raises_error(self):
        """Test that invalid key raises KeyError."""
        template = PackingTemplate('Test', 'Test template')

        with pytest.raises(KeyError, match="Invalid channel key"):
            template.is_channel_used('X')


class TestRGBADetection:
    """Test RGBA mode detection."""

    def test_is_rgba_returns_false_for_rgb_template(self):
        """Test is_rgba returns False when alpha channel is unused."""
        channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'G': ChannelMap('roughness', 0.5),
            'B': ChannelMap('metallic', 0.0)
        }
        template = PackingTemplate('ORM', 'Test', channels)

        assert template.is_rgba() is False

    def test_is_rgba_returns_true_for_rgba_template(self):
        """Test is_rgba returns True when alpha channel is used."""
        channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'G': ChannelMap('roughness', 0.5),
            'B': ChannelMap('metallic', 0.0),
            'A': ChannelMap('alpha', 1.0)
        }
        template = PackingTemplate('ORMA', 'Test', channels)

        assert template.is_rgba() is True

    def test_is_rgba_returns_false_for_empty_template(self):
        """Test is_rgba returns False for template with no channels."""
        template = PackingTemplate('Empty', 'Empty template')

        assert template.is_rgba() is False

    def test_is_rgba_with_only_alpha_channel(self):
        """Test is_rgba returns True when only alpha is defined."""
        channels = {'A': ChannelMap('alpha', 1.0)}
        template = PackingTemplate('AlphaOnly', 'Test', channels)

        assert template.is_rgba() is True


class TestGetUsedChannels:
    """Test getting dictionary of used channels."""

    def test_get_used_channels_returns_only_used(self):
        """Test get_used_channels returns only non-None channels."""
        channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'G': ChannelMap('roughness', 0.5),
            'B': ChannelMap('metallic', 0.0)
        }
        template = PackingTemplate('ORM', 'Test', channels)

        used = template.get_used_channels()

        assert len(used) == 3
        assert 'R' in used
        assert 'G' in used
        assert 'B' in used
        assert 'A' not in used

    def test_get_used_channels_empty_template(self):
        """Test get_used_channels returns empty dict for empty template."""
        template = PackingTemplate('Empty', 'Empty template')

        used = template.get_used_channels()

        assert len(used) == 0
        assert used == {}

    def test_get_used_channels_with_alpha(self):
        """Test get_used_channels includes alpha when used."""
        channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'A': ChannelMap('alpha', 1.0)
        }
        template = PackingTemplate('Test', 'Test', channels)

        used = template.get_used_channels()

        assert len(used) == 2
        assert 'R' in used
        assert 'A' in used


class TestStringRepresentation:
    """Test string representations of PackingTemplate."""

    def test_repr(self):
        """Test __repr__ returns valid representation."""
        template = PackingTemplate('ORM', 'Occlusion-Roughness-Metallic')

        result = repr(template)

        assert result == "PackingTemplate(name='ORM', channels=['R', 'G', 'B', 'A'])"

    def test_repr_with_channels(self):
        """Test __repr__ shows all channel keys regardless of usage."""
        channels = {'R': ChannelMap('ambient_occlusion', 1.0)}
        template = PackingTemplate('Test', 'Test', channels)

        result = repr(template)

        assert "name='Test'" in result
        assert "['R', 'G', 'B', 'A']" in result

    def test_str_with_rgb_channels(self):
        """Test __str__ returns human-readable format."""
        channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'G': ChannelMap('roughness', 0.5),
            'B': ChannelMap('metallic', 0.0)
        }
        template = PackingTemplate('ORM', 'Occlusion-Roughness-Metallic', channels)

        result = str(template)

        assert 'ORM: Occlusion-Roughness-Metallic' in result
        assert 'R (ambient_occlusion)' in result
        assert 'G (roughness)' in result
        assert 'B (metallic)' in result

    def test_str_empty_template(self):
        """Test __str__ with empty template."""
        template = PackingTemplate('Empty', 'Empty template')

        result = str(template)

        assert 'Empty: Empty template' in result
        assert 'Channels:' in result

    def test_str_with_alpha_channel(self):
        """Test __str__ includes alpha channel when used."""
        channels = {
            'R': ChannelMap('ambient_occlusion', 1.0),
            'A': ChannelMap('alpha', 1.0)
        }
        template = PackingTemplate('Test', 'Test', channels)

        result = str(template)

        assert 'R (ambient_occlusion)' in result
        assert 'A (alpha)' in result
