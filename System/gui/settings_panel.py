from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QSlider, QComboBox,
                           QCheckBox, QGroupBox, QSpinBox, QDoubleSpinBox,
                           QFileDialog, QTabWidget, QFormLayout)
from PyQt5.QtCore import Qt, QSettings, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

import configparser
import os

class SettingsPanel(QWidget):
    """Panel for configuring application settings"""
    
    # Add a signal to notify about settings changes
    settings_saved = pyqtSignal()
    
    def __init__(self, main_window=None):
        super().__init__()
        
        # Store reference to main window
        self.main_window = main_window
        
        # Set up layout
        main_layout = QVBoxLayout(self)
        
        # Settings tabs
        settings_tabs = QTabWidget()
        
        # General settings tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Model settings
        model_group = QGroupBox("Model Settings")
        model_layout = QFormLayout(model_group)
        
        self.model_path = QLineEdit()
        self.model_path.setReadOnly(True)
        self.model_path.setText("models/multiclass_LRCN_model___Date_Time_2025_03_27__17_30_45___Loss_0.6180427074432373___Accuracy_0.8125.keras")
        
        model_path_layout = QHBoxLayout()
        model_path_layout.addWidget(self.model_path)
        
        self.browse_model_btn = QPushButton("Browse...")
        model_path_layout.addWidget(self.browse_model_btn)
        
        model_layout.addRow("Model Path:", model_path_layout)
        
        self.confidence_threshold = QDoubleSpinBox()
        self.confidence_threshold.setRange(0, 100)
        self.confidence_threshold.setValue(60)
        self.confidence_threshold.setSuffix("%")
        model_layout.addRow("Confidence Threshold:", self.confidence_threshold)
        
        self.prediction_interval = QSpinBox()
        self.prediction_interval.setRange(1, 30)
        self.prediction_interval.setValue(5)
        self.prediction_interval.setSuffix(" frames")
        model_layout.addRow("Prediction Interval:", self.prediction_interval)
        
        # Detection settings
        detection_group = QGroupBox("Detection Settings")
        detection_layout = QFormLayout(detection_group)
        
        self.use_gpu = QCheckBox("Use GPU acceleration")
        self.use_gpu.setChecked(True)
        detection_layout.addRow(self.use_gpu)
        
        self.enable_notifications = QCheckBox("Enable event notifications")
        self.enable_notifications.setChecked(True)
        detection_layout.addRow(self.enable_notifications)
        
        self.activity_classes = QLineEdit("accident, fighting, fire, normal")
        detection_layout.addRow("Activity Classes:", self.activity_classes)
        
        self.phone_number = QLineEdit("01766687218")
        detection_layout.addRow("Phone Number:", self.phone_number)
        
        # Add groups to general tab
        general_layout.addWidget(model_group)
        general_layout.addWidget(detection_group)
        general_layout.addStretch()
        
        # Display settings tab
        display_tab = QWidget()
        display_layout = QVBoxLayout(display_tab)
        
        # UI settings
        ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout(ui_group)
        
        self.display_resolution = QComboBox()
        self.display_resolution.addItems(["1080p (1920x1080)", "720p (1280x720)", "480p (854x480)"])
        ui_layout.addRow("Display Resolution:", self.display_resolution)
        
        self.frame_rate = QSpinBox()
        self.frame_rate.setRange(1, 60)
        self.frame_rate.setValue(30)
        self.frame_rate.setSuffix(" FPS")
        ui_layout.addRow("Frame Rate Limit:", self.frame_rate)
        
        self.theme = QComboBox()
        self.theme.addItems(["Dark Theme", "Light Theme", "System Default"])
        ui_layout.addRow("Interface Theme:", self.theme)
        
        # Camera settings
        camera_group = QGroupBox("Camera Settings")
        camera_layout = QFormLayout(camera_group)
        
        self.camera_timeout = QSpinBox()
        self.camera_timeout.setRange(1, 60)
        self.camera_timeout.setValue(10)
        self.camera_timeout.setSuffix(" seconds")
        camera_layout.addRow("Connection Timeout:", self.camera_timeout)
        
        self.reconnect_attempts = QSpinBox()
        self.reconnect_attempts.setRange(0, 10)
        self.reconnect_attempts.setValue(3)
        camera_layout.addRow("Reconnect Attempts:", self.reconnect_attempts)
        
        # Add groups to display tab
        display_layout.addWidget(ui_group)
        display_layout.addWidget(camera_group)
        display_layout.addStretch()
        
        # Storage settings tab
        storage_tab = QWidget()
        storage_layout = QVBoxLayout(storage_tab)
        
        # Recording settings
        recording_group = QGroupBox("Recording Settings")
        recording_layout = QFormLayout(recording_group)
        
        self.record_events = QCheckBox("Record detected events")
        self.record_events.setChecked(True)
        recording_layout.addRow(self.record_events)
        
        self.storage_location = QLineEdit("/recordings")
        storage_path_layout = QHBoxLayout()
        storage_path_layout.addWidget(self.storage_location)
        
        self.browse_storage_btn = QPushButton("Browse...")
        storage_path_layout.addWidget(self.browse_storage_btn)
        
        recording_layout.addRow("Storage Location:", storage_path_layout)
        
        self.max_storage = QSpinBox()
        self.max_storage.setRange(1, 1000)
        self.max_storage.setValue(50)
        self.max_storage.setSuffix(" GB")
        recording_layout.addRow("Max Storage Size:", self.max_storage)
        
        self.retention_period = QSpinBox()
        self.retention_period.setRange(1, 365)
        self.retention_period.setValue(30)
        self.retention_period.setSuffix(" days")
        recording_layout.addRow("Retention Period:", self.retention_period)
        
        # Add groups to storage tab
        storage_layout.addWidget(recording_group)
        storage_layout.addStretch()
        
        # Add all tabs
        settings_tabs.addTab(general_tab, "General")
        settings_tabs.addTab(display_tab, "Display")
        settings_tabs.addTab(storage_tab, "Storage")
        
        # Buttons for saving/resetting
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setIcon(QIcon("gui/resources/save.png"))
        
        self.reset_btn = QPushButton("Reset to Default")
        
        buttons_layout.addWidget(self.reset_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)
        
        # Add components to main layout
        main_layout.addWidget(settings_tabs)
        main_layout.addLayout(buttons_layout)
        
        # Connect signals
        self.browse_model_btn.clicked.connect(self.browse_model)
        self.browse_storage_btn.clicked.connect(self.browse_storage)
        self.save_btn.clicked.connect(self.save_settings)
        self.reset_btn.clicked.connect(self.reset_settings)
        
        # Load settings if they exist
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'sentinel_settings.ini')
        self.load_settings()
        
    def browse_model(self):
        """Browse for model file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Model File", "", "Model Files (*.keras *.h5);;All Files (*.*)"
        )
        if file_path:
            self.model_path.setText(file_path)
            
    def browse_storage(self):
        """Browse for storage directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Storage Directory", ""
        )
        if dir_path:
            self.storage_location.setText(dir_path)
            
            
    def load_settings(self):
        """Load settings from config file"""
        config = configparser.ConfigParser()
        
        if os.path.exists(self.config_file):
            try:
                config.read(self.config_file)
                
                # Model settings
                if 'ModelSettings' in config:
                    if 'model_path' in config['ModelSettings']:
                        self.model_path.setText(config['ModelSettings']['model_path'])
                    if 'confidence_threshold' in config['ModelSettings']:
                        self.confidence_threshold.setValue(float(config['ModelSettings']['confidence_threshold']))
                    if 'prediction_interval' in config['ModelSettings']:
                        self.prediction_interval.setValue(int(config['ModelSettings']['prediction_interval']))
                
                # Detection settings
                if 'DetectionSettings' in config:
                    if 'use_gpu' in config['DetectionSettings']:
                        self.use_gpu.setChecked(config['DetectionSettings'].getboolean('use_gpu'))
                    if 'enable_notifications' in config['DetectionSettings']:
                        self.enable_notifications.setChecked(config['DetectionSettings'].getboolean('enable_notifications'))
                    if 'activity_classes' in config['DetectionSettings']:
                        self.activity_classes.setText(config['DetectionSettings']['activity_classes'])
                    if 'phone_number' in config['DetectionSettings']:
                        self.phone_number.setText(config['DetectionSettings']['phone_number'])
                
                # UI settings
                if 'UISettings' in config:
                    if 'display_resolution' in config['UISettings']:
                        index = self.display_resolution.findText(config['UISettings']['display_resolution'])
                        if index >= 0:
                            self.display_resolution.setCurrentIndex(index)
                    if 'frame_rate' in config['UISettings']:
                        self.frame_rate.setValue(int(config['UISettings']['frame_rate']))
                    if 'theme' in config['UISettings']:
                        index = self.theme.findText(config['UISettings']['theme'])
                        if index >= 0:
                            self.theme.setCurrentIndex(index)
                
                # Camera settings
                if 'CameraSettings' in config:
                    if 'camera_timeout' in config['CameraSettings']:
                        self.camera_timeout.setValue(int(config['CameraSettings']['camera_timeout']))
                    if 'reconnect_attempts' in config['CameraSettings']:
                        self.reconnect_attempts.setValue(int(config['CameraSettings']['reconnect_attempts']))
                
                # Recording settings
                if 'RecordingSettings' in config:
                    if 'record_events' in config['RecordingSettings']:
                        self.record_events.setChecked(config['RecordingSettings'].getboolean('record_events'))
                    if 'storage_location' in config['RecordingSettings']:
                        self.storage_location.setText(config['RecordingSettings']['storage_location'])
                    if 'max_storage' in config['RecordingSettings']:
                        self.max_storage.setValue(int(config['RecordingSettings']['max_storage']))
                    if 'retention_period' in config['RecordingSettings']:
                        self.retention_period.setValue(int(config['RecordingSettings']['retention_period']))
                        
            except Exception as e:
                print(f"Error loading settings: {str(e)}")
            
    def save_settings(self):
        """Save current settings to config file"""
        # Create config parser
        config = configparser.ConfigParser()
        
        # Model settings
        config['ModelSettings'] = {
            'model_path': self.model_path.text(),
            'confidence_threshold': str(self.confidence_threshold.value()),
            'prediction_interval': str(self.prediction_interval.value())
        }
        
        # Detection settings
        config['DetectionSettings'] = {
            'use_gpu': str(self.use_gpu.isChecked()),
            'enable_notifications': str(self.enable_notifications.isChecked()),
            'activity_classes': self.activity_classes.text(),
            'phone_number': self.phone_number.text()
        }
        
        # UI settings
        config['UISettings'] = {
            'display_resolution': self.display_resolution.currentText(),
            'frame_rate': str(self.frame_rate.value()),
            'theme': self.theme.currentText()
        }
        
        # Camera settings
        config['CameraSettings'] = {
            'camera_timeout': str(self.camera_timeout.value()),
            'reconnect_attempts': str(self.reconnect_attempts.value())
        }
        
        # Recording settings
        config['RecordingSettings'] = {
            'record_events': str(self.record_events.isChecked()),
            'storage_location': self.storage_location.text(),
            'max_storage': str(self.max_storage.value()),
            'retention_period': str(self.retention_period.value())
        }
        
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Write settings to file
            with open(self.config_file, 'w') as configfile:
                config.write(configfile)
                
            # Update status label in main window
            if self.main_window and hasattr(self.main_window, 'status_label'):
                self.main_window.status_label.setText(f"Settings saved successfully to {self.config_file}")
            else:
                print(f"Settings saved successfully to {self.config_file}")
                
            # Emit the signal to notify about settings changes
            self.settings_saved.emit()
                
        except Exception as e:
            error_message = f"Error saving settings: {str(e)}"
            if self.main_window and hasattr(self.main_window, 'status_label'):
                self.main_window.status_label.setText(error_message)
            else:
                print(error_message)
        
    def reset_settings(self):
        """Reset settings to default values"""
        # Reset all settings to default
        self.confidence_threshold.setValue(60)
        self.prediction_interval.setValue(5)
        self.use_gpu.setChecked(True)
        self.enable_notifications.setChecked(True)
        self.activity_classes.setText("accident, fighting, fire, normal")
        self.display_resolution.setCurrentIndex(0)
        self.frame_rate.setValue(30)
        self.theme.setCurrentIndex(0)
        self.camera_timeout.setValue(10)
        self.reconnect_attempts.setValue(3)
        self.record_events.setChecked(True)
        self.max_storage.setValue(50)
        self.retention_period.setValue(30)