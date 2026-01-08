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
    """
    from src.views.image_view_gui import create_app
    app = create_app()
    window = ImageViewGraphic()
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

