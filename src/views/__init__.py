"""
Views Package - MVC Architecture

View components for astronomical image processing.
"""

from .image_view import ImageView
from .image_view_gui import ImageViewGraphic

__all__ = [
    'ImageView',
    'ImageViewGraphic',
]


