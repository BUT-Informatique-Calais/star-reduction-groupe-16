"""
Pipeline controller for astronomical image processing

Orchestrates the image processing pipeline following MVC pattern:
1. Load FITS image (Model)
2. Detect stars (Model)
3. Apply global erosion (Model)
4. Apply selective erosion (Model)
5. Save results (View)
"""

from pathlib import Path
from typing import Optional
from ..models import (
    Config,
    ImageModel,
    Erosion,
    SelectiveErosion,
    StarDetector,
)
from ..views import ImageView


class PipelineController:
    """
    Controller for the astronomical image processing pipeline.

    Orchestrates the workflow by coordinating between models and views.

    Attributes:
        config: Configuration settings (Model)
        view: Image view for output (View)
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initializes the pipeline controller.

        Args:
            config: Configuration settings (defaults to Config())
        """
        self.config = config or Config()
        self.view = ImageView(self.config.RESULTS_DIR)

    def run(self, fits_file: str | Path = None) -> None:
        """
        Runs the complete image processing pipeline.

        Args:
            fits_file: Path to the FITS file (optional)
        """
        print("=" * 50)
        print("SAE Astro - Image Processing Pipeline")
        print("=" * 50)

        # Get FITS file path
        fits_path = self.config.get_fits_file(
            str(fits_file) if fits_file else None
        )

        print(f"\n[FITS File] {fits_path.name}")
        print(f"[Configuration]")
        print(f"  - Star FWHM: {self.config.STAR_FWHM} px")
        print(f"  - Detection threshold: {self.config.STAR_THRESHOLD} σ")
        print(f"  - Mask radius: {self.config.STAR_RADIUS_FACTOR} × FWHM")
        print(f"  - Erosion kernel: {self.config.EROSION_KERNEL_SIZE}×{self.config.EROSION_KERNEL_SIZE}")
        print(f"  - Mask blur: σ = {self.config.MASK_BLUR_SIGMA}")

        # Step 1: Load image (Model)
        print("\n[1/5] Loading FITS image...")
        image_model = ImageModel(fits_path)
        print(f"     Shape: {image_model.shape}, Color: {image_model.is_color}")

        # Save original image (View)
        self.view.save_original(image_model.data, is_color=image_model.is_color)

        # Step 2: Star detection (Model)
        print("\n[2/5] Detecting stars...")
        detector = StarDetector(
            fwhm=self.config.STAR_FWHM,
            threshold=self.config.STAR_THRESHOLD,
            radius_factor=self.config.STAR_RADIUS_FACTOR
        )
        image_gray = image_model.get_gray_image()
        star_mask, num_stars = detector.detect(image_gray)
        self.view.save_grayscale(star_mask, "starmask")

        # Step 3: Global erosion (Model)
        print("\n[3/5] Global erosion...")
        erosion = Erosion(
            kernel_size=self.config.EROSION_KERNEL_SIZE,
            iterations=self.config.EROSION_ITERATIONS
        )
        eroded_image = erosion.apply(image_model.image)
        if image_model.is_color:
            self.view.save_color(eroded_image, "eroded")
        else:
            self.view.save_grayscale(eroded_image, "eroded")

        # Step 4: Selective erosion (Model)
        print("\n[4/5] Selective erosion...")
        selective = SelectiveErosion(blur_sigma=self.config.MASK_BLUR_SIGMA)
        selective_result, smooth_mask = selective.apply(
            image_model.image, eroded_image, star_mask
        )
        if image_model.is_color:
            self.view.save_color(selective_result, "selective_eroded")
        else:
            self.view.save_grayscale(selective_result, "selective_eroded")
        self.view.save_float_mask(smooth_mask, "smooth_mask")

        # Step 5: Calculate and save difference (View)
        print("\n[5/5] Calculating difference...")
        self.view.save_difference(eroded_image, selective_result)

        # Summary
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
        print(f"Directory: {self.config.RESULTS_DIR}")
        print("=" * 50)

    def __repr__(self) -> str:
        return f"PipelineController(config={self.config})"

