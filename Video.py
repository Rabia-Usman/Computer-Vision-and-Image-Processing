# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 00:51:10 2024

@author: Hp
"""

import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QComboBox, QMenuBar, QMenu, QAction, QVBoxLayout, QWidget, QPushButton

class VideoPlayerApp(QMainWindow):
    def __init__(self):
        super(VideoPlayerApp, self).__init__()

        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 1200, 800)  # Increased window size
        
        self.video_size = (800, 600)  # Set the default size for the video display area
        self.video_path = None
        self.cap = None
        self.timer = QTimer(self)
        self.is_camera_mode = False
        self.is_grayscale = False
        self.is_bw = False
        self.is_gaussian_blur = False
        self.is_edge_detection = False
        self.is_dilation = False

        # Camera variables
        self.camera_index = 0  # Default camera index
        self.camera_dropdown = QComboBox(self)
        self.camera_dropdown.setGeometry(210, 500, 150, 30)
        self.camera_dropdown.setVisible(False)
        self.camera_dropdown.currentIndexChanged.connect(self.change_camera)
        
        # Status labels
        self.filter_status_label = QLabel("No Filters Applied", self)
        self.filter_status_label.setGeometry(50, 670, 200, 30)

        self.init_ui()

    def init_ui(self):
        # Video Frame
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setGeometry(50, 50, 1100, 600)  # Adjusted size

        # Create menu bar
        menubar = self.menuBar()

        # Create File menu
        file_menu = menubar.addMenu('File')

        open_action = QAction('Open Video', self)
        open_action.triggered.connect(self.open_video)
        file_menu.addAction(open_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Video Frame
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setGeometry(50, 50, *self.video_size)  # Set the size of the video display area
    
        # Create Filters menu
        filters_menu = menubar.addMenu('Filters')

        grayscale_action = QAction('Grayscale', self)
        grayscale_action.triggered.connect(self.apply_grayscale)
        filters_menu.addAction(grayscale_action)

        bw_action = QAction('Black & White', self)
        bw_action.triggered.connect(self.apply_bw)
        filters_menu.addAction(bw_action)

        reset_color_action = QAction('Reset Color', self)
        reset_color_action.triggered.connect(self.reset_color)
        filters_menu.addAction(reset_color_action)
        
        # Additional Filters
        gaussian_blur_action = QAction('Gaussian Blur', self)
        gaussian_blur_action.triggered.connect(self.apply_gaussian_blur)
        filters_menu.addAction(gaussian_blur_action)

        edge_detection_action = QAction('Edge Detection (Canny)', self)
        edge_detection_action.triggered.connect(self.apply_edge_detection)
        filters_menu.addAction(edge_detection_action)

        dilation_action = QAction('Dilation', self)
        dilation_action.triggered.connect(self.apply_dilation)
        filters_menu.addAction(dilation_action)

        # Create Navigation menu
        navigation_menu = menubar.addMenu('Navigation')

        backward_action = QAction('Backward', self)
        backward_action.triggered.connect(self.backward_video)
        navigation_menu.addAction(backward_action)

        forward_action = QAction('Forward', self)
        forward_action.triggered.connect(self.forward_video)
        navigation_menu.addAction(forward_action)

        # Create Speed menu
        speed_menu = menubar.addMenu('Speed')

        speed_dropdown_action = QAction('Change Speed', self)
        speed_menu.addAction(speed_dropdown_action)

        # Speed Submenu
        speed_submenu = QMenu(self)
        speed_menu.addMenu(speed_submenu)
        
        # Speed Dropdown
        speed_layout = QVBoxLayout()
        self.speed_dropdown = QComboBox(self)
        self.speed_dropdown.addItems(["1x", "2x", "0.5x"])
        speed_layout.addWidget(self.speed_dropdown)
        
        # Add layout to submenu
        speed_submenu.setLayout(speed_layout)
        self.speed_dropdown.currentIndexChanged.connect(self.change_speed)
        
        # Create Camera menu
        camera_menu = menubar.addMenu('Camera')

        camera_mode_action = QAction('Toggle Camera Mode', self)
        camera_mode_action.triggered.connect(self.toggle_camera_mode)
        camera_menu.addAction(camera_mode_action)

        camera_dropdown_action = QAction('Choose Camera', self)
        camera_menu.addAction(camera_dropdown_action)

        # Camera Dropdown Submenu
        camera_submenu = QMenu(self)
        camera_menu.addMenu(camera_submenu)

        # Populate camera dropdown options
        self.update_camera_dropdown()
        
        # Create Play and Pause buttons
        self.play_button = QPushButton('Play', self)
        self.play_button.setGeometry(50, 670, 100, 30)
        self.play_button.clicked.connect(self.play_video)

        self.pause_button = QPushButton('Pause', self)
        self.pause_button.setGeometry(170, 670, 100, 30)
        self.pause_button.clicked.connect(self.pause_video)

        # Set initial UI state
        self.set_ui_state()

    def update_camera_dropdown(self):
        # Clear existing items
        self.camera_dropdown.clear()

        # Get available camera devices dynamically
        for i in range(10):  # Check up to 10 cameras (you can adjust the range based on your needs)
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Use CAP_DSHOW for DirectShow backend on Windows
            if cap.isOpened():
                # Get camera name (you can use other properties like CAP_PROP_MAKE, CAP_PROP_MODEL, etc.)
                camera_name = f"Camera {i}"
                self.camera_dropdown.addItem(camera_name, i)  # Store the camera index as item data
                cap.release()
            else:
                print(f"Camera {i} is not available.")

    def set_ui_state(self):
        # Set initial UI state based on camera mode
        if self.is_camera_mode:
            self.camera_dropdown.setVisible(True)
        else:
            self.camera_dropdown.setVisible(False)

    def toggle_camera_mode(self):
        self.is_camera_mode = not self.is_camera_mode
        self.set_ui_state()
        if self.is_camera_mode:
            self.start_or_stop_camera()

    def change_camera(self, index):
        self.camera_index = self.camera_dropdown.itemData(index)
        self.start_or_stop_camera()

    def print_video_properties(self):
        if self.cap:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

            print(f"Video Properties:")
            print(f" - Resolution: {width} x {height}")
            print(f" - Frames per Second (FPS): {fps}")
            print(f" - Total Frames: {total_frames}")
            print(f" - Current Frame: {current_frame}")

    # Modify the 'open_video' method to reset the video capture when opening a new video
    def open_video(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)", options=options)
    
        if self.video_path:
            if self.cap is not None and self.cap.isOpened():
                self.timer.stop()
                self.cap.release()
                self.video_label.clear()
            self.cap = cv2.VideoCapture(self.video_path)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_size[0])  # Set the width of the video capture
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_size[1])  # Set the height of the video capture
            self.timer.timeout.connect(self.apply_filters)
            self.timer.start(30)
            self.is_camera_mode = False
            self.set_ui_state()
            self.update_frame()
            self.print_video_properties()

    def start_or_stop_camera(self, play=True):
        if self.is_camera_mode:
            if self.camera_index is not None:
                # Release previous video capture if it exists
                if self.cap is not None and self.cap.isOpened():
                    self.cap.release()
                
                # Initialize new video capture with CAP_ANY
                self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_ANY)
                
                if not play:
                    self.timer.stop()
                else:
                    self.timer.timeout.connect(self.update_frame)
                    self.timer.start(30)  # Update frame every 30 milliseconds
                
                self.is_grayscale = False
                self.is_bw = False
                self.update_frame()  # Update the frame immediately after starting the camera
        else:
            if self.cap is not None and self.cap.isOpened():
                if not play:
                    self.timer.stop()
                else:
                    self.timer.timeout.connect(self.update_frame)
                    self.timer.start(30)  # Update frame every 30 milliseconds
                self.is_grayscale = False
                self.is_bw = False
                self.update_frame()  # Update the frame immediately after stopping the camera

    def play_video(self):
        if self.is_camera_mode:
            self.start_or_stop_camera(play=True)
        elif self.cap and not self.timer.isActive():
            self.timer.timeout.connect(self.update_frame)
            self.timer.start()

    def pause_video(self):
        if self.is_camera_mode:
            self.start_or_stop_camera(play=False)
        elif self.cap and self.timer.isActive():
            self.timer.stop()


    def update_frame(self):
        if self.is_camera_mode:
            # Read the next frame from the camera
            ret, frame = self.cap.read()
            if not ret:
                return  # Break the loop if no more frames are available
        else:
            # For video files, use the original implementation
            ret, frame = self.cap.read()
            if not ret:
                return  # Break the loop if no more frames are available

            original_frame = frame.copy()  # Preserve the original color frame

            if original_frame.shape[-1] == 3 and original_frame.shape[-2] == 3:
                original_frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB)

            if self.is_grayscale:
                frame = cv2.cvtColor(original_frame, cv2.COLOR_RGB2GRAY)
                frame = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB), cv2.COLOR_BGR2RGB)
            elif self.is_bw:
                frame = cv2.cvtColor(original_frame, cv2.COLOR_RGB2GRAY)
                _, frame = cv2.threshold(frame, 128, 255, cv2.THRESH_BINARY)
                frame = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB), cv2.COLOR_BGR2RGB)
            else:
                frame = original_frame

        image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.video_label.setPixmap(pixmap)
            
    # Helper method to display the frame
    def display_frame(self, frame):
        original_frame = frame.copy()  # Preserve the original color frame

        if original_frame.shape[-1] == 3 and original_frame.shape[-2] == 3:
            original_frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB)

        if self.is_grayscale:
            frame = cv2.cvtColor(original_frame, cv2.COLOR_RGB2GRAY)
            frame = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB), cv2.COLOR_BGR2RGB)
        elif self.is_bw:
            frame = cv2.cvtColor(original_frame, cv2.COLOR_RGB2GRAY)
            _, frame = cv2.threshold(frame, 128, 255, cv2.THRESH_BINARY)
            frame = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB), cv2.COLOR_BGR2RGB)

        image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.video_label.setPixmap(pixmap)
        
    def apply_filters(self):
        if self.cap:
            ret, frame = self.cap.read()
    
            if not ret:
                self.timer.stop()
                return  # Break the loop if no more frames are available
    
            # Apply Grayscale filter
            if self.is_grayscale:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB), cv2.COLOR_BGR2RGB)
    
            # Apply Black & White filter
            if self.is_bw:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, frame = cv2.threshold(frame, 128, 255, cv2.THRESH_BINARY)
                frame = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB), cv2.COLOR_BGR2RGB)
    
            # Apply Gaussian Blur filter
            if self.is_gaussian_blur:
                frame = cv2.GaussianBlur(frame, (5, 5), 0)
    
            # Apply Edge Detection (Canny) filter
            if self.is_edge_detection:
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                frame_edges = cv2.Canny(frame_gray, 50, 150)
                frame = cv2.cvtColor(frame_edges, cv2.COLOR_GRAY2RGB)
    
            # Apply Dilation filter
            if self.is_dilation:
                kernel = np.ones((5, 5), np.uint8)
                frame = cv2.dilate(frame, kernel, iterations=1)
    
            # Display the processed frame
            self.display_frame(frame)

    def change_speed(self, index):
        if self.cap:
            speed_options = {"1x": 30, "2x": 15, "0.5x": 60}
            speed = speed_options[self.speed_dropdown.currentText()]
            self.timer.setInterval(speed)

    def apply_grayscale(self):
        if self.cap:
            self.is_grayscale = not self.is_grayscale
            self.is_bw = False
            self.update_frame()

    def apply_bw(self):
        self.is_bw = not self.is_bw
        self.apply_filters()
        self.update_filter_status("Black & White Applied" if self.is_bw else "Black & White Removed")

    def apply_gaussian_blur(self):
        self.is_gaussian_blur = not self.is_gaussian_blur
        self.apply_filters()
        self.update_filter_status("Gaussian Blur Applied" if self.is_gaussian_blur else "Gaussian Blur Removed")

    def apply_edge_detection(self):
        self.is_edge_detection = not self.is_edge_detection
        self.apply_filters()
        self.update_filter_status("Edge Detection Applied" if self.is_edge_detection else "Edge Detection Removed")

    def apply_dilation(self):
        self.is_dilation = not self.is_dilation
        self.apply_filters()
        self.update_filter_status("Dilation Applied" if self.is_dilation else "Dilation Removed")
    
    def update_filter_status(self, status):
        self.filter_status_label.setText(status)

    def reset_color(self):
        self.is_grayscale = False
        self.is_bw = False
        self.update_frame()

    def backward_video(self):
        if self.cap:
            current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            new_frame = max(0, current_frame - 30)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    def forward_video(self):
        if self.cap:
            current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            new_frame = min(total_frames - 1, current_frame + 30)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    def closeEvent(self, event):
        # Release video capture when closing the application
        if self.cap:
            self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayerApp()
    player.show()
    sys.exit(app.exec_())
