import json
import glob
from jinja2 import Environment, FileSystemLoader
from fetch_news import fetch_price
from fetch_market import (fetch_top_50, fetch_trending, fetch_market_overview,
                          format_number, format_price)
from datetime import datetime


def build_trends(price_data):
    print("Building trends page...")

    top_coins = fetch_top_50()
    trending  = fetch_trending()
    overview  = fetch_market_overview()

    # Format all coin data
    for coin in top_coins:
        coin["price_fmt"]      = format_price(coin["price"])
        coin["market_cap_fmt"] = format_number(coin["market_cap"])
        coin["volume_fmt"]     = format_number(coin["volume"])
        coin["high_fmt"]       = format_price(coin["high_24h"])
        coin["low_fmt"]        = format_price(coin["low_24h"])
        coin["ath_fmt"]        = format_price(coin["ath"])

    # Format overview
    overview["total_mcap_fmt"]   = format_number(overview.get("total_mcap", 0))
    overview["total_volume_fmt"] = format_number(overview.get("total_volume", 0))

    # Top gainers and losers from top 50
    sorted_coins = sorted(top_coins, key=lambda x: x["change_24h"], reverse=True)
    gainers = sorted_coins[:5]
    losers  = sorted_coins[-5:][::-1]

    change_class = "up" if "▲" in price_data["change"] else "down"

    env      = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("trends_template.html")

    html = template.render(
        date         = datetime.today().strftime("%B %d, %Y"),
        update_time  = datetime.now().strftime("%H:%M UTC"),
        price        = price_data["price"],
        change       = price_data["change"],
        change_class = change_class,
        top_coins    = top_coins,
        trending     = trending,
        overview     = overview,
        gainers      = gainers,
        losers       = losers,
    )

    with open("trends.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ trends.html built!")


if __name__ == "__main__":
    price_data = fetch_price()
    build_trends(price_data)
    print("\n🌐 Open trends.html to see the trends page!")