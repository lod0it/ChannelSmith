"""
ChannelSmith GUI Package

Simple tkinter interface for pack/unpack workflows.
All GUI code goes here. Core engine in channelsmith/core/.

Structure:
- app.py: Main app entry point
- main_window.py: Root window with menu bar
- template_selector.py: Template dropdown
- image_selector.py: Image picker widget
- packer_panel.py: Pack workflow
- unpacker_panel.py: Unpack workflow
- preview_panel.py: Image preview
- progress.py: Progress bar
- dialogs.py: Error/success/file dialogs
- file_manager.py: Save/load projects
- drag_drop.py: Drag-drop support

To start the app:
    from channelsmith.gui.app import ChannelSmithApp
    app = ChannelSmithApp()
    app.mainloop()

Or from command line:
    python main_gui.py
"""

__version__ = "0.2.0-beta"
