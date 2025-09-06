from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CodeSnippetRequest(BaseModel):
    language: str
    code: str
    lines: Optional[str] = None

class CodeReview(BaseModel):
    summary: str
    suggestions: List[str]
    rating: float

class CodeSnippetResponse(BaseModel):
    id: int
    language: str
    code: str
    lines: Optional[str]
    review: CodeReview
    created_at: datetime

    class Config:
        from_attributes = True

