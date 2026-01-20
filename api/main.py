from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from api.database import get_db
from api.schemas import (
    TopProduct, ChannelActivityItem,
    MessageSearchResult, VisualContentStat
)
from typing import List

app = FastAPI(
    title="Medical Telegram Analytics API",
    description="Analytical API exposing dbt data warehouse insights",
    version="1.0.0"
)

@app.get("/")
async def health_check():
    return {"status": "API running", "tip": "Go to /docs for interactive testing"}

# Endpoint 1: Top Products - with error handling + simpler fallback
@app.get("/api/reports/top-products", response_model=List[TopProduct])
async def top_products(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    # CHANGE 'analytics' to your actual schema if different (e.g. public)
    schema = "analytics"  # <-- FIX THIS if \dt shows different

    query = text(f"""
        WITH words AS (
            SELECT unnest(regexp_split_to_array(lower(message_text), '\\s+')) AS word
            FROM {schema}.fct_messages
            WHERE message_text IS NOT NULL AND message_text != ''
        )
        SELECT word, COUNT(*) AS count
FROM words
WHERE length(word) > 2
GROUP BY word
ORDER BY count DESC
LIMIT :limit
    """)

    try:
        result = await db.execute(query, {"limit": limit})
        rows = result.fetchall()
        return [{"product": row.word, "count": row.count} for row in rows]
    except ProgrammingError as e:
        raise HTTPException(status_code=500, detail=f"DB Error (check schema/table): {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Endpoint 2: Channel Activity
@app.get("/api/channels/{channel_name}/activity", response_model=List[ChannelActivityItem])
async def channel_activity(channel_name: str, db: AsyncSession = Depends(get_db)):
    schema = "analytics"  # <-- FIX if needed
    query = text(f"""
        SELECT 
            dd.full_date::date,
            COUNT(fm.message_id),
            AVG(fm.view_count)::float
        FROM {schema}.fct_messages fm
        JOIN {schema}.dim_channels dc ON fm.channel_key = dc.channel_key
        JOIN {schema}.dim_dates dd ON fm.date_key = dd.date_key
        WHERE lower(dc.channel_name) = lower(:channel_name)
        GROUP BY dd.full_date
        ORDER BY dd.full_date DESC
        LIMIT 30
    """)
    try:
        result = await db.execute(query, {"channel_name": channel_name})
        rows = result.fetchall()
        if not rows:
            return []  # empty list if no data
        return [{"post_date": r[0], "post_count": r[1], "avg_views": r[2]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")

# Endpoint 3: Message Search
@app.get("/api/search/messages", response_model=List[MessageSearchResult])
async def search_messages(
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    schema = "analytics"  # <-- FIX if needed
    sql = text(f"""
        SELECT fm.message_id, dc.channel_name, dd.full_date::date, fm.message_text, fm.view_count
        FROM {schema}.fct_messages fm
        JOIN {schema}.dim_channels dc ON fm.channel_key = dc.channel_key
        JOIN {schema}.dim_dates dd ON fm.date_key = dd.date_key
        WHERE fm.message_text ILIKE :search_term
        ORDER BY fm.view_count DESC NULLS LAST
        LIMIT :limit
    """)
    try:
        result = await db.execute(sql, {"search_term": f"%{query}%", "limit": limit})
        rows = result.fetchall()
        return [
            {"message_id": r[0], "channel_name": r[1], "message_date": r[2],
             "message_text": r[3], "views": r[4]} for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")

# Endpoint 4: Visual Content Stats
@app.get("/api/reports/visual-content", response_model=List[VisualContentStat])
async def visual_content_stats(db: AsyncSession = Depends(get_db)):
    schema = "analytics"  # <-- FIX if needed
    query = text(f"""
    SELECT 
        dc.channel_name,
        COUNT(*) AS total_messages,
        COALESCE(SUM(CASE WHEN fm.has_image = 1 THEN 1 ELSE 0 END), 0) AS messages_with_images,
        ROUND(
            100.0 * COALESCE(SUM(CASE WHEN fm.has_image = 1 THEN 1 ELSE 0 END), 0) / NULLIF(COUNT(*), 0),
            2
        ) AS percentage_with_images
    FROM {schema}.fct_messages fm
    JOIN {schema}.dim_channels dc ON fm.channel_key = dc.channel_key
    GROUP BY dc.channel_name
    ORDER BY percentage_with_images DESC
""")
    try:
        result = await db.execute(query)
        rows = result.fetchall()
        return [
            {"channel_name": r[0], "total_messages": r[1], "messages_with_images": r[2],
             "percentage_with_images": r[3] or 0} for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")