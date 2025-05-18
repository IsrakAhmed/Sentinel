import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFormLayout, QGroupBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap, QDesktopServices, QCursor
from PyQt5.QtCore import QUrl

class DeveloperInfoDialog(QDialog):
    """Dialog showing developer information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Developer Information")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Header with developer photo
        header_layout = QHBoxLayout()
        
        # Developer photo
        photo_container = QGroupBox()
        photo_layout = QVBoxLayout(photo_container)
        
        dev_photo_label = QLabel()
        dev_photo_path = "gui/resources/israk.jpg"
        
        # Use a placeholder if the photo doesn't exist
        if os.path.exists(dev_photo_path):
            photo_pixmap = QPixmap(dev_photo_path)
        else:
            photo_pixmap = QPixmap("gui/resources/placeholder_avatar.png")
            
        dev_photo_label.setPixmap(photo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        dev_photo_label.setAlignment(Qt.AlignCenter)
        photo_layout.addWidget(dev_photo_label)
        
        # Developer name as title
        info_container = QGroupBox("Developer Profile")
        info_layout = QFormLayout(info_container)
        
        # Set a nice font for the labels
        label_font = QFont()
        label_font.setBold(True)
        
        # Create and style name label
        name_label = QLabel("Israk Ahmed")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        
        # Developer info in form layout
        info_layout.addRow(QLabel("Name:"), QLabel("Israk Ahmed"))
        info_layout.addRow(QLabel("Title:"), QLabel("ML Engineer"))
        info_layout.addRow(QLabel("Institute:"), QLabel("TMSS Engineering College Affiliated with University of Rajshahi"))
        info_layout.addRow(QLabel("Email:"), self.create_link_label("israkahmed7@gmai.com"))
        info_layout.addRow(QLabel("Phone:"), QLabel("+880 1814-604703"))
        
        # Add GitHub link
        github_link = self.create_link_label("github.com/IsrakAhmed")
        github_link.setToolTip("Visit GitHub Profile")
        info_layout.addRow(QLabel("GitHub:"), github_link)
        
        # Add LinkedIn link
        linkedin_link = self.create_link_label("linkedin.com/in/israkahmed")
        linkedin_link.setToolTip("Visit LinkedIn Profile")
        info_layout.addRow(QLabel("LinkedIn:"), linkedin_link)
        
        # Add project description
        desc_container = QGroupBox("About this Project")
        desc_layout = QVBoxLayout(desc_container)
        
        project_desc = QLabel(
            "Sentinel is an advanced activity detection system using computer vision "
            "and deep learning technologies. It provides real-time monitoring and "
            "analysis of video streams to detect and classify various activities."
        )
        project_desc.setWordWrap(True)
        desc_layout.addWidget(project_desc)
        
        # Assemble the layout
        header_layout.addWidget(photo_container)
        header_layout.addWidget(info_container)
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(desc_container)
        
        # Close button
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
    
    def create_link_label(self, text):
        """Create a clickable label that opens a URL"""
        label = QLabel(f"<a href='{text}'>{text}</a>")
        label.setOpenExternalLinks(True)
        return label