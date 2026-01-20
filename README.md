# medical-telegram-warehouse
Shipping a Data Product  From Raw Telegram Data → Analytical API

✅ Task-1 README (copy-paste into your README.md or a Task-1 section)
Task 1 – Data Scraping and Collection (Extract & Load)
Objective

Build a data scraping pipeline that extracts messages and images from selected public Telegram channels related to Ethiopian medical businesses and stores them in a raw data lake for downstream analytics.

Scope

For Task-1, the pipeline focuses on:

Extracting Telegram messages

Downloading images when present

Preserving raw data structure

Logging scraping activity and errors

To reduce execution time during development, scraping is limited to 4 channels with a maximum of 300 messages per channel (1200 messages total).

Telegram Channels Scraped
Channel Name	URL
CheMed	https://t.me/CheMed123

Lobelia	https://t.me/lobelia4cosmetics

Tikvah	https://t.me/tikvahpharma

Med In Ethiopia	https://t.me/medinethiopiainsider
Data Extracted per Message

Message ID

Channel name

Message date

Text content

View count

Forward count

Media presence

Image file path (if photo exists)

Data Storage Structure
Raw Messages (JSON)
data/raw/telegram_messages/YYYY-MM-DD/channel_name.json

Images
data/raw/images/channel_name/message_id.jpg

Logs
logs/scraper.log

Implementation Details

Language: Python (async)

Library: Telethon

Authentication: Telegram API (API_ID, API_HASH)

Logging: Loguru

Rate Limiting: Safe async delays and FloodWait handling

Session Management: Local .session file (excluded from Git)

How to Run
python src/scraper.py

Deliverables

src/scraper.py – Telegram scraping pipeline

src/channels.py – Channel configuration

src/logger.py – Centralized logging

Raw JSON message files

Downloaded images organized by channel

Scraping logs

Notes

Images are downloaded only when present

Channels with fewer messages return all available messages

.session files and secrets are excluded from version control

# Task 2 - Data Modeling and Transformation (Transform)

## Objective
Transform raw Telegram message data into a clean, structured data warehouse using dbt and PostgreSQL.

## Steps

### 1. Load Raw Data to PostgreSQL
- `load_raw_to_postgres.py` reads JSON files from `data/raw/telegram_messages/` and inserts them into the `raw.telegram_messages` table.

### 2. Initialize DBT Project
- DBT project: `medical_warehouse`
- Profiles configured in `profiles.yml` to connect to PostgreSQL database `medical_warehouse`.
- Project structure:
  - `models/staging/` → staging models (cleaning and standardizing raw data)
  - `models/marts/` → dimensional models (star schema)
  - `tests/` → custom DBT tests

### 3. Staging Model
- File: `models/staging/stg_telegram_messages.sql`
- Cleans and standardizes raw data:
  - Casts `message_date` to timestamp
  - Converts views/forwards to integers
  - Adds calculated fields: `message_length`, `has_image`

### 4. Star Schema (Dimensional Models)
- Dimension tables:
  - `dim_channels.sql` → channel information (name, type, first/last post)
  - `dim_dates.sql` → date dimension (day, week, month, quarter, year)
- Fact table:
  - `fct_messages.sql` → one row per message, links to dimension tables

### 5. Tests
- `schema.yml` → primary key, not null, and relationships tests
- Custom test: `assert_no_future_messages.sql` → ensure no messages with future dates

### 6. DBT Commands
- Run models:  
  ```bash
  dbt run

  ## Task 3 – Data Enrichment with Object Detection (YOLOv8)
## Overview

Task 3 focuses on enriching Telegram message data with visual intelligence by applying computer vision techniques to images collected in Task 1. Using a pre-trained YOLOv8 object detection model, this task extracts meaningful visual signals (e.g., presence of people or products) and integrates them into the analytical data warehouse built in Task 2.

Because pre-trained object detection models cannot recognize domain-specific pharmaceutical products, the goal of this task is not fine-grained product identification, but rather to derive analytical value from general visual patterns such as promotional behavior, lifestyle imagery, and product display strategies.

This enrichment enables new business insights related to visual content usage, engagement, and channel behavior.

🎯 Business Objectives

The primary objectives of Task 3 are to:

Analyze image content posted by medical and pharmaceutical Telegram channels.

Classify visual content into meaningful analytical categories.

Integrate image-derived insights into the data warehouse.

Enable downstream analysis such as:

Do promotional images attract higher engagement?

Which channels rely more heavily on visual content?

How do visual strategies differ across channels?

🧠 Approach & Design Decisions
Why YOLOv8?

YOLOv8 is a state-of-the-art real-time object detection model

The nano version (yolov8n) is lightweight and suitable for standard laptops

Automatically downloads weights at runtime (no model files committed to Git)

Key Assumptions

Object detection is limited to general objects (e.g., person, bottle)

Analytical value is derived from patterns, not exact product recognition

Images are already downloaded during Task 1

🗂️ Input Data
Image Location

Images are read from the following directory structure:

data/raw/images/
└── channel_name/
    └── image.png


Each image is associated with a Telegram message via metadata captured during scraping.

⚙️ Implementation Details
1️⃣ YOLO Environment Setup

Dependencies used:

pip install ultralytics


Model:

YOLOv8 Nano (yolov8n.pt)

Downloaded automatically at runtime

Excluded from version control as a best practice

2️⃣ Object Detection Script

File: src/yolo_detect.py

The script performs the following steps:

Recursively scans image directories

Runs YOLOv8 object detection on each image

Extracts:

Detected object class

Confidence score

Aggregates detections per image

Writes results to a structured CSV file

Output File:
data/raw/yolo_detections.csv

3️⃣ Image Classification Logic

Detected objects are mapped into analytical image categories using the following rules:

Category	Detection Logic
promotional	Contains person + product
product_display	Contains product only
lifestyle	Contains person only
other	Contains neither

Product objects include: bottle, container, or similar detected classes.

This classification provides a high-level semantic interpretation of visual content.

🧱 Data Warehouse Integration
dbt Model

File:

models/marts/fct_image_detections.sql

Transformation Logic:

Loads YOLO detection results from yolo_detections.csv

Joins with fct_messages

Aligns with existing star schema

Final Fact Table Includes:

message_id

channel_key

date_key

detected_class

confidence_score

image_category

This model enables image-aware analytical queries across channels and time.

📊 Analytical Use Cases Enabled

This enrichment supports analysis such as:

📈 Engagement comparison between promotional vs product display images

🏥 Channel behavior analysis based on visual usage

🖼️ Visual content penetration across Telegram channels

🧪 Exploration of image-based marketing strategies

⚠️ Limitations & Considerations

YOLOv8 detects general objects only

No fine-grained product or brand recognition

False positives possible in cluttered images

Confidence scores depend on image quality

Despite these limitations, the approach provides valuable directional insights when aggregated at scale.

📁 Deliverables Summary

✔ src/yolo_detect.py – Object detection pipeline
✔ data/raw/yolo_detections.csv – Detection results
✔ models/marts/fct_image_detections.sql – dbt integration
✔ Enriched analytical capability for visual content analysis

✅ Conclusion

Task 3 successfully extends the data warehouse beyond text-based analytics by incorporating computer vision-driven enrichment. While constrained by the limitations of pre-trained models, the solution adds measurable analytical value and prepares the foundation for more advanced image intelligence in future iterations.

This task bridges data engineering and applied machine learning, reinforcing the platform’s ability to support richer, multi-modal business insights.
