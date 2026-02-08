"""
Template JSON loader for loading and saving PackingTemplate configurations.

This module provides functions to serialize and deserialize PackingTemplate
instances to/from JSON files, enabling easy template configuration management.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from channelsmith.core.channel_map import ChannelMap
from channelsmith.core.packing_template import PackingTemplate

logger = logging.getLogger(__name__)


class TemplateValidationError(Exception):
    """Raised when a template JSON file is invalid or malformed."""


def load_template(path: str) -> PackingTemplate:  # pylint: disable=too-many-branches
    """
    Load a PackingTemplate from a JSON file.

    Args:
        path: Path to the JSON template file

    Returns:
        PackingTemplate instance loaded from the JSON file

    Raises:
        FileNotFoundError: If the template file does not exist
        TemplateValidationError: If the JSON is malformed or invalid
        json.JSONDecodeError: If the file contains invalid JSON syntax

    Example:
        >>> template = load_template('templates/orm.json')
        >>> template.name
        'ORM'
        >>> template.is_rgba()
        False
    """
    # Check if file exists
    template_path = Path(path)
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {path}")

    # Load and parse JSON
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise TemplateValidationError(
            f"Invalid JSON in template file '{path}': {e}"
        ) from e

    # Validate required fields
    if not isinstance(data, dict):
        raise TemplateValidationError(
            f"Template file '{path}' must contain a JSON object, got {type(data).__name__}"
        )

    if "name" not in data:
        raise TemplateValidationError(
            f"Template file '{path}' missing required field: 'name'"
        )

    if "description" not in data:
        raise TemplateValidationError(
            f"Template file '{path}' missing required field: 'description'"
        )

    # Parse channels (optional field)
    channels_data = data.get("channels", {})
    if not isinstance(channels_data, dict):
        raise TemplateValidationError(
            f"Template 'channels' must be a dictionary, got {type(channels_data).__name__}"
        )

    # Convert channel definitions to ChannelMap instances
    channels = {}
    for channel_key, channel_info in channels_data.items():
        if channel_key not in {"R", "G", "B", "A"}:
            raise TemplateValidationError(
                f"Invalid channel key '{channel_key}' in template '{path}'. "
                f"Valid keys are: R, G, B, A"
            )

        if channel_info is None:
            channels[channel_key] = None
            continue

        if not isinstance(channel_info, dict):
            raise TemplateValidationError(
                f"Channel '{channel_key}' must be a dictionary or null, "
                f"got {type(channel_info).__name__}"
            )

        if "type" not in channel_info:
            raise TemplateValidationError(
                f"Channel '{channel_key}' missing required field: 'type'"
            )

        if "default" not in channel_info:
            raise TemplateValidationError(
                f"Channel '{channel_key}' missing required field: 'default'"
            )

        # Create ChannelMap instance
        try:
            channel_map = ChannelMap(
                map_type=channel_info["type"],
                default_value=float(channel_info["default"]),
                description=channel_info.get("description"),
            )
            channels[channel_key] = channel_map
        except (ValueError, TypeError) as e:
            raise TemplateValidationError(
                f"Invalid channel data for '{channel_key}': {e}"
            ) from e

    # Create and return PackingTemplate
    try:
        template = PackingTemplate(
            name=data["name"],
            description=data["description"],
            channels=channels if channels else None,
        )
        logger.debug("Loaded template '%s' from '%s'", template.name, path)
        return template
    except (ValueError, TypeError) as e:
        raise TemplateValidationError(
            f"Failed to create template from '{path}': {e}"
        ) from e


def save_template(template: PackingTemplate, path: str) -> None:
    """
    Save a PackingTemplate to a JSON file.

    Args:
        template: PackingTemplate instance to save
        path: Path where the JSON file should be saved

    Raises:
        IOError: If the file cannot be written
        TypeError: If template is not a PackingTemplate instance

    Example:
        >>> template = PackingTemplate('Custom', 'My custom template', {
        ...     'R': ChannelMap('ambient_occlusion', 1.0)
        ... })
        >>> save_template(template, 'templates/custom.json')
    """
    if not isinstance(template, PackingTemplate):
        raise TypeError(
            f"Expected PackingTemplate instance, got {type(template).__name__}"
        )

    # Build JSON structure
    data: Dict[str, Any] = {
        "name": template.name,
        "description": template.description,
        "channels": {},
    }

    # Convert ChannelMap instances to dictionaries
    for channel_key, channel_map in template.channels.items():
        if channel_map is None:
            # Skip unused channels in the output for cleaner JSON
            continue

        data["channels"][channel_key] = {
            "type": channel_map.map_type,
            "default": channel_map.default_value,
        }

        # Include description if it's not the auto-generated one
        auto_description = channel_map.map_type.replace("_", " ").title()
        if channel_map.description != auto_description:
            data["channels"][channel_key]["description"] = channel_map.description

    # Ensure parent directory exists
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write JSON file with pretty formatting
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")  # Add trailing newline
        logger.debug("Saved template '%s' to '%s'", template.name, path)
    except IOError as e:
        raise IOError(f"Failed to write template to '{path}': {e}") from e


def validate_template_file(path: str) -> bool:
    """
    Validate a template JSON file without loading it.

    Args:
        path: Path to the JSON template file to validate

    Returns:
        True if the template file is valid

    Raises:
        FileNotFoundError: If the template file does not exist
        TemplateValidationError: If the JSON is malformed or invalid
        json.JSONDecodeError: If the file contains invalid JSON syntax

    Example:
        >>> validate_template_file('templates/orm.json')
        True
    """
    # This is a validation-only wrapper around load_template
    load_template(path)
    return True
