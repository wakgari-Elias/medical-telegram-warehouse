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