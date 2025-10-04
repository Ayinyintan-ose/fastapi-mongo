from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[list[str]] = []

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[list[str]] = []

class DocumentResponse(DocumentBase):
    id: str
    file_path: str
    file_type: str
    file_size: int
    word_count: Optional[int] = None
    uploaded_by: str
    created_at: datetime
    updated_at: datetime

