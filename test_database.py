#!/usr/bin/env python3
"""
Test script to verify the database functionality works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import create_tables, CodeSnippet, SQLHandler
import json

def test_database():
    print("Testing database functionality...")
    
    # Create tables
    print("Creating tables...")
    create_tables()
    
    # Initialize SQL handler
    print("Initializing SQL handler...")
    sql_handler = SQLHandler()
    
    # Test data
    test_snippet = {
        "language": "python",
        "code": "def hello():\n    print('Hello, World!')",
        "lines": "1-2",
        "review_summary": "Good basic function",
        "review_suggestions": json.dumps(["Add docstring", "Consider error handling"]),
        "review_rating": 8.0
    }
    
    try:
        print("Adding test snippet...")
        record = sql_handler.add_record_to_table(CodeSnippet, test_snippet)
        print(f"✅ Successfully added record with ID: {record.id}")
        
        print("Retrieving test snippet...")
        retrieved = sql_handler.get_table_record(CodeSnippet, record.id)
        if retrieved:
            print(f"✅ Successfully retrieved record: {retrieved}")
        else:
            print("❌ Failed to retrieve record")
            
        print("Getting all records...")
        all_records = sql_handler.get_full_table(CodeSnippet)
        print(f"✅ Found {len(all_records)} total records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database()
    if success:
        print("\n🎉 Database test completed successfully!")
    else:
        print("\n💥 Database test failed!")
        sys.exit(1)
