import os
import json
import time
from datetime import datetime
from fetch_news import fetch_news, fetch_price
from ai_writer import generate_full_content
from build_page import parse_article, parse_market_section
from build_home import build_home
from build_news import build_news
from build_trends import build_trends
from build_market import build_market

# ── Logging ───────────────────────────────────────────────────────────────────

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

# ── Save backup ───────────────────────────────────────────────────────────────

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
            {
                "written":  a["written"],
                "original": a["original"]
            }
            for a in content["articles"]
        ]
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(backup, f, indent=2, ensure_ascii=False)
    log(f"Backup saved → {filename}")

# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_agent():
    log("=" * 55)
    log("CryptoDaily Agent Starting...")
    log(f"Date: {datetime.today().strftime('%B %d, %Y')}")
    log("=" * 55)

    # ── Step 1: Fetch news and price ──────────────────────────
    log("STEP 1 — Fetching Bitcoin news and price...")
    try:
        articles   = fetch_news(max_articles=6)
        price_data = fetch_price()
        log(f"✅ Got {len(articles)} articles")
        log(f"✅ Bitcoin price: {price_data['price']} {price_data['change']}")
    except Exception as e:
        log(f"❌ ERROR in Step 1: {e}")
        return False

    # ── Step 2: Generate AI content ───────────────────────────
    log("STEP 2 — Generating AI content (takes several minutes)...")
    try:
        content = generate_full_content(articles, price_data)
        log("✅ AI content generated")
    except Exception as e:
        log(f"❌ ERROR in Step 2: {e}")
        return False

    # ── Step 3: Save backup ───────────────────────────────────
    log("STEP 3 — Saving backup...")
    try:
        save_backup(content)
    except Exception as e:
        log(f"⚠️  Backup warning (non-critical): {e}")

    # ── Step 4: Parse articles ────────────────────────────────
    log("STEP 4 — Parsing AI content...")
    try:
        parsed_articles = [parse_article(a) for a in content["articles"]]
        intro = content.get("intro", "")
        log(f"✅ Parsed {len(parsed_articles)} articles")
    except Exception as e:
        log(f"❌ ERROR in Step 4: {e}")
        return False

    # ── Step 5: Build all pages ───────────────────────────────
    log("STEP 5 — Building all pages...")

    log("   Building Home page...")
    try:
        build_home(parsed_articles, price_data)
        log("   ✅ index.html done")
    except Exception as e:
        log(f"   ❌ Home page error: {e}")

    log("   Waiting 30 seconds before next API call...")
    time.sleep(30)

    log("   Building News page...")
    try:
        build_news(parsed_articles, price_data, intro)
        log("   ✅ news.html done")
    except Exception as e:
        log(f"   ❌ News page error: {e}")

    log("   Waiting 30 seconds before next API call...")
    time.sleep(30)

    log("   Building Trends page...")
    try:
        build_trends(price_data)
        log("   ✅ trends.html done")
    except Exception as e:
        log(f"   ❌ Trends page error: {e}")

    log("   Waiting 30 seconds before next API call...")
    time.sleep(30)

    log("   Building Market page...")
    try:
        build_market(price_data)
        log("   ✅ market.html done")
    except Exception as e:
        log(f"   ❌ Market page error: {e}")

    # ── Step 6: Push to GitHub ────────────────────────────────
    log("STEP 6 — Pushing to GitHub...")
    try:
        os.system('git add .')
        os.system(f'git commit -m "Daily update: {datetime.today().strftime("%Y-%m-%d")}"')
        os.system('git push origin main')
        log("✅ Pushed to GitHub successfully")
    except Exception as e:
        log(f"❌ GitHub push error: {e}")

    log("=" * 55)
    log("✅ CryptoDaily Agent completed successfully!")
    log(f"🌐 Site updated: {datetime.now().strftime('%B %d, %Y at %H:%M')}")
    log("=" * 55)
    return True

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    success = run_agent()
    if not success:
        log("Agent finished with errors. Check logs above.")
        exit(1)