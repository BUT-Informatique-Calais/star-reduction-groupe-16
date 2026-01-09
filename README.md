# SAE Astro - Selective Erosion for Astronomical Images

A Python project for processing astronomical FITS images using selective erosion and dilatation to remove bright stars while preserving nebular structures.

## Description

This project implements an image processing pipeline that:
- Detects stars in astronomical images using the DAOStarFinder algorithm
- Applies morphological erosion to reduce stellar brightness
- Uses selective erosion to protect nebular regions around detected stars
- Applies morphological dilatation to expand bright structures
- Uses selective dilatation to protect nebular regions around detected stars
- Generates various output images showing each processing step

## Key Features

- **Star Detection**: Uses photutils' DAOStarFinder with sigma-clipped background statistics
- **Morphological Operations**: OpenCV-based erosion and dilatation for processing astronomical images
- **Selective Processing**: Gaussian-blurred masks to interpolate between original and processed images
- **Multi-format Support**: Handles both grayscale and color FITS images
- **Configurable Parameters**: Adjust FWHM, detection threshold, and blur sigma via interactive CLI
- **Interactive Terminal Mode**: Choose FITS file and customize all processing parameters
- **Interactive Tutorial**: Built-in 6-step guided tutorial for new users (GUI)
- **Clickable Results**: Click on result filenames to view the corresponding image (GUI)
- **Advanced Processing**: Real-time parameter tuning with preview in separate window

## Algorithm Pipeline

```
1. LOAD        → Load FITS file (grayscale/color)
2. DETECT      → DAOStarFinder creates binary star mask
3. ERODE       → Global morphological erosion
4. SELECTIVE   → Mask-guided interpolation (protect nebulae)
5. DILATE      → Global morphological dilatation
6. SELECTIVE   → Mask-guided dilatation (protect nebulae)
7. SAVE        → Export all intermediate and final results
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

### Interactive Terminal Mode

```bash
python -m src.main
```

The terminal mode now includes an interactive configuration wizard:

**Step 1: Select FITS File**
```
==================================================
SELECT FITS FILE
==================================================
Available files:
  1. HorseHead.fits         [default]
  2. test_M31_linear.fits
  3. test_M31_raw.fits

[Enter] - Use default (HorseHead.fits)
Type the filename to select another file.
```

**Step 2: Choose Configuration Mode**
```
Configuration mode:
  [Enter] - Use default settings
  custom  - Customize parameters
```

**Step 3: Custom Parameters (if "custom" selected)**
```
==================================================
CUSTOM CONFIGURATION
==================================================
Leave empty to keep default value.
Enter 'cancel' to abort and use all defaults.

  Star FWHM (px) (default: 4.0): 
  Detection threshold (σ) (default: 2.0): 
  Mask radius factor (default: 1.5): 
  Erosion kernel size (px) (default: 3): 
  Erosion iterations (default: 1): 
  Mask blur sigma (default: 5.0): 

==================================================
Configuration complete!
==================================================
```

**Features:**
- **File Selection**: Lists all `.fits` files from `examples/`, shows default with `[default]` marker
- **Default Handling**: Press Enter to use default file or parameters
- **Invalid Input**: Displays error message and uses default value
- **Cancel Support**: Type `cancel` at any parameter prompt to abort and use all defaults
- **Custom Values**: Enter new values to override defaults

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
| **Tuto** | Launches interactive 6-step tutorial |
| **Advanced** | Opens advanced processing window with real-time parameter tuning |
| **Image Display** | Scrollable PNG image display with aspect ratio preservation |
| **Progress Bar** | 7-step processing progress indicator |
| **Stars Detected** | Real-time star count from DAOStarFinder |
| **Clickable Results** | Click filenames to view corresponding images |
| **Result Files** | Lists all output files with click-to-view |
| **Timestamp** | Shows when results were last updated |
| **State Persistence** | Saves/restores session state automatically |
| **Save/Close Dialog** | Prompts to save state before exiting |
| **Open Results Folder** | Opens the results directory in file explorer |

#### GUI Layout

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ No file selected           [Tuto] [⚙] [Open FITS]                    [Close]    │
├─────────────────────────────────────────────────────────────────────────────────┤
│ [==== 0% ====............]                                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                      │                                          │
│                                      │     Stars detected:                      │
│                                      │          XX                              │
│    [ Scrollable Image ]              │                                          │
│                                      │     Result files:                        │
│                                      │     • original.png                       │
│                                      │     • starmask.png                       │
│                                      │     • eroded.png                         │
│                                      │     ────────────────────────────         │
│                                      │     • selective_eroded.png               │
│                                      │     • smooth_mask.png                    │
│                                      │     • dilated.png                        │
│                                      │     • selective_dilated.png              │
│                                      │     • difference.png                     │
│                                      │                                          │
│                                      │     Last updated: XXXX-XX-XX XX:XX       │
└──────────────────────────────┴──────────────────────────────────────────────────┘
```

#### Interactive Tutorial

The GUI includes a built-in 6-step tutorial for new users:

**Step 1:** "Cliquez sur le bouton 'Open FITS' pour charger un fichier FITS"  
Guides users to open a FITS file for processing.

**Step 2:** "Vous avez l'image chargée sous forme de PNG..."  
Explains the displayed image, star count, and result files list.

**Step 3:** "Vous pouvez cliquer sur un nom d'image.png pour voir le résultat du traitement"  
Demonstrates the clickable result filenames feature.

**Step 4:** "Vous pouvez cliquer sur traitement avancé"  
Introduces the advanced processing window.

**Step 5:** "vous pouvez effectuer une dilatation ou érosion avec des parametres dans cette fenetre et voir le résulat en temps réel dans la fenetre principal"  
Explains how to use the advanced processing window with real-time preview.

**Step 6:** "après un traitement, la selection de l'image affiché change pour le fichier correspondant au résultat du traitement"  
Shows that the displayed image updates automatically after processing.

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

#### Advanced Processing Window

The advanced processing window allows real-time parameter tuning:

**Features:**
- **Erosion Parameters**: Kernel size (1-21 px), Iterations (1-20)
- **Dilatation Parameters**: Kernel size (1-21 px), Iterations (1-20)
- **Selective Mode**: Checkbox to enable mask-guided processing
- **Blur Sigma**: Gaussian blur standard deviation (0-50)
- **Apply Erosion**: Applies erosion with current parameters
- **Apply Dilatation**: Applies dilatation with current parameters
- **Real-time Preview**: Results displayed in main window immediately
- **Reset on Close**: Parameters reset to defaults when window closes

**Parameters:**
- Uses the last processing result as input (e.g., dilatation uses eroded image)
- Selective mode uses star mask for protected regions
- Non-selective mode applies global morphological operation

#### GUI Technical Details

- **Framework**: PyQt6
- **Main Window Class**: `ImageViewGraphic` in `src/views/image_view_gui.py`
- **Advanced Window Class**: `AdvancedProcessingWindow` in `src/views/advanced_processing_window.py`
- **Features**:
  - Custom dark theme styling (Fusion style base)
  - Scrollable image area with aspect ratio preservation
  - File dialog with FITS file filter
  - Real-time progress bar (7 steps)
  - Interactive tutorial with QMessageBox popups (6 steps)
  - Advanced processing window with parameter controls
  - Responsive layout with state save/restore on exit
  - Custom signals for MVC communication (pyqtSignal)
  - State persistence with `StateManager` class
  - Results folder explorer integration

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
| `selective_eroded.png` | Result with selective erosion (protects nebulae) |
| `smooth_mask.png` | Gaussian-blurred star mask |
| `dilated.png` | Image after global morphological dilatation |
| `selective_dilated.png` | Result with selective dilatation (protects nebulae) |
| `difference.png` | Visual difference (eroded - selective eroded) |

**Note:** PNG files are automatically deleted when closing the GUI application.

## Project Structure

```
SAE_astro/
├── requirements.txt        # Python dependencies
├── examples/               # FITS test files
│   ├── HorseHead.fits      # Grayscale test image
│   ├── test_M31_linear.fits # Color test image
│   └── test_M31_raw.fits   # Color test image
├── Phase_1/                # Phase 1 documentation
│   └── Preuve_de_concept.txt
├── Phase_2/                # Phase 2 documentation
│   ├── Preuve_EtapeA.txt   # Star detection documentation
│   └── Preuve_EtapeB.txt   # Selective erosion documentation
├── results/                # Generated output images (auto-cleaned on exit)
└── src/                    # Source code (MVC Architecture)
    ├── main.py             # Main entry point & CLI
    ├── __init__.py         # Package root
    ├── models/             # Data models & Processing algorithms
    │   ├── __init__.py
    │   ├── config.py       # Configuration data
    │   ├── image_model.py  # Image data model & processing algorithms
    │   └── state_manager.py # Session state persistence
    ├── views/              # View layer (Display/Output)
    │   ├── __init__.py
    │   ├── image_view.py   # Terminal output & interactive configuration
    │   ├── image_view_gui.py # PyQt6 GUI application
    │   └── advanced_processing_window.py # Advanced parameter controls
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
- `Dilatation`: Global morphological dilatation for astronomical image processing
- `SelectiveDilatation`: Applies selective dilatation with mask interpolation

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
- `ask_mode()`: Prompt for default or custom configuration
- `ask_fits_file()`: Interactive FITS file selection from examples/
- `get_custom_config()`: Interactive parameter configuration wizard
- `save_*()`: Export images to PNG

**Interactive Terminal Features:**
- `ask_fits_file()`: Lists available FITS files, allows selection by filename
- `ask_mode()`: Prompts for "default" or "custom" configuration
- `get_custom_config()`: Walks through all parameters one by one
- `_ask_float()` / `_ask_int()`: Input validation with error handling

#### `image_view_gui.py`
- `ImageViewGraphic`: PyQt6 main window class
  - `__init__()`: Initialize GUI with results directory
  - `_setup_ui()`: Create all UI components including progress bar and tutorial
  - `_setup_styles()`: Apply dark theme styling
  - `_on_open_fits()`: Open file dialog for FITS selection
  - `_on_tuto_clicked()`: Launch interactive 6-step tutorial
  - `_on_advanced_clicked()`: Open advanced processing window
  - `_display_image()`: Display PNG image with aspect ratio preservation
  - `_on_result_clicked()`: Handle click on result filenames
  - `_cleanup_results()`: Delete PNG files on application exit
  - Custom signals: `processing_started`, `processing_finished`, `stars_updated`, `results_updated`
- `create_app()`: Create QApplication instance
- `main()`: GUI entry point

**New GUI Features:**
- **Interactive Tutorial**: 6-step guided walkthrough using QMessageBox popups
- **Progress Bar**: Visual 7-step progress indicator during processing
- **Advanced Processing**: Separate window for real-time parameter tuning
- **Clickable Images**: All result filenames are clickable to display corresponding images
- **Visual Selection**: Currently displayed image is highlighted in green
- **State Persistence**: Saves/restores session automatically on close/launch
- **Save Confirmation Dialog**: Prompts to save state before exiting
- **Responsive Design**: Window resize handling with image aspect ratio preservation
- **Results Folder Access**: Button to open results directory in file explorer

#### `advanced_processing_window.py`
- `AdvancedProcessingWindow`: PyQt6 widget for advanced parameter control
  - `__init__()`: Initialize advanced window with parameter controls
  - `_setup_ui()`: Create parameter input fields and buttons
  - `_setup_styles()`: Apply dark theme styling
  - `_on_apply_erosion()`: Apply erosion with current parameters
  - `_on_apply_dilatation()`: Apply dilatation with current parameters
  - `processing_done`: Signal emitted when processing completes (emits result filename)
- `create_advanced_window()`: Factory function to create window instance

**Advanced Window Features:**
- **Erosion Controls**: Kernel size (odd numbers 1-21), Iterations (1-20)
- **Dilatation Controls**: Kernel size (odd numbers 1-21), Iterations (1-20)
- **Selective Mode Checkbox**: Toggle between global and selective processing
- **Blur Sigma Control**: Gaussian blur standard deviation (0-50)
- **Apply Buttons**: Real-time processing with immediate main window update
- **Reset on Close**: Parameters reset to defaults when window closes
- **Error Handling**: Warning dialog when no image is loaded

### Controllers (`src/controllers/`) - Flow Orchestration
Business logic and workflow orchestration.

#### `pipeline_controller.py`
- Orchestrates the 7-step pipeline
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

### 1. Launch Interactive Terminal Mode

```bash
python -m src.main
```

**Follow the prompts:**
1. Select a FITS file (or press Enter for default)
2. Choose "custom" to modify parameters, or press Enter for defaults
3. Enter custom values or press Enter to keep defaults

### 2. Launch GUI

```bash
python -m src.main --gui
```

### 3. Open a FITS File

Click **"Open FITS"** and navigate to `examples/` directory.

### 4. View Results

The processing pipeline runs automatically:
- Progress bar shows current step
- Stars detected count updates in real-time
- Result files appear in the list below

### 5. Compare Images

Click on any result filename to display that image:
- `original.png` - Original input
- `starmask.png` - Detected stars overlay
- `eroded.png` - After global erosion
- `selective_eroded.png` - Final selective erosion result
- `smooth_mask.png` - Gaussian-blurred mask
- `dilated.png` - After global dilatation
- `selective_dilated.png` - Final selective dilatation result
- `difference.png` - Visual difference map

### 6. Advanced Processing

Click **"⚙ Traitement avancé"** to open the advanced processing window:
1. Adjust erosion/dilatation parameters (kernel size, iterations)
2. Toggle selective mode with star mask protection
3. Set blur sigma for smooth transitions
4. Click "Appliquer érosion" or "Appliquer dilatation"
5. View results immediately in the main window

### 7. Need Help?

Click **"Tuto"** button for the interactive tutorial (GUI only)!

## Interactive Terminal Parameters

When running in "custom" mode, you can configure:

| Parameter | Description | Default | Type |
|-----------|-------------|---------|------|
| Star FWHM | Full Width at Half Maximum of stars | 4.0 px | float |
| Detection threshold | Star detection threshold | 2.0 σ | float |
| Mask radius factor | Radius = FWHM × factor | 1.5 | float |
| Erosion kernel size | Size of erosion kernel | 3 px | int |
| Erosion iterations | Number of erosion passes | 1 | int |
| Mask blur sigma | Gaussian blur for mask | 5.0 | float |

**Validation:**
- Values below minimum are rejected with error message
- Invalid input (non-numeric) shows error and re-prompts
- `cancel` aborts custom configuration and uses all defaults

## Documentation

### Phase 1: Proof of Concept
- File: `Phase_1/Preuve_de_concept.txt`
- Initial erosion implementation
- Basic FITS file handling

### Phase 2: Star Detection & Selective Erosion
- Step A: `Phase_2/Preuve_EtapeA.txt` - Star detection using DAOStarFinder
- Step B: `Phase_2/Preuve_EtapeB.txt` - Selective erosion implementation

## License

This project is part of the SAE (Synthèse d'Activités d'Évaluation) for IUT.

