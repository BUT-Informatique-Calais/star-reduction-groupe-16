"""
Models Package - MVC Architecture

Data models and processing algorithms for astronomical images.
"""


from .config import Config
from .image_model import (
    ImageModel,
    Erosion,
    Dilatation,
    SelectiveErosion,
    SelectiveDilatation,
    StarDetector,
)
from .state_manager import StateManager

__all__ = [
    'Config',
    'ImageModel',
    'Erosion',
    'Dilatation',
    'SelectiveErosion',
    'SelectiveDilatation',
    'StarDetector',
    'StateManager',
]

