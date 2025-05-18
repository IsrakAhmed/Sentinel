from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QListWidget, QListWidgetItem, QFrame,
                           QPushButton, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QSize, QDateTime, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QFont

import pyqtgraph as pg
import time

class ActivityWidget(QWidget):
    """Widget displaying information about a single detected activity"""
    
    def __init__(self, activity_type, camera_name, confidence, timestamp):
        super().__init__()
        
        self.activity_type = activity_type
        self.camera_name = camera_name
        self.confidence = confidence
        self.timestamp = timestamp
        
        # Set up UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Activity type with appropriate icon
        header_layout = QHBoxLayout()
        
        # Set icon based on activity type
        icon_path = "gui/resources/"
        if "Fire" in activity_type:
            icon_path += "fire.png"
            self.setStyleSheet("background-color: rgba(255, 100, 100, 0.2); border-radius: 5px;")
        elif "Fighting" in activity_type:
            icon_path += "fight.png"
            self.setStyleSheet("background-color: rgba(255, 100, 100, 0.2); border-radius: 5px;")
        elif "Accident" in activity_type:
            icon_path += "accident.png"
            self.setStyleSheet("background-color: rgba(255, 100, 100, 0.2); border-radius: 5px;")
        else:
            icon_path += "normal.png"
            self.setStyleSheet("background-color: rgba(100, 255, 100, 0.2); border-radius: 5px;")
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        
        activity_label = QLabel(activity_type)
        activity_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(activity_label)
        header_layout.addStretch()
        
        # Camera name and timestamp
        info_layout = QHBoxLayout()
        camera_label = QLabel(f"Camera: {camera_name}")
        camera_label.setFont(QFont("Arial", 8))
        
        time_str = QDateTime.fromMSecsSinceEpoch(int(timestamp * 1000)).toString("hh:mm:ss")
        time_label = QLabel(time_str)
        time_label.setFont(QFont("Arial", 8))
        time_label.setAlignment(Qt.AlignRight)
        
        info_layout.addWidget(camera_label)
        info_layout.addStretch()
        info_layout.addWidget(time_label)
        
        # Confidence bar
        conf_layout = QHBoxLayout()
        conf_label = QLabel("Confidence:")
        conf_label.setFont(QFont("Arial", 8))
        
        conf_bar = QProgressBar()
        conf_bar.setRange(0, 100)
        conf_bar.setValue(int(confidence))
        conf_bar.setTextVisible(True)
        conf_bar.setFormat(f"{confidence:.1f}%")
        
        # Set color based on confidence
        if confidence > 90:
            conf_bar.setStyleSheet("QProgressBar { text-align: center; } QProgressBar::chunk { background-color: #22bb22; }")
        elif confidence > 70:
            conf_bar.setStyleSheet("QProgressBar { text-align: center; } QProgressBar::chunk { background-color: #bbbb22; }")
        else:
            conf_bar.setStyleSheet("QProgressBar { text-align: center; } QProgressBar::chunk { background-color: #bb5522; }")
            
        conf_layout.addWidget(conf_label)
        conf_layout.addWidget(conf_bar)
        
        # Add all layouts to main layout
        layout.addLayout(header_layout)
        layout.addLayout(info_layout)
        layout.addLayout(conf_layout)
        
        # Set fixed height for consistent look
        self.setFixedHeight(120)


class ActivityPanel(QWidget):
    """Panel for displaying recent activities and statistics"""
    
    # Signal to request camera predictions
    request_camera_stats = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Set up layout
        main_layout = QVBoxLayout(self)
        
        # Activity graph
        graph_title = QLabel("Activity Timeline")
        graph_title.setFont(QFont("Arial", 10, QFont.Bold))
        
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('transparent')
        self.graph_widget.setMinimumHeight(150)
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        self.graph_widget.setLabel('left', 'Activity')
        self.graph_widget.setLabel('bottom', 'Time (s)')
        self.graph_widget.getAxis('bottom').setPen(pg.mkPen(color='#888'))
        self.graph_widget.getAxis('left').setPen(pg.mkPen(color='#888'))
        
        # Initialize data for the graph
        self.times = list(range(-30, 1))
        self.normal_values = [0] * len(self.times)
        self.abnormal_values = [0] * len(self.times)
        
        # Create plot items with distinct colors
        self.normal_line = self.graph_widget.plot(
            self.times, self.normal_values, 
            pen=pg.mkPen(color=(0, 200, 0), width=2),
            name="Normal"
        )
        self.abnormal_line = self.graph_widget.plot(
            self.times, self.abnormal_values,
            pen=pg.mkPen(color=(200, 0, 0), width=2),
            name="Abnormal"
        )
        
        self.graph_widget.addLegend()
        
        # Recent activities list
        activities_title = QLabel("Recent Activities")
        activities_title.setFont(QFont("Arial", 10, QFont.Bold))
        
        self.activities_list = QListWidget()
        self.activities_list.setAlternatingRowColors(True)
        self.activities_list.setSpacing(5)
        
        # Add components to main layout
        main_layout.addWidget(graph_title)
        main_layout.addWidget(self.graph_widget)
        main_layout.addWidget(activities_title)
        main_layout.addWidget(self.activities_list)
        
        # Set up timer for graph updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_graph)
        self.update_timer.start(1000)  # Update every second
        
        # Initialize storage for tracking camera predictions
        self.camera_predictions = {}
        
    def set_camera_view(self, camera_view):
        """Connect to the camera view to receive activity updates"""
        self.camera_view = camera_view
        
        # Connect to the prediction results from the camera view's worker threads
        if hasattr(camera_view, 'prediction_workers'):
            for camera_name, worker in camera_view.prediction_workers.items():
                if hasattr(worker, 'prediction_ready'):
                    worker.prediction_ready.connect(
                        lambda class_name, text, confidence, cam=camera_name: 
                        self.on_prediction(cam, class_name, text, confidence)
                    )
    
    def on_prediction(self, camera_name, class_name, activity_text, confidence):
        """Handle new prediction from camera view"""
        timestamp = time.time()
        
        # Store prediction for graph updates
        self.camera_predictions[camera_name] = {
            "class_name": class_name,
            "text": activity_text,
            "confidence": confidence,
            "timestamp": timestamp
        }
        
        # Add to activity list if abnormal or occasional normal
        if class_name != "normal":
            # Always log abnormal activities
            self.add_activity(activity_text, camera_name, confidence, timestamp)
        elif len(self.activities_list) < 2 or time.time() - getattr(self, 'last_normal_log', 0) > 60:
            # Occasionally log normal activities (if list is empty or it's been a minute)
            self.add_activity(activity_text, camera_name, confidence, timestamp)
            self.last_normal_log = time.time()
    
    def add_activity(self, activity_type, camera_name, confidence, timestamp):
        """Add a new activity to the list"""
        # Create custom widget for the activity
        activity_widget = ActivityWidget(activity_type, camera_name, confidence, timestamp)
        
        # Create list item and set it to use our custom widget
        item = QListWidgetItem()
        item.setSizeHint(activity_widget.sizeHint())
        
        # Insert at the top of the list
        self.activities_list.insertItem(0, item)
        self.activities_list.setItemWidget(item, activity_widget)
        
        # Limit list size
        while self.activities_list.count() > 50:
            self.activities_list.takeItem(self.activities_list.count() - 1)
    
    @pyqtSlot()
    def update_graph(self):
        """Update activity graph data with real prediction values"""
        # Shift data to the left
        self.times = self.times[1:] + [self.times[-1] + 1]
        
        # Calculate new values based on current predictions
        new_normal = 0.5  # Baseline
        new_abnormal = 0.0
        
        # Process all active camera predictions
        if self.camera_predictions:
            # Check for any abnormal activities in the past 5 seconds
            current_time = time.time()
            for camera_name, prediction in self.camera_predictions.items():
                # Only consider recent predictions (within last 5 seconds)
                if current_time - prediction["timestamp"] > 5:
                    continue
                    
                if prediction["class_name"] == "normal":
                    # Increase normal activity based on confidence
                    normal_factor = prediction["confidence"] / 100
                    new_normal = max(new_normal, 0.3 + (normal_factor * 0.5))
                else:
                    # For abnormal activities, base value on confidence
                    abnormal_factor = prediction["confidence"] / 100
                    
                    if prediction["class_name"] == "fire":
                        # Fire is highest priority
                        new_abnormal = max(new_abnormal, abnormal_factor * 0.9)
                    elif prediction["class_name"] == "accident":
                        new_abnormal = max(new_abnormal, abnormal_factor * 0.8)
                    elif prediction["class_name"] == "fighting":
                        new_abnormal = max(new_abnormal, abnormal_factor * 0.7)
        
        # Add the new values to the data arrays
        self.normal_values = self.normal_values[1:] + [new_normal]
        self.abnormal_values = self.abnormal_values[1:] + [new_abnormal]
        
        # Update the plot
        self.normal_line.setData(self.times, self.normal_values)
        self.abnormal_line.setData(self.times, self.abnormal_values)