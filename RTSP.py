import cv2

rtsp_url = "rtsp://admin:@@009isRak007**@192.168.0.189:554/cam/realmonitor?channel=1&subtype=0"

cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Failed to connect to the camera.")
else:
    print("Streaming... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    cv2.imshow("Live Camera Stream", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
