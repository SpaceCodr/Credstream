import numpy as np
from PIL import Image

# Load the images
image1 = np.array(Image.open('wmtemp/watermark_binary1.jpg'))
image2 = np.array(Image.open('wmtemp/watermark_binary2.jpg'))
image3 = np.array(Image.open('wmtemp/watermark_binary3.jpg'))

# Calculate the average
average_image = np.mean([image1, image2, image3], axis=0)

# Save the average image
Image.fromarray(average_image.astype(np.uint8)).save('wmtemp/watermark_average_image.jpg')
