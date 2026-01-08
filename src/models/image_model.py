"""
FITS image data model

Handles opening FITS files, normalization and conversion
for astronomical image processing.
"""

from pathlib import Path
from typing import Tuple
import numpy as np
import cv2 as cv
from astropy.io import fits


class ImageModel:
    """
    FITS image data model with preprocessing.

    Attributes:
        data: Normalized image data (float64)
        image: Image converted for OpenCV (uint8)
        header: FITS file metadata
    """

    def __init__(self, fits_path: Path | str):
        """
        Initializes the model with a FITS file.

        Args:
            fits_path: Path to the FITS file
        """
        self.fits_path = Path(fits_path)
        self.data = None
        self.image = None
        self.header = None
        self._load()

    def _load(self) -> None:
        """Loads and processes the FITS image"""
        hdul = fits.open(self.fits_path)

        self.header = hdul[0].header
        data = hdul[0].data

        # Handle color and grayscale images
        if data.ndim == 3:
            # Color image - transpose (3, height, width) -> (height, width, 3)
            if data.shape[0] == 3:
                data = np.transpose(data, (1, 2, 0))

        self.data = data
        self.image = self._prepare_for_opencv(data)
        hdul.close()

    def _prepare_for_opencv(self, data: np.ndarray) -> np.ndarray:
        """
        Converts image for OpenCV with uint8 normalization.

        Args:
            data: Image data (float or uint8)

        Returns:
            Normalized image for OpenCV (uint8)
        """
        if data.ndim == 3:
            # Color image
            image = np.zeros_like(data, dtype='uint8')
            for i in range(data.shape[2]):
                channel = data[:, :, i]
                image[:, :, i] = ((channel - channel.min()) /
                                  (channel.max() - channel.min()) * 255).astype('uint8')
            # RGB -> BGR for OpenCV
            return cv.cvtColor(image, cv.COLOR_RGB2BGR)
        else:
            # Grayscale image
            return ((data - data.min()) / (data.max() - data.min()) * 255).astype('uint8')

    def get_gray_image(self) -> np.ndarray:
        """
        Returns the image in grayscale for star detection.

        Returns:
            Grayscale image (uint8)
        """
        if self.image.ndim == 3:
            return cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        return self.image.copy()

    @property
    def is_color(self) -> bool:
        """Indicates if the image is color"""
        return self.data.ndim == 3

    @property
    def shape(self) -> Tuple[int, ...]:
        """Returns the shape of the image"""
        return self.data.shape

    @property
    def filename(self) -> str:
        """Returns the filename of the loaded FITS file"""
        return self.fits_path.name

    def __repr__(self) -> str:
        return f"ImageModel(path={self.fits_path.name}, shape={self.shape})"

