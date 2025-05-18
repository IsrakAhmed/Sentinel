import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QComboBox, QTabWidget,
                            QLineEdit, QGridLayout, QGroupBox, QCheckBox,
                            QStatusBar, QSplitter, QFrame, QSpacerItem,
                            QSizePolicy, QDialog, QFormLayout, QSpinBox,
                            QAction, QMenu)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize, QDateTime
from PyQt5.QtGui import QIcon, QFont, QPixmap

from gui.camera_view import CameraView
from gui.activity_panel import ActivityPanel
from gui.settings_panel import SettingsPanel
from gui.history_panel import HistoryPanel
from gui.add_camera_dialog import AddCameraDialog
from gui.developer_info import DeveloperInfoDialog
from core.camera_manager import CameraManager

class MainWindow(QMainWindow):
    def __init__(self, load_model):
        super().__init__()
        
        self.load_model = load_model
        
        # Set window properties
        self.setWindowTitle("Sentinel - Activity Detection System")
        self.setMinimumSize(1400, 800)
        
        # Initialize camera manager
        self.camera_manager = CameraManager()
        
        # Set up UI
        self.setup_ui()
        
        # Set up menu
        self.setup_menu()
        
        # Connect signals/slots
        self.connect_signals()
    
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create header with title and controls
        header_layout = QHBoxLayout()
        
        # Logo and title
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap("gui/resources/sentinel_logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        title_label = QLabel("SENTINEL")
        title_label.setObjectName("title-label")
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_label)
        logo_layout.addStretch()
        
        # Controls
        controls_layout = QHBoxLayout()
        self.camera_selector = QComboBox()
        self.camera_selector.setMinimumWidth(200)
        self.camera_selector.addItem("All Cameras")
        
        self.add_camera_btn = QPushButton("Add Camera")
        self.add_camera_btn.setIcon(QIcon("gui/resources/add_camera.png"))
        self.add_camera_btn.setToolTip("Add a new camera stream")
        
        # Add developer info button
        self.developer_info_btn = QPushButton("Developer Info")
        self.developer_info_btn.setIcon(QIcon("gui/resources/info.png"))
        self.developer_info_btn.setToolTip("About the developer")
        
        controls_layout.addWidget(QLabel("Camera:"))
        controls_layout.addWidget(self.camera_selector)
        controls_layout.addWidget(self.add_camera_btn)
        controls_layout.addWidget(self.developer_info_btn)
        
        header_layout.addLayout(logo_layout, 1)
        header_layout.addLayout(controls_layout)
        
        # Create main content area with splitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Camera view
        self.camera_container = QWidget()
        camera_layout = QVBoxLayout(self.camera_container)
        camera_layout.setContentsMargins(0, 0, 0, 0)
        
        self.camera_view = CameraView(camera_manager=self.camera_manager, load_model=self.load_model)
        camera_layout.addWidget(self.camera_view)
        
        # Right panel: tabs for different functions
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Activity tab
        self.activity_panel = ActivityPanel()
        self.tab_widget.addTab(self.activity_panel, "Activity")
        # Connect activity panel to camera view for real data
        self.camera_view.set_activity_panel(self.activity_panel)
        
        # History tab
        #self.history_panel = HistoryPanel()
        #self.tab_widget.addTab(self.history_panel, "History")
        
        # Settings tab
        self.settings_panel = SettingsPanel()
        self.tab_widget.addTab(self.settings_panel, "Settings")
        
        right_layout.addWidget(self.tab_widget)
        
        # Add panels to splitter
        self.splitter.addWidget(self.camera_container)
        self.splitter.addWidget(right_panel)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.status_label)
        
        # Add all components to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.splitter, 1)
    
    
    def setup_menu(self):
        """Set up the application menu bar"""
        # Create menu bar
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        # Add camera action
        add_camera_action = QAction("Add Camera", self)
        add_camera_action.triggered.connect(self.show_add_camera_dialog)
        file_menu.addAction(add_camera_action)
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        # About action
        about_action = QAction("About Developer", self)
        about_action.triggered.connect(self.show_developer_info)
        help_menu.addAction(about_action)
        
    
    def connect_signals(self):
        self.add_camera_btn.clicked.connect(self.show_add_camera_dialog)
        self.camera_selector.currentIndexChanged.connect(self.on_camera_changed)
        self.developer_info_btn.clicked.connect(self.show_developer_info)
        
        # Connect settings panel signal to camera view
        if hasattr(self, 'settings_panel') and hasattr(self, 'camera_view'):
            self.settings_panel.settings_saved.connect(self.on_settings_saved)
    
    def on_settings_saved(self):
        """Update status when settings are saved"""
        self.status_label.setText("Settings applied")
        
    def show_developer_info(self):
        """Show the developer information dialog"""
        dialog = DeveloperInfoDialog(self)
        dialog.exec_()
        
    def show_add_camera_dialog(self):
        dialog = AddCameraDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.camera_name.text().strip()
            url = dialog.camera_url.text().strip()
            cam_type = dialog.camera_type.currentText()
            username = dialog.username.text().strip()
            password = dialog.password.text().strip()
            
            if name and url:
                if username and password and "@" not in url:
                    if url.startswith("rtsp://"):
                        url = f"rtsp://{username}:{password}@" + url[len("rtsp://"):]
                        
                self.add_camera(name, url)
    
    def add_camera(self, name, url):
        # Add to camera manager
        success = self.camera_manager.add_camera(name, url)
        self.camera_view.add_camera(name)
        if success:
            # Update the combo box
            self.camera_selector.addItem(name)
            self.camera_selector.setCurrentText(name)
            self.status_label.setText(f"Camera {name} added successfully")
        else:
            self.status_label.setText(f"Failed to add camera {name}")
    
    def on_camera_changed(self, index):
        if index == 0:
            # All cameras selected
            self.camera_view.show_all_cameras()
        else:
            camera_name = self.camera_selector.currentText()
            self.camera_view.show_camera(camera_name)
            
    def closeEvent(self, event):
        # Clean up resources
        self.camera_manager.stop_all_cameras()
        event.accept()