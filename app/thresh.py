import numpy as np
from PIL import Image

# Load the grayscale image
image = np.array(Image.open('wmtemp/watermark_average_image.jpg').convert('L'))

# Define a threshold value for separating dark pixels from light pixels
threshold = 128

# Create a mask where dark pixels are set to True and light pixels are set to False
mask = image < threshold

# Set the dark pixels to 0 (black) and the light pixels to 255 (white)
image[mask] = 0
image[~mask] = 255

# Save the resulting binary image
Image.fromarray(image.astype(np.uint8)).save('wmtemp/watermark_best_image.jpg')
