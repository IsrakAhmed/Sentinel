from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QPushButton,
                            QDateEdit, QComboBox, QHeaderView)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QColor, QBrush, QIcon, QFont

import random
import time

class HistoryPanel(QWidget):
    """Panel for viewing historical activity data"""
    
    def __init__(self):
        super().__init__()
        
        # Set up layout
        main_layout = QVBoxLayout(self)
        
        # Filters section
        filters_layout = QHBoxLayout()
        
        # Date range
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        
        self.date_from = QDateEdit(QDate.currentDate().addDays(-7))
        self.date_from.setCalendarPopup(True)
        
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(QLabel("to"))
        
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        
        date_layout.addWidget(self.date_to)
        
        # Activity type filter
        activity_layout = QHBoxLayout()
        activity_layout.addWidget(QLabel("Activity:"))
        
        self.activity_filter = QComboBox()
        
        activity_layout.addWidget(self.activity_filter)
        
        # Camera filter
        camera_layout = QHBoxLayout()
        camera_layout.addWidget(QLabel("Camera:"))
        
        self.camera_filter = QComboBox()
        
        camera_layout.addWidget(self.camera_filter)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setIcon(QIcon("gui/resources/search.png"))
        
        # Export button
        self.export_button = QPushButton("Export")
        self.export_button.setIcon(QIcon("gui/resources/export.png"))
        
        # Add all filter controls to filters layout
        filters_layout.addLayout(date_layout)
        filters_layout.addLayout(activity_layout)
        filters_layout.addLayout(camera_layout)
        filters_layout.addWidget(self.search_button)
        filters_layout.addWidget(self.export_button)
        
        # Results table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Timestamp", "Camera", "Activity", "Confidence", "Duration"
        ])
        
        # Set table properties
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Results count label
        self.results_label = QLabel("Showing 0 results")
        self.results_label.setAlignment(Qt.AlignRight)
        
        # Add all components to main layout
        main_layout.addLayout(filters_layout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.results_label)
        
        # Connect signals
        self.search_button.clicked.connect(self.search_history)
        self.export_button.clicked.connect(self.export_history)
        
        # Load initial demo data
        self.search_history()
        
    def search_history(self):
        """Search historical data with the current filters"""
        # Clear existing data
        self.table.setRowCount(0)
        
        # In a real app, this would query a database
        # Generate demo data instead
        num_results = random.randint(20, 50)
        
        # Generate random results
        results = []
        
        # Get filter values
        date_from = self.date_from.date().startOfDay().toSecsSinceEpoch()
        date_to = self.date_to.date().addDays(1).startOfDay().toSecsSinceEpoch()
        activity_filter = self.activity_filter.currentText()
        camera_filter = self.camera_filter.currentText()
        
        current_time = time.time()
        
        for i in range(num_results):
            # Random timestamp within date range
            timestamp = random.uniform(date_from, date_to)
            
            # Random camera
            cameras = ["Main Entrance", "Parking Lot", "Hallway", "Office Area", "Reception"]
            if camera_filter != "All Cameras":
                camera = camera_filter
            else:
                camera = random.choice(cameras)
                
            # Random activity
            activities = {
                "Normal Activity": 70,
                "Abnormal Activity [ Fire ]": 10,
                "Abnormal Activity [ Fighting ]": 10,
                "Abnormal Activity [ Accident ]": 10
            }
            
            if activity_filter == "All Activities":
                activity = random.choices(
                    list(activities.keys()),
                    weights=list(activities.values()),
                    k=1
                )[0]
            elif activity_filter == "Normal Activity":
                activity = "Normal Activity"
            elif activity_filter == "Abnormal - Fire":
                activity = "Abnormal Activity [ Fire ]"
            elif activity_filter == "Abnormal - Fighting":
                activity = "Abnormal Activity [ Fighting ]"
            elif activity_filter == "Abnormal - Accident":
                activity = "Abnormal Activity [ Accident ]"
                
            # Random confidence and duration
            confidence = random.uniform(70, 99)
            duration = random.uniform(2, 20)
            
            # Add the result
            results.append({
                "timestamp": timestamp,
                "camera": camera,
                "activity": activity,
                "confidence": confidence,
                "duration": duration
            })
            
        # Sort results by timestamp (newest first)
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Add results to table
        self.table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            # Format timestamp
            time_str = QDateTime.fromSecsSinceEpoch(int(result["timestamp"])).toString("yyyy-MM-dd hh:mm:ss")
            self.table.setItem(row, 0, QTableWidgetItem(time_str))
            
            # Camera
            self.table.setItem(row, 1, QTableWidgetItem(result["camera"]))
            
            # Activity with color coding
            activity_item = QTableWidgetItem(result["activity"])
            if "Abnormal" in result["activity"]:
                activity_item.setForeground(QBrush(QColor(255, 0, 0)))
            else:
                activity_item.setForeground(QBrush(QColor(0, 128, 0)))
            self.table.setItem(row, 2, activity_item)
            
            # Confidence
            conf_item = QTableWidgetItem(f"{result['confidence']:.1f}%")
            self.table.setItem(row, 3, conf_item)
            
            # Duration
            duration_item = QTableWidgetItem(f"{result['duration']:.1f}s")
            self.table.setItem(row, 4, duration_item)
            
        # Update results count
        self.results_label.setText(f"Showing {len(results)} results")
            
    def export_history(self):
        """Export the current history data to a CSV file"""
        # In a real app, this would save the data to a file
        # Just show a message in the results label for demo
        self.results_label.setText("Data exported to history_export.csv")