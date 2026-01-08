"""
Centralized project configuration for SAE Astro

All configurable parameters are defined here.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Literal


@dataclass
class Config:
    """SAE Astro project configuration"""

    # Paths
    EXAMPLES_DIR: Path = Path("./examples")
    RESULTS_DIR: Path = Path("./results")

    # Default FITS file
    DEFAULT_FITS_FILE: Path = EXAMPLES_DIR / "test_M31_linear.fits"

    # Star detection parameters (DAOStarFinder)
    STAR_FWHM: float = 4.0          # Full Width at Half Maximum
    STAR_THRESHOLD: float = 2.0     # Detection threshold (sigma)
    STAR_RADIUS_FACTOR: float = 1.5 # Mask radius = FWHM * factor

    # Erosion parameters
    EROSION_KERNEL_SIZE: int = 3    # Kernel size (pixels)
    EROSION_ITERATIONS: int = 1     # Number of iterations

    # Smoothed mask parameters (Gaussian blur)
    MASK_BLUR_SIGMA: float = 5.0    # Gaussian blur standard deviation

    # Output
    OUTPUT_FORMAT: Literal["png", "tiff"] = "png"

    # List of generated files
    OUTPUT_FILES = [
        "original",
        "starmask",
        "eroded",
        "selective_eroded",
        "smooth_mask",
        "difference",
    ]

    @classmethod
    def get_fits_file(cls, filename: str = None) -> Path:
        """Returns the path to the FITS file"""
        if filename is None:
            return cls.DEFAULT_FITS_FILE
        return cls.EXAMPLES_DIR / filename

    @classmethod
    def get_result_file(cls, name: str) -> Path:
        """Returns the path to the result file"""
        cls.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        return cls.RESULTS_DIR / f"{name}.{cls.OUTPUT_FORMAT}"

