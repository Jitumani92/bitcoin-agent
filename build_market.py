from jinja2 import Environment, FileSystemLoader
from fetch_news import fetch_price
from fetch_market import (fetch_top_50, fetch_fear_greed, fetch_market_overview,
                          fetch_whale_transactions, format_number, format_price,
                          get_fear_greed_color)
from datetime import datetime


def build_market(price_data):
    print("Building market page...")

    top_coins = fetch_top_50()
    fear_greed = fetch_fear_greed()
    overview   = fetch_market_overview()
    whales     = fetch_whale_transactions()

    # Get BTC data
    btc = top_coins[0] if top_coins else {}
    btc["high_fmt"]       = format_price(btc.get("high_24h"))
    btc["low_fmt"]        = format_price(btc.get("low_24h"))
    btc["ath_fmt"]        = format_price(btc.get("ath"))
    btc["market_cap_fmt"] = format_number(btc.get("market_cap", 0))
    btc["volume_fmt"]     = format_number(btc.get("volume", 0))
    btc["circulating_fmt"] = f"{btc.get('circulating', 0):,.0f}"

    # Format overview
    overview["total_mcap_fmt"]   = format_number(overview.get("total_mcap", 0))
    overview["total_volume_fmt"] = format_number(overview.get("total_volume", 0))

    change_class = "up" if "▲" in price_data["change"] else "down"

    env      = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("market_template.html")

    html = template.render(
        date               = datetime.today().strftime("%B %d, %Y"),
        update_time        = datetime.now().strftime("%H:%M UTC"),
        price              = price_data["price"],
        change             = price_data["change"],
        change_class       = change_class,
        btc                = btc,
        overview           = overview,
        fear_greed         = fear_greed,
        fear_greed_color   = get_fear_greed_color(fear_greed["value"]),
        fear_greed_history = fear_greed.get("history", []),
        whales             = whales,
    )

    with open("market.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ market.html built!")


if __name__ == "__main__":
    price_data = fetch_price()
    build_market(price_data)
    print("\n🌐 Open market.html in your browser!")