import os
import cv2
import numpy as np
import base64
from ultralytics import YOLO

MODEL_PATH = os.path.join(os.path.dirname(__file__), "weights", "best.pt")

# Initialize globally
#model = YOLO(MODEL_PATH)
model = YOLO('weights/best.pt')

# ── Confidence gate ──────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.20  # Below this, override prediction as Healthy / Unknown

def coverage_to_severity(coverage: float) -> str:
    """Severity heuristic based on bounding-box area relative to image area.
    coverage = box_area / img_area."""
    if coverage >= 0.50:
        return "Severe"
    elif coverage >= 0.20:
        return "Moderate"
    else:
        return "Mild"

def run_inference(image_bytes):
    # Decode the bytes to a cv2 image
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Could not decode image bytes.")
        
    # Run model.predict(img, conf=0.25)
    results = model.predict(img, conf=0.25)
    
    img_height, img_width = img.shape[:2]
    img_area = img_width * img_height

    output_data = []
    
    # Iterate through results[0].boxes
    if len(results) > 0:
        for box in results[0].boxes:
            # bbox coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # label and confidence
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            confidence = float(box.conf[0])
            
            # ── CRITICAL FAILSAFE ──────────────────────────────────
            # If the class name contains "healthy" (case-insensitive),
            # override severity to "None" and normalise the label.
            if "healthy" in label.lower():
                severity_grade = "None"
                severity_pct   = 0.0
                label          = "Healthy"
            else:
                # Calculate severity from bounding-box coverage
                box_area = (x2 - x1) * (y2 - y1)
                coverage = box_area / img_area if img_area > 0 else 0
                severity_grade = coverage_to_severity(coverage)
                severity_pct   = coverage * 100   # store as percentage
                
            # Format a dictionary containing: label, confidence, bbox coordinates, severity_grade, and severity_percentage
            output_data.append({
                "label": label,
                "confidence": confidence,
                "bbox": [x1, y1, x2, y2],
                "severity_grade": severity_grade,
                "severity_percentage": severity_pct
            })
            
    # ── Post-processing: confidence threshold gate ──────────────
    max_conf = max((d["confidence"] for d in output_data), default=0.0)
    if not output_data or max_conf < CONFIDENCE_THRESHOLD:
        h, w = img.shape[:2]
        output_data = [{
            "label": "Healthy / Unknown",
            "confidence": max_conf,
            "bbox": [0, 0, w, h],
            "severity_grade": "None",
            "severity_percentage": 0.0
        }]

    # Return the list of dictionaries and the original image matrix
    return output_data, img

def draw_annotations_and_encode(img_matrix, predictions_list):
    """
    Iterates through the predictions, uses cv2.rectangle and cv2.putText to draw 
    the bounding boxes on the img_matrix along with label, confidence, and severity_grade.
    Returns the annotated image as a base64 encoded string.
    """
    for pred in predictions_list:
        x1, y1, x2, y2 = pred["bbox"]
        label = pred["label"]
        confidence = pred["confidence"]
        severity_grade = pred["severity_grade"]
        
        # Define the text string
        text = f"{label} {confidence:.2f} ({severity_grade})"
        
        # Red bounding box
        color = (0, 0, 255)
        
        # Draw bounding box
        cv2.rectangle(img_matrix, (x1, y1), (x2, y2), color, 2)
        
        # Put text just above it
        cv2.putText(img_matrix, text, (x1, max(y1 - 10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
    # Convert image to a JPEG
    success, buffer = cv2.imencode('.jpg', img_matrix)
    if not success:
        raise RuntimeError("Failed to encode image to JPEG")
        
    # Encode as base64 string
    base64_str = base64.b64encode(buffer).decode('utf-8')
    
    return base64_str

