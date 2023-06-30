import sqlite3


class DataBase:
    """Class to work with SQLite database."""

    def __init__(self):
        self.connection = sqlite3.connect('db/juniors.sqlite')
        self.cursor = self.connection.cursor()

    def create_database(self):
        """Initialization of the database."""
        with self.connection:
            self.cursor.executescript(
                '''
            CREATE TABLE IF NOT EXISTS scores(
                id INTEGER PRIMARY KEY,
                time TEXT,
                faculty TEXT,
                points INTEGER
            );
            '''
            )
        return True

    def save_points(self, faculty, points):
        """Saves points associated with faculty"""
        with self.connection:
            self.cursor.execute(
                '''
                INSERT INTO scores (time, faculty, points)
                VALUES(datetime('now'), ?, ?);
                ''',
                (faculty, points),
            )

    def get_all_points(self):
        """Fetches all score summary"""
        with self.connection:
            self.cursor.execute(
                '''
            SELECT faculty, SUM(points) AS score
            FROM scores
            GROUP BY faculty
            ORDER BY score DESC;
            '''
            )
        return self.cursor.fetchall()

    def close(self):
        """Closes the database connection"""
        self.connection.close()
