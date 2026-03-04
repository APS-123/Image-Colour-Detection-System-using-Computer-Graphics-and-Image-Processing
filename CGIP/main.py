import cv2
import numpy as np
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os
from colors_db import CSS_COLORS

# System Requirements and Limits
MAX_IMAGE_SIZE_MB = 50  # Maximum image file size in MB
MAX_IMAGE_DIMENSION = 4096  # Maximum width or height in pixels
MIN_ROI_SIZE = 10  # Minimum ROI width/height in pixels
MAX_ROI_PIXELS = 10000000  # Maximum ROI area (10 million pixels)
WARN_ROI_PIXELS = 5000000  # Warning threshold for large ROI
RECOMMENDED_MIN_IMAGE_SIZE = 100  # Recommended minimum dimension
MAX_COLORS_TO_DETECT = 10  # Maximum number of colors to detect


class ColorDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Color Detection System")
        self.root.geometry("1200x750")
        self.root.configure(bg="#1e1e1e")
        
        # Variables
        self.image_path = None
        self.original_image = None
        self.display_image = None
        self.display_pil = None
        self.roi_coords = None
        self.analyzing = False
        
        # ROI drawing variables
        self.drawing = False
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        
        # Image scaling
        self.scale_factor = 1.0
        self.display_offset_x = 0
        self.display_offset_y = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1a1a1a", height=100)
        header.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(
            header, 
            text="🎨 Image Color Detection System",
            font=("Segoe UI", 24, "bold"),
            bg="#1a1a1a",
            fg="#ffffff"
        )
        title.pack(pady=(15, 5))
        
        subtitle = tk.Label(
            header,
            text="Select an image → Draw a rectangle on the area to analyze → Click Analyze",
            font=("Segoe UI", 10),
            bg="#1a1a1a",
            fg="#b0b0b0"
        )
        subtitle.pack()
        
        # Requirements info
        req_label = tk.Label(
            header,
            text=f"⚠️ Limits: Max {MAX_IMAGE_SIZE_MB}MB, {MAX_IMAGE_DIMENSION}px | Min ROI: {MIN_ROI_SIZE}px",
            font=("Segoe UI", 8),
            bg="#1a1a1a",
            fg="#707070"
        )
        req_label.pack(pady=(2, 5))
        
        # Main container
        main_container = tk.Frame(self.root, bg="#1e1e1e")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Image display
        left_panel = tk.Frame(main_container, bg="#2a2a2a", relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Image canvas with instructions
        canvas_frame = tk.Frame(left_panel, bg="#2a2a2a")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.image_canvas = tk.Canvas(canvas_frame, bg="#0d0d0d", highlightthickness=0, cursor="crosshair")
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events for ROI selection
        self.image_canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.image_canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.image_canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.image_canvas.bind("<Configure>", self.on_canvas_resize)
        
        # Placeholder text (will be centered on resize)
        self.placeholder_id = None
        self.root.after(100, self.center_placeholder)
        
        # Button panel
        button_frame = tk.Frame(left_panel, bg="#2a2a2a")
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.select_btn = tk.Button(
            button_frame,
            text="📁 Select Image",
            command=self.select_image,
            font=("Segoe UI", 11, "bold"),
            bg="#0e639c",
            fg="white",
            activebackground="#1177bb",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        self.analyze_btn = tk.Button(
            button_frame,
            text="🔍 Analyze Colors",
            command=self.analyze_colors,
            font=("Segoe UI", 11, "bold"),
            bg="#0e8a16",
            fg="white",
            activebackground="#0aa01e",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(
            button_frame,
            text="🔄 Clear Selection",
            command=self.clear_selection,
            font=("Segoe UI", 11, "bold"),
            bg="#6e40aa",
            fg="white",
            activebackground="#8855cc",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(
            button_frame,
            text="↺ Reset All",
            command=self.reset_all,
            font=("Segoe UI", 11, "bold"),
            bg="#d73a49",
            fg="white",
            activebackground="#e85565",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        self.help_btn = tk.Button(
            button_frame,
            text="❔ Help",
            command=self.show_help,
            font=("Segoe UI", 11, "bold"),
            bg="#6c757d",
            fg="white",
            activebackground="#868e96",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10
        )
        self.help_btn.pack(side=tk.RIGHT, padx=5)
        
        # Right panel - Results
        right_panel = tk.Frame(main_container, bg="#2a2a2a", width=350, relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        results_header = tk.Label(
            right_panel,
            text="Color Analysis Results",
            font=("Segoe UI", 14, "bold"),
            bg="#1a1a1a",
            fg="#ffffff",
            pady=15
        )
        results_header.pack(fill=tk.X)
        
        # Results container with scrollbar
        results_container = tk.Frame(right_panel, bg="#2a2a2a")
        results_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.results_canvas = tk.Canvas(results_container, bg="#0d0d0d", highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_container, orient="vertical", command=self.results_canvas.yview)
        self.results_frame = tk.Frame(self.results_canvas, bg="#0d0d0d")
        
        # Configure scrolling
        self.results_frame.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
        )
        
        self.results_canvas.create_window((0, 0), window=self.results_frame, anchor="nw", width=330)
        self.results_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mousewheel for scrolling
        self.results_canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.results_canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())
        
        self.results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Progress bar
        self.progress_frame = tk.Frame(right_panel, bg="#2a2a2a")
        self.progress = ttk.Progressbar(
            self.progress_frame,
            mode='indeterminate',
            length=300
        )
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="💡 Ready - Load an image to get started",
            font=("Segoe UI", 9),
            bg="#3a3a3a",
            fg="white",
            anchor=tk.W,
            padx=10
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message, color="#3a3a3a"):
        self.status_label.config(text=f"💡 {message}", bg=color)
        self.root.update()
    
    def on_canvas_resize(self, event=None):
        """Handle canvas resize event and recenter placeholder if visible"""
        if self.placeholder_id is not None and self.original_image is None:
            self.center_placeholder()
    
    def center_placeholder(self):
        """Create or update placeholder text centered in canvas"""
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        
        # Use default dimensions if canvas hasn't been sized yet
        if canvas_width <= 1:
            canvas_width = 600
        if canvas_height <= 1:
            canvas_height = 400
        
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        if self.placeholder_id is not None:
            # Update existing placeholder position
            self.image_canvas.coords(self.placeholder_id, center_x, center_y)
        else:
            # Create new placeholder
            self.placeholder_id = self.image_canvas.create_text(
                center_x, center_y,
                text="📷 No Image Loaded\n\n"
                     "Click 'Select Image' button below\n"
                     "to get started",
                font=("Segoe UI", 16),
                fill="#606060",
                justify=tk.CENTER
            )
    
    def _bind_mousewheel(self):
        """Bind mousewheel to canvas for scrolling"""
        self.results_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _unbind_mousewheel(self):
        """Unbind mousewheel from canvas"""
        self.results_canvas.unbind_all("<MouseWheel>")
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.results_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            # Validate file exists
            if not os.path.exists(file_path):
                messagebox.showerror("Error", "Selected file does not exist!")
                return
            
            # Check file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > MAX_IMAGE_SIZE_MB:
                messagebox.showerror(
                    "File Too Large",
                    f"Image file is {file_size_mb:.1f}MB.\n"
                    f"Maximum allowed size is {MAX_IMAGE_SIZE_MB}MB.\n\n"
                    f"Please use a smaller image or compress it."
                )
                self.update_status("Image too large - Select a smaller file", "#2a2a2a")
                return
            
            # Warn about large files
            if file_size_mb > MAX_IMAGE_SIZE_MB * 0.7:
                result = messagebox.askokcancel(
                    "Large File Warning",
                    f"Image file is {file_size_mb:.1f}MB (near the limit).\n"
                    f"This may take longer to process.\n\n"
                    f"Continue anyway?"
                )
                if not result:
                    self.update_status("Image loading cancelled", "#3a3a3a")
                    return
            
            self.image_path = file_path
            self.load_image()
            filename = file_path.split('/')[-1].split('\\')[-1]
            self.update_status(f"Image loaded: {filename} ({file_size_mb:.1f}MB) - Now draw a rectangle on the area to analyze", "#3a3a3a")
            self.analyze_btn.config(state=tk.DISABLED)
            self.clear_btn.config(state=tk.NORMAL)
            self.roi_coords = None
            self.clear_results()
    
    def load_image(self):
        try:
            # Load with OpenCV
            self.original_image = cv2.imread(self.image_path)
            if self.original_image is None:
                raise Exception("Could not load image. File may be corrupted or unsupported format.")
            
            # Check image dimensions
            height, width = self.original_image.shape[:2]
            
            # Check if image is too large
            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                messagebox.showerror(
                    "Image Too Large",
                    f"Image dimensions: {width}×{height}px\n"
                    f"Maximum allowed: {MAX_IMAGE_DIMENSION}×{MAX_IMAGE_DIMENSION}px\n\n"
                    f"Please resize your image and try again."
                )
                self.original_image = None
                raise Exception(f"Image dimensions exceed maximum of {MAX_IMAGE_DIMENSION}px")
            
            # Check if image is too small
            if width < RECOMMENDED_MIN_IMAGE_SIZE or height < RECOMMENDED_MIN_IMAGE_SIZE:
                result = messagebox.askokcancel(
                    "Small Image Warning",
                    f"Image dimensions: {width}×{height}px\n"
                    f"This image is quite small.\n"
                    f"Color detection may be less accurate.\n\n"
                    f"Continue anyway?"
                )
                if not result:
                    self.original_image = None
                    raise Exception("Image loading cancelled")
            
            # Show dimension info
            total_pixels = width * height
            if total_pixels > 5000000:  # 5 megapixels
                messagebox.showinfo(
                    "Large Image",
                    f"Image size: {width}×{height}px ({total_pixels:,} pixels)\n\n"
                    f"💡 Tip: For faster analysis, select smaller regions."
                )
            
            print(f"Image loaded: {width}×{height}px ({total_pixels:,} pixels)")
            
            # Convert for display
            img_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            
            # Resize to fit canvas
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 700
            if canvas_height <= 1:
                canvas_height = 500
            
            # Calculate scale factor
            img_width, img_height = img_pil.size
            max_width = canvas_width - 20
            max_height = canvas_height - 20
            
            self.scale_factor = min(max_width / img_width, max_height / img_height, 1.0)
            
            new_width = int(img_width * self.scale_factor)
            new_height = int(img_height * self.scale_factor)
            
            img_pil = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Store PIL image for drawing
            self.display_pil = img_pil.copy()
            self.display_image = ImageTk.PhotoImage(img_pil)
            
            # Calculate offset to center image
            self.display_offset_x = (canvas_width - new_width) // 2
            self.display_offset_y = (canvas_height - new_height) // 2
            
            # Clear canvas and display
            self.image_canvas.delete("all")
            self.placeholder_id = None  # Placeholder was deleted
            self.image_canvas.create_image(
                self.display_offset_x,
                self.display_offset_y,
                image=self.display_image,
                anchor=tk.NW,
                tags="image"
            )
            
            # Show instruction overlay
            self.show_instruction_overlay()
            
        except Exception as e:
            error_msg = str(e)
            if "cancelled" not in error_msg.lower():
                messagebox.showerror("Error", f"Failed to load image:\n{error_msg}")
            self.update_status("Error loading image" if "cancelled" not in error_msg.lower() else "Loading cancelled", "#2a2a2a")
    
    def show_instruction_overlay(self):
        """Show instructions on how to select area"""
        if self.display_pil:
            width, height = self.display_pil.size
            center_x = self.display_offset_x + width // 2
            center_y = self.display_offset_y + 30
            
            self.image_canvas.create_text(
                center_x, center_y,
                text="👆 Click and drag to select the area you want to analyze",
                font=("Segoe UI", 12, "bold"),
                fill="#cccccc",
                tags="instruction"
            )
            # Auto-hide after 5 seconds
            self.root.after(5000, lambda: self.image_canvas.delete("instruction"))
    
    def on_mouse_down(self, event):
        """Start drawing ROI rectangle"""
        if self.original_image is None or self.analyzing:
            return
        
        # Remove instruction overlay
        self.image_canvas.delete("instruction")
        
        self.drawing = True
        self.start_x = event.x
        self.start_y = event.y
        
        # Delete previous rectangle
        if self.rect_id:
            self.image_canvas.delete(self.rect_id)
        
        self.update_status("Drawing selection... Release mouse when done", "#4a4a4a")
    
    def on_mouse_drag(self, event):
        """Update ROI rectangle while dragging"""
        if not self.drawing or self.original_image is None:
            return
        
        # Delete old rectangle
        if self.rect_id:
            self.image_canvas.delete(self.rect_id)
        
        # Draw new rectangle
        self.rect_id = self.image_canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline="#ffffff",
            width=3,
            dash=(5, 5),
            tags="roi"
        )
    
    def on_mouse_up(self, event):
        """Finish drawing ROI rectangle"""
        if not self.drawing or self.original_image is None:
            return
        
        self.drawing = False
        
        # Calculate ROI coordinates in original image space
        x1 = min(self.start_x, event.x) - self.display_offset_x
        y1 = min(self.start_y, event.y) - self.display_offset_y
        x2 = max(self.start_x, event.x) - self.display_offset_x
        y2 = max(self.start_y, event.y) - self.display_offset_y
        
        # Convert from display coordinates to original image coordinates
        orig_x1 = int(x1 / self.scale_factor)
        orig_y1 = int(y1 / self.scale_factor)
        orig_x2 = int(x2 / self.scale_factor)
        orig_y2 = int(y2 / self.scale_factor)
        
        w = orig_x2 - orig_x1
        h = orig_y2 - orig_y1
        
        # Validate selection
        area_pixels = w * h
        
        # Check minimum size
        if w < MIN_ROI_SIZE or h < MIN_ROI_SIZE:
            if self.rect_id:
                self.image_canvas.delete(self.rect_id)
            self.roi_coords = None
            self.analyze_btn.config(state=tk.DISABLED)
            messagebox.showwarning(
                "Selection Too Small",
                f"Selected area: {w}×{h}px\n"
                f"Minimum required: {MIN_ROI_SIZE}×{MIN_ROI_SIZE}px\n\n"
                f"Please select a larger area."
            )
            self.update_status(f"Selection too small (min {MIN_ROI_SIZE}×{MIN_ROI_SIZE}px) - Draw a larger area", "#2a2a2a")
            return
        
        # Check maximum size
        if area_pixels > MAX_ROI_PIXELS:
            if self.rect_id:
                self.image_canvas.delete(self.rect_id)
            self.roi_coords = None
            self.analyze_btn.config(state=tk.DISABLED)
            messagebox.showerror(
                "Selection Too Large",
                f"Selected area: {w}×{h}px = {area_pixels:,} pixels\n"
                f"Maximum allowed: {MAX_ROI_PIXELS:,} pixels\n\n"
                f"Please select a smaller area to avoid performance issues."
            )
            self.update_status("Selection too large - Draw a smaller area", "#2a2a2a")
            return
        
        # Warn about large selections
        if area_pixels > WARN_ROI_PIXELS:
            result = messagebox.askokcancel(
                "Large Selection Warning",
                f"Selected area: {w}×{h}px = {area_pixels:,} pixels\n\n"
                f"This is a large area and may take longer to process.\n"
                f"For faster results, consider selecting a smaller region.\n\n"
                f"Continue with this selection?"
            )
            if not result:
                if self.rect_id:
                    self.image_canvas.delete(self.rect_id)
                self.roi_coords = None
                self.analyze_btn.config(state=tk.DISABLED)
                self.update_status("Selection cancelled - Draw a smaller area", "#3a3a3a")
                return
        
        # Valid selection
        self.roi_coords = (orig_x1, orig_y1, w, h)
        self.analyze_btn.config(state=tk.NORMAL)
        
        # Provide helpful feedback
        if area_pixels < 1000:
            status_msg = f"Area selected ({w}×{h} = {area_pixels} pixels) - Very small, results may vary"
            color = "#4a4a4a"
        elif area_pixels < 10000:
            status_msg = f"Area selected ({w}×{h} = {area_pixels:,} pixels) - Good size for quick analysis"
            color = "#3a3a3a"
        elif area_pixels < WARN_ROI_PIXELS:
            status_msg = f"Area selected ({w}×{h} = {area_pixels:,} pixels) - Good selection"
            color = "#3a3a3a"
        else:
            status_msg = f"Area selected ({w}×{h} = {area_pixels:,} pixels) - Large area, may take time"
            color = "#4a4a4a"
        
        self.update_status(status_msg + " - Click 'Analyze Colors' to continue", color)
    
    def clear_selection(self):
        """Clear the current ROI selection"""
        if self.rect_id:
            self.image_canvas.delete(self.rect_id)
            self.rect_id = None
        self.roi_coords = None
        self.analyze_btn.config(state=tk.DISABLED)
        self.update_status("Selection cleared - Draw a new rectangle on the image", "#3a3a3a")
        self.clear_results()
        if self.display_pil:
            self.show_instruction_overlay()
    
    def reset_all(self):
        """Reset everything and start fresh"""
        # Clear canvas
        self.image_canvas.delete("all")
        
        # Reset variables
        self.image_path = None
        self.original_image = None
        self.display_image = None
        self.display_pil = None
        self.roi_coords = None
        self.rect_id = None
        self.placeholder_id = None  # Will be recreated centered
        
        # Reset buttons
        self.analyze_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.DISABLED)
        
        # Clear results
        self.clear_results()
        
        # Show placeholder
        self.center_placeholder()
        
        self.update_status("Reset complete - Load an image to get started", "#3a3a3a")
    
    def show_help(self):
        """Show help dialog with system requirements and limits"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Help & Requirements")
        help_window.geometry("600x700")
        help_window.configure(bg="#0d0d0d")
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Header
        header = tk.Frame(help_window, bg="#1a1a1a")
        header.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(
            header,
            text="📖 System Requirements & Usage Guide",
            font=("Segoe UI", 16, "bold"),
            bg="#1a1a1a",
            fg="#ffffff"
        )
        title.pack(pady=15)
        
        # Content frame with scrollbar
        content_frame = tk.Frame(help_window, bg="#0d0d0d")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(content_frame, bg="#0d0d0d", highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0d0d0d")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        help_text = f"""
📋 SYSTEM LIMITS

• Maximum Image File Size: {MAX_IMAGE_SIZE_MB} MB
• Maximum Image Dimensions: {MAX_IMAGE_DIMENSION} × {MAX_IMAGE_DIMENSION} pixels
• Minimum ROI Selection: {MIN_ROI_SIZE} × {MIN_ROI_SIZE} pixels
• Maximum ROI Area: {MAX_ROI_PIXELS:,} pixels
• Warning Threshold: {WARN_ROI_PIXELS:,} pixels
• Maximum Colors Detected: {MAX_COLORS_TO_DETECT}

🛠️ SUPPORTED FORMATS

• JPEG/JPG - Recommended for photos
• PNG - Best for graphics with transparency
• BMP - Uncompressed format
• GIF - Animated images (first frame only)

💡 HOW TO USE

1️⃣ Select Image
   Click 'Select Image' or drag & drop an image file
   
2️⃣ Draw Selection
   Click and drag on the image to select the area
   you want to analyze
   
3️⃣ Analyze Colors
   Click 'Analyze Colors' to detect dominant colors
   Results show color names, RGB, HEX, and percentages
   
4️⃣ Clear & Retry
   Use 'Clear Selection' to choose a different area
   Use 'Reset All' to start with a new image

✅ TIPS FOR BEST RESULTS

• Use clear, high-quality images
• Select specific regions for more accurate results
• Smaller selections analyze faster
• For large images, select regions instead of whole image
• Well-lit images give better color detection
• Avoid extremely dark or bright images

⚠️ PERFORMANCE TIPS

• Images over 3000×3000px may be slow
• ROI selections over 1M pixels take longer
• Compress large files before loading
• Close other applications for faster processing

🎨 COLOR DETECTION INFO

• Uses K-means clustering algorithm
• Detects 3-7 colors based on selection size
• Colors matched to CSS color names database
• Percentages show color distribution in selection
• Results sorted by dominance (highest first)

🔧 TROUBLESHOOTING

Q: "Selection too small" error?
A: Draw a larger rectangle (min {MIN_ROI_SIZE}×{MIN_ROI_SIZE}px)

Q: Analysis takes too long?
A: Select a smaller region or use a smaller image

Q: Colors seem inaccurate?
A: Try selecting a more specific area or use
   a higher quality image

Q: Can't see all colors?
A: Scroll in the results panel using mouse wheel
   or the scrollbar
"""
        
        # Add text labels
        for line in help_text.split('\n'):
            if line.strip():
                if line.strip().startswith(('📋', '🛠', '💡', '✅', '⚠', '🎨', '🔧')):
                    # Section headers
                    label = tk.Label(
                        scrollable_frame,
                        text=line,
                        font=("Segoe UI", 12, "bold"),
                        bg="#0d0d0d",
                        fg="#cccccc",
                        anchor=tk.W,
                        justify=tk.LEFT
                    )
                    label.pack(fill=tk.X, pady=(10, 5), padx=10)
                elif line.strip().startswith(('Q:', 'A:')):
                    # Q&A
                    color = "#b0b0b0" if line.startswith('Q:') else "#909090"
                    label = tk.Label(
                        scrollable_frame,
                        text=line,
                        font=("Segoe UI", 9),
                        bg="#0d0d0d",
                        fg=color,
                        anchor=tk.W,
                        justify=tk.LEFT,
                        wraplength=520
                    )
                    label.pack(fill=tk.X, pady=2, padx=15)
                elif line.strip().startswith(('•', '1', '2', '3', '4')):
                    # Bullet points
                    label = tk.Label(
                        scrollable_frame,
                        text=line,
                        font=("Segoe UI", 9),
                        bg="#0d0d0d",
                        fg="#a0a0a0",
                        anchor=tk.W,
                        justify=tk.LEFT,
                        wraplength=520
                    )
                    label.pack(fill=tk.X, pady=2, padx=20)
                else:
                    # Regular text
                    label = tk.Label(
                        scrollable_frame,
                        text=line,
                        font=("Segoe UI", 9),
                        bg="#0d0d0d",
                        fg="#808080",
                        anchor=tk.W,
                        justify=tk.LEFT,
                        wraplength=520
                    )
                    label.pack(fill=tk.X, pady=1, padx=15)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        close_btn = tk.Button(
            help_window,
            text="Close",
            command=help_window.destroy,
            font=("Segoe UI", 10, "bold"),
            bg="#404040",
            fg="white",
            activebackground="#505050",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=8
        )
        close_btn.pack(pady=15)
        
        # Bind mousewheel
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda ev: canvas.yview_scroll(int(-1*(ev.delta/120)), "units")))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
    
    def analyze_colors(self):
        if self.original_image is None or self.roi_coords is None:
            return
        
        if self.analyzing:
            return
        
        # Run analysis in a separate thread
        thread = threading.Thread(target=self._analyze_colors_thread, daemon=True)
        thread.start()
    
    def _analyze_colors_thread(self):
        self.analyzing = True
        
        # Update UI from main thread
        self.root.after(0, self._show_progress)
        self.root.after(0, lambda: self.update_status("Analyzing colors...", "#4a4a4a"))
        
        try:
            x, y, w, h = self.roi_coords
            selected_area = self.original_image[y:y+h, x:x+w]
            
            # Process colors
            image_rgb = cv2.cvtColor(selected_area, cv2.COLOR_BGR2RGB)
            pixels = image_rgb.reshape((-1, 3))
            pixels = np.float32(pixels)
            
            # Calculate optimal number of colors based on ROI size
            total_pixels = w * h
            if total_pixels < 1000:
                k = 3  # Small area: 3 colors
            elif total_pixels < 10000:
                k = 5  # Medium area: 5 colors
            else:
                k = min(7, MAX_COLORS_TO_DETECT)  # Large area: up to 7 colors
            
            # Adjust k if there are fewer pixels than requested colors
            unique_colors_estimate = min(total_pixels, 1000000)
            k = min(k, max(3, int(unique_colors_estimate ** 0.5) // 10))
            
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
            
            pixels_umat = cv2.UMat(pixels)
            best_labels = cv2.UMat((len(pixels), 1), cv2.CV_32S)
            centers = cv2.UMat((k, 3), cv2.CV_32F)
            
            _, labels, centers = cv2.kmeans(
                pixels_umat, k, best_labels, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
            )
            
            labels = best_labels.get()
            centers = centers.get()
            
            centers = np.uint8(centers)
            labels = labels.flatten()
            
            unique, counts = np.unique(labels, return_counts=True)
            percentages = counts / len(labels)
            
            # Sort by percentage
            sorted_indices = np.argsort(percentages)[::-1]
            
            results = []
            for i in sorted_indices:
                rgb = tuple(map(int, centers[i]))
                name = self.get_color_name(rgb)
                percentage = round(percentages[i] * 100, 2)
                results.append((name, rgb, percentage))
            
            # Update UI from main thread
            self.root.after(0, lambda: self._display_results(results))
            analysis_msg = f"Analysis complete! Found {len(results)} dominant colors in {w}×{h}px area"
            self.root.after(0, lambda: self.update_status(analysis_msg, "#3a3a3a"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed:\n{str(e)}"))
            self.root.after(0, lambda: self.update_status("Analysis failed", "#2a2a2a"))
        
        finally:
            self.analyzing = False
            self.root.after(0, self._hide_progress)
    
    def _show_progress(self):
        self.progress_frame.pack(fill=tk.X, padx=10, pady=10)
        self.progress.pack(fill=tk.X)
        self.progress.start(10)
        self.analyze_btn.config(state=tk.DISABLED)
        self.select_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.DISABLED)
        self.reset_btn.config(state=tk.DISABLED)
    
    def _hide_progress(self):
        self.progress.stop()
        self.progress_frame.pack_forget()
        self.analyze_btn.config(state=tk.NORMAL)
        self.select_btn.config(state=tk.NORMAL)
        self.clear_btn.config(state=tk.NORMAL)
        self.reset_btn.config(state=tk.NORMAL)
    
    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
    
    def _display_results(self, results):
        self.clear_results()
        
        for i, (name, rgb, percentage) in enumerate(results):
            # Animate entry
            self._create_color_card(i, name, rgb, percentage)
        
        # Update scroll region after adding all cards
        self.results_canvas.update_idletasks()
        self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
        # Scroll to top
        self.results_canvas.yview_moveto(0)
    
    def _create_color_card(self, index, name, rgb, percentage):
        # Card container
        card = tk.Frame(self.results_frame, bg="#1a1a1a", relief=tk.RAISED, bd=1)
        card.pack(fill=tk.X, pady=8, padx=5)
        
        # Color preview
        hex_color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        color_box = tk.Frame(card, bg=hex_color, width=60, height=60)
        color_box.pack(side=tk.LEFT, padx=10, pady=10)
        color_box.pack_propagate(False)
        
        # Info section
        info_frame = tk.Frame(card, bg="#1a1a1a")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Rank badge
        rank_label = tk.Label(
            info_frame,
            text=f"#{index+1}",
            font=("Segoe UI", 9, "bold"),
            bg="#1a1a1a",
            fg="#a0a0a0",
            anchor=tk.W
        )
        rank_label.pack(fill=tk.X)
        
        # Color name
        name_label = tk.Label(
            info_frame,
            text=name,
            font=("Segoe UI", 11, "bold"),
            bg="#1a1a1a",
            fg="#ffffff",
            anchor=tk.W
        )
        name_label.pack(fill=tk.X)
        
        # RGB values
        rgb_label = tk.Label(
            info_frame,
            text=f"RGB: {rgb}",
            font=("Segoe UI", 9),
            bg="#1a1a1a",
            fg="#b0b0b0",
            anchor=tk.W
        )
        rgb_label.pack(fill=tk.X)
        
        # Hex value
        hex_label = tk.Label(
            info_frame,
            text=f"HEX: {hex_color.upper()}",
            font=("Segoe UI", 9),
            bg="#1a1a1a",
            fg="#b0b0b0",
            anchor=tk.W
        )
        hex_label.pack(fill=tk.X)
        
        # Percentage bar
        bar_frame = tk.Frame(info_frame, bg="#0d0d0d", height=20)
        bar_frame.pack(fill=tk.X, pady=(5, 0))
        bar_frame.pack_propagate(False)
        
        # Create grayscale version for bar
        gray_value = int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
        bar_color = f'#{gray_value:02x}{gray_value:02x}{gray_value:02x}'
        
        bar_fill = tk.Frame(bar_frame, bg=bar_color)
        bar_fill.place(x=0, y=0, relheight=1, width=0)
        
        percent_label = tk.Label(
            bar_frame,
            text=f"{percentage}%",
            font=("Segoe UI", 9, "bold"),
            bg="#0d0d0d",
            fg="#ffffff"
        )
        percent_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Animate the bar
        self._animate_bar(bar_fill, percentage)
    
    def _animate_bar(self, bar, target_percent, current=0):
        if current <= target_percent:
            bar.config(width=int(current * 3))
            self.root.after(10, lambda: self._animate_bar(bar, target_percent, current + 1))
    
    def get_color_name(self, rgb):
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


def main():
    root = tk.Tk()
    app = ColorDetectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
