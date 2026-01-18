import os
import json
import asyncio
from datetime import datetime, timezone
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from dotenv import load_dotenv
from logger import logger  # use your loguru logger
from channels import CHANNELS  # use your 4-channel dictionary

# -----------------------------
# Load API credentials
# -----------------------------
load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = "medical_telegram"  # session file

# -----------------------------
# Scraper settings
# -----------------------------
TOTAL_MESSAGES = 1200
NUM_CHANNELS = len(CHANNELS)
MESSAGES_PER_CHANNEL = TOTAL_MESSAGES // NUM_CHANNELS  # 1200 / 4 = 300

# -----------------------------
# Helpers
# -----------------------------
def save_json(channel_name, messages):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = os.path.join("data", "raw", "telegram_messages", today)
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, f"{channel_name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(messages)} messages for {channel_name} at {file_path}")
    return file_path


async def download_media(client, message, channel_name):
    """Download media asynchronously if the message has a photo"""
    if message.photo:
        image_dir = os.path.join("data", "raw", "images", channel_name)
        os.makedirs(image_dir, exist_ok=True)
        file_path = os.path.join(image_dir, f"{message.id}.jpg")
        if os.path.exists(file_path):
            return file_path  # skip if already downloaded
        try:
            await client.download_media(message, file_path)
            return file_path
        except Exception as e:
            logger.error(f"Failed to download media {message.id} | {e}")
    return None


# -----------------------------
# Scrape a single channel
# -----------------------------
async def scrape_channel(client, channel_name, channel_link, limit):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    json_path = os.path.join("data", "raw", "telegram_messages", today, f"{channel_name}.json")
    if os.path.exists(json_path):
        logger.info(f"{channel_name} already scraped today. Skipping.")
        return

    logger.info(f"Starting scrape for channel: {channel_name} | Limit: {limit} messages")
    messages_data = []

    try:
        async for message in client.iter_messages(channel_link, limit=limit):
            await asyncio.sleep(1)  # Safe delay to avoid hitting rate limits
            image_path = await download_media(client, message, channel_name)

            messages_data.append({
                "message_id": message.id,
                "channel_name": channel_name,
                "message_date": message.date.isoformat(),
                "message_text": message.message,
                "has_media": bool(message.media),
                "image_path": image_path,
                "views": message.views or 0,
                "forwards": message.forwards or 0
            })

    except FloodWaitError as e:
        logger.warning(f"FloodWait {e.seconds} seconds on {channel_name}")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        logger.error(f"Error scraping {channel_name}: {e}")

    save_json(channel_name, messages_data)
    logger.info(f"Finished channel {channel_name} | Messages scraped: {len(messages_data)}")


# -----------------------------
# Main scraper loop
# -----------------------------
async def main():
    os.makedirs(os.path.join("data", "raw", "images"), exist_ok=True)

    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        for name, link in CHANNELS.items():
            await scrape_channel(client, name, link, MESSAGES_PER_CHANNEL)


if __name__ == "__main__":
    logger.info("Starting Telegram scraping...")
    asyncio.run(main())
    logger.info("Scraping completed!")
