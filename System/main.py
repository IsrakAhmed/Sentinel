from keras.models import load_model
import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import setup_logger

setup_logger()
    
# Create Qt application
app = QApplication(sys.argv)
    
# Set application style
app.setStyle("Fusion")
    
# Load and set stylesheet
with open("gui/resources/style.qss", "r") as f:
    app.setStyleSheet(f.read())
    
# Create and show main window
window = MainWindow(load_model = load_model)
window.show()
    
# Run application
sys.exit(app.exec_())