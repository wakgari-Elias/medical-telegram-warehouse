# api/routers/reports.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, AsyncGenerator

from api.database import async_session
from api.schemas import TopProduct, ChannelActivity, VisualContentStats, ErrorResponse

router = APIRouter()

# async session dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# --- Top Products ---
@router.get("/reports/top-products", response_model=List[TopProduct], responses={500: {"model": ErrorResponse}})
async def top_products(limit: int = Query(10, ge=1), session: AsyncSession = Depends(get_session)):
    try:
        query = text("""
            SELECT message_text AS product_name, COUNT(*) AS mentions
            FROM analytics.fct_messages
            GROUP BY message_text
            ORDER BY mentions DESC
            LIMIT :limit
        """)
        result = await session.execute(query, {"limit": limit})
        rows = result.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="No products found")
        return [{"product_name": r.product_name, "mentions": r.mentions} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Channel Activity ---
@router.get("/channels/{channel_name}/activity", response_model=List[ChannelActivity], responses={500: {"model": ErrorResponse}})
async def channel_activity(channel_name: str, session: AsyncSession = Depends(get_session)):
    try:
        query = text("""
            SELECT c.channel_name, COUNT(m.message_text) AS messages_count
            FROM analytics.fct_messages m
            JOIN analytics.dim_channels c ON m.channel_id = c.channel_id
            WHERE c.channel_name = :channel_name
            GROUP BY c.channel_name
        """)
        result = await session.execute(query, {"channel_name": channel_name})
        rows = result.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail=f"No data for channel '{channel_name}'")
        return [{"channel_name": r.channel_name, "messages_count": r.messages_count} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Visual Content Stats ---
@router.get("/reports/visual-content", response_model=List[VisualContentStats], responses={500: {"model": ErrorResponse}})
async def visual_content_stats(session: AsyncSession = Depends(get_session)):
    try:
        query = text("""
            SELECT file_name, detected_label, COUNT(*) AS count
            FROM analytics.fct_image_detections
            GROUP BY file_name, detected_label
            ORDER BY count DESC
        """)
        result = await session.execute(query)
        rows = result.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="No visual content found")
        return [{"file_name": r.file_name, "detected_label": r.detected_label, "count": r.count} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
