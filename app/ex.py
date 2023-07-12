# from matplotlib import pyplot as plt
# import main
# r=main.Extract("theif-007.mp4")
# plt.imshow(r,cmap="gray")
# plt.show 

#!ffprobe -show_format -show_streams E:/phase_3\input\theif.mp4

import cv2
from matplotlib import pyplot as plt
import main
from models import User

# Extract the watermark
id=28
user=User.query.get(id)


# Apply a threshold to convert the image to binary
# _, thresholded = cv2.threshold(watermark, 125, 255, cv2.THRESH_BINARY)

# # Define a kernel for morphological operations
# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))

# # Perform morphological closing to fill in small gaps in the watermark
# closed = cv2.morphologyEx(watermark, cv2.MORPH_CLOSE, kernel)

# # Perform morphological opening to smooth out the watermark
# opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)

# Apply median filter to the thresholded image
# watermark = cv2.medianBlur(watermark, 3)

# Apply median filter to the thresholded image
# denoised = cv2.medianBlur(thresholded, 3)


# Display the binary watermark
# plt.imshow(watermark, cmap="gray")
# plt.show()
watermark = main.Extract("theif-001.mp4",user)
cv2.imwrite("wmtemp/watermark_binary1.jpg", watermark)

