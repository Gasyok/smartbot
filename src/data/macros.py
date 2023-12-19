import sqlite3


class Macros:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Macros, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "is_initialized"):
            self.db = "data/macros.db"
            self.initialize_db()
            self.is_initialized = True

    def initialize_db(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS macros (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                code TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()

    def get_user_macro(self, user_id):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM macros WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def get_macros_id(self, user_id, name):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT code FROM macros WHERE user_id = ? AND name = ?",
            (user_id, name)
        )
        result = cursor.fetchall()
        code = result[0][0] if result else None
        conn.close()
        return code

    def set_user_macro(self, user_id, name, code):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO macros (user_id, name, code) VALUES (?, ?, ?)",
            (user_id, name, code),
        )
        conn.commit()
        conn.close()


macros = Macros()
