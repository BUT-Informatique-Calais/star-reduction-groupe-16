#!/usr/bin/env python3
"""
Main entry point for SAE Astro project

Orchestrates the astronomical image processing pipeline:
1. Load FITS file (Model)
2. Star detection (Model)
3. Global erosion (Model)
4. Selective erosion (Model)
5. Save results (View)

Supports both terminal and GUI modes.
"""

import sys
from src import (
    PipelineController,
)
from src.views import ImageViewGraphic


def run_pipeline() -> None:
    """
    Runs the complete image processing pipeline using default configuration.
    """
    controller = PipelineController()
    controller.run()


def run_gui() -> None:
    """
    Launches the graphical user interface.
    Loads saved state if available.
    """
    from src.views.image_view_gui import create_app, create_window
    from src.models import Config, StateManager

    app = create_app()

    # Check for saved state
    state_manager = StateManager(Config.STATE_FILE)
    saved_state = state_manager.load_state() if state_manager.has_saved_state() else None

    window = create_window(saved_state=saved_state)
    window.show()
    app.exec()


def main():
    """Main entry point with mode selection"""
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        run_gui()
    else:
        run_pipeline()


if __name__ == "__main__":
    main()

