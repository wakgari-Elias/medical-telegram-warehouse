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
