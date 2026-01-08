"""
Models Package - MVC Architecture

Data models and processing algorithms for astronomical images.
"""

from .config import Config
from .image_model import (
    ImageModel,
    Erosion,
    SelectiveErosion,
    StarDetector,
)

__all__ = [
    'Config',
    'ImageModel',
    'Erosion',
    'SelectiveErosion',
    'StarDetector',
]

