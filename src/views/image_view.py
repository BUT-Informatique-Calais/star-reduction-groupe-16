"""
Image view component

Handles display and saving of processing results:
- Terminal output (headers, steps, summaries)
- Image export (PNG format)
"""

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional


class ImageView:
    """
    Manages display and saving of results.

    Handles both terminal output and image export.

    Attributes:
        results_dir: Destination directory for files
    """

    def __init__(self, results_dir: Path | str = "./results"):
        """
        Initializes the view component.

        Args:
            results_dir: Destination directory
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

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

    # === Image Saving Methods ===

    def save_original(
        self,
        data: np.ndarray,
        is_color: bool = False
    ) -> Path:
        """
        Saves the original image with matplotlib.

        Args:
            data: Image data (float or uint8)
            is_color: True if color image

        Returns:
            Path to saved file
        """
        path = self.results_dir / "original.png"

        if is_color:
            data_norm = (data - data.min()) / (data.max() - data.min())
            plt.imsave(path, data_norm)
        else:
            plt.imsave(path, data, cmap='gray')

        print(f"  → Saved: {path.name}")
        return path

    def save_grayscale(
        self,
        image: np.ndarray,
        filename: str
    ) -> Path:
        """
        Saves a grayscale image with OpenCV.

        Args:
            image: Grayscale image (uint8)
            filename: Filename (without extension)

        Returns:
            Path to saved file
        """
        path = self.results_dir / f"{filename}.png"
        cv.imwrite(str(path), image)
        print(f"  → Saved: {path.name}")
        return path

    def save_color(
        self,
        image: np.ndarray,
        filename: str
    ) -> Path:
        """
        Saves a color image with OpenCV.

        Args:
            image: Color BGR image (uint8)
            filename: Filename (without extension)

        Returns:
            Path to saved file
        """
        path = self.results_dir / f"{filename}.png"
        cv.imwrite(str(path), image)
        print(f"  → Saved: {path.name}")
        return path

    def save_difference(
        self,
        img1: np.ndarray,
        img2: np.ndarray
    ) -> Path:
        """
        Computes and saves the difference between two images.

        Args:
            img1: First image
            img2: Second image

        Returns:
            Path to saved file
        """
        diff = np.abs(img1.astype(np.float32) - img2.astype(np.float32))

        if diff.max() > 0:
            diff_norm = (diff / diff.max() * 255).astype(np.uint8)
        else:
            diff_norm = diff.astype(np.uint8)

        path = self.results_dir / "difference.png"
        cv.imwrite(str(path), diff_norm)
        print(f"  → Saved: {path.name}")
        return path

    def save_float_mask(
        self,
        mask: np.ndarray,
        filename: str
    ) -> Path:
        """
        Saves a float mask [0, 1] as uint8 image.

        Args:
            mask: Float64 mask [0, 1]
            filename: Filename (without extension)

        Returns:
            Path to saved file
        """
        visual = (mask * 255).astype(np.uint8)
        return self.save_grayscale(visual, filename)

    def __repr__(self) -> str:
        return f"ImageView(results_dir={self.results_dir})"


