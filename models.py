from pydantic import BaseModel
from typing import List, Dict, Any


class MessageIn(BaseModel):
    user_id: str
    message: str


class MessageRecord(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class UserHistory(BaseModel):
    messages: List[MessageRecord]
    metadata: Dict[str, Any]
