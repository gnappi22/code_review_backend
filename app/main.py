from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from .database import get_db, create_tables, CodeSnippet
from .models import CodeSnippetRequest, CodeSnippetResponse, CodeReview
from .llm_service import LLMService

app = FastAPI(
    title="Code Review Service",
    description="A service that reviews code snippets using LLM",
    version="1.0.0"
)

# Initialize database tables
create_tables()

# Initialize LLM service
llm_service = LLMService()

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    print("Code Review Service starting up...")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Code Review Service is running", "status": "healthy"}

@app.post("/snippets", response_model=CodeSnippetResponse)
async def create_snippet(snippet_request: CodeSnippetRequest, db: Session = Depends(get_db)):
    """
    Submit a code snippet for review
    """
    try:
        # Create new snippet record
        db_snippet = CodeSnippet(
            language=snippet_request.language,
            code=snippet_request.code,
            lines=snippet_request.lines
        )
        
        # Save to database first to get the ID
        db.add(db_snippet)
        db.commit()
        db.refresh(db_snippet)
        
        # Generate review using LLM
        review_data = await llm_service.review_code(
            language=snippet_request.language,
            code=snippet_request.code,
            lines=snippet_request.lines
        )
        
        # Update snippet with review data
        db_snippet.review_summary = review_data["summary"]
        db_snippet.review_suggestions = json.dumps(review_data["suggestions"])
        db_snippet.review_rating = review_data["rating"]
        
        db.commit()
        db.refresh(db_snippet)
        
        # Return the response
        return CodeSnippetResponse(
            id=db_snippet.id,
            language=db_snippet.language,
            code=db_snippet.code,
            lines=db_snippet.lines,
            review=CodeReview(
                summary=db_snippet.review_summary,
                suggestions=json.loads(db_snippet.review_suggestions),
                rating=db_snippet.review_rating
            ),
            created_at=db_snippet.created_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing snippet: {str(e)}")

@app.get("/snippets/{snippet_id}", response_model=CodeSnippetResponse)
async def get_snippet(snippet_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a snippet and its review by ID
    """
    db_snippet = db.query(CodeSnippet).filter(CodeSnippet.id == snippet_id).first()
    
    if not db_snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    
    if not db_snippet.review_summary:
        raise HTTPException(status_code=404, detail="Review not found for this snippet")
    
    return CodeSnippetResponse(
        id=db_snippet.id,
        language=db_snippet.language,
        code=db_snippet.code,
        lines=db_snippet.lines,
        review=CodeReview(
            summary=db_snippet.review_summary,
            suggestions=json.loads(db_snippet.review_suggestions),
            rating=db_snippet.review_rating
        ),
        created_at=db_snippet.created_at
    )

@app.get("/snippets", response_model=List[CodeSnippetResponse])
async def list_snippets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all snippets with their reviews
    """
    snippets = db.query(CodeSnippet).filter(CodeSnippet.review_summary.isnot(None)).offset(skip).limit(limit).all()
    
    return [
        CodeSnippetResponse(
            id=snippet.id,
            language=snippet.language,
            code=snippet.code,
            lines=snippet.lines,
            review=CodeReview(
                summary=snippet.review_summary,
                suggestions=json.loads(snippet.review_suggestions),
                rating=snippet.review_rating
            ),
            created_at=snippet.created_at
        )
        for snippet in snippets
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
