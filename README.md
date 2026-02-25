🎨 Image Color Detection System (CGIP Project)

📌 Overview

This project implements an Image Color Detection System using Computer Graphics and Image Processing techniques. The system analyzes digital images to identify multiple dominant colors using K-Means clustering and pixel-level processing. It extracts RGB values, classifies common colors (grey, beige, brown, purple, pink, etc.), and displays color distribution with percentage visualization.

🎯 Features

Detects multiple dominant colors from an image

Uses K-Means clustering for color extraction

Identifies common colors (Brown, Grey, Beige, Purple, Pink, etc.)

Displays color percentage distribution

Shows color preview using OpenCV

Simple and efficient CGIP implementation

⚙️ Technologies Used

Python 3

OpenCV – Image processing

NumPy – Matrix and pixel operations

K-Means Clustering – Color extraction

🧠 Methodology

The system follows these steps:

Image acquisition using OpenCV.

Conversion of image into RGB color space.

Pixel matrix transformation.

K-Means clustering to identify dominant colors.

Color classification using RGB thresholding.

Visualization of color results and percentages.

💻 Installation
Install required libraries:
pip install opencv-python numpy

▶️ How to Run

Place your image in the project folder.

Update the image path in the code if needed.

Run the program:

python color_detection.py
📊 Output

Displays dominant colors in the terminal.

Shows color percentage.

Opens preview windows for detected colors.

📂 Project Structure
project-folder/
│── color_detection.py
│── image.jpeg
│── README.md

👥 Team Members

Arun Prabhasankar (33)

Aswathi M (36)

Abel Abraham Panicker (2)

Amala Jose (22)


📚 Applications

Image analysis

Computer vision preprocessing

Content-based image retrieval

Multimedia systems

Visual data processing

🚀 Future Improvements

GUI-based image upload

HSV color detection for higher accuracy

Extended color database

Single palette visualization
