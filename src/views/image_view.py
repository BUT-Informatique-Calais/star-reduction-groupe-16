"""
Image view component

Handles display of processing results:
- Terminal output (headers, steps, summaries)
- Interactive parameter configuration
"""

import numpy as np
from pathlib import Path
from typing import Optional, Tuple
from ..models import Config


class ImageView:
    """
    Manages display of results.

    Handles terminal output for the processing pipeline.
    """

    def __init__(self, results_dir: Optional[str] = "./results"):
        """
        Initializes the view component.

        Args:
            results_dir: Destination directory (not used for saving anymore)
        """
        pass  # Results dir is now managed by ImageModel

    # === Interactive Configuration Methods ===

    def ask_mode(self) -> str:
        """
        Asks user to choose between default and custom configuration.
        
        Returns:
            "default" or "custom"
        """
        print("\nConfiguration mode:")
        print("  [Enter] - Use default settings")
        print("  custom  - Customize parameters")
        choice = input("Choice: ").strip().lower()
        
        if choice == "custom":
            return "custom"
        return "default"

    def ask_fits_file(self, examples_dir: Path, default_file: Path) -> Tuple[Path, bool]:
        """
        Asks user to select a FITS file from the examples directory.
        
        Args:
            examples_dir: Path to examples directory
            default_file: Default FITS file path
            
        Returns:
            Tuple of (selected_path, was_default_used)
        """
        # List all .fits files in examples directory
        fits_files = sorted(examples_dir.glob("*.fits"))
        
        print("\n" + "=" * 50)
        print("SELECT FITS FILE")
        print("=" * 50)
        
        # Display available files
        print("Available files:")
        for i, f in enumerate(fits_files, 1):
            marker = " [default]" if f == default_file else ""
            print(f"  {i}. {f.name}{marker}")
        
        print(f"\n[Enter] - Use default ({default_file.name})")
        print("Type the filename to select another file.")
        
        user_input = input("Choice: ").strip()
        
        if user_input == "":
            return default_file, True
        
        # Try to find the file by name
        for f in fits_files:
            if f.name == user_input:
                return f, True
        
        # Invalid input - use default and warn
        print(f"    → Invalid file '{user_input}', using default: {default_file.name}")
        return default_file, False

    def get_custom_config(self, default_config: Config) -> Config:
        """
        Interactive configuration wizard - asks for each parameter one by one.
        
        Args:
            default_config: Configuration with default values
            
        Returns:
            Config: Modified configuration (does not modify original defaults)
        """
        print("\n" + "=" * 50)
        print("CUSTOM CONFIGURATION")
        print("=" * 50)
        print("Leave empty to keep default value.")
        print("Enter 'cancel' to abort and use all defaults.\n")
        
        # Create a copy of default config
        config = Config(
            STAR_FWHM=default_config.STAR_FWHM,
            STAR_THRESHOLD=default_config.STAR_THRESHOLD,
            STAR_RADIUS_FACTOR=default_config.STAR_RADIUS_FACTOR,
            EROSION_KERNEL_SIZE=default_config.EROSION_KERNEL_SIZE,
            EROSION_ITERATIONS=default_config.EROSION_ITERATIONS,
            MASK_BLUR_SIGMA=default_config.MASK_BLUR_SIGMA,
            EXAMPLES_DIR=default_config.EXAMPLES_DIR,
            RESULTS_DIR=default_config.RESULTS_DIR,
            DEFAULT_FITS_FILE=default_config.DEFAULT_FITS_FILE,
            OUTPUT_FORMAT=default_config.OUTPUT_FORMAT,
            STATE_FILE=default_config.STATE_FILE
        )
        
        # Ask for each parameter
        config.STAR_FWHM = self._ask_float("Star FWHM (px)", config.STAR_FWHM, 0.1)
        config.STAR_THRESHOLD = self._ask_float("Detection threshold (σ)", config.STAR_THRESHOLD, 0.1)
        config.STAR_RADIUS_FACTOR = self._ask_float("Mask radius factor", config.STAR_RADIUS_FACTOR, 0.1)
        config.EROSION_KERNEL_SIZE = self._ask_int("Erosion kernel size (px)", config.EROSION_KERNEL_SIZE, 1)
        config.EROSION_ITERATIONS = self._ask_int("Erosion iterations", config.EROSION_ITERATIONS, 0)
        config.MASK_BLUR_SIGMA = self._ask_float("Mask blur sigma", config.MASK_BLUR_SIGMA, 0.1)
        
        print("\n" + "=" * 50)
        print("Configuration complete!")
        print("=" * 50)
        
        return config

    def _ask_float(self, prompt: str, default: float, min_val: float) -> float:
        """
        Ask user for a float value.
        
        Args:
            prompt: Parameter description
            default: Default value
            min_val: Minimum allowed value
            
        Returns:
            User input or default value
        """
        while True:
            user_input = input(f"  {prompt} (default: {default}): ").strip()
            
            if user_input == "":
                return default
            
            if user_input.lower() == "cancel":
                print("    → Aborted, using all defaults")
                return default
            
            try:
                value = float(user_input)
                if value < min_val:
                    print(f"    → Invalid: value must be >= {min_val}")
                    continue
                return value
            except ValueError:
                print("    → Invalid input, please enter a number")

    def _ask_int(self, prompt: str, default: int, min_val: int) -> int:
        """
        Ask user for an integer value.
        
        Args:
            prompt: Parameter description
            default: Default value
            min_val: Minimum allowed value
            
        Returns:
            User input or default value
        """
        while True:
            user_input = input(f"  {prompt} (default: {default}): ").strip()
            
            if user_input == "":
                return default
            
            if user_input.lower() == "cancel":
                print("    → Aborted, using all defaults")
                return default
            
            try:
                value = int(user_input)
                if value < min_val:
                    print(f"    → Invalid: value must be >= {min_val}")
                    continue
                return value
            except ValueError:
                print("    → Invalid input, please enter an integer")

    # === Terminal Display Methods ===

    def display_header(self) -> None:
        """Displays the project header"""
        print("=" * 50)
        print("SAE Astro - Image Processing Pipeline")
        print("=" * 50)

    def display_config(self, filename: str, config) -> None:
        """Displays configuration settings"""
        print(f"\n[FITS File] {filename}")
        print("[Configuration]")
        print(f"  - Star FWHM: {config.STAR_FWHM} px")
        print(f"  - Detection threshold: {config.STAR_THRESHOLD} σ")
        print(f"  - Mask radius: {config.STAR_RADIUS_FACTOR} × FWHM")
        print(f"  - Erosion kernel: {config.EROSION_KERNEL_SIZE}×{config.EROSION_KERNEL_SIZE}")
        print(f"  - Mask blur: σ = {config.MASK_BLUR_SIGMA}")

    def display_step(self, step: int, message: str) -> None:
        """Displays current processing step"""
        print(f"\n[{step}/5] {message}")

    def display_info(self, message: str) -> None:
        """Displays informational message"""
        print(f"     {message}")

    def display_summary(self, num_stars: int) -> None:
        """Displays processing summary"""
        print("\n" + "=" * 50)
        print("SUMMARY OF GENERATED FILES")
        print("=" * 50)
        print("1. original.png        → Original image")
        print("2. starmask.png        → Star mask (binary)")
        print("3. eroded.png          → Global erosion")
        print("4. selective_eroded.png → Selective erosion")
        print("5. smooth_mask.png     → Smoothed mask (gaussian)")
        print("6. difference.png      → Difference (global - selective)")
        print(f"\nStars detected: {num_stars}")
        print("=" * 50)

    def __repr__(self) -> str:
        return f"ImageView()"

