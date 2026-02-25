import cv2
import numpy as np
import os
print(os.getcwd())
# Load image (change file name if needed)
image = cv2.imread("image.jpg")

# Check if image loaded
if image is None:
    print("Error: Image not found")
    exit()

# Convert BGR (OpenCV default) to RGB
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Reshape image into list of pixels
pixels = image_rgb.reshape((-1, 3))

# Convert to integer type
pixels = np.float32(pixels)

# Use KMeans to find dominant color
# We take 1 cluster = most dominant color
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
k = 1
_, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

# Get dominant color
dominant_color = centers[0].astype(int)

print("Dominant RGB Color:", tuple(dominant_color))

# Create a color preview window
color_box = np.zeros((200, 200, 3), dtype="uint8")
color_box[:] = dominant_color[::-1]  # Convert RGB back to BGR for display

# Show image and detected color
cv2.imshow("Original Image", image)
cv2.imshow("Dominant Color", color_box)

cv2.waitKey(0)
cv2.destroyAllWindows()