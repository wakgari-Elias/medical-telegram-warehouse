import os
import json
import glob
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

RAW_DATA_PATH = "data/raw/telegram_messages"

def load_json_to_postgres():
    all_files = glob.glob(f"{RAW_DATA_PATH}/**/*.json", recursive=True)
    records = []

    for file in all_files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            records.extend(data)

    df = pd.DataFrame(records)

    df.to_sql(
        "telegram_messages",
        engine,
        schema="raw",
        if_exists="replace",
        index=False
    )

    print(f"Loaded {len(df)} records into raw.telegram_messages")

if __name__ == "__main__":
    load_json_to_postgres()
