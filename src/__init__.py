"""
SAE Astro - Source Package

Modules for astronomical image processing (erosion, star detection, etc.)
"""

from .config import Config
from .image_loader import ImageLoader
from .star_detector import StarDetector
from .erosion import Erosion
from .selective_erosion import SelectiveErosion
from .image_saver import ImageSaver

__all__ = [
    'Config',
    'ImageLoader',
    'StarDetector',
    'Erosion',
    'SelectiveErosion',
    'ImageSaver',
]

