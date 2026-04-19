import requests
from datetime import datetime

# ── Top 50 Crypto Prices from CoinGecko ──────────────────────────────────────

def fetch_top_50():
    print("   Fetching top 50 crypto prices...")
    import time
    for attempt in range(3):
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 50,
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "1h,24h,7d"
            }
            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            # Check if we got rate limited
            if isinstance(data, dict) and "status" in data:
                print(f"   Rate limited, waiting 30 seconds... (attempt {attempt+1}/3)")
                time.sleep(30)
                continue

            coins = []
            for coin in data:
                if not isinstance(coin, dict):
                    continue
                change_24h = coin.get("price_change_percentage_24h") or 0
                change_7d  = coin.get("price_change_percentage_7d_in_currency") or 0
                change_1h  = coin.get("price_change_percentage_1h_in_currency") or 0

                coins.append({
                    "rank":         coin.get("market_cap_rank", 0),
                    "name":         coin.get("name", ""),
                    "symbol":       coin.get("symbol", "").upper(),
                    "price":        coin.get("current_price", 0),
                    "change_1h":    round(change_1h, 2),
                    "change_24h":   round(change_24h, 2),
                    "change_7d":    round(change_7d, 2),
                    "market_cap":   coin.get("market_cap", 0),
                    "volume":       coin.get("total_volume", 0),
                    "image":        coin.get("image", ""),
                    "high_24h":     coin.get("high_24h") or 0,
                    "low_24h":      coin.get("low_24h") or 0,
                    "ath":          coin.get("ath") or 0,
                    "ath_change":   round(coin.get("ath_change_percentage") or 0, 2),
                    "circulating":  coin.get("circulating_supply") or 0,
                    "total_supply": coin.get("total_supply") or 0,
                })

            print(f"   Got {len(coins)} coins")
            return coins

        except Exception as e:
            print(f"   ERROR fetching top 50: {e}")
            if attempt < 2:
                print(f"   Retrying in 15 seconds...")
                time.sleep(15)

    return []


# ── Fear & Greed Index ────────────────────────────────────────────────────────

def fetch_fear_greed():
    print("   Fetching Fear & Greed index...")
    try:
        url = "https://api.alternative.me/fng/?limit=7"
        response = requests.get(url, timeout=10)
        data = response.json()

        entries = data.get("data", [])
        today = entries[0] if entries else {}

        history = []
        for entry in entries:
            history.append({
                "value":       int(entry.get("value", 0)),
                "label":       entry.get("value_classification", ""),
                "timestamp":   entry.get("timestamp", "")
            })

        return {
            "value":   int(today.get("value", 0)),
            "label":   today.get("value_classification", "Neutral"),
            "history": history
        }

    except Exception as e:
        print(f"   ERROR fetching Fear & Greed: {e}")
        return {"value": 50, "label": "Neutral", "history": []}


# ── Trending Coins from CoinGecko ─────────────────────────────────────────────

def fetch_trending():
    print("   Fetching trending coins...")
    try:
        url = "https://api.coingecko.com/api/v3/search/trending"
        response = requests.get(url, timeout=10)
        data = response.json()

        trending = []
        for item in data.get("coins", []):
            coin = item.get("item", {})
            trending.append({
                "rank":   coin.get("market_cap_rank", "N/A"),
                "name":   coin.get("name", ""),
                "symbol": coin.get("symbol", "").upper(),
                "image":  coin.get("large", ""),
                "score":  coin.get("score", 0),
                "price_btc": coin.get("price_btc", 0),
            })

        print(f"   Got {len(trending)} trending coins")
        return trending

    except Exception as e:
        print(f"   ERROR fetching trending: {e}")
        return []


# ── Market Cap Overview ───────────────────────────────────────────────────────

def fetch_market_overview():
    print("   Fetching global market overview...")
    try:
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url, timeout=10)
        data = response.json().get("data", {})

        total_mcap = data.get("total_market_cap", {}).get("usd", 0)
        total_volume = data.get("total_volume", {}).get("usd", 0)
        btc_dominance = data.get("market_cap_percentage", {}).get("btc", 0)
        eth_dominance = data.get("market_cap_percentage", {}).get("eth", 0)
        active_coins = data.get("active_cryptocurrencies", 0)
        mcap_change = data.get("market_cap_change_percentage_24h_usd", 0)

        return {
            "total_mcap":     total_mcap,
            "total_volume":   total_volume,
            "btc_dominance":  round(btc_dominance, 2),
            "eth_dominance":  round(eth_dominance, 2),
            "active_coins":   active_coins,
            "mcap_change_24h": round(mcap_change, 2)
        }

    except Exception as e:
        print(f"   ERROR fetching market overview: {e}")
        return {}


# ── Whale Transactions via RSS ────────────────────────────────────────────────

def fetch_whale_transactions():
    print("   Fetching whale transactions...")
    try:
        # Use blockchain.info for large recent Bitcoin transactions
        url = "https://blockchain.info/unconfirmed-transactions?format=json&limit=50"
        response = requests.get(url, timeout=15)
        data = response.json()

        whales = []
        for tx in data.get("txs", []):
            # Total output value in BTC
            total_out = sum(o.get("value", 0) for o in tx.get("out", [])) / 100_000_000

            # Only show transactions over 10 BTC
            if total_out >= 10:
                whales.append({
                    "title":   f"{total_out:,.2f} BTC moved",
                    "summary": f"Large Bitcoin transaction detected: {total_out:,.2f} BTC (approx ${total_out * 67000:,.0f} USD) moving through the network.",
                    "hash":    tx.get("hash", ""),
                    "link":    f"https://blockchain.info/tx/{tx.get('hash', '')}",
                    "date":    datetime.utcfromtimestamp(tx.get("time", 0)).strftime("%Y-%m-%d %H:%M UTC") if tx.get("time") else "",
                    "btc_amount": round(total_out, 4)
                })

        # Sort by biggest transaction first
        whales = sorted(whales, key=lambda x: x["btc_amount"], reverse=True)[:10]

        print(f"   Got {len(whales)} whale transactions (10+ BTC)")
        return whales

    except Exception as e:
        print(f"   ERROR fetching whale transactions: {e}")
        return []


# ── Helper: format large numbers ──────────────────────────────────────────────

def format_number(num):
    if num >= 1_000_000_000_000:
        return f"${num / 1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:
        return f"${num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num / 1_000_000:.2f}M"
    else:
        return f"${num:,.2f}"


def format_price(price):
    if price is None:
        return "N/A"
    if price >= 1:
        return f"${price:,.2f}"
    elif price >= 0.01:
        return f"${price:.4f}"
    else:
        return f"${price:.8f}"
    

def get_fear_greed_color(value):
    if value <= 25:   return "#f44336"
    elif value <= 45: return "#ff9800"
    elif value <= 55: return "#ffeb3b"
    elif value <= 75: return "#8bc34a"
    else:             return "#4caf50"    


# ── Test ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🚀 Testing all market data fetchers...\n")

    print("1. Top 50 Coins:")
    coins = fetch_top_50()
    for coin in coins[:3]:
        print(f"   #{coin['rank']} {coin['name']} ({coin['symbol']}): "
              f"{format_price(coin['price'])} | "
              f"24h: {coin['change_24h']}% | "
              f"MCap: {format_number(coin['market_cap'])}")

    print("\n2. Fear & Greed Index:")
    fg = fetch_fear_greed()
    print(f"   Value: {fg['value']} — {fg['label']}")

    print("\n3. Trending Coins:")
    trending = fetch_trending()
    for t in trending[:3]:
        print(f"   {t['name']} ({t['symbol']}) — Rank #{t['rank']}")

    print("\n4. Market Overview:")
    overview = fetch_market_overview()
    print(f"   Total Market Cap: {format_number(overview.get('total_mcap', 0))}")
    print(f"   BTC Dominance: {overview.get('btc_dominance', 0)}%")
    print(f"   Active Coins: {overview.get('active_coins', 0):,}")

    print("\n5. Whale Transactions:")
    whales = fetch_whale_transactions()
    for w in whales[:3]:
        print(f"   {w['title']}")

    print("\n✅ All market data fetched!")