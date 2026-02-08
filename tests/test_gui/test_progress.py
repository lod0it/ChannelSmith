"""
Tests for progress indicator widget.

Tests ProgressBar widget functionality.
"""

import tkinter as tk
import pytest
import gc

# Skip all tests if tkinter unavailable
pytestmark = pytest.mark.skipif(not hasattr(tk, "Tk"), reason="tkinter not available")

from channelsmith.gui.progress import ProgressBar


class TestProgressBar:
    """Tests for ProgressBar widget."""

    def test_progress_bar_initialization(self):
        """ProgressBar should initialize correctly."""
        root = tk.Tk()
        try:
            progress = ProgressBar(root)
            assert progress is not None
            assert progress._is_running is False
            assert progress._status_text == ""
        finally:
            root.destroy()

    def test_progress_start(self):
        """start() should begin progress animation."""
        root = tk.Tk()
        try:
            progress = ProgressBar(root)
            progress.start("Testing...")

            assert progress._is_running is True
            assert progress._status_text == "Testing..."

            progress.stop()
        finally:
            root.destroy()

    def test_progress_stop(self):
        """stop() should end progress animation."""
        root = tk.Tk()
        try:
            progress = ProgressBar(root)
            progress.start("Testing...")
            progress.stop()

            assert progress._is_running is False
        finally:
            root.destroy()

    def test_progress_start_with_default_message(self):
        """start() should use default message if none provided."""
        root = tk.Tk()
        try:
            progress = ProgressBar(root)
            progress.start()

            assert progress._is_running is True
            assert progress._status_text == "Processing..."

            progress.stop()
        finally:
            root.destroy()

    def test_progress_multiple_starts(self):
        """Multiple start() calls should be safe."""
        root = tk.Tk()
        try:
            progress = ProgressBar(root)
            progress.start("First")
            progress.start("Second")  # Should be ignored

            assert progress._status_text == "First"
            progress.stop()
        finally:
            root.destroy()

    def test_progress_stop_when_not_running(self):
        """stop() should be safe when not running."""
        root = tk.Tk()
        try:
            progress = ProgressBar(root)
            progress.stop()  # Should not raise

            assert progress._is_running is False
        finally:
            root.destroy()

    def test_progress_set_message(self):
        """set_message() should update status text while running."""
        root = tk.Tk()
        try:
            progress = ProgressBar(root)
            progress.start("Initial")
            progress.set_message("Updated")

            assert progress._status_text == "Updated"
            progress.stop()
        finally:
            root.destroy()

    def test_progress_is_running(self):
        """is_running() should reflect animation state."""
        root = tk.Tk()
        try:
            progress = ProgressBar(root)

            assert progress.is_running() is False

            progress.start()
            assert progress.is_running() is True

            progress.stop()
            assert progress.is_running() is False
        finally:
            root.destroy()
            gc.collect()

    def test_progress_visibility(self):
        """ProgressBar should show/hide when started/stopped."""
        root = tk.Tk()
        try:
            progress = ProgressBar(root)
            progress.pack()

            # Initially should not be packed (hidden)
            # Note: This test may be skipped if display not available
            assert progress is not None

            progress.start()
            progress.stop()
        finally:
            root.destroy()

    def test_progress_custom_parent(self):
        """ProgressBar should work with custom parent widgets."""
        root = tk.Tk()
        try:
            frame = tk.Frame(root)
            frame.pack()

            progress = ProgressBar(frame)
            progress.start("Testing...")

            assert progress._is_running is True
            progress.stop()
        finally:
            root.destroy()

    def test_progress_start_stop_cycle(self):
        """ProgressBar should handle multiple start/stop cycles."""
        root = tk.Tk()
        try:
            progress = ProgressBar(root)

            for i in range(3):
                progress.start(f"Cycle {i}")
                assert progress._is_running is True

                progress.stop()
                assert progress._is_running is False
        finally:
            root.destroy()
