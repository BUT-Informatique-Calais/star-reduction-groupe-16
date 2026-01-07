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
- scipy==1.15.2

## Usage

### Command Line

```bash
python main.py [FITS_FILE]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `FITS_FILE` | Path to FITS file (relative to `examples/`) | `test_M31_linear.fits` |

### Examples

```bash
# Using default file (test_M31_linear.fits)
python main.py

# Using a specific FITS file
python main.py HorseHead.fits
```

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
├── main.py                 # Main entry point & CLI
├── requirements.txt        # Python dependencies
├── examples/               # FITS test files
│   ├── HorseHead.fits      # Grayscale test image
│   ├── test_M31_linear.fits # Color test image
│   └── test_M31_raw.fits   # Color test image
├── results/                # Generated output images
└── src/                    # Source code
    ├── config.py           # Centralized configuration
    ├── image_loader.py     # FITS file loading (astropy)
    ├── image_saver.py      # PNG export utilities
    ├── star_detector.py    # DAOStarFinder integration
    ├── erosion.py          # Morphological erosion (OpenCV)
    └── selective_erosion.py # Mask-guided interpolation
```

## Source Code Overview

### `src/config.py`
Centralized configuration with default parameters:
- `STAR_FWHM`: 4.0 (pixel size of stars)
- `STAR_THRESHOLD`: 2.0 (sigma detection threshold)
- `STAR_RADIUS_FACTOR`: 1.5 (mask radius multiplier)
- `EROSION_KERNEL_SIZE`: 3 (pixels)
- `MASK_BLUR_SIGMA`: 5.0 (gaussian blur)

### `src/star_detector.py`
- Uses `photutils.detection.DAOStarFinder`
- Sigma-clipped background statistics
- Creates binary circular masks around detected stars

### `src/erosion.py`
- OpenCV morphological erosion
- Configurable kernel size and iterations

### `src/selective_erosion.py`
- Applies formula: I_final = I_original + 0.5 × (I_eroded - I_original) × M
- Gaussian-smoothed mask prevents sharp transitions
- Protects nebular structures while reducing star brightness

## Example Files

Test FITS files are located in the `examples/` directory:

| File | Type | Description |
|------|------|-------------|
| `HorseHead.fits` | Grayscale | Horse Head Nebula region |
| `test_M31_linear.fits` | Color | Andromeda Galaxy (linear stretch) |
| `test_M31_raw.fits` | Color | Andromeda Galaxy (raw) |
