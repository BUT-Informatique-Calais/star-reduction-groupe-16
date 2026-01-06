#!/usr/bin/env python3
"""
Main entry point for SAE Astro project

Orchestrates the astronomical image processing pipeline:
1. Load FITS file
2. Star detection
3. Global erosion
4. Selective erosion
5. Save results
"""

from pathlib import Path
from src import (
    Config,
    ImageLoader,
    StarDetector,
    Erosion,
    SelectiveErosion,
    ImageSaver,
)


def run_pipeline(fits_file: str | Path = None) -> None:
    """
    Runs the complete image processing pipeline.

    Args:
        fits_file: Path to the FITS file (optional)
    """
    print("=" * 50)
    print("SAE Astro - Image Processing Pipeline")
    print("=" * 50)

    # Configuration
    config = Config()
    fits_path = config.get_fits_file(str(fits_file) if fits_file else None)

    print(f"\n[FITS File] {fits_path.name}")
    print(f"[Configuration]")
    print(f"  - Star FWHM: {config.STAR_FWHM} px")
    print(f"  - Detection threshold: {config.STAR_THRESHOLD} σ")
    print(f"  - Mask radius: {config.STAR_RADIUS_FACTOR} × FWHM")
    print(f"  - Erosion kernel: {config.EROSION_KERNEL_SIZE}×{config.EROSION_KERNEL_SIZE}")
    print(f"  - Mask blur: σ = {config.MASK_BLUR_SIGMA}")

    # Step 1: Load image
    print("\n[1/5] Loading FITS image...")
    loader = ImageLoader(fits_path)
    print(f"     Shape: {loader.shape}, Color: {loader.is_color}")

    # Save original image
    saver = ImageSaver(config.RESULTS_DIR)
    saver.save_original(loader.data, is_color=loader.is_color)

    # Step 2: Star detection
    print("\n[2/5] Detecting stars...")
    detector = StarDetector(
        fwhm=config.STAR_FWHM,
        threshold=config.STAR_THRESHOLD,
        radius_factor=config.STAR_RADIUS_FACTOR
    )
    image_gray = loader.get_gray_image()
    star_mask, num_stars = detector.detect(image_gray)
    saver.save_grayscale(star_mask, "starmask")

    # Step 3: Global erosion
    print("\n[3/5] Global erosion...")
    erosion = Erosion(
        kernel_size=config.EROSION_KERNEL_SIZE,
        iterations=config.EROSION_ITERATIONS
    )
    eroded_image = erosion.apply(loader.image)
    if loader.is_color:
        saver.save_color(eroded_image, "eroded")
    else:
        saver.save_grayscale(eroded_image, "eroded")

    # Step 4: Selective erosion
    print("\n[4/5] Selective erosion...")
    selective = SelectiveErosion(blur_sigma=config.MASK_BLUR_SIGMA)
    selective_result, smooth_mask = selective.apply(
        loader.image, eroded_image, star_mask
    )
    if loader.is_color:
        saver.save_color(selective_result, "selective_eroded")
    else:
        saver.save_grayscale(selective_result, "selective_eroded")
    saver.save_float_mask(smooth_mask, "smooth_mask")

    # Step 5: Calculate and save difference
    print("\n[5/5] Calculating difference...")
    saver.save_difference(eroded_image, selective_result)

    # Summary
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
    print(f"Directory: {config.RESULTS_DIR}")
    print("=" * 50)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Astronomical image processing - Selective erosion"
    )
    parser.add_argument(
        "fits_file",
        nargs="?",
        default=None,
        help="FITS file to process (default: HorseHead.fits)"
    )
    parser.add_argument(
        "--fwhm",
        type=float,
        default=Config.STAR_FWHM,
        help=f"Full Width at Half Maximum (default: {Config.STAR_FWHM})"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=Config.STAR_THRESHOLD,
        help=f"Detection threshold in sigma (default: {Config.STAR_THRESHOLD})"
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=Config.MASK_BLUR_SIGMA,
        help=f"Gaussian blur sigma (default: {Config.MASK_BLUR_SIGMA})"
    )
    
    args = parser.parse_args()
    
    # Dynamic configuration update
    Config.STAR_FWHM = args.fwhm
    Config.STAR_THRESHOLD = args.threshold
    Config.MASK_BLUR_SIGMA = args.sigma
    
    run_pipeline(args.fits_file)


if __name__ == "__main__":
    main()