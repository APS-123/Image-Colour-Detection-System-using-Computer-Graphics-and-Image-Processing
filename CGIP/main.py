import cv2
import numpy as np
import math
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from colors_db import CSS_COLORS

def get_color_name(rgb):
    min_distance = float("inf")
    closest_color = None

    for name, value in CSS_COLORS.items():
        distance = math.sqrt(
            (rgb[0] - value[0])**2 +
            (rgb[1] - value[1])**2 +
            (rgb[2] - value[2])**2
        )
        if distance < min_distance:
            min_distance = distance
            closest_color = name

    return closest_color


# -------- Select Image --------
Tk().withdraw()
file_path = askopenfilename(
    title="Select Image",
    filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
)

if not file_path:
    print("No image selected.")
    exit()

image = cv2.imread(file_path)

if image is None:
    print("Error loading image.")
    exit()

# -------- Select ROI --------
roi = cv2.selectROI("Select Area and Press ENTER", image, False, False)
cv2.destroyAllWindows()

x, y, w, h = roi

if w == 0 or h == 0:
    print("No area selected.")
    exit()

selected_area = image[y:y+h, x:x+w]

# -------- Process Selected Area --------
image_rgb = cv2.cvtColor(selected_area, cv2.COLOR_BGR2RGB)
pixels = image_rgb.reshape((-1, 3))
pixels = np.float32(pixels)

k = 3
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)

_, labels, centers = cv2.kmeans(
    pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
)

centers = np.uint8(centers)
labels = labels.flatten()

unique, counts = np.unique(labels, return_counts=True)
percentages = counts / len(labels)

print("\nColors in Selected Area:\n")

for i in range(k):
    rgb = tuple(map(int, centers[i]))
    name = get_color_name(rgb)
    percentage = round(percentages[i] * 100, 2)

    print(f"{name} - RGB{rgb} - {percentage}%")

    color_box = np.zeros((200, 300, 3), dtype="uint8")
    color_box[:] = rgb[::-1]

    cv2.putText(
        color_box,
        f"{name} ({percentage}%)",
        (10, 180),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 0),
        2,
        cv2.LINE_AA
    )

    cv2.imshow(f"Color {i+1}", color_box)

cv2.imshow("Selected Area", selected_area)

cv2.waitKey(0)
cv2.destroyAllWindows()