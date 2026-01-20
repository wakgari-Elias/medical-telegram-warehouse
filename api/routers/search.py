# api/routers/search.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, AsyncGenerator

from api.database import async_session
from api.schemas import MessageSearch, ErrorResponse

router = APIRouter()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.get("/search/messages", response_model=List[MessageSearch], responses={500: {"model": ErrorResponse}})
async def message_search(query: str = Query(..., min_length=1), limit: int = Query(20, ge=1), session: AsyncSession = Depends(get_session)):
    try:
        sql = text("""
            SELECT m.message_id, c.channel_name, m.message_text
            FROM analytics.fct_messages m
            JOIN analytics.dim_channels c ON m.channel_id = c.channel_id
            WHERE m.message_text ILIKE :query
            LIMIT :limit
        """)
        result = await session.execute(sql, {"query": f"%{query}%", "limit": limit})
        rows = result.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail=f"No messages found for '{query}'")
        return [{"message_id": r.message_id, "channel_name": r.channel_name, "message_text": r.message_text} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
