import RPi.GPIO as GPIO
import cv2
import numpy as np
import time
from picamera2 import Picamera2

motor1_in1 = 17  # IN1
motor1_in2 = 27  # IN2
motor2_in1 = 22  # IN3
motor2_in2 = 23  # IN4
enable1 = 18  # ENA
enable2 = 19  # ENB

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup([motor1_in1, motor1_in2, motor2_in1, motor2_in2, enable1, enable2], GPIO.OUT)

pwm1 = GPIO.PWM(enable1, 1000)
pwm2 = GPIO.PWM(enable2, 1000)
pwm1.start(50)  # Default speed 50%
pwm2.start(50)

def move_motor(m1_in1, m1_in2, m2_in1, m2_in2):
    GPIO.output(motor1_in1, m1_in1)
    GPIO.output(motor1_in2, m1_in2)
    GPIO.output(motor2_in1, m2_in1)
    GPIO.output(motor2_in2, m2_in2)

def stop_motor():
    move_motor(0, 0, 0, 0)

class ObjectTracker:
    def __init__(self):
        self.picam2 = Picamera2()
        self.config = self.picam2.create_still_configuration(main={"size": (320, 240)})  # Lower resolution
        self.picam2.configure(self.config)
        self.picam2.start()
        time.sleep(2)

        self.conf_threshold = 0.5
        self.nms_threshold = 0.4
        self.load_yolo_model()
        self.frame_counter = 0

    def capture_frame(self):
        self.picam2.start()
        time.sleep(0.1)
        frame = self.picam2.capture_array()
        self.picam2.stop()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame
        
    def load_yolo_model(self):
        self.net = cv2.dnn.readNet('yolov3-tiny.weights', 'yolov3-tiny.cfg')
        with open('coco.names', 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.output_layers = self.net.getUnconnectedOutLayersNames()

    def detect_person(self, frame):
        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        detections = self.net.forward(self.output_layers)

        for detection in detections:
            for obj in detection:
                scores = obj[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > self.conf_threshold and self.classes[class_id] == "person":
                    print(f"Detected class: {self.classes[class_id]}, Confidence: {confidence:.2f}")
                    center_x, center_y, w, h = (obj[:4] * [width, height, width, height]).astype(int)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    # Draw bounding box
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, "Person", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    return center_x, center_y, w, h
        return None
    
    def track_person(self):
        while True:
            print("Capturing frame...")
            frame = self.capture_frame()

            # Skip every 2nd or 3rd frame to save computation
            self.frame_counter += 1
            if self.frame_counter % 3 != 0:  # Process every 3rd frame
                continue  # Skip processing

            print("Detecting person...")
            person_bbox = self.detect_person(frame)

            if person_bbox:
                center_x, center_y, w, h = person_bbox
                frame_width = frame.shape[1]

                print(f"Person detected at X: {center_x}, Moving accordingly...")

                # Determine movement direction
                if center_x < frame_width * 0.3:
                    print("Turning Left")
                    move_motor(0, 1, 1, 0)  # Turn Left
                elif center_x > frame_width * 0.7:
                    print("Turning Right")
                    move_motor(1, 0, 0, 1)  # Turn Right
                else:
                    print("Moving Forward")
                    move_motor(1, 0, 1, 0)  # Move Forward
            else:
                print("No person detected. Stopping motors.")
                stop_motor()  # Stop if no person detected

            # Optional: Show camera feed (Comment out for headless usage)
            cv2.imshow("Camera View", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.1)  # Reduced sleep to smoothen operation, but it's now more efficient
            
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tracker = ObjectTracker()
    try:
        tracker.track_person()
    except KeyboardInterrupt:
        print("Interrupted by user. Cleaning up GPIO...")
        stop_motor()
        GPIO.cleanup()
        cv2.destroyAllWindows()