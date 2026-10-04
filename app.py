"""Web dashboard.  Local: streamlit run app.py   Online: deploy to Streamlit Community Cloud (see README)."""
import os, json
import streamlit.components.v1 as components
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Market Intelligence", page_icon="📈", layout="wide")

# Load keys from Streamlit secrets (online) or .env (local)
try:
    for k in ["FRED_API_KEY", "EIA_API_KEY", "ANTHROPIC_API_KEY", "SEC_USER_AGENT", "APP_PASSWORD"]:
        if k in st.secrets: os.environ[k] = str(st.secrets[k])
except Exception:
    pass
from dotenv import load_dotenv; load_dotenv()

import ingest, brief
from db import conn

# Password gate: this app spends your API credit, so keep it private
pw = os.getenv("APP_PASSWORD")
if pw and st.session_state.get("ok") != True:
    if st.text_input("Password", type="password") == pw:
        st.session_state["ok"] = True; st.rerun()
    st.stop()

@st.cache_data(ttl=1800, show_spinner="Refreshing news, prices and macro data...")
def refresh_core():
    ingest.ingest_news(); ingest.ingest_prices(); ingest.ingest_macro()
    return True

def tv(script, cfg, h):
    components.html(f'<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/{script}" async>{json.dumps(cfg)}</script></div>', height=h)

tv("embed-widget-ticker-tape.js", {"symbols": [
    {"proName": "FOREXCOM:SPXUSD", "title": "S&P 500"}, {"proName": "TVC:DXY", "title": "DXY"},
    {"proName": "TVC:US10Y", "title": "US 10Y"}, {"proName": "OANDA:XAUUSD", "title": "Gold"},
    {"proName": "TVC:USOIL", "title": "WTI"}, {"proName": "FX:EURUSD", "title": "EUR/USD"},
    {"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"}], "colorTheme": "dark", "isTransparent": True, "displayMode": "adaptive", "locale": "en"}, 80)
st.title("📈 Global Market Intelligence")
c1, c2, _ = st.columns([1, 1, 4])
if c1.button("🔄 Refresh data"): refresh_core.clear()
if c2.button("🌍 Load geopolitics (GDELT)"):
    with st.spinner("Querying GDELT (about 1 minute)..."): ingest.ingest_gdelt()
refresh_core()
db = conn()

tab_brief, tab_chart, tab_cal, tab_reg, tab_mkt, tab_macro, tab_news = st.tabs(["🧠 AI Desk", "📊 Charts", "📅 Calendar", "🧭 Regime", "💹 Markets", "🏛 Macro", "📰 Headlines"])

with tab_brief:
    q = st.text_input("Ask anything (leave blank for a full cross-asset brief)",
                      placeholder="Why is gold moving and what does it mean for EM currencies?")
    if st.button("Generate analysis"):
        if not os.getenv("ANTHROPIC_API_KEY"): st.error("Add ANTHROPIC_API_KEY in settings/secrets.")
        else:
            with st.spinner("Analysing..."):
                st.session_state["out"] = brief.generate_brief(q or "Produce today's cross-asset brief.")
    st.markdown(st.session_state.get("out", "_Click Generate analysis._"))
    st.caption("AI analysis is decision support, not a trading signal. Verify against the cited headlines.")

with tab_mkt:
    rows = []
    for sym, name, ac in db.execute("SELECT DISTINCT symbol,name,asset_class FROM prices").fetchall():
        p = db.execute("SELECT close FROM prices WHERE symbol=? ORDER BY date DESC LIMIT 22", (sym,)).fetchall()
        if len(p) > 1:
            rows.append({"Asset class": ac, "Market": name, "Last": round(p[0][0], 4),
                         "1d %": round((p[0][0]/p[1][0]-1)*100, 2), "1m %": round((p[0][0]/p[-1][0]-1)*100, 2)})
    if rows:
        df = pd.DataFrame(rows)
        for ac, g in df.groupby("Asset class", sort=False):
            st.subheader(ac.replace("_", " ").title())
            st.dataframe(g.drop(columns="Asset class"), hide_index=True, use_container_width=True)
    else: st.info("No price data yet. Click Refresh data.")

with tab_macro:
    m = db.execute("SELECT DISTINCT series_id,name,theme FROM macro").fetchall()
    if not m: st.info("Add FRED_API_KEY to load macro data.")
    for theme in sorted({t for _, _, t in m}):
        st.subheader(theme.replace("_", " ").title())
        for sid, name, t in [x for x in m if x[2] == theme]:
            d = pd.DataFrame(db.execute("SELECT date,value FROM macro WHERE series_id=? ORDER BY date", (sid,)).fetchall(), columns=["date", "value"])
            st.caption(f"{name}  |  latest {d['value'].iloc[-1]:.4g}")
            st.line_chart(d.set_index("date")["value"], height=120)

with tab_news:
    cats = [r[0] for r in db.execute("SELECT DISTINCT category FROM articles")]
    pick = st.multiselect("Category", cats, default=cats)
    if pick:
        qs = ",".join("?" * len(pick))
        for cat, src, title, link in db.execute(f"SELECT category,source,title,link FROM articles WHERE category IN ({qs}) ORDER BY fetched DESC LIMIT 150", pick):
            st.markdown(f"**[{title}]({link})**  \n<small>{src}</small>", unsafe_allow_html=True)

with tab_chart:
    syms = {"Gold": "OANDA:XAUUSD", "EUR/USD": "FX:EURUSD", "USD/JPY": "FX:USDJPY", "S&P 500": "FOREXCOM:SPXUSD",
            "Nasdaq 100": "FOREXCOM:NSXUSD", "WTI Oil": "TVC:USOIL", "US 10Y": "TVC:US10Y", "Bitcoin": "BITSTAMP:BTCUSD", "DXY": "TVC:DXY"}
    pick = st.selectbox("Market", list(syms))
    tv("embed-widget-advanced-chart.js", {"autosize": False, "width": "100%", "height": 620, "symbol": syms[pick], "interval": "60",
       "theme": "dark", "style": "1", "locale": "en", "allow_symbol_change": True, "hide_side_toolbar": False, "studies": ["RSI@tv-basicstudies"]}, 640)

with tab_cal:
    st.caption("Live economic calendar with forecast, previous and actual values.")
    tv("embed-widget-events.js", {"colorTheme": "dark", "isTransparent": False, "width": "100%", "height": 650, "locale": "en",
       "importanceFilter": "0,1", "countryFilter": "us,eu,gb,jp,cn,in,ca,au,de"}, 670)

def val(sid, back=0):
    r = db.execute("SELECT value FROM macro WHERE series_id=? ORDER BY date DESC LIMIT 1 OFFSET ?", (sid, back)).fetchone()
    return r[0] if r else None

with tab_reg:
    st.subheader("Market regime: risk-on or risk-off?")
    sig = []
    v = val("VIXCLS")
    if v is not None: sig.append(("VIX (fear gauge)", f"{v:.1f}", -1 if v > 25 else 1 if v < 16 else 0))
    v, p = val("BAMLH0A0HYM2"), val("BAMLH0A0HYM2", 21)
    if v and p: sig.append(("High-yield credit spread, 1m change", f"{v:.2f}% ({v-p:+.2f})", -1 if v > p + .25 else 1 if v < p - .25 else 0))
    v = val("T10Y2Y")
    if v is not None: sig.append(("Yield curve 10Y-2Y", f"{v:+.2f}", -1 if v < 0 else 1 if v > .5 else 0))
    v = val("NFCI")
    if v is not None: sig.append(("Financial conditions (NFCI)", f"{v:+.2f}", -1 if v > 0 else 1))
    v, p = val("DFII10"), val("DFII10", 21)
    if v is not None and p is not None: sig.append(("US 10Y real yield, 1m change", f"{v:.2f}% ({v-p:+.2f})", -1 if v > p + .15 else 1 if v < p - .15 else 0))
    v, p = val("DTWEXBGS"), val("DTWEXBGS", 21)
    if v and p: sig.append(("US dollar index, 1m change", f"{(v/p-1)*100:+.2f}%", -1 if v/p > 1.01 else 1 if v/p < .99 else 0))
    if not sig: st.info("Add FRED_API_KEY in Secrets to unlock the regime view.")
    else:
        tot = sum(x[2] for x in sig)
        st.metric("Regime", "RISK-ON" if tot >= 2 else "RISK-OFF" if tot <= -2 else "MIXED", f"score {tot:+d} of {len(sig)}")
        st.dataframe(pd.DataFrame([{"Signal": a, "Reading": b, "Leans": {1: "Risk-on", 0: "Neutral", -1: "Risk-off"}[c]} for a, b, c in sig]), hide_index=True, use_container_width=True)
        st.caption("Simple rules-based score from free FRED data. A starting point, not a trading signal.")

with tab_news:
    st.divider()
    if st.button("🤖 Tag top headlines: assets affected and direction"):
        if not os.getenv("ANTHROPIC_API_KEY"): st.error("Add ANTHROPIC_API_KEY in Secrets.")
        else:
            with st.spinner("Reading headlines..."):
                st.markdown(brief.generate_brief("From the headlines, pick the 15 most market-relevant. For each: headline [n], assets affected, direction (up/down), and a one-line reason. Table format."))
