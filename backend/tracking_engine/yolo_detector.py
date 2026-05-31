from pathlib import Path
import cv2
import numpy as np
import logging

from config import YOLO_MODEL_DIR, YOLO_CONFIDENCE

logger = logging.getLogger(__name__)


class YOLODetector:
    _instance = None

    def __init__(self):
        self.model = None
        self.face_cascade = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self):
        from ultralytics import YOLO
        logger.info("Loading YOLOv8n person detector...")
        self.model = YOLO("yolov8n.pt")
        logger.info("YOLO model loaded")

        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        logger.info("OpenCV face cascade loaded")

    def detect_faces(self, frame: np.ndarray) -> list[dict]:
        if self.model is None:
            self.load()

        faces = []

        # Method 1: OpenCV Haar cascade for fast face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        haar_faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        for (x, y, w, h) in haar_faces:
            faces.append({
                "bbox": [int(x), int(y), int(x + w), int(y + h)],
                "confidence": 0.9,
                "cx": (x + w / 2) / frame.shape[1],
                "cy": (y + h / 2) / frame.shape[0],
                "source": "haar",
            })

        # Method 2: YOLO person detection as fallback / refinement
        results = self.model(frame, conf=YOLO_CONFIDENCE, verbose=False, classes=[0])
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = box.conf[0].item()
            # estimate face region from top portion of person bbox
            face_h = int((y2 - y1) * 0.25)
            face_y1 = y1
            face_y2 = y1 + face_h
            face_w = int(face_h * 0.8)
            face_x1 = (x1 + x2) // 2 - face_w // 2
            face_x2 = face_x1 + face_w

            faces.append({
                "bbox": [face_x1, face_y1, face_x2, face_y2],
                "confidence": round(conf, 3),
                "cx": (x1 + x2) / 2 / frame.shape[1],
                "cy": (y1 + face_h / 2) / frame.shape[0],
                "source": "yolo",
            })

        # Merge: prefer Haar cascade faces (more precise for faces)
        if len(haar_faces) > 0:
            faces = [f for f in faces if f["source"] == "haar"]

        return faces
