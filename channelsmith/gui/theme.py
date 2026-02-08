"""
Modern dark theme for ChannelSmith UI.

Provides a cohesive dark theme with rounded corners and modern aesthetics.
"""

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
}

def configure_styles(root):
    """Configure modern dark theme styles for tkinter.

    Args:
        root: tk.Tk root window
    """
    # Configure main window style
    root.configure(bg=COLORS["bg_dark"])

    # Set default font
    root.option_add("*Font", ("Segoe UI", 10))
    root.option_add("*Background", COLORS["bg_dark"])
    root.option_add("*Foreground", COLORS["text_primary"])

    # Button styling
    root.option_add("*Button*Background", COLORS["bg_panel"])
    root.option_add("*Button*Foreground", COLORS["text_primary"])
    root.option_add("*Button*activeBackground", COLORS["accent"])
    root.option_add("*Button*activeForeground", "white")
    root.option_add("*Button*relief", "flat")
    root.option_add("*Button*borderWidth", 0)
    root.option_add("*Button*padX", 12)
    root.option_add("*Button*padY", 6)

    # Frame styling
    root.option_add("*Frame*Background", COLORS["bg_dark"])

    # Label styling
    root.option_add("*Label*Background", COLORS["bg_dark"])
    root.option_add("*Label*Foreground", COLORS["text_primary"])


def apply_modern_button_style(button, bg=None, fg=None):
    """Apply modern dark theme to a button.

    Args:
        button: tk.Button widget
        bg: Background color (optional, uses theme default)
        fg: Foreground color (optional, uses theme default)
    """
    button.configure(
        bg=bg or COLORS["bg_panel"],
        fg=fg or COLORS["text_primary"],
        activebackground=COLORS["accent"],
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        padx=12,
        pady=6,
        cursor="hand2",
    )


def apply_modern_frame_style(frame, bg=None):
    """Apply modern dark theme to a frame.

    Args:
        frame: tk.Frame widget
        bg: Background color (optional, uses theme default)
    """
    frame.configure(
        bg=bg or COLORS["bg_dark"],
        borderwidth=0,
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
    )
