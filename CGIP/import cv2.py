import cv2
import numpy as np

# -------- COLOR NAME DETECTION FUNCTION --------
def get_color_name(rgb):
    r, g, b = rgb

    # -------- Neutral Colors --------
    if r > 220 and g > 220 and b > 220:
        return "White"

    if r < 50 and g < 50 and b < 50:
        return "Black"

    if abs(r - g) < 20 and abs(r - b) < 20 and abs(g - b) < 20:
        return "Grey"

    # -------- Brown (check BEFORE red) --------
    # Brown has r > g, g > b (or g ≈ b), and moderate overall brightness
    if r > g and r > b:
        # Dark brown: overall low brightness with proper ratios
        if r + g + b < 350 and g > 25 and b < 100:
            if g > b * 0.8:  # g should be similar to or greater than b
                return "Brown"
        # Medium brown
        if r < 200 and g > 40 and g < 160 and b < 120:
            if r > g * 1.1 and g > b * 0.9:
                return "Brown"

    # -------- Beige / Tan --------
    if r > 180 and g > 160 and b < 160:
        return "Beige / Tan"

    # -------- Pink --------
    if r > 200 and g > 150 and b > 150:
        return "Pink"

    # -------- Purple --------
    if r > 120 and b > 120 and g < 120:
        return "Purple"

    # -------- Yellow --------
    if r > 200 and g > 200 and b < 120:
        return "Yellow"

    # -------- Orange --------
    if r > 200 and g > 120 and b < 80:
        return "Orange"

    # -------- Primary Colors --------
    if r > g and r > b:
        return "Red"

    if g > r and g > b:
        return "Green"

    if b > r and b > g:
        return "Blue"

    return "Unknown"


# -------- LOAD IMAGE --------
image = cv2.imread(r"C:\Users\HP\Desktop\s5\CGIP\image.jpeg")

if image is None:
    print("Error: Image not found")
    exit()

# Convert BGR → RGB
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# -------- RESHAPE PIXELS --------
pixels = image_rgb.reshape((-1, 3))
pixels = np.float32(pixels)

# -------- KMEANS CLUSTERING (MULTIPLE COLORS) --------
k = 4   # number of dominant colors (change if needed)

criteria = (
    cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
    100,
    0.2
)

_, labels, centers = cv2.kmeans(
    pixels,
    k,
    None,
    criteria,
    10,
    cv2.KMEANS_RANDOM_CENTERS
)

centers = np.uint8(centers)
labels = labels.flatten()

# -------- CALCULATE COLOR PERCENTAGE --------
unique, counts = np.unique(labels, return_counts=True)
percentages = counts / len(labels)

# -------- DISPLAY RESULTS --------
print("\nDominant Colors:\n")

for i in range(k):
    rgb = tuple(map(int, centers[i]))
    color_name = get_color_name(rgb)
    percentage = round(percentages[i] * 100, 2)

    print(f"RGB: {rgb} | Name: {color_name} | {percentage}%")
    print(f"  Debug: R={rgb[0]}, G={rgb[1]}, B={rgb[2]}, Sum={sum(rgb)}")

    # Create preview box
    color_box = np.zeros((200, 300, 3), dtype="uint8")
    color_box[:] = rgb[::-1]  # RGB → BGR for OpenCV display

    text = f"{color_name} ({percentage}%)"

    cv2.putText(
        color_box,
        text,
        (10, 180),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 0),
        2,
        cv2.LINE_AA
    )

    cv2.imshow(f"Color {i+1}", color_box)

# Show original image
cv2.imshow("Original Image", image)

cv2.waitKey(0)
cv2.destroyAllWindows()