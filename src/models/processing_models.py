"""
Processing models for astronomical image manipulation

Contains image processing algorithms:
- Erosion: Morphological erosion
- SelectiveErosion: Selective erosion with mask interpolation
- StarDetector: Star detection using DAOStarFinder
"""

import numpy as np
import cv2 as cv
from astropy.stats import sigma_clipped_stats
from photutils.detection import DAOStarFinder
from typing import Tuple, Optional


class Erosion:
    """
    Applies morphological erosion on images.

    Uses a structuring kernel to reduce bright regions
    in the image, which allows detailing structures.

    Attributes:
        kernel_size: Size of the structuring kernel (pixels)
        iterations: Number of erosion iterations
    """

    def __init__(
        self,
        kernel_size: int = 3,
        iterations: int = 1
    ):
        """
        Initializes erosion with specified parameters.

        Args:
            kernel_size: Size of the kernel square (must be > 0)
            iterations: Number of times erosion is applied
        """
        self.kernel_size = kernel_size
        self.iterations = iterations

    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        Applies erosion on the image.

        Args:
            image: Input image (uint8, grayscale or color)

        Returns:
            Eroded image with same type and dimensions
        """
        kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
        return cv.erode(image, kernel, iterations=self.iterations)

    def __repr__(self) -> str:
        return (f"Erosion(kernel_size={self.kernel_size}, "
                f"iterations={self.iterations})")


class SelectiveErosion:
    """
    Applies selective erosion with mask interpolation.

    Combines eroded and original images according to a
    smoothed mask to protect structures while eroding stars.

    Formula: I_final = I_original + 0.5 * (I_eroded - I_original) * M

    Attributes:
        blur_sigma: Gaussian blur standard deviation for mask smoothing
    """

    def __init__(self, blur_sigma: float = 5.0):
        """
        Initializes selective erosion.

        Args:
            blur_sigma: Gaussian blur standard deviation (pixels)
        """
        self.blur_sigma = blur_sigma

    def apply(
        self,
        original: np.ndarray,
        eroded: np.ndarray,
        mask: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Applies selective erosion on the image.

        Args:
            original: Original image
            eroded: Image after global erosion
            mask: Binary star mask (uint8, 0 or 255)

        Returns:
            Tuple[result, smooth_mask]: Result image and smoothed mask
        """
        # Convert mask to normalized float64 [0, 1]
        mask_float = mask.astype(np.float64) / 255.0

        # Apply Gaussian blur to smooth transitions
        mask_smooth = cv.GaussianBlur(
            mask_float,
            (3, 3),
            sigmaX=0,
            sigmaY=0
        )

        # Clamp to valid range
        mask_smooth = np.clip(mask_smooth, 0, 1)

        # Apply formula: I_final = I_original + 0.5 * (I_eroded - I_original) * M
        weight = 0.5 * mask_smooth

        # Apply interpolation formula
        if original.ndim == 3:
            # Color image - channel by channel
            result = np.zeros_like(original, dtype=np.float64)
            for i in range(original.shape[2]):
                result[:, :, i] = original[:, :, i].astype(np.float64) + \
                    weight * (eroded[:, :, i].astype(np.float64) - original[:, :, i].astype(np.float64))
        else:
            # Grayscale image
            result = original.astype(np.float64) + \
                weight * (eroded.astype(np.float64) - original.astype(np.float64))

        # Convert to uint8
        result_uint8 = np.clip(result, 0, 255).astype(np.uint8)

        return result_uint8, mask_smooth

    def __repr__(self) -> str:
        return f"SelectiveErosion(blur_sigma={self.blur_sigma})"


class StarDetector:
    """
    Detects stars in an astronomical image and creates a mask.

    Uses the DAOStarFinder algorithm for point source detection
    with background statistics via sigma-clipping.

    Attributes:
        fwhm: Full Width at Half Maximum of stars (pixels)
        threshold: Detection threshold (sigma above background)
        radius_factor: Multiplier factor for mask radius
    """

    def __init__(
        self,
        fwhm: float = 4.0,
        threshold: float = 2.0,
        radius_factor: float = 1.5
    ):
        """
        Initializes the star detector.

        Args:
            fwhm: Full Width at Half Maximum of stars in pixels
            threshold: Detection threshold in number of sigma
            radius_factor: Factor to calculate mask radius
        """
        self.fwhm = fwhm
        self.threshold = threshold
        self.radius_factor = radius_factor

    def detect(self, image: np.ndarray) -> tuple[np.ndarray, int]:
        """
        Detects stars and creates a binary mask.

        Args:
            image: Grayscale image (uint8 or float)

        Returns:
            Tuple[mask, num_stars]: Binary mask and number of detected stars
        """
        # Convert to float64 for calculations
        if image.dtype == np.uint8:
            image_float = image.astype(np.float64)
        else:
            image_float = image.copy()

        # Background statistics with sigma-clipping
        mean, median, std = sigma_clipped_stats(image_float, sigma=3.0)

        # Configure DAOStarFinder
        daofind = DAOStarFinder(
            fwhm=self.fwhm,
            threshold=self.threshold * std
        )

        # Detect sources
        sources = daofind(image_float - median)

        # Handle case where no stars are detected
        if sources is None:
            print("No stars detected!")
            return np.zeros_like(image_float, dtype=np.uint8), 0

        num_stars = len(sources)
        print(f"Number of stars detected: {num_stars}")

        # Create mask
        mask = np.zeros_like(image_float, dtype=np.uint8)
        radius = int(self.fwhm * self.radius_factor)

        # Draw circles around each star
        for x, y in zip(sources['xcentroid'], sources['ycentroid']):
            x, y = int(x), int(y)
            cv.circle(mask, (x, y), radius, (255, 255, 255), -1)

        return mask, num_stars

    def __repr__(self) -> str:
        return (f"StarDetector(fwhm={self.fwhm}, threshold={self.threshold}, "
                f"radius_factor={self.radius_factor})")

