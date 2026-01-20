from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.database import get_db
from api.schemas import ChannelActivity

router = APIRouter(prefix="/api/channels", tags=["Channels"])


@router.get(
    "/{channel_name}/activity",
    response_model=ChannelActivity,
    summary="Channel activity"
)
def channel_activity(channel_name: str, db: Session = Depends(get_db)):
    query = text("""
        SELECT channel_name, message_count
        FROM mart_channel_activity
        WHERE channel_name = :channel_name
    """)

    result = db.execute(query, {"channel_name": channel_name}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Channel not found")

    return result
