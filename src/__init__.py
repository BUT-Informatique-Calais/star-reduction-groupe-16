"""
SAE Astro - Source Package

MVC Architecture for astronomical image processing.

Package structure:
- models/: Data models only
- views/: Display and terminal output
- controllers/: Processing algorithms and flow control
"""

# Models (Data only)
from .models import (
    Config,
    ImageModel,
    Erosion,
    SelectiveErosion,
    StarDetector,
)

# Views (Display/Output)
from .views import ImageView

# Controllers (Processing and flow)
from .controllers import (
    PipelineController,
)

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


