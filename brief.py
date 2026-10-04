"""Generate a cross-asset brief with causal reasoning.  Usage: python brief.py ["optional question"]"""
import os, sys, datetime as dt
from dotenv import load_dotenv
from db import conn

load_dotenv()
MODEL = "claude-sonnet-5-5"

FRAMEWORK = """You are a senior macro strategist assisting a financial market analyst.
Use ONLY the data supplied below. If something is not in the data, say so; never invent facts, numbers, or quotes.
Cite headlines by their [number]. For each major theme (max 6, ranked by market importance) give:
1. EVENT - what happened (cite [n])
2. TRANSMISSION CHANNEL - how it reaches markets (rates, inflation expectations, USD, risk sentiment, supply/demand, earnings, flows)
3. ASSET IMPACT - direction and rough magnitude for Equities, Rates, Credit, FX, Energy, Metals, Agriculture, Crypto (only those that matter)
4. PRICED IN? - compare with the price moves provided
5. SECOND-ORDER EFFECTS - the next links in the chain
6. CONFIDENCE and WHAT WOULD INVALIDATE THIS VIEW
Finish with: a cross-asset dashboard of signals that conflict (e.g. stocks up while credit spreads widen), and the key risks/events to watch next."""

def build_context():
    db = conn()
    out = ["## MARKET MOVES (latest close, 1-day % and 1-month %)"]
    rows = db.execute("SELECT DISTINCT symbol,name,asset_class FROM prices ORDER BY asset_class").fetchall()
    for sym, name, ac in rows:
        p = db.execute("SELECT date,close FROM prices WHERE symbol=? ORDER BY date DESC LIMIT 25", (sym,)).fetchall()
        if len(p) < 2: continue
        d1 = (p[0][1] / p[1][1] - 1) * 100
        d21 = (p[0][1] / p[min(21, len(p)-1)][1] - 1) * 100
        out.append(f"[{ac}] {name}: {p[0][1]:.4g} ({d1:+.2f}% 1d, {d21:+.2f}% 1m) as of {p[0][0]}")
    out.append("\n## MACRO (latest, previous)")
    for sid, name in db.execute("SELECT DISTINCT series_id,name FROM macro"):
        m = db.execute("SELECT date,value FROM macro WHERE series_id=? ORDER BY date DESC LIMIT 2", (sid,)).fetchall()
        if m: out.append(f"{name}: {m[0][1]:.4g} ({m[0][0]})" + (f", prior {m[1][1]:.4g}" if len(m) > 1 else ""))
    out.append("\n## HEADLINES (last ~36h of fetches)")
    arts = db.execute("SELECT category,source,title,summary FROM articles WHERE fetched >= datetime('now','-36 hours') ORDER BY category LIMIT 220").fetchall()
    for i, (cat, src, title, summ) in enumerate(arts, 1):
        out.append(f"[{i}] ({cat}/{src}) {title}" + (f" - {summ[:160]}" if summ else ""))
    return "\n".join(out)

def generate_brief(question="Produce today's cross-asset brief."):
    import anthropic
    ctx = build_context()
    client = anthropic.Anthropic()
    msg = client.messages.create(model=MODEL, max_tokens=4000, system=FRAMEWORK,
        messages=[{"role": "user", "content": f"{ctx}\n\n---\nTASK: {question}"}])
    return msg.content[0].text

if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "Produce today's cross-asset brief."
    text = generate_brief(question)
    os.makedirs("briefs", exist_ok=True)
    path = f"briefs/brief_{dt.date.today()}.md"
    open(path, "w").write(text)
    print(text); print(f"\nSaved to {path}")
