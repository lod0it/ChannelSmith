"""
Tests for the template_loader module.

This module contains unit tests for loading and saving PackingTemplate
instances from/to JSON files.
"""

import json
import pytest
from pathlib import Path
from channelsmith.core.channel_map import ChannelMap
from channelsmith.core.packing_template import PackingTemplate
from channelsmith.templates.template_loader import (
    load_template,
    save_template,
    validate_template_file,
    TemplateValidationError,
)


class TestLoadTemplate:
    """Test loading templates from JSON files."""

    def test_load_orm_template(self):
        """Test loading the predefined ORM template."""
        template = load_template('channelsmith/templates/orm.json')

        assert template.name == 'ORM'
        assert template.description == 'Occlusion-Roughness-Metallic (Standard PBR)'
        assert template.is_channel_used('R')
        assert template.is_channel_used('G')
        assert template.is_channel_used('B')
        assert template.is_channel_used('A')  # Alpha now supported (optional)
        assert template.get_channel('R').map_type == 'ambient_occlusion'
        assert template.get_channel('G').map_type == 'roughness'
        assert template.get_channel('B').map_type == 'metallic'

    def test_load_ord_template(self):
        """Test loading the predefined ORD template."""
        template = load_template('channelsmith/templates/ord.json')

        assert template.name == 'ORD'
        assert template.description == 'Occlusion-Roughness-Displacement'
        assert template.is_channel_used('R')
        assert template.is_channel_used('G')
        assert template.is_channel_used('B')
        assert template.is_channel_used('A')  # Alpha now supported (optional)
        assert template.get_channel('R').map_type == 'ambient_occlusion'
        assert template.get_channel('G').map_type == 'roughness'
        assert template.get_channel('B').map_type == 'displacement'

    def test_load_template_channel_default_values(self):
        """Test that channel default values are loaded correctly."""
        template = load_template('channelsmith/templates/orm.json')

        assert template.get_channel('R').default_value == 1.0
        assert template.get_channel('G').default_value == 0.5
        assert template.get_channel('B').default_value == 0.0

    def test_load_nonexistent_file_raises_error(self):
        """Test that loading a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Template file not found"):
            load_template('nonexistent_template.json')

    def test_load_invalid_json_raises_error(self, tmp_path):
        """Test that loading invalid JSON raises TemplateValidationError."""
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("{ invalid json }", encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="Invalid JSON"):
            load_template(str(invalid_json))

    def test_load_json_array_raises_error(self, tmp_path):
        """Test that loading a JSON array raises TemplateValidationError."""
        json_array = tmp_path / "array.json"
        json_array.write_text("[]", encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="must contain a JSON object"):
            load_template(str(json_array))

    def test_load_missing_name_raises_error(self, tmp_path):
        """Test that missing 'name' field raises TemplateValidationError."""
        missing_name = tmp_path / "missing_name.json"
        missing_name.write_text(json.dumps({
            "description": "Test template"
        }), encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="missing required field: 'name'"):
            load_template(str(missing_name))

    def test_load_missing_description_raises_error(self, tmp_path):
        """Test that missing 'description' field raises TemplateValidationError."""
        missing_desc = tmp_path / "missing_desc.json"
        missing_desc.write_text(json.dumps({
            "name": "Test"
        }), encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="missing required field: 'description'"):
            load_template(str(missing_desc))

    def test_load_template_without_channels(self, tmp_path):
        """Test loading a template with no channels defined."""
        no_channels = tmp_path / "no_channels.json"
        no_channels.write_text(json.dumps({
            "name": "Empty",
            "description": "Empty template"
        }), encoding='utf-8')

        template = load_template(str(no_channels))

        assert template.name == 'Empty'
        assert not template.is_channel_used('R')
        assert not template.is_channel_used('G')
        assert not template.is_channel_used('B')
        assert not template.is_channel_used('A')

    def test_load_template_with_explicit_null_channels(self, tmp_path):
        """Test loading a template with explicit null channel values."""
        null_channels = tmp_path / "null_channels.json"
        null_channels.write_text(json.dumps({
            "name": "Partial",
            "description": "Partial template with null channels",
            "channels": {
                "R": {"type": "ambient_occlusion", "default": 1.0},
                "G": None,
                "B": {"type": "metallic", "default": 0.0},
                "A": None
            }
        }), encoding='utf-8')

        template = load_template(str(null_channels))

        assert template.is_channel_used('R')
        assert not template.is_channel_used('G')
        assert template.is_channel_used('B')
        assert not template.is_channel_used('A')

    def test_load_invalid_channel_key_raises_error(self, tmp_path):
        """Test that invalid channel key raises TemplateValidationError."""
        invalid_key = tmp_path / "invalid_key.json"
        invalid_key.write_text(json.dumps({
            "name": "Invalid",
            "description": "Invalid template",
            "channels": {
                "X": {"type": "test", "default": 0.5}
            }
        }), encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="Invalid channel key 'X'"):
            load_template(str(invalid_key))

    def test_load_channel_missing_type_raises_error(self, tmp_path):
        """Test that channel missing 'type' field raises error."""
        missing_type = tmp_path / "missing_type.json"
        missing_type.write_text(json.dumps({
            "name": "Test",
            "description": "Test template",
            "channels": {
                "R": {"default": 1.0}
            }
        }), encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="missing required field: 'type'"):
            load_template(str(missing_type))

    def test_load_channel_missing_default_raises_error(self, tmp_path):
        """Test that channel missing 'default' field raises error."""
        missing_default = tmp_path / "missing_default.json"
        missing_default.write_text(json.dumps({
            "name": "Test",
            "description": "Test template",
            "channels": {
                "R": {"type": "ambient_occlusion"}
            }
        }), encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="missing required field: 'default'"):
            load_template(str(missing_default))

    def test_load_channel_invalid_default_value_raises_error(self, tmp_path):
        """Test that invalid default value raises error."""
        invalid_default = tmp_path / "invalid_default.json"
        invalid_default.write_text(json.dumps({
            "name": "Test",
            "description": "Test template",
            "channels": {
                "R": {"type": "ambient_occlusion", "default": 2.0}  # Out of range
            }
        }), encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="Invalid channel data"):
            load_template(str(invalid_default))

    def test_load_channels_not_dict_raises_error(self, tmp_path):
        """Test that non-dict channels field raises error."""
        invalid_channels = tmp_path / "invalid_channels.json"
        invalid_channels.write_text(json.dumps({
            "name": "Test",
            "description": "Test template",
            "channels": "not a dict"
        }), encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="'channels' must be a dictionary"):
            load_template(str(invalid_channels))

    def test_load_channel_info_not_dict_raises_error(self, tmp_path):
        """Test that non-dict channel info raises error."""
        invalid_info = tmp_path / "invalid_info.json"
        invalid_info.write_text(json.dumps({
            "name": "Test",
            "description": "Test template",
            "channels": {
                "R": "not a dict"
            }
        }), encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="must be a dictionary or null"):
            load_template(str(invalid_info))


class TestSaveTemplate:
    """Test saving templates to JSON files."""

    def test_save_simple_template(self, tmp_path):
        """Test saving a simple template to JSON."""
        template = PackingTemplate(
            'Test',
            'Test template',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5)
            }
        )

        output_file = tmp_path / "test.json"
        save_template(template, str(output_file))

        assert output_file.exists()

        # Verify the saved content
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data['name'] == 'Test'
        assert data['description'] == 'Test template'
        assert 'R' in data['channels']
        assert 'G' in data['channels']
        assert data['channels']['R']['type'] == 'ambient_occlusion'
        assert data['channels']['R']['default'] == 1.0
        assert data['channels']['G']['type'] == 'roughness'
        assert data['channels']['G']['default'] == 0.5

    def test_save_template_skips_unused_channels(self, tmp_path):
        """Test that unused channels are not included in saved JSON."""
        template = PackingTemplate(
            'Partial',
            'Partial template',
            {'R': ChannelMap('ambient_occlusion', 1.0)}
        )

        output_file = tmp_path / "partial.json"
        save_template(template, str(output_file))

        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert 'R' in data['channels']
        assert 'G' not in data['channels']
        assert 'B' not in data['channels']
        assert 'A' not in data['channels']

    def test_save_template_creates_parent_directory(self, tmp_path):
        """Test that save_template creates parent directories if needed."""
        template = PackingTemplate('Test', 'Test template')

        nested_path = tmp_path / "subdir" / "nested" / "test.json"
        save_template(template, str(nested_path))

        assert nested_path.exists()
        assert nested_path.parent.exists()

    def test_save_template_with_custom_description(self, tmp_path):
        """Test saving template with custom channel descriptions."""
        template = PackingTemplate(
            'Custom',
            'Custom template',
            {'R': ChannelMap('custom_type', 1.0, 'Custom Description')}
        )

        output_file = tmp_path / "custom.json"
        save_template(template, str(output_file))

        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data['channels']['R']['description'] == 'Custom Description'

    def test_save_template_skips_auto_generated_description(self, tmp_path):
        """Test that auto-generated descriptions are not saved."""
        template = PackingTemplate(
            'Test',
            'Test template',
            {'R': ChannelMap('ambient_occlusion', 1.0)}  # Will auto-generate "Ambient Occlusion"
        )

        output_file = tmp_path / "test.json"
        save_template(template, str(output_file))

        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Auto-generated description should not be in JSON
        assert 'description' not in data['channels']['R']

    def test_save_non_template_raises_error(self, tmp_path):
        """Test that saving a non-PackingTemplate raises TypeError."""
        output_file = tmp_path / "test.json"

        with pytest.raises(TypeError, match="Expected PackingTemplate instance"):
            save_template("not a template", str(output_file))

    def test_save_template_invalid_path_raises_error(self):
        """Test that saving to an invalid path raises IOError."""
        template = PackingTemplate('Test', 'Test template')

        # Use an invalid path (e.g., a directory that can't be created)
        # On Windows, paths with certain characters are invalid
        invalid_path = "Z:\\nonexistent\\invalid\x00path.json"

        with pytest.raises(IOError):
            save_template(template, invalid_path)


class TestRoundTrip:
    """Test saving and loading templates (round-trip)."""

    def test_round_trip_simple_template(self, tmp_path):
        """Test saving and loading a template produces identical result."""
        original = PackingTemplate(
            'RoundTrip',
            'Round trip test template',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0)
            }
        )

        output_file = tmp_path / "roundtrip.json"
        save_template(original, str(output_file))
        loaded = load_template(str(output_file))

        assert loaded.name == original.name
        assert loaded.description == original.description
        assert loaded.get_channel('R').map_type == original.get_channel('R').map_type
        assert loaded.get_channel('R').default_value == original.get_channel('R').default_value
        assert loaded.get_channel('G').map_type == original.get_channel('G').map_type
        assert loaded.get_channel('B').map_type == original.get_channel('B').map_type

    def test_round_trip_rgba_template(self, tmp_path):
        """Test round-trip with RGBA template."""
        original = PackingTemplate(
            'RGBA',
            'RGBA template',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
                'A': ChannelMap('alpha', 1.0)
            }
        )

        output_file = tmp_path / "rgba.json"
        save_template(original, str(output_file))
        loaded = load_template(str(output_file))

        assert loaded.is_rgba() == original.is_rgba()
        assert loaded.get_channel('A').map_type == 'alpha'

    def test_round_trip_empty_template(self, tmp_path):
        """Test round-trip with empty template (no channels)."""
        original = PackingTemplate('Empty', 'Empty template')

        output_file = tmp_path / "empty.json"
        save_template(original, str(output_file))
        loaded = load_template(str(output_file))

        assert loaded.name == original.name
        assert loaded.description == original.description
        assert not loaded.is_channel_used('R')
        assert not loaded.is_channel_used('G')
        assert not loaded.is_channel_used('B')
        assert not loaded.is_channel_used('A')


class TestValidateTemplateFile:
    """Test template file validation."""

    def test_validate_valid_template(self):
        """Test validating a valid template file."""
        result = validate_template_file('channelsmith/templates/orm.json')
        assert result is True

    def test_validate_invalid_template_raises_error(self, tmp_path):
        """Test validating an invalid template raises error."""
        invalid = tmp_path / "invalid.json"
        invalid.write_text("{ invalid json }", encoding='utf-8')

        with pytest.raises(TemplateValidationError):
            validate_template_file(str(invalid))

    def test_validate_nonexistent_file_raises_error(self):
        """Test validating non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            validate_template_file('nonexistent.json')
