# Market Intelligence System (free-data edition)

Collects news, macro data, prices and geopolitical events for every major asset class,
then asks Claude to explain what it means: the cause, the transmission channel, and the effect.

## Setup (10 minutes)
1. Install Python 3.10+ then:  `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in the free keys (FRED is the most important).
3. Load data:        `python ingest.py all`
4. Get your brief:   `python brief.py`
5. Ask a question:   `python brief.py "Why is gold moving and what does it mean for EM currencies?"`

## Automate
Use `run_daily.sh` with cron (see comments inside) so data refreshes every 30 minutes and a brief is made each morning.

## Coverage
Equities (US, Europe, Asia, India, Pakistan), rates, credit, FX majors + PKR/INR/CNY,
energy, metals, agriculture, crypto, volatility, central banks, geopolitics (GDELT + world news).
Edit `config.py` to add any source, ticker or macro series.

## Known limits
- Free news is delayed by minutes and RSS feed URLs sometimes change (the ingest log shows which feeds fail).
- yfinance is unofficial and can occasionally break; swap in another free API if so.
- Output is analysis support, not a trading signal. Always check the cited headlines.

## Next modules to add
SEC EDGAR filings, CFTC positioning, EIA inventories, USDA crop reports, CoinGecko/on-chain data,
a Streamlit dashboard, Telegram alerts, and a log that scores past AI calls against outcomes.

## Put it online (free link, about 10 minutes)
1. Create a free account at github.com, make a new **private** repository, and upload everything in this folder (not your `.env`).
2. Go to share.streamlit.io, sign in with GitHub, click **New app**, choose your repository, and set the main file to `app.py`.
3. Open **Advanced settings > Secrets** and paste:
   ```
   FRED_API_KEY = "your key"
   ANTHROPIC_API_KEY = "your key"
   SEC_USER_AGENT = "Your Name your@email.com"
   APP_PASSWORD = "choose-a-password"
   ```
4. Click **Deploy**. You get a link like `yourname-marketintel.streamlit.app`. Open it from any device.

APP_PASSWORD matters: without it anyone with the link can spend your Anthropic credit.
Free hosting sleeps when idle and wakes in about 30 seconds, and its storage resets on restart, so data reloads on each wake-up. That is fine for now; a paid VM (about 5 USD/month) removes both limits later.
Test locally first with `streamlit run app.py`.
