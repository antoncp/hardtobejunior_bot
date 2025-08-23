import sqlite3

from config import settings


class DataBase:
    """Class to work with SQLite database."""

    def __init__(self, database="juniors.sqlite"):
        if settings.DEBUG:
            database = "tests.sqlite"
        self.connection = sqlite3.connect(f"db/{database}")
        self.cursor = self.connection.cursor()

    def create_database(self):
        """Initialization of the database."""
        with self.connection:
            self.cursor.executescript(
                """
            CREATE TABLE IF NOT EXISTS scores(
                id INTEGER PRIMARY KEY,
                time TEXT,
                faculty TEXT,
                points INTEGER
            );
            CREATE TABLE IF NOT EXISTS test_scores(
                id INTEGER PRIMARY KEY,
                time TEXT,
                faculty TEXT,
                points INTEGER
            );
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY,
                time TEXT,
                timestamp INTEGER,
                chat_id INTEGER,
                user_id INTEGER,
                username TEXT,
                user_first_name TEXT,
                user_last_name TEXT,
                text TEXT
            );
            CREATE TABLE IF NOT EXISTS interview_questions(
                id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                question TEXT NOT NULL,
                is_used INTEGER DEFAULT 0,
                date_added TEXT DEFAULT (datetime('now')),
                date_used TEXT
            );
            CREATE TABLE IF NOT EXISTS daily_questions(
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL UNIQUE,
                question_id INTEGER,
                question_text TEXT,
                category TEXT,
                FOREIGN KEY (question_id) REFERENCES interview_questions(id)
            );
            """
            )
        return True

    def save_points(self, faculty, points):
        """Saves points associated with faculty"""
        with self.connection:
            self.cursor.execute(
                """
                INSERT INTO scores (time, faculty, points)
                VALUES(datetime('now'), ?, ?);
                """,
                (faculty, points),
            )

    def save_message(
        self,
        timestamp,
        chat_id,
        user_id,
        username,
        user_first_name,
        user_last_name,
        text,
    ):
        """Saves message to the database"""
        with self.connection:
            self.cursor.execute(
                """
                INSERT INTO messages (time,
                                      timestamp,
                                      chat_id,
                                      user_id,
                                      username,
                                      user_first_name,
                                      user_last_name,
                                      text
                                     )
                VALUES(datetime('now'), ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    timestamp,
                    chat_id,
                    user_id,
                    username,
                    user_first_name,
                    user_last_name,
                    text,
                ),
            )

    def read_last_message(self):
        """Reads last message from database"""
        with self.connection:
            self.cursor.execute(
                """
                SELECT text
                FROM messages
                ORDER BY id DESC
                LIMIT 1;
                """,
            )
        return self.cursor.fetchone()

    def read_messages(self, num_messages):
        """Reads last n-messages from database"""
        with self.connection:
            self.cursor.execute(
                """
                SELECT user_first_name, user_last_name, text
                FROM messages
                WHERE chat_id = -1001493663500
                ORDER BY id DESC
                LIMIT ?;
                """,
                (num_messages,),
            )
        return self.cursor.fetchall()

    def read_user_messages(self, user, num_messages):
        """Reads last n-messages from database"""
        with self.connection:
            self.cursor.execute(
                """
                SELECT user_first_name, user_last_name, text
                FROM messages
                WHERE user_id = ? AND
                chat_id = -1001493663500
                ORDER BY id DESC
                LIMIT ?;
                """,
                (user, num_messages),
            )
        return self.cursor.fetchall()

    def get_all_points(self):
        """Fetches all score summary"""
        with self.connection:
            self.cursor.execute(
                """
            SELECT faculty, SUM(points) AS score
            FROM scores
            GROUP BY faculty
            ORDER BY score DESC;
            """
            )
        return self.cursor.fetchall()

    def test_save_points(self, faculty, points):
        """Saves points associated with faculty"""
        with self.connection:
            self.cursor.execute(
                """
                INSERT INTO test_scores (time, faculty, points)
                VALUES(datetime('now'), ?, ?);
                """,
                (faculty, points),
            )

    def test_get_all_points(self):
        """Fetches all score summary"""
        with self.connection:
            self.cursor.execute(
                """
            SELECT faculty, SUM(points) AS score
            FROM test_scores
            GROUP BY faculty
            ORDER BY score DESC;
            """
            )
        return self.cursor.fetchall()

    def populate_interview_questions(self, questions_list):
        """Populates the interview_questions table with initial questions"""
        with self.connection:
            for category, question in questions_list:
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO interview_questions (category, question)
                    VALUES (?, ?);
                    """,
                    (category, question)
                )

    def get_random_unused_question(self, category=None):
        """Gets a random unused interview question, optionally filtered by category"""
        query = """
            SELECT id, category, question 
            FROM interview_questions 
            WHERE is_used = 0
        """
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
            
        query += " ORDER BY RANDOM() LIMIT 1;"
        
        with self.connection:
            self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def mark_question_as_used(self, question_id):
        """Marks a question as used"""
        with self.connection:
            self.cursor.execute(
                """
                UPDATE interview_questions 
                SET is_used = 1, date_used = datetime('now')
                WHERE id = ?;
                """,
                (question_id,)
            )

    def save_daily_question(self, date, question_id, question_text, category):
        """Saves the daily question for tracking"""
        with self.connection:
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO daily_questions 
                (date, question_id, question_text, category)
                VALUES (?, ?, ?, ?);
                """,
                (date, question_id, question_text, category)
            )

    def get_daily_question(self, date):
        """Gets the daily question for a specific date"""
        with self.connection:
            self.cursor.execute(
                """
                SELECT question_text, category 
                FROM daily_questions 
                WHERE date = ?;
                """,
                (date,)
            )
        return self.cursor.fetchone()

    def reset_all_questions(self):
        """Resets all questions to unused state (for cycling through questions again)"""
        with self.connection:
            self.cursor.execute(
                """
                UPDATE interview_questions 
                SET is_used = 0, date_used = NULL;
                """
            )

    def get_question_stats(self):
        """Gets statistics about interview questions"""
        with self.connection:
            self.cursor.execute(
                """
                SELECT 
                    category,
                    COUNT(*) as total,
                    SUM(is_used) as used,
                    COUNT(*) - SUM(is_used) as remaining
                FROM interview_questions 
                GROUP BY category;
                """
            )
        return self.cursor.fetchall()

    def close(self):
        """Closes the database connection"""
        self.connection.close()
