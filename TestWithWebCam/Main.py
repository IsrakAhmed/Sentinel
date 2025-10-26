from keras.models import load_model
from Predictor import predict_from_webcam

# Load the trained model (absolute path)
model = load_model(r"f:/Study/Academic/Part 4/Project/Sentinel/TestWithWebCam/final_cv_model_optimized.keras")

# Use default webcam (index 0)
webcam_index = 0

# Start prediction
predict_from_webcam(webcam_index, model)
