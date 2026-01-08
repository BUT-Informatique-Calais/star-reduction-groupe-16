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
- **Interactive Tutorial**: Built-in 3-step guided tutorial for new users
- **Clickable Results**: Click on result filenames to view the corresponding image

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
| **Close** | Exits with save/cleanup confirmation dialog |
| **Tuto** | Launches interactive 3-step tutorial |
| **Image Display** | Scrollable PNG image display with aspect ratio preservation |
| **Progress Bar** | 5-step processing progress indicator |
| **Stars Detected** | Real-time star count from DAOStarFinder |
| **Clickable Results** | Click filenames to view corresponding images |
| **Result Files** | Lists all output files with click-to-view |
| **Timestamp** | Shows when results were last updated |
| **State Persistence** | Saves/restores session state automatically |
| **Save/Close Dialog** | Prompts to save state before exiting |

#### GUI Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ No file selected           [Tuto] [Open FITS]            [Close]    │
├─────────────────────────────────────────────────────────────────────┤
│ [==== 0% ====............]                                          |
├─────────────────────────────────────────────────────────────────────┤
│                              │                                      │
│                              │     Stars detected:                  │
│                              │          XX                          │
│    [ Scrollable Image ]      │                                      │
│                              │     Result files:                    │
│                              │     • original.png                   │
│                              │     • starmask.png                   │
│                              │     • eroded.png                     │
│                              │     ────────────────────────────     │
│                              │     • selective_eroded.png           │
│                              │     • smooth_mask.png                │
│                              │     • difference.png                 │
│                              │                                      │
│                              │     Last updated: XXXX-XX-XX XX:XX   │
└──────────────────────────────┴──────────────────────────────────────┘
```

#### Interactive Tutorial

The GUI includes a built-in 3-step tutorial for new users:

**Step 1:** "Cliquez sur le bouton 'Open FITS' pour charger un fichier FITS"  
Guides users to open a FITS file for processing.

**Step 2:** "Vous avez l'image chargée sous forme de PNG..."  
Explains the displayed image, star count, and result files list.

**Step 3:** "Vous pouvez cliquer sur un nom d'image.png pour voir le résultat du traitement"  
Demonstrates the clickable result filenames feature.

To start the tutorial, click the **"Tuto"** button in the top-right corner.

#### Clickable Result Images

All result filenames in the GUI are clickable:
- Click any filename (e.g., "starmask.png") to display that image
- Currently displayed image is highlighted in green
- Enables easy comparison between processing stages

#### State Persistence

The GUI includes automatic state save/restore functionality:

**Saving State:**
When closing the application, a dialog asks whether to save the current session:
- **Yes**: Saves current FITS file path, displayed image, and star count to `results/state.json`
- **No**: Deletes all PNG files and clears saved state
- **Cancel**: Returns to the application without closing

**Restoring State:**
On next launch:
- Automatically detects if saved state exists
- Restores the previously loaded FITS file path
- Shows the last displayed image
- Restores star count and timestamp

**State File:**
- Location: `results/state.json`
- Contains: `fits_file`, `displayed_image`, `num_stars`, `timestamp`
- Cleared when clicking "No" in close dialog

#### GUI Technical Details

- **Framework**: PyQt6
- **Class**: `ImageViewGraphic` in `src/views/image_view_gui.py`
- **Features**:
  - Custom dark theme styling (Fusion style base)
  - Scrollable image area with aspect ratio preservation
  - File dialog with FITS file filter
  - Real-time progress bar (5 steps)
  - Interactive tutorial with QMessageBox popups
  - Responsive layout with state save/restore on exit
  - Custom signals for MVC communication (pyqtSignal)
  - State persistence with `StateManager` class

#### State Manager (`src/models/state_manager.py`)

State management for GUI session persistence:

- `StateManager`: Handles save/load of application state
  - `save_state(fits_file, displayed_image, num_stars)`: Saves session to JSON
  - `load_state()`: Loads saved session from JSON
  - `has_saved_state()`: Checks if saved state exists
  - `clear_state()`: Removes saved state file
  - State file: `results/state.json`

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

**Note:** PNG files are automatically deleted when closing the application.

## Project Structure

```
SAE_astro/
├── requirements.txt        # Python dependencies
├── examples/               # FITS test files
│   ├── HorseHead.fits      # Grayscale test image
│   ├── test_M31_linear.fits # Color test image
│   └── test_M31_raw.fits   # Color test image
├── results/                # Generated output images (auto-cleaned on exit)
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

#### `state_manager.py`
State management for GUI session persistence:

- `StateManager`: Handles save/load of application state
  - `__init__(state_file)`: Initialize with path to state file
  - `save_state(fits_file, displayed_image, num_stars)`: Saves session to JSON
  - `load_state()`: Loads saved session from JSON
  - `has_saved_state()`: Checks if saved state exists
  - `clear_state()`: Removes saved state file

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
  - `_setup_ui()`: Create all UI components including progress bar and tutorial
  - `_setup_styles()`: Apply dark theme styling
  - `_on_open_fits()`: Open file dialog for FITS selection
  - `_on_tuto_clicked()`: Launch interactive 3-step tutorial
  - `_display_image()`: Display PNG image with aspect ratio preservation
  - `_on_result_clicked()`: Handle click on result filenames
  - `_cleanup_results()`: Delete PNG files on application exit
  - Custom signals: `processing_started`, `processing_finished`, `stars_updated`, `results_updated`
- `create_app()`: Create QApplication instance
- `main()`: GUI entry point

**New GUI Features:**
- **Interactive Tutorial**: 3-step guided walkthrough using QMessageBox popups
- **Progress Bar**: Visual 5-step progress indicator during processing
- **Clickable Images**: All result filenames are clickable to display corresponding images
- **Visual Selection**: Currently displayed image is highlighted in green
- **State Persistence**: Saves/restores session automatically on close/launch
- **Save Confirmation Dialog**: Prompts to save state before exiting
- **Responsive Design**: Window resize handling with image aspect ratio preservation

### Controllers (`src/controllers/`) - Flow Orchestration
Business logic and workflow orchestration.

#### `pipeline_controller.py`
- Orchestrates the 5-step pipeline
- Coordinates models and views
- Handles CLI arguments
- Supports callback-based progress tracking
- Callback signatures:
  - `on_progress(step, message)`: Progress update callback
  - `on_stars_detected(count)`: Stars count callback
  - `on_results_ready(paths)`: Results ready callback

## Example Files

Test FITS files are located in the `examples/` directory:

| File | Type | Description |
|------|------|-------------|
| `HorseHead.fits` | Grayscale | Horse Head Nebula region |
| `test_M31_linear.fits` | Color | Andromeda Galaxy (linear stretch) |
| `test_M31_raw.fits` | Color | Andromeda Galaxy (raw) |

## Quick Start

### 1. Launch GUI

```bash
python -m src.main --gui
```

### 2. Open a FITS File

Click **"Open FITS"** and navigate to `examples/` directory.

### 3. View Results

The processing pipeline runs automatically:
- Progress bar shows current step
- Stars detected count updates in real-time
- Result files appear in the list below

### 4. Compare Images

Click on any result filename to display that image:
- `original.png` - Original input
- `starmask.png` - Detected stars overlay
- `eroded.png` - After global erosion
- `selective_eroded.png` - Final selective erosion result
- `smooth_mask.png` - Gaussian-blurred mask
- `difference.png` - Visual difference map

### 5. Need Help?

Click **"Tuto"** button for the interactive tutorial!
