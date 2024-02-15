# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 21:16:30 2024

@author: Hp
"""
import sys
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QFileDialog, QComboBox

class VideoPlayerApp(QMainWindow):
    def __init__(self):
        super(VideoPlayerApp, self).__init__()

        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)

        self.video_path = None
        self.cap = None
        self.timer = QTimer(self)
        self.is_camera_mode = False
        self.is_grayscale = False
        self.is_bw = False

        # Camera variables
        self.camera_index = None
        self.camera_dropdown = QComboBox(self)
        self.camera_dropdown.setGeometry(210, 500, 150, 30)
        self.camera_dropdown.setVisible(False)
        self.camera_dropdown.currentIndexChanged.connect(self.change_camera)

        self.init_ui()

    def init_ui(self):
        # Video Frame
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setGeometry(50, 50, 700, 400)

        # Camera Mode Button
        self.camera_button = QPushButton("Camera Mode", self)
        self.camera_button.setGeometry(50, 500, 150, 30)
        self.camera_button.clicked.connect(self.toggle_camera_mode)

        # Camera Dropdown
        self.camera_dropdown = QComboBox(self)
        self.camera_dropdown.setGeometry(210, 500, 150, 30)
        self.camera_dropdown.setVisible(False)
        self.camera_dropdown.currentIndexChanged.connect(self.change_camera)

        # Open File Button
        self.open_button = QPushButton("Open Video", self)
        self.open_button.setGeometry(370, 500, 150, 30)
        self.open_button.clicked.connect(self.open_video)

        # Play Button
        self.play_button = QPushButton("Play", self)
        self.play_button.setGeometry(530, 500, 70, 30)
        self.play_button.clicked.connect(self.play_video)

        # Pause Button
        self.pause_button = QPushButton("Pause", self)
        self.pause_button.setGeometry(610, 500, 70, 30)
        self.pause_button.clicked.connect(self.pause_video)

        # Speed Dropdown
        self.speed_dropdown = QComboBox(self)
        self.speed_dropdown.setGeometry(50, 550, 150, 30)
        self.speed_dropdown.addItems(["1x", "2x", "0.5x"])
        self.speed_dropdown.currentIndexChanged.connect(self.change_speed)

        # Grayscale Button
        self.grayscale_button = QPushButton("Grayscale", self)
        self.grayscale_button.setGeometry(210, 550, 150, 30)
        self.grayscale_button.clicked.connect(self.apply_grayscale)

        # Black & White Button
        self.bw_button = QPushButton("Black & White", self)
        self.bw_button.setGeometry(370, 550, 150, 30)
        self.bw_button.clicked.connect(self.apply_bw)
        
        # Reset Color Button
        self.reset_color_button = QPushButton("Reset Color", self)
        self.reset_color_button.setGeometry(690, 550, 100, 30)  # Adjusted position
        self.reset_color_button.clicked.connect(self.reset_color)

        # Backward Button
        self.backward_button = QPushButton("Backward", self)
        self.backward_button.setGeometry(530, 550, 70, 30)
        self.backward_button.clicked.connect(self.backward_video)

        # Forward Button
        self.forward_button = QPushButton("Forward", self)
        self.forward_button.setGeometry(610, 550, 70, 30)
        self.forward_button.clicked.connect(self.forward_video)

        # Initialize camera dropdown options
        self.update_camera_dropdown()

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
            self.camera_button.setText("Video Mode")
            self.camera_dropdown.setVisible(True)
            self.open_button.setDisabled(True)
        else:
            self.camera_button.setText("Camera Mode")
            self.camera_dropdown.setVisible(False)
            self.open_button.setEnabled(True)

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
    
    def open_video(self):
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)")
        if self.video_path:
            if self.cap is not None and self.cap.isOpened():
                self.timer.stop()
                self.cap.release()
                self.video_label.clear()
            self.cap = cv2.VideoCapture(self.video_path)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)  # Update frame every 30 milliseconds
            self.is_camera_mode = False
            self.set_ui_state()
            self.update_frame()  # Update the frame immediately after loading
            self.print_video_properties()  # Print video properties
    
    def start_or_stop_camera(self):
        if self.is_camera_mode:
            if self.camera_index is not None:
                if self.cap is not None and self.cap.isOpened():
                    self.timer.stop()
                    self.cap.release()
                    self.video_label.clear()
                self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                self.timer.timeout.connect(self.update_frame)
                self.timer.start(30)  # Update frame every 30 milliseconds
                self.is_grayscale = False
                self.is_bw = False
                self.update_frame()  # Update the frame immediately after starting the camera
        else:
            if self.cap is not None and self.cap.isOpened():
                self.timer.stop()
                self.cap.release()
                self.video_label.clear()
                self.is_grayscale = False
                self.is_bw = False
                self.update_frame()  # Update the frame immediately after stopping the camera

    def play_video(self):
        if self.cap:
            self.timer.start()

    def pause_video(self):
        if self.cap:
            self.timer.stop()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            original_frame = frame.copy()  # Preserve the original color frame
    
            # Check if the original frame is in BGR format
            if original_frame.shape[-1] == 3 and original_frame.shape[-2] == 3:
                # Convert BGR to RGB
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

    def change_speed(self, index):
        if self.cap:
            speed_options = {"1x": 30, "2x": 15, "0.5x": 60}
            speed = speed_options[self.speed_dropdown.currentText()]
            self.timer.setInterval(speed)

    def apply_grayscale(self):
        if self.cap:
            self.is_grayscale = not self.is_grayscale
            self.is_bw = False

    def apply_bw(self):
        if self.cap:
            self.is_bw = not self.is_bw
            self.is_grayscale = False
            
    def reset_color(self):
        self.is_grayscale = False
        self.is_bw = False
        self.update_frame() # Update the frame immediately after resetting color

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
