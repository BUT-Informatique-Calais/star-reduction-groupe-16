"""
FITS image data model and processing algorithms for astronomical images.
"""

from pathlib import Path
from typing import Tuple, Optional
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from astropy.io import fits
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats


class ImageModel:
    """
    FITS image data model with preprocessing.

    Attributes:
        data: Normalized image data (float64)
        image: Image converted for OpenCV (uint8)
        header: FITS file metadata
        results_dir: Destination directory for saved files
    """

    def __init__(self, fits_path: Path | str, results_dir: Path | str = "./results"):
        """
        Initializes the model with a FITS file.

        Args:
            fits_path: Path to the FITS file
            results_dir: Destination directory for saved files
        """
        self.fits_path = Path(fits_path)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
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


class StarDetector:
    """
    Star detection using DAOStarFinder from photutils.
    
    Detects stars in astronomical images using the DAOFIND algorithm.
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
            fwhm: Full Width at Half Maximum of stellar PSF
            threshold: Detection threshold in sigma
            radius_factor: Factor to multiply FWHM for mask radius
        """
        self.fwhm = fwhm
        self.threshold = threshold
        self.radius_factor = radius_factor

    def detect(self, image: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        Detects stars in the image.
        
        Args:
            image: Grayscale image (uint8)
            
        Returns:
            Tuple of (star_mask, num_stars)
        """
        # Calculate background and threshold
        mean, median, std = sigma_clipped_stats(image, sigma=3.0)
        
        # Create star finder
        finder = DAOStarFinder(
            fwhm=self.fwhm,
            threshold=self.threshold * std,
        )
        
        # Find stars
        sources = finder(image - median)
        
        if sources is None:
            return np.zeros_like(image, dtype=np.uint8), 0
        
        num_stars = len(sources)
        
        # Create star mask
        star_mask = np.zeros_like(image, dtype=np.uint8)
        
        for star in sources:
            x, y = star['xcentroid'], star['ycentroid']
            radius = self.fwhm * self.radius_factor
            
            # Draw filled circle for each star
            cv.circle(star_mask, (int(x), int(y)), int(radius), 255, -1)
        
        return star_mask, num_stars


class Erosion:
    """
    Global morphological erosion for astronomical image processing.
    
    Applies erosion to remove small structures and noise from images.
    """

    def __init__(
        self,
        kernel_size: int = 3,
        iterations: int = 1
    ):
        """
        Initializes the erosion processor.
        
        Args:
            kernel_size: Size of the morphological kernel (odd number)
            iterations: Number of times to apply erosion
        """
        self.kernel_size = kernel_size
        self.iterations = iterations

    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        Applies erosion to the image.
        
        Args:
            image: Input image (uint8, grayscale or BGR)
            
        Returns:
            Eroded image
        """
        kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
        eroded = cv.erode(image, kernel, iterations=self.iterations)
        return eroded


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

