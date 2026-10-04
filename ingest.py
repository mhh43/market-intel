"""Pull data from all free sources into SQLite.  Usage: python ingest.py [news|macro|prices|gdelt|all]"""
import os, sys, hashlib, time, datetime as dt
import requests, feedparser
from dotenv import load_dotenv
from config import RSS_FEEDS, FRED_SERIES, PRICES, GDELT_QUERIES
from db import conn

load_dotenv()
UA = {"User-Agent": os.getenv("SEC_USER_AGENT", "market-intel research@example.com")}

def _id(*parts): return hashlib.sha1("|".join(parts).encode()).hexdigest()

def ingest_news():
    db, new = conn(), 0
    for cat, feeds in RSS_FEEDS.items():
        for source, url in feeds.items():
            try:
                feed = feedparser.parse(url, request_headers=UA)
                for e in feed.entries[:40]:
                    title, link = e.get("title", "").strip(), e.get("link", "")
                    if not title: continue
                    cur = db.execute("INSERT OR IGNORE INTO articles(id,category,source,title,link,published,summary) VALUES(?,?,?,?,?,?,?)",
                        (_id(title.lower()), cat, source, title, link,
                         e.get("published", ""), (e.get("summary", "") or "")[:600]))
                    new += cur.rowcount
                print(f"  ok  {source}: {len(feed.entries)} items")
            except Exception as ex:
                print(f"  ERR {source}: {ex}")
    db.commit(); print(f"News: {new} new articles")

def ingest_gdelt():
    db, new = conn(), 0
    for theme, q in GDELT_QUERIES.items():
        try:
            r = requests.get("https://api.gdeltproject.org/api/v2/doc/doc", timeout=30, params={
                "query": q, "mode": "artlist", "maxrecords": 25, "format": "json", "timespan": "1d", "sort": "hybridrel"})
            for a in r.json().get("articles", []):
                cur = db.execute("INSERT OR IGNORE INTO articles(id,category,source,title,link,published,summary) VALUES(?,?,?,?,?,?,?)",
                    (_id(a["title"].lower()), "geopolitics", f"GDELT/{theme} ({a.get('domain','')})",
                     a["title"], a["url"], a.get("seendate", ""), ""))
                new += cur.rowcount
            print(f"  ok  GDELT {theme}")
        except Exception as ex:
            print(f"  ERR GDELT {theme}: {ex}")
        time.sleep(6)  # GDELT asks for roughly one request per 5 seconds
    db.commit(); print(f"GDELT: {new} new articles")

def ingest_macro():
    key = os.getenv("FRED_API_KEY")
    if not key: print("Set FRED_API_KEY in .env (free) to load macro data."); return
    db, n = conn(), 0
    start = (dt.date.today() - dt.timedelta(days=800)).isoformat()
    for theme, series in FRED_SERIES.items():
        for sid, name in series.items():
            try:
                r = requests.get("https://api.stlouisfed.org/fred/series/observations", timeout=30, params={
                    "series_id": sid, "api_key": key, "file_type": "json", "observation_start": start})
                for o in r.json().get("observations", []):
                    if o["value"] in (".", ""): continue
                    db.execute("INSERT OR REPLACE INTO macro VALUES(?,?,?,?,?)", (sid, name, theme, o["date"], float(o["value"]))); n += 1
                print(f"  ok  {sid}")
            except Exception as ex:
                print(f"  ERR {sid}: {ex}")
    db.commit(); print(f"Macro: {n} observations")

def ingest_prices():
    import yfinance as yf
    db, n = conn(), 0
    for ac, symbols in PRICES.items():
        for sym, name in symbols.items():
            try:
                hist = yf.Ticker(sym).history(period="3mo")
                for d, row in hist.iterrows():
                    if row["Close"] == row["Close"]:  # skip NaN
                        db.execute("INSERT OR REPLACE INTO prices VALUES(?,?,?,?,?)", (sym, name, ac, d.strftime("%Y-%m-%d"), float(row["Close"]))); n += 1
                print(f"  ok  {sym}")
            except Exception as ex:
                print(f"  ERR {sym}: {ex}")
    db.commit(); print(f"Prices: {n} rows")

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    steps = {"news": ingest_news, "gdelt": ingest_gdelt, "macro": ingest_macro, "prices": ingest_prices}
    for k, f in steps.items():
        if what in (k, "all"): print(f"== {k} =="); f()
