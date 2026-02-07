"""
Template management for ChannelSmith.

This package contains template loader functions and predefined template
JSON files for common channel packing configurations.
"""

from channelsmith.templates.template_loader import (
    load_template,
    save_template,
    validate_template_file,
    TemplateValidationError,
)

__all__ = [
    'load_template',
    'save_template',
    'validate_template_file',
    'TemplateValidationError',
]
