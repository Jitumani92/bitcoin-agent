import json
from jinja2 import Environment, FileSystemLoader
from fetch_news import fetch_news, fetch_price
from fetch_market import (fetch_top_50, fetch_fear_greed, fetch_trending,
                          fetch_market_overview, fetch_whale_transactions,
                          format_number, format_price)
from datetime import datetime

def get_fear_greed_color(value):
    if value <= 25:   return "#f44336"
    elif value <= 45: return "#ff9800"
    elif value <= 55: return "#ffeb3b"
    elif value <= 75: return "#8bc34a"
    else:             return "#4caf50"

def build_home(articles, price_data):
    print("Building home page...")

    # Fetch all market data
    top_coins   = fetch_top_50()
    fear_greed  = fetch_fear_greed()
    trending    = fetch_trending()
    overview    = fetch_market_overview()
    whales      = fetch_whale_transactions()

    # Format coin prices
    for coin in top_coins:
        coin["price_fmt"]      = format_price(coin["price"])
        coin["market_cap_fmt"] = format_number(coin["market_cap"])
        coin["volume_fmt"]     = format_number(coin["volume"])

    # Format overview numbers
    overview["total_mcap_fmt"]   = format_number(overview.get("total_mcap", 0))
    overview["total_volume_fmt"] = format_number(overview.get("total_volume", 0))

    # Get BTC specific data
    btc = top_coins[0] if top_coins else {}

    change_class = "up" if "▲" in price_data["change"] else "down"

    from jinja2 import Environment, FileSystemLoader, ChoiceLoader
    env = Environment(loader=ChoiceLoader([
        FileSystemLoader("templates"),
         FileSystemLoader(".")
    ]))
    template = env.get_template("index_template.html")
    
    html = template.render(
        page_title   = "Home",
        active_page  = "home",
        date         = datetime.today().strftime("%B %d, %Y"),
        update_time  = datetime.now().strftime("%H:%M UTC"),
        price        = price_data["price"],
        change       = price_data["change"],
        change_class = change_class,
        intro        = "Welcome to CryptoDaily — your trusted source for Bitcoin and cryptocurrency news, market data, and analysis. Today's market is showing strong activity across all major cryptocurrencies.",
        articles     = articles,
        top_coins    = top_coins,
        fear_greed   = fear_greed,
        fear_greed_color = get_fear_greed_color(fear_greed["value"]),
        trending     = trending,
        overview     = overview,
        whales       = whales,
        btc_high     = format_price(btc.get("high_24h", 0)),
        btc_low      = format_price(btc.get("low_24h", 0)),
        btc_ath      = format_price(btc.get("ath", 0)),
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ index.html built!")

if __name__ == "__main__":
    # Use saved backup articles so we don't run AI again
    import os, glob
    backup_files = sorted(glob.glob("backups/*.json"), reverse=True)

    if backup_files:
        with open(backup_files[0], "r", encoding="utf-8") as f:
            content = json.load(f)
        from build_page import parse_article, parse_market_section
        articles = [parse_article(a) for a in content["articles"]]
    else:
        articles = []

    price_data = fetch_price()
    build_home(articles, price_data)

    print("\n🌐 Open index.html to see the home page!")