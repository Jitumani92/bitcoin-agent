import ollama
from datetime import datetime

# ── Write full detailed daily Bitcoin content ─────────────────────────────────

def write_full_article(article):
    prompt = f"""
You are a professional Bitcoin news journalist.

Write a detailed, informative news article based on this headline and summary:

Title: {article['title']}
Summary: {article['summary']}
Source: {article['source']}

Write the article in this exact format:

ARTICLE_TITLE: (write an engaging title here)

ARTICLE_BODY:
(Write 3 detailed paragraphs about this news story. Each paragraph should be
4-5 sentences long. Explain what happened, why it matters for Bitcoin, and
what it means for regular people interested in Bitcoin. Use simple, clear
language. Do not use hashtags, emojis, or markdown formatting.)

KEY_TAKEAWAY:
(Write one single sentence summarising the most important point of this story.)
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


def write_market_mood(articles, price_data):
    headlines = "\n".join([f"- {a['title']}" for a in articles])

    prompt = f"""
You are a Bitcoin market analyst.

Today's Bitcoin price: {price_data['price']}
24 hour change: {price_data['change']}

Today's headlines:
{headlines}

Write two sections:

MARKET_MOOD:
(In 3-4 sentences, describe whether today's market is bullish or bearish 
and the main reasons why. Be specific and informative.)

WATCH_TOMORROW:
(In 2-3 sentences, tell readers what key events, price levels, or news 
stories to watch out for tomorrow. Be specific.)
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


def write_daily_intro(articles, price_data):
    headlines = "\n".join([f"- {a['title']}" for a in articles[:3]])

    prompt = f"""
You are a friendly Bitcoin news editor writing the opening of a daily news page.

Today's date: {datetime.today().strftime('%B %d, %Y')}
Bitcoin price: {price_data['price']} ({price_data['change']})

Top headlines today:
{headlines}

Write a welcoming intro paragraph (4-5 sentences) that:
- Greets the reader and mentions today's date
- Mentions the current Bitcoin price naturally
- Teases the biggest stories of the day
- Sets an informative, friendly tone
- Plain text only, no hashtags or emojis
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


def generate_full_content(articles, price_data):
    print("✍️  Writing intro...")
    intro = write_daily_intro(articles, price_data)

    print("✍️  Writing full articles (this takes a few minutes)...")
    full_articles = []
    for i, article in enumerate(articles, 1):
        print(f"   → Article {i} of {len(articles)}: {article['title'][:50]}...")
        written = write_full_article(article)
        full_articles.append({
            "original": article,
            "written": written
        })

    print("✍️  Writing market mood and outlook...")
    market_section = write_market_mood(articles, price_data)

    return {
        "date": datetime.today().strftime('%B %d, %Y'),
        "price": price_data['price'],
        "change": price_data['change'],
        "intro": intro,
        "articles": full_articles,
        "market_section": market_section
    }


# ── Test ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample_articles = [
        {
            "title": "Bitcoin Surges Past $67,000 on ETF Inflows",
            "summary": "Bitcoin rose sharply today as institutional investors poured money into spot ETFs, pushing the price above $67,000 for the first time this week.",
            "source": "CoinTelegraph",
            "link": "https://cointelegraph.com"
        },
        {
            "title": "BTC Miners Report Record Revenue Ahead of Halving",
            "summary": "Bitcoin miners are reporting record revenues as the upcoming halving event approaches, with many upgrading hardware to prepare.",
            "source": "Bitcoin Magazine",
            "link": "https://bitcoinmagazine.com"
        },
        {
            "title": "El Salvador Adds More Bitcoin to National Reserves",
            "summary": "El Salvador announced it has added another 30 BTC to its national reserves, doubling down on its Bitcoin strategy.",
            "source": "CoinDesk",
            "link": "https://coindesk.com"
        },
    ]

    sample_price = {
        "price": "$67,432.10",
        "change": "▲ 2.34% (24h)"
    }

    print("🤖 AI is generating full content...\n")
    content = generate_full_content(sample_articles, sample_price)

    print("\n" + "="*60)
    print(f"DATE: {content['date']}")
    print(f"PRICE: {content['price']} {content['change']}")
    print("="*60)

    print(f"\nINTRO:\n{content['intro']}")

    for i, article in enumerate(content['articles'], 1):
        print(f"\n{'='*60}")
        print(f"ARTICLE {i}:")
        print(article['written'])

    print(f"\n{'='*60}")
    print("MARKET SECTION:")
    print(content['market_section'])

    print("\n✅ All content generated!")