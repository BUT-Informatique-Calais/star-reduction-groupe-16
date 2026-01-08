"""
Models Package - MVC Architecture

Data models for astronomical image processing.
"""

from .config import Config
from .image_model import ImageModel
from .processing_models import (
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

