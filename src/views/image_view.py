"""
Image view component

Handles display of processing results:
- Terminal output (headers, steps, summaries)
"""

import numpy as np
from typing import Optional


class ImageView:
    """
    Manages display of results.

    Handles terminal output for the processing pipeline.
    """

    def __init__(self, results_dir: Optional[str] = "./results"):
        """
        Initializes the view component.

        Args:
            results_dir: Destination directory (not used for saving anymore)
        """
        pass  # Results dir is now managed by ImageModel

    # === Terminal Display Methods ===

    def display_header(self) -> None:
        """Displays the project header"""
        print("=" * 50)
        print("SAE Astro - Image Processing Pipeline")
        print("=" * 50)

    def display_config(self, filename: str, config) -> None:
        """Displays configuration settings"""
        print(f"\n[FITS File] {filename}")
        print("[Configuration]")
        print(f"  - Star FWHM: {config.STAR_FWHM} px")
        print(f"  - Detection threshold: {config.STAR_THRESHOLD} σ")
        print(f"  - Mask radius: {config.STAR_RADIUS_FACTOR} × FWHM")
        print(f"  - Erosion kernel: {config.EROSION_KERNEL_SIZE}×{config.EROSION_KERNEL_SIZE}")
        print(f"  - Mask blur: σ = {config.MASK_BLUR_SIGMA}")

    def display_step(self, step: int, message: str) -> None:
        """Displays current processing step"""
        print(f"\n[{step}/5] {message}")

    def display_info(self, message: str) -> None:
        """Displays informational message"""
        print(f"     {message}")

    def display_summary(self, num_stars: int) -> None:
        """Displays processing summary"""
        print("\n" + "=" * 50)
        print("SUMMARY OF GENERATED FILES")
        print("=" * 50)
        print("1. original.png        → Original image")
        print("2. starmask.png        → Star mask (binary)")
        print("3. eroded.png          → Global erosion")
        print("4. selective_eroded.png → Selective erosion")
        print("5. smooth_mask.png     → Smoothed mask (gaussian)")
        print("6. difference.png      → Difference (global - selective)")
        print(f"\nStars detected: {num_stars}")
        print("=" * 50)

    def __repr__(self) -> str:
        return f"ImageView()"

