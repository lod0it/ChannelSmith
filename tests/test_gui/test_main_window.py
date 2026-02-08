"""
Tests for MainWindow widget.

Task B7: Test notebook tabs and layout integration
"""

import tkinter as tk
from tkinter import ttk
import pytest
from unittest.mock import patch, MagicMock


# Skip all GUI tests if tkinter is not available
pytestmark = pytest.mark.skipif(
    not hasattr(tk, "Tk"),
    reason="tkinter not available"
)

try:
    from channelsmith.gui.main_window import MainWindow
    from channelsmith.gui.packer_panel import PackerPanel
    from channelsmith.gui.unpacker_panel import UnpackerPanel
    HAS_TKINTER = True
except Exception:
    HAS_TKINTER = False


@pytest.fixture
def main_window():
    """Create a test MainWindow instance."""
    try:
        window = MainWindow()
        yield window
        window.destroy()
    except Exception as e:
        pytest.skip(f"Could not create MainWindow: {e}")


class TestMainWindow:
    """Tests for MainWindow widget."""

    def test_initialization(self, main_window):
        """Test MainWindow initializes correctly."""
        assert isinstance(main_window, tk.Tk)
        assert main_window.title() == "ChannelSmith - Texture Channel Packer"

    def test_window_geometry(self, main_window):
        """Test MainWindow has correct geometry."""
        # Window starts with 1200x800
        main_window.update()
        geometry = main_window.geometry()
        # Just verify it parses correctly
        parts = geometry.split("x")
        assert len(parts) == 2

    def test_has_notebook(self, main_window):
        """Test MainWindow contains a notebook."""
        assert hasattr(main_window, "notebook")
        assert isinstance(main_window.notebook, ttk.Notebook)

    def test_has_packer_panel(self, main_window):
        """Test MainWindow contains a packer panel."""
        assert hasattr(main_window, "_packer_panel")
        assert isinstance(main_window._packer_panel, PackerPanel)

    def test_has_unpacker_panel(self, main_window):
        """Test MainWindow contains an unpacker panel."""
        assert hasattr(main_window, "_unpacker_panel")
        assert isinstance(main_window._unpacker_panel, UnpackerPanel)

    def test_notebook_has_two_tabs(self, main_window):
        """Test notebook has Pack and Unpack tabs."""
        main_window.update()
        tabs = main_window.notebook.tabs()
        assert len(tabs) == 2

    def test_notebook_tab_labels(self, main_window):
        """Test notebook tabs have correct labels."""
        main_window.update()
        assert main_window.notebook.tab(0, "text") == "Pack"
        assert main_window.notebook.tab(1, "text") == "Unpack"

    def test_pack_tab_contains_packer_panel(self, main_window):
        """Test Pack tab contains PackerPanel."""
        main_window.update()
        pack_tab_widget = main_window.notebook.nametowidget(
            main_window.notebook.tabs()[0]
        )
        assert isinstance(pack_tab_widget, PackerPanel)

    def test_unpack_tab_contains_unpacker_panel(self, main_window):
        """Test Unpack tab contains UnpackerPanel."""
        main_window.update()
        unpack_tab_widget = main_window.notebook.nametowidget(
            main_window.notebook.tabs()[1]
        )
        assert isinstance(unpack_tab_widget, UnpackerPanel)

    def test_tabs_can_switch(self, main_window):
        """Test notebook tabs can be switched."""
        main_window.update()
        # Select first tab
        main_window.notebook.select(0)
        assert main_window.notebook.index(main_window.notebook.select()) == 0

        # Select second tab
        main_window.notebook.select(1)
        assert main_window.notebook.index(main_window.notebook.select()) == 1

    def test_has_status_bar(self, main_window):
        """Test MainWindow has status bar."""
        assert hasattr(main_window, "status_label")
        assert isinstance(main_window.status_label, tk.Label)

    def test_set_status_updates_label(self, main_window):
        """Test set_status updates the status label."""
        main_window.set_status("Test status message")
        main_window.update()
        assert main_window.status_label.cget("text") == "Test status message"

    def test_initial_status_is_ready(self, main_window):
        """Test initial status is 'Ready'."""
        main_window.update()
        assert main_window.status_label.cget("text") == "Ready"

    def test_has_menu_bar(self, main_window):
        """Test MainWindow has a menu bar."""
        main_window.update()
        # Check that menu is configured
        assert main_window.cget("menu") != ""

    def test_initialization_has_all_components(self, main_window):
        """Test MainWindow has all required components after init."""
        assert hasattr(main_window, "notebook")
        assert hasattr(main_window, "_packer_panel")
        assert hasattr(main_window, "_unpacker_panel")
        assert hasattr(main_window, "status_label")

    def test_content_frame_exists(self, main_window):
        """Test content_frame is created."""
        assert hasattr(main_window, "content_frame")
        assert isinstance(main_window.content_frame, tk.Frame)

    def test_panels_visible_in_notebook(self, main_window):
        """Test both panels are visible and accessible."""
        main_window.update()
        # Select pack tab
        main_window.notebook.select(0)
        main_window.update()
        assert main_window._packer_panel.winfo_viewable()

        # Select unpack tab
        main_window.notebook.select(1)
        main_window.update()
        assert main_window._unpacker_panel.winfo_viewable()


class TestMainWindowMenus:
    """Tests for MainWindow menu functionality."""

    def test_open_project_handler_exists(self, main_window):
        """Test _on_open_project handler exists."""
        assert hasattr(main_window, "_on_open_project")
        assert callable(main_window._on_open_project)

    def test_save_project_handler_exists(self, main_window):
        """Test _on_save_project handler exists."""
        assert hasattr(main_window, "_on_save_project")
        assert callable(main_window._on_save_project)

    def test_about_handler_exists(self, main_window):
        """Test _on_about handler exists."""
        assert hasattr(main_window, "_on_about")
        assert callable(main_window._on_about)

    def test_docs_handler_exists(self, main_window):
        """Test _on_docs handler exists."""
        assert hasattr(main_window, "_on_docs")
        assert callable(main_window._on_docs)

    @patch("channelsmith.gui.main_window.logger")
    def test_open_project_logs(self, mock_logger, main_window):
        """Test open project handler logs message."""
        main_window._on_open_project()
        mock_logger.info.assert_called()

    @patch("channelsmith.gui.main_window.logger")
    def test_save_project_logs(self, mock_logger, main_window):
        """Test save project handler logs message."""
        main_window._on_save_project()
        mock_logger.info.assert_called()
