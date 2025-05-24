from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QGridLayout, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal, QSize, QThread
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QFont


import cv2
import numpy as np
import time
from collections import deque
import threading
import configparser
import os
import time


class CameraViewport(QLabel):
    """Widget for displaying a single camera stream with overlaid information"""
    
    def __init__(self, camera_name="Camera"):
        super().__init__()
        self.camera_name = camera_name
        self.current_frame = None
        self.current_activity = "Detecting..."
        self.activity_color = QColor(255, 255, 0)  # Yellow for detecting
        self.confidence = 0
        self.last_updated = time.time()
        
        # Set up appearance
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(320, 240)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333333;")
        self.setText("Initializing camera...")
        
    def update_frame(self, frame, activity=None, confidence=None):
        """Update the displayed frame and activity information"""
        self.current_frame = frame
        
        if activity:
            self.current_activity = activity
            self.confidence = confidence
            self.last_updated = time.time()
            
            # Set color based on activity
            if activity == "Normal Activity":
                self.activity_color = QColor(0, 255, 0)  # Green
            elif activity.startswith("Abnormal"):
                self.activity_color = QColor(255, 0, 0)  # Red
            else:
                self.activity_color = QColor(255, 255, 0)  # Yellow
        
        # Convert frame to QImage for display
        if frame is not None:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            
            # Scale the image to fit the label while maintaining aspect ratio
            pixmap = QPixmap.fromImage(q_img)
            self.setPixmap(pixmap.scaled(self.width(), self.height(), 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation))
        
    def paintEvent(self, event):
        """Override paint event to add overlay information"""
        super().paintEvent(event)
        
        if self.current_frame is not None:
            painter = QPainter(self)
            
            # Set up fonts
            title_font = QFont("Arial", 10, QFont.Bold)
            info_font = QFont("Arial", 9)
            
            # Draw semi-transparent header bar
            painter.setOpacity(0.7)
            painter.fillRect(0, 0, self.width(), 30, QColor(0, 0, 0))
            
            # Draw camera name
            painter.setOpacity(1.0)
            painter.setPen(Qt.white)
            painter.setFont(title_font)
            painter.drawText(10, 20, self.camera_name)
            
            # Draw semi-transparent footer bar
            painter.setOpacity(0.7)
            painter.fillRect(0, self.height() - 30, self.width(), 30, QColor(0, 0, 0))
            
            # Draw activity status
            painter.setOpacity(1.0)
            painter.setPen(self.activity_color)
            painter.setFont(info_font)
            
            activity_text = self.current_activity
            if self.confidence:
                activity_text += f" ({self.confidence:.1f}%)"
                
            painter.drawText(10, self.height() - 10, activity_text)
            
            # Draw timestamp
            timestamp = time.strftime("%H:%M:%S", time.localtime(self.last_updated))
            timestamp_width = painter.fontMetrics().horizontalAdvance(timestamp)
            painter.setPen(Qt.white)
            painter.drawText(self.width() - timestamp_width - 10, self.height() - 10, timestamp)



# Threaded video stream class
class VideoStream:
    def __init__(self, src):
        self.capture = cv2.VideoCapture(src)
        self.ret, self.frame = self.capture.read()
        self.stopped = False
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while not self.stopped:
            self.ret, self.frame = self.capture.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.stopped = True
        self.capture.release()



class PredictionWorker(QThread):
    """Worker thread for running predictions without blocking UI"""
    prediction_ready = pyqtSignal(str, str, float)
    
    def __init__(self, model, frames_queue, classes_list, confidence_threshold=60.0):
        super().__init__()
        self.model = model
        self.frames_queue = list(frames_queue)  # Create a copy of the frames
        self.classes_list = classes_list
        self.confidence_threshold = confidence_threshold
        
    def run(self):
        """Process predictions in background thread"""
        try:
            input_frames = np.expand_dims(self.frames_queue, axis=0)
            predicted_label_probs = self.model.predict(input_frames, verbose=0)[0]
            predicted_label = np.argmax(predicted_label_probs)
            predicted_class_name = self.classes_list[predicted_label]
            confidence = predicted_label_probs[predicted_label] * 100
            
            # Emit signal with results
            #self.prediction_ready.emit(predicted_class_name, self._get_display_text(predicted_class_name), confidence)
        
            # Apply confidence threshold
            if confidence < self.confidence_threshold:
                predicted_class_name = "normal"
                display_text = self._get_display_text(predicted_class_name)
                confidence = 80
            else:
                display_text = self._get_display_text(predicted_class_name)
            
            # Emit signal with results
            self.prediction_ready.emit(predicted_class_name, display_text, confidence)
        
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            
    def _get_display_text(self, class_name):
        """Convert class name to display text"""
        if class_name == "accident":
            return "Abnormal Activity [ Accident ]"
        elif class_name == "fighting":
            return "Abnormal Activity [ Fighting ]"
        elif class_name == "fire":
            return "Abnormal Activity [ Fire ]"
        else:
            return "Normal Activity"



class CameraView(QWidget):
    """Widget for displaying multiple camera streams"""
    
    def __init__(self, camera_manager=None, setting_panel=None, load_model=None, message_sender=None):
        super().__init__()
        self.camera_manager = camera_manager
        self.settings_panel = setting_panel
        self.message_sender = message_sender  # For sending SMS alerts
        self.last_sms_time = {}
        self.cameras = {}  # Dictionary of camera viewports
        self.layout_mode = "grid"  # or "single"
        
        self.load_model_func = load_model
        self.model = None
        self.CLASSES_LIST = ["accident", "fighting", "fire", "normal"]  # Default classes
        self.IMAGE_HEIGHT, self.IMAGE_WIDTH = 128, 128
        self.SEQUENCE_LENGTH = 10
        self.confidence_threshold = 60.0  # Default confidence threshold
        self.prediction_interval = 5  # Default prediction interval
        
        
        # Dictionary to store frame queues for each camera
        self.frames_queues = {}
        self.frame_counters = {}
        self.prediction_workers = {}
        self.camera_predictions = {}
        
        # Reference to activity panel (will be set from MainWindow)
        self.activity_panel = None
        
        
        # Set up layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        
        # Create grid layout for cameras
        self.grid_layout = QGridLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(5)
        
        # Create grid layout for cameras
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)
        
        self.main_layout.addLayout(self.grid_layout)
        
        # Load configuration
        self.load_config()
        
        # Try to load the model during initialization
        self.try_load_model()
        
        if self.settings_panel:
            self.settings_panel.settings_saved.connect(self.on_settings_saved)
        
        # Create demo cameras for testing
        #self.create_demo_cameras()
        
        # Start update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_cameras)
        self.timer.start(33)  # ~30 FPS
        
    
    def should_send_sms(self, camera_name, interval_minutes=5):
        now = time.time()
        
        last = self.last_sms_time.get(camera_name, 0)
        interval_seconds = interval_minutes * 60
        
        if now - last > interval_seconds:
            self.last_sms_time[camera_name] = now
            return True
        
        return False

    
    
    def load_config(self):
        """Load configuration settings from file"""
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'sentinel_settings.ini')
        
        if os.path.exists(config_file):
            try:
                config = configparser.ConfigParser()
                config.read(config_file)
                
                # Load model settings
                if 'ModelSettings' in config:
                    if 'model_path' in config['ModelSettings']:
                        self.model_path = config['ModelSettings']['model_path']
                    if 'confidence_threshold' in config['ModelSettings']:
                        self.confidence_threshold = float(config['ModelSettings']['confidence_threshold'])
                    if 'prediction_interval' in config['ModelSettings']:
                        self.prediction_interval = int(config['ModelSettings']['prediction_interval'])
                
                # Load detection settings
                if 'DetectionSettings' in config:
                    if 'activity_classes' in config['DetectionSettings']:
                        self.CLASSES_LIST = [cls.strip() for cls in config['DetectionSettings']['activity_classes'].split(",")]
                    if 'phone_number' in config['DetectionSettings']:
                        self.phone_number = config['DetectionSettings']['phone_number'].strip()
                        if self.settings_panel:
                            self.settings_panel.phone_number.setText(self.phone_number)
                
                # Load UI settings
                if 'UISettings' in config:
                    if 'frame_rate' in config['UISettings']:
                        fps = int(config['UISettings']['frame_rate'])
                        if fps > 0:
                            self.timer.setInterval(1000 // fps)  # Convert FPS to interval in ms
                
                print(f"Configuration loaded successfully.")
                print(f"Using model path: {getattr(self, 'model_path', 'Default')}")
                print(f"Classes: {self.CLASSES_LIST}")
                print(f"Confidence threshold: {self.confidence_threshold}%")
                print(f"Prediction interval: {self.prediction_interval} frames")
                
            except Exception as e:
                print(f"Error loading configuration: {str(e)}")
                
    
    def on_settings_saved(self):
        """Handle settings saved event by reloading configuration"""
        print("Settings have been saved, reloading configuration...")
        
        # Store current model path to check if it changed
        old_model_path = getattr(self, 'model_path', None)
        old_classes = self.CLASSES_LIST.copy()
        
        # Reload the configuration
        self.load_config()
        
        # Check if we need to reload the model due to changes
        new_model_path = getattr(self, 'model_path', None)
        if old_model_path != new_model_path or old_classes != self.CLASSES_LIST:
            print("Model path or classes changed, reloading model...")
            self.model = None  # Force model reload
            self.try_load_model()
    
        
    def try_load_model(self):
        """Try to load the model if the load_model function is available"""
        try:
            if self.load_model_func:
                # Use the model path from config if available
                model_path = getattr(self, 'model_path', None)
                
                # If no model path in config, use default
                if not model_path:
                    model_path = "models/multiclass_LRCN_model___Date_Time_2025_03_27__17_30_45___Loss_0.6180427074432373___Accuracy_0.8125.keras"
                    
                self.model = self.load_model_func(model_path)
                print(f"Model loaded successfully from {model_path}")
            else:
                print("No load_model function provided, model will not be loaded")
        except Exception as e:
            print(f"Error loading model during initialization: {str(e)}")
            
    
    def set_activity_panel(self, activity_panel):
        """Connect to the activity panel for sending activity updates"""
        self.activity_panel = activity_panel
        
        # Connect the existing prediction workers to the activity panel
        for camera_name, worker in self.prediction_workers.items():
            if hasattr(worker, 'prediction_ready'):
                worker.prediction_ready.connect(
                    lambda class_name, text, confidence, cam=camera_name: 
                    self.activity_panel.on_prediction(cam, class_name, text, confidence)
                    if self.activity_panel else None
                )
    
        
    def add_camera(self, name):
        """Add a new camera viewport"""
        viewport = CameraViewport(name)
        self.cameras[name] = viewport
        
        # Initialize frame queue for this camera
        self.frames_queues[name] = deque(maxlen=self.SEQUENCE_LENGTH)
        self.frame_counters[name] = 0
        self.camera_predictions[name] = {"text": "Detecting...", "confidence": 0}
        
        self.update_layout()
        return viewport
        
    def remove_camera(self, name):
        """Remove a camera viewport"""
        if name in self.cameras:
            self.grid_layout.removeWidget(self.cameras[name])
            self.cameras[name].deleteLater()
            del self.cameras[name]
            
            # Clean up resources for this camera
            if name in self.frames_queues:
                del self.frames_queues[name]
            if name in self.frame_counters:
                del self.frame_counters[name]
            if name in self.prediction_workers and self.prediction_workers[name].isRunning():
                self.prediction_workers[name].terminate()
                self.prediction_workers[name].wait()
                del self.prediction_workers[name]
            if name in self.camera_predictions:
                del self.camera_predictions[name]
            
            self.update_layout()
    
    def update_layout(self):
        """Update the grid layout based on the number of cameras"""
        # Clear the grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        if not self.cameras:
            placeholder = QLabel("No cameras available.\nAdd a camera to begin monitoring.")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #888; font-size: 14px;")
            self.grid_layout.addWidget(placeholder, 0, 0)
            return
            
        # Determine grid dimensions based on camera count
        count = len(self.cameras)
        if count == 1:
            cols, rows = 1, 1
        elif count <= 4:
            cols, rows = 2, 2
        elif count <= 9:
            cols, rows = 3, 3
        else:
            cols, rows = 4, 3  # Max 12 cameras
            
        # Add cameras to grid
        camera_items = list(self.cameras.items())
        for i, (name, viewport) in enumerate(camera_items):
            if i >= cols * rows:
                break  # Don't add more than the grid can hold
                
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(viewport, row, col)
    
    def show_camera(self, name):
        """Show a single camera view"""
        if name in self.cameras:
            # Hide all viewports
            for cam_name, viewport in self.cameras.items():
                viewport.hide()
            
            # Show only the selected viewport
            self.cameras[name].show()
            self.layout_mode = "single"
    
    def show_all_cameras(self):
        """Show all cameras in grid view"""
        for cam_name, viewport in self.cameras.items():
            viewport.show()
        self.layout_mode = "grid"
        self.update_layout()
    
    @pyqtSlot()
    def update_cameras(self):
        """Update all camera viewports with new frames without freezing UI"""
        # Try to load model settings if available
        if self.settings_panel and (self.model is None):
            try:
                model_path = self.settings_panel.model_path.text()
                if self.load_model_func:
                    self.model = self.load_model_func(model_path)
                    self.CLASSES_LIST = [cls.strip() for cls in self.settings_panel.activity_classes.text().split(",")]
                print(f"Model loaded with classes: {self.CLASSES_LIST}")
            except Exception as e:
                print(f"Error loading model: {str(e)}")
                return
                
        # Get prediction interval from settings if available
        #prediction_interval = getattr(self, 'prediction_interval', 5)  # Use from config or default to 5
        #confidence_threshold = getattr(self, 'confidence_threshold', 60.0)  # Use from config or default to 60%
        
        # If settings panel is available, get the latest settings from it
        #if self.settings_panel:
        #    prediction_interval = self.settings_panel.prediction_interval.value()
        #    confidence_threshold = self.settings_panel.confidence_threshold.value()
            
        # Get prediction interval and confidence threshold from instance variables
        # (these are updated when config is loaded or settings are saved)
        prediction_interval = self.prediction_interval
        confidence_threshold = self.confidence_threshold
        
        # Process each camera
        for name, viewport in self.cameras.items():
            camera = self.camera_manager.get_camera(name)
            if not camera:
                continue
                
            # Get the latest frame from camera manager
            frame = camera.get_frame()
            if frame is None:
                continue
                
            # Process the frame
            try:
                # Resize for display
                display_frame = cv2.resize(frame, (1080, 720))
                
                # Resize for model input
                resized_frame = cv2.resize(frame, (self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
                normalized_frame = resized_frame / 255.0
                
                # Store frame in queue
                if name in self.frames_queues:
                    self.frames_queues[name].append(normalized_frame)
                    
                    # Increment counter and check if we should predict
                    self.frame_counters[name] += 1
                    
                    # If we have enough frames and it's time to predict
                    if (len(self.frames_queues[name]) == self.SEQUENCE_LENGTH and 
                        self.frame_counters[name] % prediction_interval == 0 and
                        self.model is not None and
                        name not in self.prediction_workers):
                        
                        # Create and start worker thread for prediction
                        worker = PredictionWorker(
                            self.model, 
                            self.frames_queues[name], 
                            self.CLASSES_LIST, 
                            confidence_threshold
                        )
                        worker.prediction_ready.connect(lambda class_name, text, confidence, cam=name: 
                            self.handle_prediction_result(cam, class_name, text, confidence))
                        
                        # Also connect to activity panel if available
                        if self.activity_panel:
                            worker.prediction_ready.connect(lambda class_name, text, confidence, cam=name: 
                                self.activity_panel.on_prediction(cam, class_name, text, confidence))
                        
                        worker.finished.connect(lambda cam=name: self.clean_up_worker(cam))
                        
                        self.prediction_workers[name] = worker
                        worker.start()
                
                # Get current prediction text and confidence
                prediction_text = self.camera_predictions[name]["text"]
                confidence = self.camera_predictions[name]["confidence"]
                
                # Draw prediction text on frame
                text = prediction_text
                if "Abnormal" in prediction_text:
                    color = (0, 0, 255)  # Red for abnormal
                elif prediction_text == "Normal Activity":
                    color = (0, 255, 0)  # Green for normal
                else:
                    color = (255, 255, 0)  # Yellow for detecting
                    
                cv2.putText(display_frame, text, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 4)
                
                # Update the viewport with frame and prediction
                viewport.update_frame(display_frame, activity=prediction_text, confidence=confidence)
                
            except Exception as e:
                print(f"Error processing camera {name}: {str(e)}")
        
                
    def handle_prediction_result(self, camera_name, class_name, text, confidence):
        """Handle prediction results from worker thread"""
        self.camera_predictions[camera_name] = {"text": text, "confidence": confidence}
        
        phone_number = self.phone_number if hasattr(self, 'phone_number') else None
        if not phone_number:
            print("No phone number configured for SMS alerts.")
            return
        
        #print(f"Phone number for SMS: {phone_number}")
        #print(f"Prediction for {camera_name}: {text} ({confidence:.1f}%)")
        
        if self.message_sender and "Abnormal" in text and self.should_send_sms(camera_name, interval_minutes=5):
            self.message_sender.send_sms(
                phone_number = phone_number,
                message=f"Alert from {camera_name}: {text} ({confidence:.1f}%) detected at {time.strftime('%H:%M:%S')}."
            )
        
        
    def clean_up_worker(self, camera_name):
        """Clean up the worker thread when finished"""
        if camera_name in self.prediction_workers:
            del self.prediction_workers[camera_name]