"""Web dashboard.  Local: streamlit run app.py   Online: deploy to Streamlit Community Cloud (see README)."""
import os
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

st.title("📈 Global Market Intelligence")
c1, c2, _ = st.columns([1, 1, 4])
if c1.button("🔄 Refresh data"): refresh_core.clear()
if c2.button("🌍 Load geopolitics (GDELT)"):
    with st.spinner("Querying GDELT (about 1 minute)..."): ingest.ingest_gdelt()
refresh_core()
db = conn()

tab_brief, tab_mkt, tab_macro, tab_news = st.tabs(["🧠 AI Brief & Q&A", "💹 Markets", "🏛 Macro", "📰 News & Geopolitics"])

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
