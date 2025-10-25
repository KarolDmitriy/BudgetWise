from .database import get_conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('expense','income'))
    );

    CREATE TABLE IF NOT EXISTS operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,        -- YYYY-MM-DD
        amount REAL NOT NULL,      -- positive number
        category_id INTEGER,
        note TEXT,
        FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL
    );
    """)
    conn.commit()
    # ensure some default categories
    try:
        cur.execute("INSERT OR IGNORE INTO categories (name, type) VALUES (?,?)", ("Продукты", "expense"))
        cur.execute("INSERT OR IGNORE INTO categories (name, type) VALUES (?,?)", ("Транспорт", "expense"))
        cur.execute("INSERT OR IGNORE INTO categories (name, type) VALUES (?,?)", ("Зарплата", "income"))
        cur.execute("INSERT OR IGNORE INTO categories (name, type) VALUES (?,?)", ("Фриланс", "income"))
        conn.commit()
    finally:
        conn.close()
