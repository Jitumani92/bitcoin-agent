import sys
sys.stdout.reconfigure(encoding='utf-8')

import re
import requests
import feedparser
from datetime import datetime


def strip_html_simple(text):
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://bitcoinmagazine.com/.rss/full/",
    "https://feeds.feedburner.com/CoinDesk",
]


def fetch_news(max_articles=6):
    articles = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title   = strip_html_simple(entry.get("title", ""))
                summary = strip_html_simple(entry.get("summary", ""))

                if "bitcoin" in title.lower() or "btc" in title.lower():
                    articles.append({
                        "title":   title,
                        "summary": summary[:400],
                        "link":    entry.get("link", ""),
                        "source":  strip_html_simple(feed.feed.get("title", "Unknown")),
                        "date":    entry.get("published", str(datetime.today().date()))
                    })

            if len(articles) >= max_articles:
                break
        except Exception as e:
            print(f"Feed error {feed_url}: {e}")
            continue

    return articles[:max_articles]


def fetch_price():
    import time
    for attempt in range(3):
        try:
            url    = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids":                "bitcoin",
                "vs_currencies":      "usd",
                "include_24hr_change": "true"
            }
            response = requests.get(url, params=params, timeout=10)
            data     = response.json()

            if "bitcoin" not in data:
                raise ValueError(f"Unexpected response: {data}")

            price     = data["bitcoin"]["usd"]
            change    = data["bitcoin"]["usd_24h_change"]
            direction = "UP" if change >= 0 else "DOWN"

            return {
                "price":  f"${price:,.2f}",
                "change": f"{direction} {abs(change):.2f}% (24h)"
            }

        except Exception as e:
            print(f"Price fetch failed: {e}")
            if attempt < 2:
                print("Retrying in 15 seconds...")
                time.sleep(15)

    return {"price": "Unavailable", "change": ""}


if __name__ == "__main__":
    print("\nFetching Bitcoin news...\n")
    articles = fetch_news()
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Source:  {article['source']}")
        print(f"   Summary: {article['summary'][:100]}...")
        print()

    print("Fetching Bitcoin price...\n")
    price_data = fetch_price()
    print(f"   Price:  {price_data['price']}")
    print(f"   Change: {price_data['change']}")