
# 🔭 Sentinel

Sentinel is an advanced AI-powered surveillance system designed to monitor live camera feeds and intelligently detect abnormal activities such as **fighting**, **fire**, and **accidents**, along with normal behavior. Built using PyQt5 and integrated with deep learning models, Sentinel provides a sleek GUI, real-time predictions, alert visualizations, and camera stream management.

---

## 🚀 Features

- 🔌 **Multi-Camera RTSP Streaming** – Seamlessly connect and monitor multiple IP camera streams.
- 🧠 **Deep Learning Activity Detection** – Classifies events into normal or abnormal using a trained model.
- 📈 **Real-Time Activity Graphs** – Live charts showing trends in activity over time.
- 🔔 **Dynamic Alerts** – Visual alerts for abnormal events with activity icons and confidence meters.
- 🧩 **Modular GUI** – Designed with PyQt5 using custom widgets and layouts.
- 🧪 **RTSP Connection Tester** – Verify stream URLs before adding cameras.

---

## 🖼 GUI Overview

- **Camera Viewport**: Displays real-time RTSP feeds and overlays predictions.
- **Activity Panel**: Timeline graph and list of recent detected activities.
- **Add Camera Dialog**: Form to input and test RTSP streams with optional credentials.

---

## 🛠 Tech Stack

- **Frontend**: PyQt5, QtWidgets, QtCore, PyQtGraph
- **Backend**: Python 3, OpenCV
- **AI/ML**: Deep learning model based on CNN and LSTM for activity classification
- **Other**: QThreads for async prediction, QProgressBar for confidence display, QListWidget for dynamic logging

---


## 🧠 How It Works

Each connected camera stream is handled in its own worker thread. Frames are periodically passed through a deep learning model that returns:

- \`class_name\`: one of \`[normal, fire, fighting, accident]\`
- \`confidence\`: prediction confidence percentage

The UI updates in real-time, logging events and showing graph trends based on prediction data.

---

## 📊 Real-Time Graph Example

Activity intensities are visualized over a 30-second rolling window:
- 🟢 Green Line: Normal behavior confidence
- 🔴 Red Line: Abnormal activity intensity

---

## 🙋 Developer Info

Developed by **Israk Ahmed**  
📧 israkahmed7@gmail.com  
🔗 [GitHub](https://github.com/IsrakAhmed) | [LinkedIn](https://linkedin.com/in/israkahmed)

---

## 🙏 Acknowledgments

Thanks to open-source communities for PyQt5, OpenCV, and all contributors to computer vision research.

---
