"""
Simple test script for the interview feature
"""
import os
import tempfile
from interview_questions import get_all_questions, get_questions_by_category

def test_question_loading():
    """Test that questions are loaded correctly"""
    questions = get_all_questions()
    print(f"✓ Total questions loaded: {len(questions)}")
    
    # Test categories
    categories = ["behavioral", "soft_skill", "culture_fit", "it_specific"]
    for category in categories:
        cat_questions = get_questions_by_category(category)
        print(f"✓ {category}: {len(cat_questions)} questions")
    
    return len(questions) > 0

def test_database_operations():
    """Test database operations with a temporary database"""
    import sqlite3
    from interview_questions import get_all_questions
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create database schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.executescript("""
            CREATE TABLE interview_questions(
                id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                question TEXT NOT NULL,
                is_used INTEGER DEFAULT 0,
                date_added TEXT DEFAULT (datetime('now')),
                date_used TEXT
            );
            CREATE TABLE daily_questions(
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL UNIQUE,
                question_id INTEGER,
                question_text TEXT,
                category TEXT,
                FOREIGN KEY (question_id) REFERENCES interview_questions(id)
            );
        """)
        
        # Load questions
        questions = get_all_questions()
        for category, question in questions:
            cursor.execute(
                "INSERT INTO interview_questions (category, question) VALUES (?, ?)",
                (category, question)
            )
        
        conn.commit()
        
        # Test random selection
        cursor.execute("""
            SELECT id, category, question 
            FROM interview_questions 
            WHERE is_used = 0 
            ORDER BY RANDOM() 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✓ Random question retrieved: {result[1]} - {result[2][:50]}...")
        else:
            print("✗ No questions found")
            return False
            
        # Test category filtering
        cursor.execute("""
            SELECT COUNT(*) 
            FROM interview_questions 
            WHERE category = 'behavioral'
        """)
        
        count = cursor.fetchone()[0]
        print(f"✓ Behavioral questions in DB: {count}")
        
        conn.close()
        
        # Clean up
        os.unlink(db_path)
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        if os.path.exists(db_path):
            os.unlink(db_path)
        return False

def main():
    """Run all tests"""
    print("Testing Interview Feature Implementation")
    print("=" * 40)
    
    success = True
    
    print("\n1. Testing question loading...")
    success &= test_question_loading()
    
    print("\n2. Testing database operations...")
    success &= test_database_operations()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! Interview feature is ready to use.")
        print("\nFeature Summary:")
        print("- 🎯 Daily automated questions at 9:00 AM")
        print("- 🔤 Manual /interview command with category support")
        print("- 📊 Admin statistics with /interview_stats")
        print("- 🗃️ Database tracking of used questions")
        print("- 🔄 Automatic reset when all questions are used")
    else:
        print("✗ Some tests failed. Please check the implementation.")
    
    return success

if __name__ == "__main__":
    main()