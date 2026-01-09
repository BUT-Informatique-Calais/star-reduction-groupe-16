"""
Pipeline controller for astronomical image processing

Orchestrates the image processing pipeline following MVC pattern:
1. Load FITS image (Model)
2. Detect stars (Controller/Processing)
3. Apply global erosion (Controller/Processing)
4. Apply selective erosion (Controller/Processing)
5. Apply global dilatation (Controller/Processing)
6. Apply selective dilatation (Controller/Processing)
7. Display results (View)

Supports both terminal and GUI modes.
"""

from typing import Optional, Callable, List
from pathlib import Path
from ..models import Config, ImageModel
from ..views import ImageView
from ..models import Erosion, Dilatation, SelectiveErosion, SelectiveDilatation, StarDetector


class PipelineController:
    """
    Controller for the astronomical image processing pipeline.

    Orchestrates the workflow by coordinating between models and views.

    Attributes:
        config: Configuration settings (Model)
        view: Image view for output (View)
        on_stars_detected: Callback for star count updates
        on_results_ready: Callback for result paths updates
        on_progress: Callback for progress updates
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        on_stars_detected: Optional[Callable[[int], None]] = None,
        on_results_ready: Optional[Callable[[List[str]], None]] = None,
        on_progress: Optional[Callable[[int, str], None]] = None
    ):
        """
        Initializes the pipeline controller.

        Args:
            config: Configuration settings (defaults to Config())
            on_stars_detected: Callback when stars are detected (receives count)
            on_results_ready: Callback when results are ready (receives paths)
            on_progress: Callback for progress updates (step, message)
        """
        self.config = config or Config()
        self.view = ImageView(self.config.RESULTS_DIR)
        self.on_stars_detected = on_stars_detected
        self.on_results_ready = on_results_ready
        self.on_progress = on_progress
        self._num_stars = 0
        self._result_paths: List[str] = []

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
        image_model = ImageModel(fits_path, self.config.RESULTS_DIR)
        self.view.display_info(f"Shape: {image_model.shape}, Color: {image_model.is_color}")

        # Save original image (Model)
        image_model.save_original(image_model.data, is_color=image_model.is_color)

        # Step 2: Star detection (Controller/Processing)
        self.view.display_step(2, "Detecting stars...")
        detector = StarDetector(
            fwhm=self.config.STAR_FWHM,
            threshold=self.config.STAR_THRESHOLD,
            radius_factor=self.config.STAR_RADIUS_FACTOR
        )
        image_gray = image_model.get_gray_image()
        star_mask, num_stars = detector.detect(image_gray)
        image_model.save_grayscale(star_mask, "starmask")

        # Step 3: Global erosion (Controller/Processing)
        self.view.display_step(3, "Global erosion...")
        erosion = Erosion(
            kernel_size=self.config.EROSION_KERNEL_SIZE,
            iterations=self.config.EROSION_ITERATIONS
        )
        eroded_image = erosion.apply(image_model.image)
        if image_model.is_color:
            image_model.save_color(eroded_image, "eroded")
        else:
            image_model.save_grayscale(eroded_image, "eroded")

        # Step 4: Selective erosion (Controller/Processing)
        self.view.display_step(4, "Selective erosion...")
        selective = SelectiveErosion(blur_sigma=self.config.MASK_BLUR_SIGMA)
        selective_result, smooth_mask = selective.apply(
            image_model.image, eroded_image, star_mask
        )
        if image_model.is_color:
            image_model.save_color(selective_result, "selective_eroded")
        else:
            image_model.save_grayscale(selective_result, "selective_eroded")
        image_model.save_float_mask(smooth_mask, "smooth_mask")

        # Step 5: Global dilatation (Controller/Processing)
        # Apply dilatation to the eroded image
        self.view.display_step(5, "Global dilatation...")
        dilatation = Dilatation(
            kernel_size=self.config.EROSION_KERNEL_SIZE,
            iterations=self.config.EROSION_ITERATIONS
        )
        dilated_image = dilatation.apply(eroded_image)
        if image_model.is_color:
            image_model.save_color(dilated_image, "dilated")
        else:
            image_model.save_grayscale(dilated_image, "dilated")

        # Step 6: Selective dilatation (Controller/Processing)
        # Apply selective dilatation to the dilated image
        self.view.display_step(6, "Selective dilatation...")
        selective_dilatation = SelectiveDilatation(blur_sigma=self.config.MASK_BLUR_SIGMA)
        selective_dilatation_result, _ = selective_dilatation.apply(
            image_model.image, dilated_image, star_mask
        )
        if image_model.is_color:
            image_model.save_color(selective_dilatation_result, "selective_dilated")
        else:
            image_model.save_grayscale(selective_dilatation_result, "selective_dilated")

        # Step 7: Display results (View)
        self.view.display_step(7, "Calculating difference...")
        image_model.save_difference(eroded_image, selective_result)

        # Summary (View)
        self.view.display_summary(num_stars)

    def run_with_fits_path(self, fits_path: Path) -> ImageModel:
        """
        Runs the pipeline with a specific FITS file path.

        Args:
            fits_path: Path to the FITS file to process

        Returns:
            ImageModel: The loaded image model
        """
        # Notify progress
        if self.on_progress:
            self.on_progress(0, "Loading FITS image...")

        # Step 1: Load image (Model)
        image_model = ImageModel(fits_path, self.config.RESULTS_DIR)

        # Save original image (Model)
        image_model.save_original(image_model.data, is_color=image_model.is_color)

        # Notify progress
        if self.on_progress:
            self.on_progress(1, "Detecting stars...")

        # Step 2: Star detection (Controller/Processing)
        detector = StarDetector(
            fwhm=self.config.STAR_FWHM,
            threshold=self.config.STAR_THRESHOLD,
            radius_factor=self.config.STAR_RADIUS_FACTOR
        )
        image_gray = image_model.get_gray_image()
        star_mask, num_stars = detector.detect(image_gray)
        image_model.save_grayscale(star_mask, "starmask")

        # Store and notify star count
        self._num_stars = num_stars
        if self.on_stars_detected:
            self.on_stars_detected(num_stars)

        # Notify progress
        if self.on_progress:
            self.on_progress(2, "Global erosion...")

        # Step 3: Global erosion (Controller/Processing)
        erosion = Erosion(
            kernel_size=self.config.EROSION_KERNEL_SIZE,
            iterations=self.config.EROSION_ITERATIONS
        )
        eroded_image = erosion.apply(image_model.image)
        if image_model.is_color:
            image_model.save_color(eroded_image, "eroded")
        else:
            image_model.save_grayscale(eroded_image, "eroded")

        # Notify progress
        if self.on_progress:
            self.on_progress(3, "Selective erosion...")

        # Step 4: Selective erosion (Controller/Processing)
        selective = SelectiveErosion(blur_sigma=self.config.MASK_BLUR_SIGMA)
        selective_result, smooth_mask = selective.apply(
            image_model.image, eroded_image, star_mask
        )
        if image_model.is_color:
            image_model.save_color(selective_result, "selective_eroded")
        else:
            image_model.save_grayscale(selective_result, "selective_eroded")
        image_model.save_float_mask(smooth_mask, "smooth_mask")

        # Notify progress
        if self.on_progress:
            self.on_progress(4, "Global dilatation...")

        # Step 5: Global dilatation (Controller/Processing)
        # Apply dilatation to the eroded image
        dilatation = Dilatation(
            kernel_size=self.config.EROSION_KERNEL_SIZE,
            iterations=self.config.EROSION_ITERATIONS
        )
        dilated_image = dilatation.apply(eroded_image)
        if image_model.is_color:
            image_model.save_color(dilated_image, "dilated")
        else:
            image_model.save_grayscale(dilated_image, "dilated")

        # Notify progress
        if self.on_progress:
            self.on_progress(5, "Selective dilatation...")

        # Step 6: Selective dilatation (Controller/Processing)
        # Apply selective dilatation to the dilated image
        selective_dilatation = SelectiveDilatation(blur_sigma=self.config.MASK_BLUR_SIGMA)
        selective_dilatation_result, _ = selective_dilatation.apply(
            image_model.image, dilated_image, star_mask
        )
        if image_model.is_color:
            image_model.save_color(selective_dilatation_result, "selective_dilated")
        else:
            image_model.save_grayscale(selective_dilatation_result, "selective_dilated")

        # Notify progress
        if self.on_progress:
            self.on_progress(6, "Calculating difference...")

        # Step 7: Display results (View)
        image_model.save_difference(eroded_image, selective_result)

        # Store result paths (now including dilatation results)
        self._result_paths = [
            str(self.config.RESULTS_DIR / "original.png"),
            str(self.config.RESULTS_DIR / "starmask.png"),
            str(self.config.RESULTS_DIR / "eroded.png"),
            str(self.config.RESULTS_DIR / "selective_eroded.png"),
            str(self.config.RESULTS_DIR / "smooth_mask.png"),
            str(self.config.RESULTS_DIR / "dilated.png"),
            str(self.config.RESULTS_DIR / "selective_dilated.png"),
            str(self.config.RESULTS_DIR / "difference.png"),
        ]

        # Notify results ready
        if self.on_results_ready:
            self.on_results_ready(self._result_paths)

        return image_model

    @property
    def num_stars(self) -> int:
        """Returns the number of detected stars"""
        return self._num_stars

    @property
    def result_paths(self) -> List[str]:
        """Returns the list of result file paths"""
        return self._result_paths

    def __repr__(self) -> str:
        return f"PipelineController(config={self.config})"
