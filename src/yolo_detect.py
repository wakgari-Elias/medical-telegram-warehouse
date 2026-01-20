# src/yolo_detect.py

import os
import csv
from ultralytics import YOLO
from pathlib import Path
from tqdm import tqdm

# -----------------------------
# Configuration
# -----------------------------
IMAGE_ROOT = "data/raw/images"
OUTPUT_CSV = "data/raw/yolo_detections.csv"
MODEL_NAME = "yolov8n.pt"

# YOLO classes we care about
PERSON_CLASS_ID = 0       # person
PRODUCT_CLASS_IDS = [39, 41, 44]  # bottle, cup, box

# -----------------------------
# Load YOLO model
# -----------------------------
model = YOLO(MODEL_NAME)

# -----------------------------
# Helper: classify image
# -----------------------------
def classify_image(detected_classes):
    has_person = PERSON_CLASS_ID in detected_classes
    has_product = any(c in PRODUCT_CLASS_IDS for c in detected_classes)

    if has_person and has_product:
        return "promotional"
    elif has_product and not has_person:
        return "product_display"
    elif has_person and not has_product:
        return "lifestyle"
    else:
        return "other"

# -----------------------------
# Main detection logic
# -----------------------------
rows = []

for channel_dir in Path(IMAGE_ROOT).iterdir():
    if not channel_dir.is_dir():
        continue

    channel_name = channel_dir.name

    for image_path in tqdm(channel_dir.iterdir(), desc=f"Processing {channel_name}"):
        if image_path.suffix.lower() not in [".jpg", ".png", ".jpeg"]:
            continue

        message_id = image_path.stem

        results = model(image_path, verbose=False)[0]

        detected_classes = []
        confidences = []

        for box in results.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            detected_classes.append(cls)
            confidences.append(conf)

        image_category = classify_image(detected_classes)
        max_conf = max(confidences) if confidences else 0.0

        rows.append([
            message_id,
            channel_name,
            image_category,
            max_conf
        ])

# -----------------------------
# Write CSV
# -----------------------------
os.makedirs("data/raw", exist_ok=True)

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "message_id",
        "channel_name",
        "image_category",
        "confidence_score"
    ])
    writer.writerows(rows)

print(f"YOLO detection completed. Results saved to {OUTPUT_CSV}")
