from PyQt5.QtCore import QObject, pyqtSignal, QThread
import cv2
import time
import threading

class Camera:
    """Represents a camera with its stream and properties"""
    
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.stream = None
        self.thread = None
        self.is_running = False
        self.last_frame = None
        self.connected = False
        self.last_error = None
    
    def start(self):
        """Start the camera stream"""
        if self.is_running:
            return True
            
        try:
            self.thread = threading.Thread(target=self._stream_thread, daemon=True)
            self.is_running = True
            self.thread.start()
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def stop(self):
        """Stop the camera stream"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        if self.stream:
            self.stream.release()
            self.stream = None
    
    def _stream_thread(self):
        """Thread function for streaming from the actual camera source"""

        # Open video capture with the URL
        self.stream = cv2.VideoCapture(self.url)

        if not self.stream.isOpened():
            self.connected = False
            self.last_error = f"Unable to open stream: {self.url}"
            return

        self.connected = True

        while self.is_running:
            #print(f"Reading from {self.name} stream...")
            try:
                ret, frame = self.stream.read()
                if not ret or frame is None:
                    # Failed to grab frame, try reconnecting
                    self.connected = False
                    self.last_error = "Failed to read frame"
                    # Try to reopen stream after a delay
                    self.stream.release()
                    time.sleep(2)
                    self.stream = cv2.VideoCapture(self.url)
                    if not self.stream.isOpened():
                        time.sleep(2)
                    continue

                # Successfully got a frame
                self.last_frame = frame
                self.connected = True

                # Sleep briefly to control frame rate (optional)
                time.sleep(0.03)  # ~30fps

            except Exception as e:
                self.connected = False
                self.last_error = str(e)
                time.sleep(2)

    
    def get_frame(self):
        """Get the latest frame from the camera"""
        return self.last_frame

class CameraManager(QObject):
    """Manages multiple camera streams"""
    
    camera_added = pyqtSignal(str)
    camera_removed = pyqtSignal(str)
    camera_error = pyqtSignal(str, str)  # name, error
    
    def __init__(self):
        super().__init__()
        self.cameras = {}
    
    def add_camera(self, name, url):
        """Add and start a new camera stream"""
        if name in self.cameras:
            return False
            
        camera = Camera(name, url)
        if camera.start():
            self.cameras[name] = camera
            self.camera_added.emit(name)
            #self.sync_with_manager()
            return True
        else:
            self.camera_error.emit(name, camera.last_error)
            return False
    
    def remove_camera(self, name):
        """Remove and stop a camera stream"""
        if name in self.cameras:
            self.cameras[name].stop()
            del self.cameras[name]
            self.camera_removed.emit(name)
            #self.sync_with_manager()
            return True
        return False
    
    def get_cameras(self):
        """Get a list of all camera names"""
        return list(self.cameras.keys())
    
    def get_camera(self, name):
        """Get a specific camera by name"""
        return self.cameras.get(name)
    
    def get_frame(self, name):
        """Get the latest frame from a camera"""
        if name in self.cameras:
            return self.cameras[name].get_frame()
        return None
    
    def stop_all_cameras(self):
        """Stop all camera streams"""
        for name, camera in self.cameras.items():
            camera.stop()
            
    def sync_with_manager(self, external_manager):
        """Synchronize cameras with an external camera manager
        This allows multiple components to share camera information
        without causing infinite recursion or reference loops
        """
        if not external_manager:
            return
            
        current_names = set(self.cameras.keys())
        external_names = set(external_manager.get_cameras())

        # Add new cameras from external manager
        for name in external_names - current_names:
            camera = external_manager.get_camera(name)
            if camera:
                self.cameras[name] = camera
                # Don't emit signal here as it could cause loops

        # Remove cameras that don't exist in external manager
        for name in current_names - external_names:
            # Just remove references, don't stop cameras
            # as they're managed by the external manager
            if name in self.cameras:
                del self.cameras[name]

