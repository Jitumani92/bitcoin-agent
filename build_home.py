import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import glob
from jinja2 import Environment, FileSystemLoader
from fetch_news import fetch_price
from fetch_market import (fetch_top_50, fetch_fear_greed, fetch_trending,
                          fetch_market_overview, fetch_whale_transactions,
                          format_number, format_price, get_fear_greed_color)
from build_page import parse_article, strip_html
from datetime import datetime


def build_home(articles, price_data, intro=""):
    print("Building home page...")

    top_coins  = fetch_top_50()
    fear_greed = fetch_fear_greed()
    trending   = fetch_trending()
    overview   = fetch_market_overview()
    whales     = fetch_whale_transactions()

    for coin in top_coins:
        coin["price_fmt"]      = format_price(coin["price"])
        coin["market_cap_fmt"] = format_number(coin["market_cap"])
        coin["volume_fmt"]     = format_number(coin["volume"])

    overview["total_mcap_fmt"]   = format_number(overview.get("total_mcap", 0))
    overview["total_volume_fmt"] = format_number(overview.get("total_volume", 0))

    btc          = top_coins[0] if top_coins else {}
    change_class = "up" if "UP" in price_data["change"] or "▲" in price_data["change"] else "down"

    if not intro and articles:
        intro = articles[0]["paragraphs"][0] if articles[0]["paragraphs"] else ""

    env      = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("index_template.html")

    html = template.render(
        date             = datetime.today().strftime("%B %d, %Y"),
        update_time      = datetime.now().strftime("%H:%M UTC"),
        price            = price_data["price"],
        change           = price_data["change"],
        change_class     = change_class,
        intro            = intro,
        articles         = articles,
        top_coins        = top_coins,
        fear_greed       = fear_greed,
        fear_greed_color = get_fear_greed_color(fear_greed["value"]),
        trending         = trending,
        overview         = overview,
        whales           = whales,
        btc_high         = format_price(btc.get("high_24h")),
        btc_low          = format_price(btc.get("low_24h")),
        btc_ath          = format_price(btc.get("ath")),
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("OK index.html built!")


if __name__ == "__main__":
    backup_files = sorted(glob.glob("backups/*.json"), reverse=True)
    if not backup_files:
        print("No backup files found.")
        exit()

    with open(backup_files[0], "r", encoding="utf-8") as f:
        content = json.load(f)

    articles   = [parse_article(a) for a in content["articles"]]
    intro      = strip_html(content.get("intro", ""))
    price_data = fetch_price()

    build_home(articles, price_data, intro)
    print("Done! Open index.html in your browser.")