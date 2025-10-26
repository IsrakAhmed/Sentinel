import cv2 as cv
import numpy as np
from collections import deque
import threading
import sys
import os

IMAGE_HEIGHT, IMAGE_WIDTH = 224, 224
SEQUENCE_LENGTH = 10
PREDICTION_INTERVAL = 5
CLASSES_LIST = ["accident", "fighting", "fire", "normal_resized"]

def predict_from_webcam(webcam_index, model):
    cap = cv.VideoCapture(webcam_index)
    if not cap.isOpened():
        print("\u274c Unable to access webcam.")
        return
    print("Webcam connected. Predicting...")
    frames_queue = deque(maxlen=SEQUENCE_LENGTH)
    predicted_class_name = ""
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("\u274c Failed to grab frame from webcam.")
            break
        resized_frame = cv.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH))
        normalized_frame = resized_frame / 255.0
        frames_queue.append(normalized_frame)
        frame_count += 1
        if len(frames_queue) == SEQUENCE_LENGTH and frame_count % PREDICTION_INTERVAL == 0:
            input_frames = np.array(frames_queue)
            input_frames = np.expand_dims(input_frames, axis=0)
            predictions = model.predict(input_frames, verbose=0)
            predicted_label = np.argmax(predictions)
            predicted_class_name = CLASSES_LIST[predicted_label]
        display_text = f"Prediction: {predicted_class_name}"
        cv.putText(frame, display_text, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv.imshow("Webcam Activity Detection", frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv.destroyAllWindows()
