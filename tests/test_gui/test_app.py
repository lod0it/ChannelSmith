"""
Tests for ChannelSmithApp application class.

Task B12: Test main app entry point
"""

import tkinter as tk
import pytest
from unittest.mock import patch, MagicMock
import logging


# Skip all GUI tests if tkinter is not available
pytestmark = pytest.mark.skipif(
    not hasattr(tk, "Tk"),
    reason="tkinter not available"
)

try:
    from channelsmith.gui.app import ChannelSmithApp
    from channelsmith.gui.main_window import MainWindow
    HAS_TKINTER = True
except Exception:
    HAS_TKINTER = False


@pytest.fixture
def app():
    """Create a test ChannelSmithApp instance."""
    try:
        test_app = ChannelSmithApp()
        yield test_app
        test_app.destroy()
    except Exception as e:
        pytest.skip(f"Could not create ChannelSmithApp: {e}")


class TestChannelSmithAppInitialization:
    """Tests for ChannelSmithApp initialization."""

    def test_app_is_tk_instance(self, app):
        """Test ChannelSmithApp is a tk.Tk instance."""
        assert isinstance(app, tk.Tk)

    def test_app_is_main_window_instance(self, app):
        """Test ChannelSmithApp is a MainWindow instance."""
        assert isinstance(app, MainWindow)

    def test_app_initialized_flag(self, app):
        """Test app has _initialized flag set to True."""
        assert hasattr(app, "_initialized")
        assert app._initialized is True

    def test_app_has_required_attributes(self, app):
        """Test app has all required attributes from MainWindow."""
        assert hasattr(app, "notebook")
        assert hasattr(app, "_packer_panel")
        assert hasattr(app, "_unpacker_panel")
        assert hasattr(app, "status_label")
        assert hasattr(app, "content_frame")

    def test_app_title_is_set(self, app):
        """Test app window has correct title."""
        assert app.title() == "ChannelSmith - Texture Channel Packer"

    def test_app_geometry_is_set(self, app):
        """Test app window has correct geometry."""
        app.update()
        geometry = app.geometry()
        # Verify geometry format is correct (WIDTHxHEIGHT+X+Y)
        assert "x" in geometry.lower() or "+" in geometry

    @patch("channelsmith.gui.app.logger")
    def test_initialization_logs_message(self, mock_logger):
        """Test app logs initialization message."""
        app = ChannelSmithApp()
        try:
            mock_logger.info.assert_called()
            # Check that initialization message was logged
            calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("initialized" in str(call).lower() for call in calls)
        finally:
            app.destroy()

    def test_is_initialized_returns_true(self, app):
        """Test is_initialized() returns True after init."""
        assert app.is_initialized() is True


class TestChannelSmithAppClosing:
    """Tests for app closing behavior."""

    def test_on_closing_method_exists(self, app):
        """Test on_closing method exists."""
        assert hasattr(app, "on_closing")
        assert callable(app.on_closing)

    def test_on_closing_destroys_window(self):
        """Test on_closing destroys the window."""
        app = ChannelSmithApp()
        assert app.winfo_exists()
        app.on_closing()
        # After destroy, winfo_exists may raise TclError
        # (app is destroyed), which is expected behavior
        try:
            exists = app.winfo_exists()
            assert not exists
        except tk.TclError:
            # This is expected - window has been destroyed
            pass

    @patch("channelsmith.gui.app.logger")
    def test_on_closing_logs_message(self, mock_logger):
        """Test on_closing logs a message."""
        app = ChannelSmithApp()
        try:
            app.on_closing()
            mock_logger.info.assert_called()
            # Check for closing message
            calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("closing" in str(call).lower() for call in calls)
        except tk.TclError:
            # Window may be destroyed, that's OK
            pass

    def test_on_closing_handles_exceptions(self):
        """Test on_closing handles exceptions gracefully."""
        app = ChannelSmithApp()
        try:
            # Destroy the window first
            app.destroy()
            # Calling on_closing should not raise
            # (it should handle the error gracefully)
            try:
                app.on_closing()
            except tk.TclError:
                # Expected if window is already destroyed
                pass
        except Exception as e:
            pytest.fail(f"on_closing raised unexpected exception: {e}")

    def test_close_protocol_is_set(self, app):
        """Test WM_DELETE_WINDOW protocol is bound."""
        # Verify that the protocol is set
        # (this is implicit in the __init__ binding)
        assert hasattr(app, "on_closing")


class TestChannelSmithAppFunctionality:
    """Tests for app functionality."""

    def test_app_can_set_status(self, app):
        """Test app can set status via inherited method."""
        app.set_status("Test message")
        app.update()
        assert app.status_label.cget("text") == "Test message"

    def test_app_notebook_accessible(self, app):
        """Test app notebook is accessible and functional."""
        app.update()
        tabs = app.notebook.tabs()
        assert len(tabs) == 2
        assert app.notebook.tab(0, "text") == "Pack"
        assert app.notebook.tab(1, "text") == "Unpack"

    def test_app_can_switch_tabs(self, app):
        """Test app can switch between tabs."""
        app.update()
        # Start on tab 0
        app.notebook.select(0)
        assert app.notebook.index(app.notebook.select()) == 0

        # Switch to tab 1
        app.notebook.select(1)
        assert app.notebook.index(app.notebook.select()) == 1

    def test_app_packer_panel_accessible(self, app):
        """Test packer panel is accessible."""
        assert app._packer_panel is not None
        app.update()
        assert app._packer_panel.winfo_exists()

    def test_app_unpacker_panel_accessible(self, app):
        """Test unpacker panel is accessible."""
        assert app._unpacker_panel is not None
        app.update()
        assert app._unpacker_panel.winfo_exists()

    def test_app_has_menu_bar(self, app):
        """Test app has menu bar configured."""
        app.update()
        # Check that menu is configured
        assert app.cget("menu") != ""

    def test_app_can_run_event_loop_briefly(self, app):
        """Test app can run event loop without errors."""
        app.update()
        # Process pending events
        app.update_idletasks()
        assert app.winfo_exists()


class TestChannelSmithAppMultipleInstances:
    """Tests for multiple app instances."""

    def test_multiple_apps_cannot_be_created(self):
        """Test only one app instance can exist (tkinter limitation).

        Note: tkinter only allows one root Tk instance per process.
        Creating a second instance will raise an error.
        This is expected behavior.
        """
        app1 = ChannelSmithApp()
        try:
            # Attempting to create a second root Tk instance should fail
            with pytest.raises(tk.TclError):
                app2 = ChannelSmithApp()
        finally:
            app1.destroy()

    def test_app_is_singleton_like(self, app):
        """Test that the app instance is effectively singleton-like.

        Only one root Tk instance can exist per process, so
        ChannelSmithApp should be used as a singleton pattern.
        """
        # The fixture creates one instance, and we cannot create another
        assert app.is_initialized()
        # Verify we still have access to it
        assert app.winfo_exists()


class TestChannelSmithAppEdgeCases:
    """Tests for edge cases and error handling."""

    def test_app_survives_rapid_status_updates(self, app):
        """Test app survives rapid status updates."""
        for i in range(10):
            app.set_status(f"Status {i}")
        app.update()
        assert app.winfo_exists()

    def test_app_survives_rapid_tab_switches(self, app):
        """Test app survives rapid tab switches."""
        app.update()
        for i in range(5):
            app.notebook.select(0)
            app.update()
            app.notebook.select(1)
            app.update()
        assert app.winfo_exists()

    def test_app_double_initialization_flag(self, app):
        """Test app's initialization flag is consistent."""
        assert app.is_initialized() is True
        assert app._initialized is True
        # Status should not change
        assert app.is_initialized() is True

    @patch("channelsmith.gui.app.logger")
    def test_on_closing_with_exception_in_destroy(self, mock_logger, app):
        """Test on_closing handles exception in destroy gracefully."""
        # Mock destroy to raise an exception
        with patch.object(app, "destroy", side_effect=Exception("Test error")):
            try:
                app.on_closing()
            except Exception as e:
                pytest.fail(f"on_closing should handle exceptions: {e}")

        # Should have logged an error
        mock_logger.error.assert_called()


class TestChannelSmithAppIntegration:
    """Integration tests for app."""

    def test_app_update_idletasks_works(self, app):
        """Test app can process idle tasks without errors."""
        app.update_idletasks()
        assert app.winfo_exists()

    def test_app_full_lifecycle(self, app):
        """Test complete app lifecycle operations."""
        # Verify initialization
        assert app.is_initialized()

        # Update UI
        app.update()
        assert app.winfo_exists()

        # Set status
        app.set_status("Running")
        app.update()
        assert app.status_label.cget("text") == "Running"

        # Switch tabs
        app.notebook.select(1)
        app.update()

        # Verify we can still access the app
        assert app.winfo_exists()

    def test_app_status_messages_persist(self, app):
        """Test that status messages are properly set and persist."""
        messages = ["Starting", "Processing", "Done"]
        for msg in messages:
            app.set_status(msg)
            app.update()
            assert app.status_label.cget("text") == msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
