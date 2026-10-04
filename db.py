import sqlite3
DB_PATH = "market_intel.db"

def conn():
    c = sqlite3.connect(DB_PATH)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS articles(
        id TEXT PRIMARY KEY, category TEXT, source TEXT, title TEXT, link TEXT,
        published TEXT, summary TEXT, fetched TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS macro(
        series_id TEXT, name TEXT, theme TEXT, date TEXT, value REAL,
        PRIMARY KEY(series_id, date));
    CREATE TABLE IF NOT EXISTS prices(
        symbol TEXT, name TEXT, asset_class TEXT, date TEXT, close REAL,
        PRIMARY KEY(symbol, date));
    """)
    return c
