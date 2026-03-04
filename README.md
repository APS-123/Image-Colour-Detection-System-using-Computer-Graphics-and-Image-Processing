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
│── # 🎨 Image Color Detection System

A modern GUI application for detecting and analyzing dominant colors in images using Computer Graphics and Image Processing techniques.

## ✨ Features

- **Modern GUI Interface** - Clean, dark-themed interface with smooth animations
- **Easy Image Selection** - Simple file browser to select images
- **Interactive ROI Selection** - Select specific areas of your image to analyze
- **Top 5 Color Detection** - Uses K-means clustering to find dominant colors
- **Detailed Results** - Shows color names, RGB values, HEX codes, and percentages
- **Animated Progress** - Visual feedback during analysis with progress indicators
- **Color Database** - Matches detected colors to CSS color names

## 🚀 Quick Start

### Option 1: Double-click to run
Simply double-click `run.bat` to start the application!

### Option 2: Command line
```bash
cd CGIP
python main.py
```

### Option 3: With virtual environment
```bash
# Create virtual environment (first time only)
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
cd CGIP
python main.py
```

## 📋 Requirements

- Python 3.7+
- OpenCV (opencv-python)
- NumPy
- Pillow (PIL)

All dependencies are listed in `requirements.txt`

## 🎯 How to Use

1. **Launch the Application** - Run `run.bat` or execute `python main.py`

2. **Select an Image** - Click the "📁 Select Image" button and choose your image file

3. **Select Analysis Area** - Click "🎯 Select Area" and draw a rectangle over the area you want to analyze, then press ENTER

4. **Analyze Colors** - Click "🔍 Analyze Colors" to start the detection process

5. **View Results** - The right panel will display the top 5 colors with:
   - Color preview
   - Color name (from CSS colors database)
   - RGB values
   - HEX code
   - Percentage in selected area (with animated bar)

## 🛠️ Technology Stack

- **OpenCV** - Image processing and K-means clustering
- **NumPy** - Numerical operations and array handling
- **Tkinter** - GUI framework
- **PIL (Pillow)** - Image handling and display
- **Threading** - Smooth UI experience during analysis

## 📁 Project Structure

```
├── CGIP/
│   ├── main.py          # Main application with GUI
│   └── colors_db.py     # CSS color names database
├── requirements.txt     # Python dependencies
├── run.bat             # Quick launch script
└── README.md           # This file
```

## 🎨 Color Detection Algorithm

The application uses K-means clustering to identify the 5 most dominant colors in the selected area:

1. Converts the selected image region to RGB color space
2. Reshapes pixels into a dataset
3. Applies K-means clustering (k=5) to group similar colors
4. Calculates the percentage of each color cluster
5. Matches detected colors to the nearest CSS color name

## 🔧 Troubleshooting

**Module not found errors?**
- Make sure you've installed all dependencies: `pip install -r requirements.txt`

**Application won't start?**
- Ensure you have Python 3.7 or higher installed
- Try running from command line to see error messages

**ROI selection window not appearing?**
- The window might be behind other windows - check your taskbar
- Press Alt+Tab to switch to the ROI selection window

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to fork this project and submit pull requests for any improvements!

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
