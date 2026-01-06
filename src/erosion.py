"""
Morphological erosion module

Applies morphological erosion on astronomical images
using a structuring kernel with OpenCV.
"""

import numpy as np
import cv2 as cv
from typing import Optional


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

