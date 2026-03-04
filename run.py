"""
Simple launcher for Image Color Detection System
Run this file directly from VS Code or command line
"""
import sys
import os

# Add CGIP directory to path
cgip_dir = os.path.join(os.path.dirname(__file__), 'CGIP')
sys.path.insert(0, cgip_dir)

# Change to CGIP directory
os.chdir(cgip_dir)

# Import and run
from main import ColorDetectionApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorDetectionApp(root)
    root.mainloop()
