# scripts/load_yolo_results.py

import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "dbname": "medical_warehouse",
    "user": "postgres",
    "password": os.getenv("POSTGRES_PASSWORD"),
    "port": 5432
}

CSV_PATH = "data/raw/yolo_detections.csv"

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS raw.yolo_detections (
    message_id TEXT,
    channel_name TEXT,
    image_category TEXT,
    confidence_score FLOAT
);
""")

df = pd.read_csv(CSV_PATH)

for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO raw.yolo_detections
        VALUES (%s, %s, %s, %s)
    """, tuple(row))

conn.commit()
cur.close()
conn.close()

print("YOLO detections loaded into PostgreSQL.")
