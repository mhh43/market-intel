"""Source registry. Add or remove entries here; no other code changes needed.
Feed URLs change over time: if one returns nothing, check the publisher's RSS page."""

RSS_FEEDS = {
    "central_banks": {
        "Federal Reserve": "https://www.federalreserve.gov/feeds/press_all.xml",
        "ECB": "https://www.ecb.europa.eu/rss/press.html",
        "Bank of England": "https://www.bankofengland.co.uk/rss/news",
        "BIS": "https://www.bis.org/doclist/bis_fsi_publs.rss",
        "IMF": "https://www.imf.org/en/News/rss?language=eng",
    },
    "markets_news": {
        "CNBC Top News": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "CNBC Economy": "https://www.cnbc.com/id/20910258/device/rss/rss.html",
        "MarketWatch": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "Investing.com": "https://www.investing.com/rss/news.rss",
        "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    },
    "geopolitics": {
        "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "Guardian World": "https://www.theguardian.com/world/rss",
        "DW": "https://rss.dw.com/rdf/rss-en-all",
        "UN News": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    },
    "energy_commodities": {
        "OilPrice": "https://oilprice.com/rss/main",
        "EIA Today in Energy": "https://www.eia.gov/rss/todayinenergy.xml",
    },
    "crypto": {
        "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "Cointelegraph": "https://cointelegraph.com/rss",
    },
}

# FRED macro series (free API key)
FRED_SERIES = {
    "rates": {"DGS2": "US 2Y yield", "DGS10": "US 10Y yield", "DFF": "Fed funds rate",
              "T10Y2Y": "10Y-2Y curve", "DFII10": "US 10Y real yield"},
    "inflation": {"CPIAUCSL": "US CPI", "PCEPILFE": "Core PCE", "T5YIE": "5Y breakeven inflation"},
    "growth_labor": {"UNRATE": "Unemployment rate", "PAYEMS": "Nonfarm payrolls", "GDPC1": "Real GDP"},
    "credit_risk": {"BAMLH0A0HYM2": "US high-yield spread", "BAMLC0A0CM": "US IG spread",
                    "VIXCLS": "VIX", "NFCI": "Chicago Fed financial conditions"},
    "fx_liquidity": {"DTWEXBGS": "Broad USD index", "WALCL": "Fed balance sheet"},
}

# Market prices via yfinance (free, no key; unofficial so can occasionally break)
PRICES = {
    "equities": {"^GSPC": "S&P 500", "^IXIC": "Nasdaq", "^DJI": "Dow", "^STOXX50E": "Euro Stoxx 50",
                 "^FTSE": "FTSE 100", "^N225": "Nikkei 225", "^HSI": "Hang Seng",
                 "000001.SS": "Shanghai Comp", "^NSEI": "Nifty 50", "^KSE": "KSE-100 (Pakistan)"},
    "rates": {"^TNX": "US 10Y yield", "^FVX": "US 5Y yield", "^IRX": "US 3M yield", "TLT": "20Y+ Treasury ETF"},
    "fx": {"DX-Y.NYB": "US Dollar Index", "EURUSD=X": "EUR/USD", "GBPUSD=X": "GBP/USD",
           "USDJPY=X": "USD/JPY", "USDCHF=X": "USD/CHF", "AUDUSD=X": "AUD/USD",
           "USDCAD=X": "USD/CAD", "USDCNY=X": "USD/CNY", "USDINR=X": "USD/INR", "USDPKR=X": "USD/PKR"},
    "energy": {"CL=F": "WTI crude", "BZ=F": "Brent crude", "NG=F": "Natural gas", "RB=F": "Gasoline"},
    "metals": {"GC=F": "Gold", "SI=F": "Silver", "HG=F": "Copper", "PL=F": "Platinum"},
    "agriculture": {"ZW=F": "Wheat", "ZC=F": "Corn", "ZS=F": "Soybeans", "KC=F": "Coffee", "SB=F": "Sugar"},
    "crypto": {"BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "SOL-USD": "Solana"},
    "credit_vol": {"^VIX": "VIX", "HYG": "High-yield bond ETF", "LQD": "IG bond ETF", "EMB": "EM bond ETF"},
}

# GDELT (free, no key): global news-event monitoring, queried by theme
GDELT_QUERIES = {
    "Middle East conflict": "(Israel OR Iran OR Gaza OR Houthi OR Hormuz) sourcelang:english",
    "Russia-Ukraine": "(Russia OR Ukraine) (sanctions OR attack OR ceasefire) sourcelang:english",
    "China-Taiwan-US": "(Taiwan OR \"South China Sea\" OR tariffs) China sourcelang:english",
    "Sanctions & trade": "(sanctions OR tariff OR embargo OR \"export controls\") sourcelang:english",
    "Energy supply": "(OPEC OR pipeline OR refinery OR LNG) sourcelang:english",
    "Central banks": "(\"rate decision\" OR \"interest rates\" OR \"central bank\") sourcelang:english",
    "Elections & unrest": "(election OR coup OR protests OR strike) sourcelang:english",
    "Pakistan & South Asia": "(Pakistan OR IMF OR \"State Bank of Pakistan\") sourcelang:english",
}
