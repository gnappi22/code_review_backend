import json
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import dotenv

dotenv.load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/code_review.db")
print(f"[DEBUG] DATABASE_URL: {DATABASE_URL}")

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
    
    def __repr__(self):
        return f"<CodeSnippet(id={self.id}, language='{self.language}', code='{self.code[:50]}...')>"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    print("[DEBUG] Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("[DEBUG] Tables created successfully")

class SQLHandler():
    def __init__(self):
        self.engine = engine
        self.valid_tables = [CodeSnippet]
        print("[DEBUG] SQLHandler initialized")

    def get_db_session(self):
        """Create and return a new database session"""
        session = SessionLocal()
        print(f"[DEBUG] Created new session: {session}")
        return session

    def add_record_to_table(self, table_class, record: dict):
        print(f"[DEBUG] Starting add_record_to_table")
        print(f"[DEBUG] Table class: {table_class}")
        print(f"[DEBUG] Record data: {record}")
        
        # Check if table_class is valid
        if table_class not in self.valid_tables:
            raise ValueError(f"Invalid table class: {table_class}")

        db = self.get_db_session()
        try:
            print("[DEBUG] Creating new record instance...")
            new_record = table_class(**record)
            print(f"[DEBUG] New record instance: {new_record}")
            
            print("[DEBUG] Adding to session...")
            db.add(new_record)
            
            print("[DEBUG] Committing...")
            db.commit()
            
            print("[DEBUG] Refreshing record...")
            db.refresh(new_record)
            
            print(f"[DEBUG] Final record: {new_record}")
            print(f"[DEBUG] Record ID: {new_record.id}")
            print(f"[DEBUG] Record dict: {new_record.__dict__}")
            
            return new_record
        except Exception as e:
            print(f"[ERROR] Exception occurred: {e}")
            print(f"[ERROR] Exception type: {type(e)}")
            db.rollback()
            raise
        finally:
            print("[DEBUG] Closing session")
            db.close()

    def get_table_record(self, table_class, id: int):
        """Get a single record by ID"""
        print(f"[DEBUG] Getting record with ID: {id}")
        db = self.get_db_session()
        try:
            result = db.query(table_class).filter(table_class.id == id).first()
            print(f"[DEBUG] Query result: {result}")
            return result
        finally:
            db.close()

    def get_full_table(self, table_class):
        """Get all records from a table"""
        print(f"[DEBUG] Getting all records from: {table_class}")
        db = self.get_db_session()
        try:
            results = db.query(table_class).all()
            print(f"[DEBUG] Found {len(results)} records")
            for i, record in enumerate(results):
                print(f"[DEBUG] Record {i}: {record}")
            return results
        finally:
            db.close()
    
    def debug_table_info(self, table_class):
        """Debug function to check table structure and contents"""
        print(f"[DEBUG] === TABLE DEBUG INFO for {table_class.__tablename__} ===")
        
        db = self.get_db_session()
        try:
            # Check if table exists
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            print(f"[DEBUG] All tables in database: {tables}")
            
            if table_class.__tablename__ in tables:
                print(f"[DEBUG] Table '{table_class.__tablename__}' exists")
                
                # Get column info
                columns = inspector.get_columns(table_class.__tablename__)
                print(f"[DEBUG] Table columns: {[col['name'] for col in columns]}")
                
                # Count records
                count = db.query(table_class).count()
                print(f"[DEBUG] Record count: {count}")
                
                # Show all records
                records = db.query(table_class).all()
                print(f"[DEBUG] All records:")
                for record in records:
                    print(f"[DEBUG]   {record}")
            else:
                print(f"[DEBUG] Table '{table_class.__tablename__}' does NOT exist!")
                
        except Exception as e:
            print(f"[ERROR] Debug info failed: {e}")
        finally:
            db.close()

if __name__ == "__main__":
    print("[DEBUG] Starting main execution...")
    
    # Create tables first
    create_tables()
    
    sql_handler = SQLHandler()
    
    # Debug table info before adding
    print("\n=== BEFORE ADDING RECORD ===")
    sql_handler.debug_table_info(CodeSnippet)
    
    # Example usage
    new_snippet = {
        "language": "python",
        "code": "print('Hello, World!')",
        "lines": "1",
        "review_summary": "Good code",
        "review_suggestions": json.dumps(["Use more descriptive variable names.", "Add error handling."]),
        "review_rating": 8.0
    }
    
    try:
        print("\n=== ADDING RECORD ===")
        record = sql_handler.add_record_to_table(CodeSnippet, new_snippet)
        print(f"[SUCCESS] Added record ID: {record.id}")
        
        print("\n=== AFTER ADDING RECORD ===")
        sql_handler.debug_table_info(CodeSnippet)
        
        print("\n=== TESTING RETRIEVAL ===")
        # Test reading the record back
        retrieved_record = sql_handler.get_table_record(CodeSnippet, record.id)
        if retrieved_record:
            print(f"[SUCCESS] Retrieved record: {retrieved_record}")
        else:
            print("[ERROR] Could not retrieve the record we just added!")
        
        # Test getting all records
        all_records = sql_handler.get_full_table(CodeSnippet)
        print(f"[INFO] Total records in table: {len(all_records)}")
        
    except Exception as e:
        print(f"[ERROR] Main execution failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Still show table info even if add failed
        print("\n=== TABLE INFO AFTER ERROR ===")
        sql_handler.debug_table_info(CodeSnippet)
