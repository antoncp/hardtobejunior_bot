import sqlite3


class DataBase:
    """Class to work with SQLite database."""

    def __init__(self, database="juniors.sqlite"):
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
                '''
                SELECT text
                FROM messages
                ORDER BY id DESC
                LIMIT 1;
                ''',
            )
        return self.cursor.fetchone()

    def read_messages(self, num_messages):
        """Reads last n-messages from database"""
        with self.connection:
            self.cursor.execute(
                '''
                SELECT user_first_name, user_last_name, text
                FROM messages
                WHERE chat_id = -1001493663500
                ORDER BY id DESC
                LIMIT ?;
                ''',
                (num_messages,),
            )
        return self.cursor.fetchall()

    def read_user_messages(self, user, num_messages):
        """Reads last n-messages from database"""
        with self.connection:
            self.cursor.execute(
                '''
                SELECT user_first_name, user_last_name, text
                FROM messages
                WHERE user_id = ? AND
                chat_id = -1001493663500
                ORDER BY id DESC
                LIMIT ?;
                ''',
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

    def close(self):
        """Closes the database connection"""
        self.connection.close()
