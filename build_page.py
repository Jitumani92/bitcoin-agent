import re
from jinja2 import Environment, FileSystemLoader

# ── Parse AI written content into structured data ─────────────────────────────

def parse_article(article_data):
    written = article_data["written"]
    original = article_data["original"]

    # Extract title
    title = original["title"]
    title_match = re.search(r'ARTICLE_TITLE:\s*(.+)', written)
    if title_match:
        title = title_match.group(1).strip()

    # Clean markdown symbols from title
    title = re.sub(r'\*+', '', title).strip()

    # Extract body paragraphs
    paragraphs = []
    body_match = re.search(r'ARTICLE_BODY:\s*(.*?)(?=KEY_TAKEAWAY:|$)', written, re.DOTALL)
    if body_match:
        body_text = body_match.group(1).strip()
        # Remove numbered list markers and asterisks
        body_text = re.sub(r'\*+', '', body_text)
        body_text = re.sub(r'^\d+\.\s*', '', body_text, flags=re.MULTILINE)
        raw_paragraphs = [p.strip() for p in body_text.split('\n\n') if p.strip()]
        paragraphs = raw_paragraphs[:3]

    if not paragraphs:
        paragraphs = [original.get("summary", "")]

    # Extract key takeaway
    takeaway = ""
    takeaway_match = re.search(r'KEY_TAKEAWAY:\s*(.+)', written, re.DOTALL)
    if takeaway_match:
        takeaway = takeaway_match.group(1).strip().split('\n')[0]
        takeaway = re.sub(r'\*+', '', takeaway).strip()

    return {
        "title": title,
        "paragraphs": paragraphs,
        "takeaway": takeaway,
        "source": original.get("source", ""),
        "link": original.get("link", "")
    }


def parse_market_section(market_text):
    mood = ""
    watch = ""

    mood_match = re.search(r'MARKET_MOOD:\s*(.*?)(?=WATCH_TOMORROW:|$)', market_text, re.DOTALL)
    if mood_match:
        mood = mood_match.group(1).strip()

    watch_match = re.search(r'WATCH_TOMORROW:\s*(.*?)$', market_text, re.DOTALL)
    if watch_match:
        watch = watch_match.group(1).strip()

    return mood, watch


# ── Build the HTML page ───────────────────────────────────────────────────────

def build_page(content):
    # Parse all articles
    parsed_articles = [parse_article(a) for a in content["articles"]]

    # Parse market section
    market_mood, watch_tomorrow = parse_market_section(content["market_section"])

    # Determine if price change is up or down for CSS class
    change_class = "up" if "▲" in content["change"] else "down"

    # Set up Jinja2 template engine
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')

    # Fill the template with all content
    html = template.render(
        date=content["date"],
        price=content["price"],
        change=content["change"],
        change_class=change_class,
        intro=content["intro"],
        articles=parsed_articles,
        market_mood=market_mood,
        watch_tomorrow=watch_tomorrow
    )

    # Save as index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ index.html built successfully!")
    return html


# ── Test ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Sample content to test page building without running AI
    sample_content = {
        "date": "April 18, 2026",
        "price": "$67,432.10",
        "change": "▲ 2.34% (24h)",
        "intro": "Welcome to Bitcoin Daily! Today is April 18 and Bitcoin is trading strong at $67,432. Institutional investors continue to drive demand through ETF products, while miners prepare for the upcoming halving event. Read on for today's full coverage.",
        "articles": [
            {
                "original": {
                    "title": "Bitcoin Surges Past $67,000 on ETF Inflows",
                    "source": "CoinTelegraph",
                    "link": "https://cointelegraph.com",
                    "summary": "Bitcoin rose sharply today."
                },
                "written": """ARTICLE_TITLE: Bitcoin Breaks $67,000 as ETF Demand Surges

ARTICLE_BODY:
Bitcoin crossed the $67,000 mark today in a strong rally driven by record inflows into spot Bitcoin ETFs. Institutional investors have been pouring billions into these products since their approval, and today's numbers suggest that trend is accelerating. The price surge caught many short sellers off guard, triggering over $200 million in liquidations.

The ETF products from major asset managers have collectively accumulated over 400,000 BTC since their launch. This represents a significant portion of the circulating supply being locked away in institutional hands. Many analysts believe this supply squeeze is one of the main drivers of the current price appreciation.

Market participants are watching closely to see if Bitcoin can sustain above $67,000 into the weekend. Historically, weekends tend to see lower volume, which can lead to increased volatility in either direction. The next key resistance level sits at $70,000.

KEY_TAKEAWAY: Record ETF inflows are driving Bitcoin to new weekly highs as institutional demand continues to outpace new supply."""
            }
        ],
        "market_section": """MARKET_MOOD:
Today's market sentiment is strongly bullish, driven by continued institutional buying through ETF products and positive macroeconomic signals. The overall crypto market is up across the board, with Bitcoin leading the gains. Trading volume is above average, suggesting genuine buying interest rather than speculative moves.

WATCH_TOMORROW:
Watch for any announcements from major ETF providers regarding their daily inflow numbers, as these have been the primary market catalyst this week. Also keep an eye on the $70,000 resistance level — a break above this could trigger significant upward momentum."""
    }

    print("🔨 Building webpage...\n")
    build_page(sample_content)
    print("\n🌐 Open index.html in your browser to see the webpage!")