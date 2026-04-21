import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import time
from datetime import datetime
from fetch_news import fetch_news, fetch_price
from ai_writer import generate_full_content
from build_page import parse_article, strip_html
from build_home import build_home
from build_news import build_news
from build_trends import build_trends
from build_market import build_market

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def save_backup(content):
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    filename = f"{backup_dir}/content_{datetime.today().strftime('%Y-%m-%d')}.json"
    backup = {
        "date":           content["date"],
        "price":          content["price"],
        "change":         content["change"],
        "intro":          content["intro"],
        "market_section": content["market_section"],
        "articles": [
            {"written": a["written"], "original": a["original"]}
            for a in content["articles"]
        ]
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(backup, f, indent=2, ensure_ascii=False)
    log(f"Backup saved to {filename}")

def run_agent():
    log("=" * 55)
    log("CryptoDaily Agent Starting...")
    log(f"Date: {datetime.today().strftime('%B %d, %Y')}")
    log("=" * 55)

    # Step 1 - Fetch news
    log("STEP 1 - Fetching Bitcoin news and price...")
    try:
        articles   = fetch_news(max_articles=6)
        price_data = fetch_price()
        log(f"OK Got {len(articles)} articles")
        log(f"OK Bitcoin price: {price_data['price']} {price_data['change']}")
    except Exception as e:
        log(f"ERROR in Step 1: {e}")
        return False

    # Step 2 - Generate AI content
    log("STEP 2 - Generating AI content (takes several minutes)...")
    try:
        content = generate_full_content(articles, price_data)
        log("OK AI content generated")
    except Exception as e:
        log(f"ERROR in Step 2: {e}")
        return False

    # Step 3 - Save backup
    log("STEP 3 - Saving backup...")
    try:
        save_backup(content)
    except Exception as e:
        log(f"WARNING Backup non-critical: {e}")

    # Step 4 - Parse articles
    log("STEP 4 - Parsing AI content...")
    try:
        parsed_articles = [parse_article(a) for a in content["articles"]]
        intro = strip_html(content.get("intro", ""))
        log(f"OK Parsed {len(parsed_articles)} articles")
    except Exception as e:
        log(f"ERROR in Step 4: {e}")
        return False

    # Step 5 - Build all pages
    log("STEP 5 - Building all pages...")

    log("   Building Home page...")
    try:
        build_home(parsed_articles, price_data, intro)
        log("   OK index.html done")
    except Exception as e:
        log(f"   ERROR Home page: {e}")

    log("   Waiting 30 seconds...")
    time.sleep(30)

    log("   Building News page...")
    try:
        build_news(parsed_articles, price_data, intro)
        log("   OK news.html done")
    except Exception as e:
        log(f"   ERROR News page: {e}")

    log("   Waiting 30 seconds...")
    time.sleep(30)

    log("   Building Trends page...")
    try:
        build_trends(price_data)
        log("   OK trends.html done")
    except Exception as e:
        log(f"   ERROR Trends page: {e}")

    log("   Waiting 30 seconds...")
    time.sleep(30)

    log("   Building Market page...")
    try:
        build_market(price_data)
        log("   OK market.html done")
    except Exception as e:
        log(f"   ERROR Market page: {e}")

    # Step 6 - Push to GitHub
    log("STEP 6 - Pushing to GitHub...")
    try:
        os.system('git add .')
        os.system(f'git commit -m "Daily update: {datetime.today().strftime("%Y-%m-%d")}"')
        os.system('git push origin main')
        log("OK Pushed to GitHub successfully")
    except Exception as e:
        log(f"ERROR GitHub push: {e}")

    log("=" * 55)
    log("CryptoDaily Agent completed successfully!")
    log(f"Site updated: {datetime.now().strftime('%B %d, %Y at %H:%M')}")
    log("=" * 55)
    return True

if __name__ == "__main__":
    success = run_agent()
    if not success:
        log("Agent finished with errors. Check logs above.")
        exit(1)