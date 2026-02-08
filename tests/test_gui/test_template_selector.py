"""
Tests for TemplateSelector widget.

Task B2: Test template selector functionality
"""

import tkinter as tk
from tkinter import ttk
import pytest
from unittest.mock import patch, MagicMock


# Skip all GUI tests if tkinter display is not available
pytestmark = pytest.mark.skipif(
    not hasattr(tk, "Tk"),
    reason="tkinter not available"
)

try:
    from channelsmith.gui.template_selector import TemplateSelector, BUILTIN_TEMPLATES
    HAS_TKINTER = True
except Exception:
    HAS_TKINTER = False


@pytest.fixture
def root():
    """Create a test root window."""
    try:
        root = tk.Tk()
        yield root
        root.destroy()
    except Exception as e:
        pytest.skip(f"Could not create tk.Tk: {e}")


@pytest.fixture
def selector(root):
    """Create a TemplateSelector widget."""
    selector = TemplateSelector(root)
    selector.pack()
    root.update()
    return selector


class TestTemplateSelector:
    """Tests for TemplateSelector widget."""

    def test_initialization(self, selector):
        """Test TemplateSelector initializes with correct defaults."""
        assert selector.get_selected_template() == "ORM"

    def test_dropdown_contains_builtin_templates(self, selector):
        """Test dropdown contains ORM and ORD options."""
        values = selector._combo["values"]
        assert "ORM" in values
        assert "ORD" in values

    def test_dropdown_selection(self, selector):
        """Test selecting different template from dropdown."""
        selector._combo.set("ORD")
        selector._combo.event_generate("<<ComboboxSelected>>")
        assert selector.get_selected_template() == "ORD"

    def test_builtin_templates_constant(self):
        """Test BUILTIN_TEMPLATES constant is correct."""
        assert BUILTIN_TEMPLATES == ["ORM", "ORD"]

    def test_get_selected_template_returns_string(self, selector):
        """Test get_selected_template returns a string."""
        result = selector.get_selected_template()
        assert isinstance(result, str)

    @patch("tkinter.filedialog.askopenfilename")
    def test_load_custom_template(self, mock_dialog, selector):
        """Test loading a custom template file."""
        # Mock the file dialog to return a test path
        mock_dialog.return_value = "/path/to/custom.json"

        # Click the Load Custom button
        selector._on_load_custom()

        # Verify file dialog was called
        mock_dialog.assert_called_once()

        # Verify the selected template is now the custom path
        assert selector.get_selected_template() == "/path/to/custom.json"

    @patch("tkinter.filedialog.askopenfilename")
    def test_load_custom_template_cancelled(self, mock_dialog, selector):
        """Test cancelling custom template load."""
        # Mock the file dialog to return empty string (cancelled)
        mock_dialog.return_value = ""
        original_template = selector.get_selected_template()

        # Click the Load Custom button
        selector._on_load_custom()

        # Verify the selected template hasn't changed
        assert selector.get_selected_template() == original_template

    def test_widget_is_frame(self, selector):
        """Test TemplateSelector is a tk.Frame."""
        assert isinstance(selector, tk.Frame)
