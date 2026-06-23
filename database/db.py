# SQLite connection logic
import sqlite3
import os
import queue
from threading import Lock
from contextlib import contextmanager

class DatabaseManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, db_path="database/events.db", pool_size=20):
        if self._initialized:
            return
            
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool = queue.Queue(maxsize=pool_size)
        self._initialized = True
        
        # Pre-fill the pool
        for _ in range(pool_size):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._pool.put(conn)

    @contextmanager
    def get_connection(self):
        """Context manager for borrowing and returning connections from the pool."""
        conn = self._pool.get(timeout=10) # Wait up to 10s for a free connection
        try:
            yield conn
        finally:
            self._pool.put(conn)

    def init_db(self):
        """Initialize the database with the schema."""
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with self.get_connection() as conn:
            try:
                with open(schema_path, "r") as f:
                    sql_script = "\n".join(
                        line for line in f.read().split("\n")
                        if line.strip() and not line.strip().startswith("--")
                    )
                    conn.executescript(sql_script)
                conn.commit()
            except Exception as e:
                print(f"Error initializing database: {e}")

# For backward compatibility
def get_connection():
    return DatabaseManager().get_connection()

def init_db():
    DatabaseManager().init_db()
