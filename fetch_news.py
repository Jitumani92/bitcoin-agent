import feedparser
import requests
from datetime import datetime

# ── 1. Bitcoin news from RSS feeds ──────────────────────────────────────────

RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://bitcoinmagazine.com/.rss/full/",
    "https://feeds.feedburner.com/CoinDesk",
]

def fetch_news(max_articles=8):
    articles = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            # Only take articles that mention Bitcoin or BTC
            title = entry.get("title", "")
            summary = entry.get("summary", "")

            if "bitcoin" in title.lower() or "btc" in title.lower():
                articles.append({
                    "title": title,
                    "summary": summary[:300],   # first 300 characters only
                    "link": entry.get("link", ""),
                    "source": feed.feed.get("title", "Unknown"),
                    "date": entry.get("published", str(datetime.today().date()))
                })

        if len(articles) >= max_articles:
            break

    return articles[:max_articles]


# ── 2. Bitcoin price from CoinGecko (free, no API key needed) ───────────────

def fetch_price():
    import time
    for attempt in range(3):
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": "bitcoin",
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "bitcoin" not in data:
                raise ValueError(f"Unexpected response: {data}")

            price  = data["bitcoin"]["usd"]
            change = data["bitcoin"]["usd_24h_change"]
            direction = "▲" if change >= 0 else "▼"

            return {
                "price":  f"${price:,.2f}",
                "change": f"{direction} {abs(change):.2f}% (24h)"
            }

        except Exception as e:
            print(f"Price fetch failed: {e}")
            if attempt < 2:
                print(f"   Retrying in 15 seconds...")
                time.sleep(15)

    return {"price": "Unavailable", "change": ""}


# ── 3. Test: run this file directly to see output ───────────────────────────

if __name__ == "__main__":
    print("\n📰 Fetching Bitcoin news...\n")
    articles = fetch_news()

    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Source : {article['source']}")
        print(f"   Link   : {article['link']}")
        print(f"   Summary: {article['summary'][:100]}...")
        print()

    print("💰 Fetching Bitcoin price...\n")
    price_data = fetch_price()
    print(f"   Price  : {price_data['price']}")
    print(f"   Change : {price_data['change']}")
    print()