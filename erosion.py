from astropy.io import fits
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np

# Open and read the FITS file
# Try M31 image first for better star detection, then HorseHead
fits_file = './examples/test_M31_linear.fits'
hdul = fits.open(fits_file)

# Display information about the file
hdul.info()

# Access the data from the primary HDU
data = hdul[0].data

# Access header information
header = hdul[0].header

# Handle both monochrome and color images
if data.ndim == 3:
    # Color image - need to transpose to (height, width, channels)
    if data.shape[0] == 3:  # If channels are first: (3, height, width)
        data = np.transpose(data, (1, 2, 0))
    # If already (height, width, 3), no change needed
    
    # Normalize the entire image to [0, 1] for matplotlib
    data_normalized = (data - data.min()) / (data.max() - data.min())
    
    # Save the data as a png image (no cmap for color images)
    plt.imsave('./results/original.png', data_normalized)
    
    # Normalize each channel separately to [0, 255] for OpenCV
    image = np.zeros_like(data, dtype='uint8')
    for i in range(data.shape[2]):
        channel = data[:, :, i]
        image[:, :, i] = ((channel - channel.min()) / (channel.max() - channel.min()) * 255).astype('uint8')
    
    # Convert RGB to BGR for OpenCV to make colors correctly displayed
    image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
else:
    # Monochrome image
    plt.imsave('./results/original.png', data, cmap='gray')
    
    # Convert to uint8 for OpenCV
    image = ((data - data.min()) / (data.max() - data.min()) * 255).astype('uint8')

# Function to create a star mask
def create_star_mask(image, fwhm=3.0, threshold=5.0):
    """
    Creates a binary mask of stars using DAOStarFinder.
    
    Parameters:
    -----------
    image : ndarray
        Grayscale monochrome image (uint8 or float)
    fwhm : float
        Full Width at Half Maximum (FWHM) of stars in pixels
    threshold : float
        Detection threshold in number of sigma above background
    
    Returns:
    --------
    mask : ndarray
        Binary mask where 1 = stars, 0 = background
    """
    # Ensure image is float64 for calculations
    if image.dtype == np.uint8:
        image_float = image.astype(np.float64)
    else:
        image_float = image.copy()
    
    # Compute mean and standard deviation of background with sigma-clipping
    mean, median, std = sigma_clipped_stats(image_float, sigma=3.0)
    
    # Create DAOStarFinder
    daofind = DAOStarFinder(fwhm=fwhm, threshold=threshold*std)
    
    # Find sources (stars)
    sources = daofind(image_float - median)
    
    # Check if any stars were detected
    if sources is None:
        print("No stars detected!")
        return np.zeros_like(image_float, dtype=np.uint8)
    
    # Print number of detected stars
    print(f"Number of stars detected: {len(sources)}")
    
    # Create empty mask
    mask = np.zeros_like(image_float, dtype=np.uint8)
    
    # Mark star positions on mask
    # Use radius based on FWHM to cover the star
    radius = int(fwhm * 1.5)  # 50% margin around FWHM
    
    for x, y in zip(sources['xcentroid'], sources['ycentroid']):
        x, y = int(x), int(y)
        # Draw a circle around each star
        cv.circle(mask, (x, y), radius, (255, 255, 255), -1)
    
    return mask


# Create star mask
# Convert to grayscale for star detection
if image.ndim == 3:
    # For color images, use luminance (image is in BGR after conversion)
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
else:
    image_gray = image
star_mask = create_star_mask(image_gray, fwhm=4.0, threshold=2.0)

# Save the mask
cv.imwrite('./results/starmask.png', star_mask)

# Function to perform selective erosion
def selective_erosion(original, eroded, mask, blur_sigma=5.0):
    """
    Implements selective erosion by interpolation.
    
    Formula: I_final = (M × I_erode) + ((1-M) × I_original)
    
    Parameters:
    -----------
    original : ndarray
        Original image
    eroded : ndarray
        Eroded image
    mask : ndarray
        Binary star mask (uint8, 0 or 255)
    blur_sigma : float
        Standard deviation of Gaussian blur to smooth mask edges
    
    Returns:
    --------
    result : ndarray
        Resulting image from selective erosion
    """
    # Convert mask to float64 and normalize to [0, 1]
    mask_float = mask.astype(np.float64) / 255.0
    
    # Apply Gaussian blur to smooth mask edges
    # This avoids abrupt transitions at star/background boundaries
    mask_smooth = cv.GaussianBlur(mask_float, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)
    
    # Ensure mask stays within [0, 1]
    mask_smooth = np.clip(mask_smooth, 0, 1)
    
    # Apply interpolation formula
    # For color images, apply on each channel
    if original.ndim == 3:
        # Color image
        result = np.zeros_like(original, dtype=np.float64)
        for i in range(original.shape[2]):
            # I_final = (M × I_erode) + ((1-M) × I_original)
            result[:, :, i] = (mask_smooth * eroded[:, :, i].astype(np.float64) + 
                              (1 - mask_smooth) * original[:, :, i].astype(np.float64))
    else:
        # Monochrome image
        result = mask_smooth * eroded.astype(np.float64) + (1 - mask_smooth) * original.astype(np.float64)
    
    # Convert to uint8 for saving
    result_uint8 = np.clip(result, 0, 255).astype(np.uint8)
    
    return result_uint8, mask_smooth


# Create eroded image
kernel = np.ones((3, 3), np.uint8)
eroded_image = cv.erode(image, kernel, iterations=1)

# Apply selective erosion with smoothed mask with sigma 5.0
selective_result, smooth_mask = selective_erosion(image, eroded_image, star_mask, blur_sigma=5.0)

# Save results
cv.imwrite('./results/eroded.png', eroded_image)
cv.imwrite('./results/selective_eroded.png', selective_result)

# Save smoothed mask (visualization)
smooth_mask_visual = (smooth_mask * 255).astype(np.uint8)
cv.imwrite('./results/smooth_mask.png', smooth_mask_visual)

# Save difference between global and selective erosion
diff = np.abs(eroded_image.astype(np.float32) - selective_result.astype(np.float32))
diff_normalized = (diff / diff.max() * 255).astype(np.uint8) if diff.max() > 0 else diff.astype(np.uint8)
cv.imwrite('./results/difference.png', diff_normalized)

print("\n=== SUMMARY OF GENERATED FILES ===")
print("1. results/original.png - Original image")
print("2. results/starmask.png - Star mask (raw)")
print("3. results/eroded.png - Global erosion")
print("4. results/selective_eroded.png - Selective erosion")
print("5. results/smooth_mask.png - Smoothed mask")
print("6. results/difference.png - Difference global vs selective erosion")

# Close the file
hdul.close()

