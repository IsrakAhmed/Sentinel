from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFormLayout, QComboBox)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QThread, pyqtSignal
import cv2
from PyQt5.QtGui import QIcon


class CameraTestThread(QThread):
    result = pyqtSignal(bool)

    def __init__(self, rtsp_url):
        super().__init__()
        self.rtsp_url = rtsp_url

    def run(self):
        import cv2
        cap = cv2.VideoCapture(self.rtsp_url)
        success, _ = cap.read()
        cap.release()
        self.result.emit(success)
            

class AddCameraDialog(QDialog):
    """Dialog for adding a new camera stream"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Add Camera")
        self.setMinimumWidth(400)
        
        # Set up layout
        layout = QVBoxLayout(self)
        
        # Form layout for camera details
        form_layout = QFormLayout()
        
        # Camera name
        self.camera_name = QLineEdit()
        form_layout.addRow("Camera Name:", self.camera_name)
        
        # Camera URL
        self.camera_url = QLineEdit()
        self.camera_url.setPlaceholderText("rtsp://username:password@ip:port/stream")
        form_layout.addRow("RTSP URL:", self.camera_url)
        
        # Camera type
        self.camera_type = QComboBox()
        self.camera_type.addItems(["Dahua", "Hikvision", "Generic RTSP"])
        form_layout.addRow("Camera Type:", self.camera_type)
        
        # Username and password (optional fields)
        self.username = QLineEdit()
        form_layout.addRow("Username (optional):", self.username)
        
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password (optional):", self.password)
        
        # Testing connection option
        self.test_connection = QPushButton("Test Connection")
        self.test_connection.setIcon(QIcon("gui/resources/test.png"))
        form_layout.addRow("", self.test_connection)
        
        # Add form layout to main layout
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.add_btn = QPushButton("Add Camera")
        self.add_btn.setDefault(True)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_btn)
        
        # Add buttons to main layout
        layout.addLayout(buttons_layout)
        
        # Connect signals
        self.cancel_btn.clicked.connect(self.reject)
        self.add_btn.clicked.connect(self.accept)
        self.test_connection.clicked.connect(self.test_camera_connection)
        
        
    def test_camera_connection(self):
        """Test the connection to the camera using the provided details"""
        import time
        self.test_connection.setText("Testing...")
        self.test_connection.setEnabled(False)
        
        rtsp_url = self.camera_url.text().strip()
        
        username = self.username.text().strip()
        password = self.password.text().strip()
        
        if username and password and "@" not in rtsp_url:
            # Insert credentials into the RTSP URL if not already there
            parts = rtsp_url.split("rtsp://")
            if len(parts) == 2:
                rtsp_url = f"rtsp://{username}:{password}@{parts[1]}"
        
        # Start worker thread
        self.worker = CameraTestThread(rtsp_url)
        self.worker.result.connect(self.connection_test_complete)
        self.worker.start()
        
        
    def connection_test_complete(self, success=True):
        """Called when connection test completes"""
        if success:
            self.test_connection.setText("Connection Successful ✓")
            self.test_connection.setStyleSheet("color: green;")
        else:
            self.test_connection.setText("Connection Failed ✗")
            self.test_connection.setStyleSheet("color: red;")

        # Re-enable after a delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(2000, self.reset_test_button)
        
        
    def reset_test_button(self):
        """Reset the test button to its original state"""
        self.test_connection.setText("Test Connection")
        self.test_connection.setStyleSheet("")
        self.test_connection.setEnabled(True)