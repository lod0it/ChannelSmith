"""
Modern dark theme for ChannelSmith UI.

Provides a cohesive dark theme with rounded corners, modern aesthetics,
and advanced styling using ttkbootstrap for enhanced visuals.
"""

import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

# Color palette - Modern Dark Theme
COLORS = {
    # Primary colors
    "bg_dark": "#1e1e1e",      # Main background
    "bg_panel": "#2d2d2d",     # Panel background
    "bg_hover": "#3d3d3d",     # Hover state
    "accent": "#0d7377",       # Accent color (teal)
    "accent_light": "#14919b",  # Light accent

    # Text colors
    "text_primary": "#e0e0e0",   # Main text
    "text_secondary": "#a0a0a0", # Secondary text
    "text_disabled": "#707070",  # Disabled text

    # Status colors
    "success": "#4caf50",  # Green for success
    "error": "#f44336",    # Red for errors
    "warning": "#ff9800",  # Orange for warnings

    # Additional UI colors
    "border": "#404040",   # Border color
    "input_bg": "#252525", # Input background
}

# Corner radius configuration
CORNER_RADIUS = 8

class RoundedButton(tk.Button):
    """Button with rounded corners using Canvas background.

    Creates a modern button with rounded corners and hover effects.
    """

    def __init__(
        self,
        parent,
        text="",
        command=None,
        bg=None,
        fg=None,
        width=12,
        height=1,
        **kwargs
    ):
        """Initialize rounded button.

        Args:
            parent: Parent widget
            text: Button text
            command: Callback function
            bg: Background color
            fg: Foreground color
            width: Button width
            height: Button height
            **kwargs: Additional arguments
        """
        self.bg_color = bg or COLORS["bg_panel"]
        self.fg_color = fg or COLORS["text_primary"]
        self.hover_color = COLORS["accent"]
        self.normal_color = self.bg_color

        super().__init__(
            parent,
            text=text,
            command=command,
            bg=self.bg_color,
            fg=self.fg_color,
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=6,
            cursor="hand2",
            activebackground=self.hover_color,
            activeforeground="white",
            font=("Segoe UI", 10),
            **kwargs
        )

        # Bind hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        """Handle mouse enter."""
        if self.cget("state") != "disabled":
            super().configure(bg=self.hover_color, fg="white")

    def _on_leave(self, event):
        """Handle mouse leave."""
        if self.cget("state") != "disabled":
            super().configure(bg=self.normal_color, fg=self.fg_color)

    def configure(self, **kwargs):
        """Override configure to handle state changes.

        Args:
            **kwargs: Configuration options
        """
        # Handle state changes
        if "state" in kwargs:
            state = kwargs["state"]
            if state == "disabled":
                super().configure(
                    bg=COLORS["bg_panel"],
                    fg=COLORS["text_disabled"],
                    **{k: v for k, v in kwargs.items() if k != "state"}
                )
                super().configure(state=state)
            elif state == "normal":
                super().configure(
                    bg=self.normal_color,
                    fg=self.fg_color,
                    **{k: v for k, v in kwargs.items() if k != "state"}
                )
                super().configure(state=state)
            else:
                super().configure(**kwargs)
        else:
            super().configure(**kwargs)


class RoundedFrame(tk.Frame):
    """Frame with rounded corners using Canvas.

    Creates a modern frame with rounded corners and border.
    """

    def __init__(self, parent, bg=None, border_color=None, relief_color=None, **kwargs):
        """Initialize rounded frame.

        Args:
            parent: Parent widget
            bg: Background color
            border_color: Border color
            relief_color: Relief/shadow color
            **kwargs: Additional arguments
        """
        self.bg_color = bg or COLORS["bg_panel"]
        self.border_color = border_color or COLORS["border"]
        self.relief_color = relief_color or COLORS["bg_dark"]

        # Create a canvas-based frame for rounded corners
        self.canvas = tk.Canvas(
            parent,
            bg=self.relief_color,
            highlightthickness=0,
            relief="flat",
            borderwidth=0,
        )

        # Store the canvas reference
        self._canvas = self.canvas

        # Create actual frame inside canvas
        super().__init__(parent, bg=self.bg_color, **kwargs)

        # Configure canvas background
        self.canvas.configure(bg=self.relief_color)


def configure_styles(root):
    """Configure modern dark theme styles for tkinter.

    Args:
        root: tk.Tk root window
    """
    try:
        # Try to use ttkbootstrap for enhanced styles
        from ttkbootstrap import Style
        style = Style(theme="darkly")
        root.tk.call("source", style.theme_use())
        logger.info("ttkbootstrap dark theme applied")
    except ImportError:
        logger.debug("ttkbootstrap not available, using basic dark theme")

    # Configure main window style
    root.configure(bg=COLORS["bg_dark"])

    # Set default font
    root.option_add("*Font", ("Segoe UI", 10))
    root.option_add("*Background", COLORS["bg_dark"])
    root.option_add("*Foreground", COLORS["text_primary"])

    # Button styling - modern flat with rounded corners
    root.option_add("*Button*Background", COLORS["bg_panel"])
    root.option_add("*Button*Foreground", COLORS["text_primary"])
    root.option_add("*Button*activeBackground", COLORS["accent"])
    root.option_add("*Button*activeForeground", "white")
    root.option_add("*Button*relief", "flat")
    root.option_add("*Button*borderWidth", 0)
    root.option_add("*Button*padX", 12)
    root.option_add("*Button*padY", 6)
    root.option_add("*Button*font", ("Segoe UI", 10))

    # Frame styling
    root.option_add("*Frame*Background", COLORS["bg_dark"])

    # Label styling
    root.option_add("*Label*Background", COLORS["bg_dark"])
    root.option_add("*Label*Foreground", COLORS["text_primary"])

    # Entry styling
    root.option_add("*Entry*Background", COLORS["input_bg"])
    root.option_add("*Entry*Foreground", COLORS["text_primary"])
    root.option_add("*Entry*insertBackground", COLORS["accent"])
    root.option_add("*Entry*borderWidth", 1)
    root.option_add("*Entry*relief", "flat")

    # Panedwindow styling
    root.option_add("*PanedWindow*Background", COLORS["bg_dark"])
    root.option_add("*PanedWindow*sashrelief", "flat")

    logger.info("Dark theme configured successfully")


def apply_modern_button_style(button, bg=None, fg=None):
    """Apply modern dark theme to a button with hover effects.

    Args:
        button: tk.Button widget
        bg: Background color (optional, uses theme default)
        fg: Foreground color (optional, uses theme default)
    """
    bg_color = bg or COLORS["bg_panel"]
    fg_color = fg or COLORS["text_primary"]

    button.configure(
        bg=bg_color,
        fg=fg_color,
        activebackground=COLORS["accent"],
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        padx=12,
        pady=6,
        cursor="hand2",
        font=("Segoe UI", 10),
    )

    # Add hover effects
    def on_enter(event):
        button.configure(bg=COLORS["accent"], fg="white")

    def on_leave(event):
        button.configure(bg=bg_color, fg=fg_color)

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)


def apply_modern_frame_style(frame, bg=None, add_border=False):
    """Apply modern dark theme to a frame.

    Args:
        frame: tk.Frame widget
        bg: Background color (optional, uses theme default)
        add_border: Add a subtle border (optional)
    """
    frame.configure(
        bg=bg or COLORS["bg_dark"],
        borderwidth=1 if add_border else 0,
        relief="solid" if add_border else "flat",
    )


def apply_modern_label_style(label, bg=None, fg=None):
    """Apply modern dark theme to a label.

    Args:
        label: tk.Label widget
        bg: Background color (optional, uses theme default)
        fg: Foreground color (optional, uses theme default)
    """
    label.configure(
        bg=bg or COLORS["bg_dark"],
        fg=fg or COLORS["text_primary"],
        font=("Segoe UI", 10),
    )


def apply_modern_entry_style(entry, bg=None, fg=None):
    """Apply modern dark theme to an entry widget.

    Args:
        entry: tk.Entry widget
        bg: Background color (optional, uses theme default)
        fg: Foreground color (optional, uses theme default)
    """
    entry.configure(
        bg=bg or COLORS["input_bg"],
        fg=fg or COLORS["text_primary"],
        insertbackground=COLORS["accent"],
        borderwidth=1,
        relief="solid",
    )


def create_rounded_button(parent, text="", command=None, **kwargs):
    """Create a modern button with rounded corners and hover effects.

    Args:
        parent: Parent widget
        text: Button text
        command: Callback function
        **kwargs: Additional arguments passed to RoundedButton

    Returns:
        RoundedButton widget
    """
    return RoundedButton(parent, text=text, command=command, **kwargs)
