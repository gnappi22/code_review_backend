from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./code_review.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class CodeSnippet(Base):
    __tablename__ = "code_snippets"
    
    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(50), nullable=False)
    code = Column(Text, nullable=False)
    lines = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Review fields
    review_summary = Column(Text, nullable=True)
    review_suggestions = Column(Text, nullable=True)  # JSON string
    review_rating = Column(Float, nullable=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

