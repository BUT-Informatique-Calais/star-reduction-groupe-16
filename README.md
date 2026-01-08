# SAE Astro - Selective Erosion for Astronomical Images

A Python project for processing astronomical FITS images using selective erosion and erosion to remove bright stars while preserving nebular structures.

## Description

This project implements an image processing pipeline that:
- Detects stars in astronomical images using the DAOStarFinder algorithm
- Applies morphological erosion to reduce stellar brightness
- Uses selective erosion to protect nebular regions around detected stars
- Generates various output images showing each processing step

## Key Features

- **Star Detection**: Uses photutils' DAOStarFinder with sigma-clipped background statistics
- **Morphological Operations**: OpenCV-based erosion for reducing stellar halos
- **Selective Processing**: Gaussian-blurred masks to interpolate between original and eroded images
- **Multi-format Support**: Handles both grayscale and color FITS images
- **Configurable Parameters**: Adjust FWHM, detection threshold, and blur sigma via CLI

## Algorithm Pipeline

```
1. LOAD        → Load FITS file (grayscale/color)
2. DETECT      → DAOStarFinder creates binary star mask
3. ERODE       → Global morphological erosion
4. SELECTIVE   → Mask-guided interpolation (protect nebulae)
5. SAVE        → Export all intermediate and final results
```

## Installation

### Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Dependencies

```bash
pip install -r requirements.txt
```

**Requirements:**
- Python 3.8+
- astropy==7.2.0
- matplotlib==3.10.8
- numpy==2.4.0
- opencv_python==4.12.0.88
- photutils==1.13.0
- PyQt6==6.8.1
- scipy==1.15.2

## Usage

### Command Line (Terminal Mode)

```bash
python -m src.main
```

### Graphical User Interface (GUI)

The project includes a full-featured PyQt6-based graphical interface:

```bash
python -m src.main --gui
```

#### GUI Features

| Feature | Description |
|---------|-------------|
| **Open FITS** | Opens a file dialog to select a FITS file |
| **Close** | Exits the application |
| **Image Display** | Displays the processed PNG image with scroll support |
| **Stars Detected** | Shows the number of stars found by DAOStarFinder |
| **Result Files** | Lists all output files with paths |
| **Timestamp** | Shows when the results were last updated |

#### GUI Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ [Open FITS]                                              [Close]   │
├─────────────────────────────────────────────────────────────────────┤
│                              │                                      │
│                              │     Stars detected:                  │
│                              │          42                          │
│    [ Scrollable Image ]      │                                      │
│                              │     Result files:                    │
│                              │     • original.png                  │
│                              │     • starmask.png                  │
│                              │     • eroded.png                    │
│                              │     • selective_eroded.png          │
│                              │     • smooth_mask.png               │
│                              │     • difference.png                │
│                              │                                      │
│                              │     Last updated: 2025-01-15 14:30  │
└──────────────────────────────┴──────────────────────────────────────┘
```

#### GUI Technical Details

- **Framework**: PyQt6
- **Class**: `ImageViewGraphic` in `src/views/image_view_gui.py`
- **Features**:
  - Custom dark theme styling
  - Scrollable image area with aspect ratio preservation
  - File dialog with FITS file filter
  - Real-time info panel updates
  - Responsive layout (60% image, 40% info panel)

## Output Files

All results are saved to the `results/` directory:

| File | Description |
|------|-------------|
| `original.png` | Original input image |
| `starmask.png` | Binary mask of detected stars |
| `eroded.png` | Image after global morphological erosion |
| `selective_eroded.png` | Final result with selective erosion |
| `smooth_mask.png` | Gaussian-blurred star mask |
| `difference.png` | Visual difference (eroded - selective) |

## Project Structure

```
SAE_astro/
├── requirements.txt        # Python dependencies
├── examples/               # FITS test files
│   ├── HorseHead.fits      # Grayscale test image
│   ├── test_M31_linear.fits # Color test image
│   └── test_M31_raw.fits   # Color test image
├── results/                # Generated output images
└── src/                    # Source code (MVC Architecture)
    ├── main.py             # Main entry point & CLI
    ├── __init__.py         # Package root
    ├── models/             # Data models & Processing algorithms
    │   ├── __init__.py
    │   ├── config.py       # Configuration data
    │   └── image_model.py  # Image data model & processing algorithms
    ├── views/              # View layer (Display/Output)
    │   ├── __init__.py
    │   ├── image_view.py   # Terminal output & image export
    │   └── image_view_gui.py # PyQt6 GUI application
    └── controllers/        # Controller layer (Flow Orchestration)
        ├── __init__.py
        └── pipeline_controller.py # Pipeline orchestration
```

## MVC Architecture

### Models (`src/models/`) - Data & Processing
Data models and processing algorithms for astronomical images.

#### `config.py`
Configuration data:
```python
@dataclass
class Config:
    STAR_FWHM: float = 4.0
    STAR_THRESHOLD: float = 2.0
    STAR_RADIUS_FACTOR: float = 1.5
    EROSION_KERNEL_SIZE: int = 3
    EROSION_ITERATIONS: int = 1
    MASK_BLUR_SIGMA: float = 5.0
```

#### `image_model.py`
Image data model and processing algorithms:

**Data Model:**
- `ImageModel`: FITS image data model with preprocessing
  - Raw FITS data (float64)
  - Processed image for OpenCV (uint8)
  - FITS header metadata

**Processing Algorithms:**
- `StarDetector`: Star detection using DAOStarFinder from photutils
- `Erosion`: Global morphological erosion for astronomical image processing
- `SelectiveErosion`: Applies selective erosion with mask interpolation

### Views (`src/views/`) - Display/Output
Handles all output (terminal and GUI).

#### `image_view.py`
- `display_header()`: Print project header
- `display_config()`: Print configuration
- `display_step()`: Print processing step
- `display_summary()`: Print summary
- `save_*()`: Export images to PNG

#### `image_view_gui.py`
- `ImageViewGraphic`: PyQt6 main window class
  - `__init__()`: Initialize GUI with results directory
  - `_setup_ui()`: Create all UI components
  - `_setup_styles()`: Apply dark theme styling
  - `_on_open_fits()`: Open file dialog for FITS selection
- `create_app()`: Create QApplication instance
- `main()`: GUI entry point

### Controllers (`src/controllers/`) - Flow Orchestration
Business logic and workflow orchestration.

#### `pipeline_controller.py`
- Orchestrates the 5-step pipeline
- Coordinates models and views
- Handles CLI arguments

## Example Files

Test FITS files are located in the `examples/` directory:

| File | Type | Description |
|------|------|-------------|
| `HorseHead.fits` | Grayscale | Horse Head Nebula region |
| `test_M31_linear.fits` | Color | Andromeda Galaxy (linear stretch) |
| `test_M31_raw.fits` | Color | Andromeda Galaxy (raw) |
