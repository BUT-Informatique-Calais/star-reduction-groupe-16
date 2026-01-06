"""
Selective erosion by interpolation module

Implements selective erosion that protects nebular structures
while only eroding bright stars.

Formula: I_final = (M × I_erode) + ((1-M) × I_original)
"""

import numpy as np
import cv2 as cv
from typing import Tuple


class SelectiveErosion:
    """
    Applies selective erosion with mask interpolation.
    
    Combines eroded and original images according to a
    smoothed mask to protect structures while eroding stars.
    
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
        # Use 3x3 kernel to preserve mask values while smoothing edges
        mask_smooth = cv.GaussianBlur(
            mask_float,
            (3, 3),
            sigmaX=0,
            sigmaY=0
        )
        
        # Clamp to valid range
        mask_smooth = np.clip(mask_smooth, 0, 1)
        
        # Apply interpolation formula
        if original.ndim == 3:
            # Color image - channel by channel
            result = np.zeros_like(original, dtype=np.float64)
            for i in range(original.shape[2]):
                result[:, :, i] = (
                    mask_smooth * eroded[:, :, i].astype(np.float64) +
                    (1 - mask_smooth) * original[:, :, i].astype(np.float64)
                )
        else:
            # Grayscale image
            result = (
                mask_smooth * eroded.astype(np.float64) +
                (1 - mask_smooth) * original.astype(np.float64)
            )
        
        # Convert to uint8
        result_uint8 = np.clip(result, 0, 255).astype(np.uint8)
        
        return result_uint8, mask_smooth
    
    def __repr__(self) -> str:
        return f"SelectiveErosion(blur_sigma={self.blur_sigma})"

