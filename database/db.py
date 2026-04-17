# SQLite connection logic
import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="database/events.db"):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize the database with the schema."""
        conn = self.get_connection()
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        try:
            with open(schema_path, "r") as f:
                # Filter out comment lines and empty lines, then execute
                sql_script = "\n".join(
                    line for line in f.read().split("\n")
                    if line.strip() and not line.strip().startswith("--")
                )
                conn.executescript(sql_script)
            conn.commit()
        finally:
            conn.close()

# For backward compatibility if needed, but we should use the class
def get_connection():
    return DatabaseManager().get_connection()

def init_db():
    DatabaseManager().init_db()
