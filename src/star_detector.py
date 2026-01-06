"""
Star detection and mask creation module

Uses DAOStarFinder (photutils) to detect point sources
and creates a binary mask of detected stars.
"""

import numpy as np
import cv2 as cv
from astropy.stats import sigma_clipped_stats
from photutils.detection import DAOStarFinder
from typing import Optional


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

