from fastapi import FastAPI, HTTPException
from typing import List
import json

from app.database import create_tables, CodeSnippet, SQLHandler
from app.models import CodeSnippetRequest, CodeSnippetResponse, CodeReview
from app.llm_service import LLMService
from app.code_reviewer_service import CodeReviewService

app = FastAPI(
    title="Code Review Service",
    description="A service that reviews code snippets using LLM",
    version="1.0.0"
)

# Initialize database tables
create_tables()

# Initialize services
llm_service = LLMService()
sql_handler = SQLHandler()
code_reviewer_service = CodeReviewService()

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    print("Code Review Service starting up...")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Code Review Service is running", "status": "healthy"}

@app.post("/snippets", response_model=CodeSnippetResponse)
async def create_snippet(snippet_request: CodeSnippetRequest):
    """
    Submit a code snippet for review
    """
    try:
        review_data = await code_reviewer_service.review_code(
            language=snippet_request.language,
            code=snippet_request.code,
            lines=snippet_request.lines
        )
        # Defensive: ensure suggestions is a list
        try:
            suggestions = json.loads(review_data.review_suggestions)
            if not isinstance(suggestions, list):
                suggestions = [suggestions]
        except Exception:
            suggestions = [review_data.review_suggestions]
                
        return CodeSnippetResponse(
            id=review_data.id,
            language=review_data.language,
            code=review_data.code,
            lines=review_data.lines,
            review=CodeReview(
                summary=review_data.review_summary,
                suggestions=suggestions,
                rating=review_data.review_rating
            ),
            created_at=review_data.created_at
        )
        
    except Exception as e:
        print(f"Error processing snippet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing snippet: {str(e)}")

@app.get("/snippets/{snippet_id}", response_model=CodeSnippetResponse)
async def get_snippet(snippet_id: int):
    """
    Retrieve a snippet and its review by ID
    """
    db_snippet = sql_handler.get_table_record(CodeSnippet, snippet_id)
    
    if not db_snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    
    if not db_snippet.review_summary:
        raise HTTPException(status_code=404, detail="Review not found for this snippet")
    
    try:
        suggestions = json.loads(db_snippet.review_suggestions)
        if not isinstance(suggestions, list):
            suggestions = [suggestions]
    except Exception:
        suggestions = [db_snippet.review_suggestions]
    return CodeSnippetResponse(
        id=db_snippet.id,
        language=db_snippet.language,
        code=db_snippet.code,
        lines=db_snippet.lines,
        review=CodeReview(
            summary=db_snippet.review_summary,
            suggestions=suggestions,
            rating=db_snippet.review_rating
        ),
        created_at=db_snippet.created_at
    )

@app.get("/snippets", response_model=List[CodeSnippetResponse])
async def list_snippets(skip: int = 0, limit: int = 100):
    """
    List all snippets with their reviews
    """
    all_snippets = sql_handler.get_full_table(CodeSnippet)
    
    # Filter snippets that have reviews and apply pagination
    snippets_with_reviews = [s for s in all_snippets if s.review_summary is not None]
    paginated_snippets = snippets_with_reviews[skip:skip + limit]
    
    return [
        CodeSnippetResponse(
            id=snippet.id,
            language=snippet.language,
            code=snippet.code,
            lines=snippet.lines,
            review=CodeReview(
                summary=snippet.review_summary,
                suggestions=(
                    json.loads(snippet.review_suggestions)
                    if _is_json_list(snippet.review_suggestions)
                    else [snippet.review_suggestions]
                ),
                rating=snippet.review_rating
            ),
            created_at=snippet.created_at
        )
        for snippet in paginated_snippets
    ]

def _is_json_list(s):
    try:
        obj = json.loads(s)
        return isinstance(obj, list)
    except Exception:
        return False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
