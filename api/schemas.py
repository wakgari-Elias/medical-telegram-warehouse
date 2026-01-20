from pydantic import BaseModel
from typing import Optional
from datetime import date

class TopProduct(BaseModel):
    product: str
    count: int

class ChannelActivityItem(BaseModel):
    post_date: date
    post_count: int
    avg_views: Optional[float] = None

class MessageSearchResult(BaseModel):
    message_id: int
    channel_name: str
    message_date: date
    message_text: str
    views: Optional[int] = None

class VisualContentStat(BaseModel):
    channel_name: str
    total_messages: int
    messages_with_images: int
    percentage_with_images: float