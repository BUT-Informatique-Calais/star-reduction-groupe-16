"""
SAE Astro - Source Package

MVC Architecture for astronomical image processing.

Package structure:
- models/: Data models and processing algorithms
- views/: Output and visualization components
- controllers/: Pipeline orchestration
"""

# Models
from .models import (
    Config,
    ImageModel,
    Erosion,
    SelectiveErosion,
    StarDetector,
)

# Views
from .views import ImageView

# Controllers
from .controllers import PipelineController

__all__ = [
    # Models
    'Config',
    'ImageModel',
    'Erosion',
    'SelectiveErosion',
    'StarDetector',
    # Views
    'ImageView',
    # Controllers
    'PipelineController',
]

__version__ = "2.0.0"

