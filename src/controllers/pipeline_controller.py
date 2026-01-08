"""
Pipeline controller for astronomical image processing

Orchestrates the image processing pipeline following MVC pattern:
1. Load FITS image (Model)
2. Detect stars (Controller/Processing)
3. Apply global erosion (Controller/Processing)
4. Apply selective erosion (Controller/Processing)
5. Display results (View)
"""

from typing import Optional
from ..models import Config, ImageModel
from ..views import ImageView
from ..models import Erosion, SelectiveErosion, StarDetector


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

    def run(self) -> None:
        """
        Runs the complete image processing pipeline using default configuration.
        """
        self.view.display_header()

        # Get FITS file path (uses default)
        fits_path = self.config.get_fits_file()

        self.view.display_config(fits_path.name, self.config)

        # Step 1: Load image (Model)
        self.view.display_step(1, "Loading FITS image...")
        image_model = ImageModel(fits_path)
        self.view.display_info(f"Shape: {image_model.shape}, Color: {image_model.is_color}")

        # Save original image (View)
        self.view.save_original(image_model.data, is_color=image_model.is_color)

        # Step 2: Star detection (Controller/Processing)
        self.view.display_step(2, "Detecting stars...")
        detector = StarDetector(
            fwhm=self.config.STAR_FWHM,
            threshold=self.config.STAR_THRESHOLD,
            radius_factor=self.config.STAR_RADIUS_FACTOR
        )
        image_gray = image_model.get_gray_image()
        star_mask, num_stars = detector.detect(image_gray)
        self.view.save_grayscale(star_mask, "starmask")

        # Step 3: Global erosion (Controller/Processing)
        self.view.display_step(3, "Global erosion...")
        erosion = Erosion(
            kernel_size=self.config.EROSION_KERNEL_SIZE,
            iterations=self.config.EROSION_ITERATIONS
        )
        eroded_image = erosion.apply(image_model.image)
        if image_model.is_color:
            self.view.save_color(eroded_image, "eroded")
        else:
            self.view.save_grayscale(eroded_image, "eroded")

        # Step 4: Selective erosion (Controller/Processing)
        self.view.display_step(4, "Selective erosion...")
        selective = SelectiveErosion(blur_sigma=self.config.MASK_BLUR_SIGMA)
        selective_result, smooth_mask = selective.apply(
            image_model.image, eroded_image, star_mask
        )
        if image_model.is_color:
            self.view.save_color(selective_result, "selective_eroded")
        else:
            self.view.save_grayscale(selective_result, "selective_eroded")
        self.view.save_float_mask(smooth_mask, "smooth_mask")

        # Step 5: Display results (View)
        self.view.display_step(5, "Calculating difference...")
        self.view.save_difference(eroded_image, selective_result)

        # Summary (View)
        self.view.display_summary(num_stars)

    def __repr__(self) -> str:
        return f"PipelineController(config={self.config})"


