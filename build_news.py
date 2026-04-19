import json
import glob
from jinja2 import Environment, FileSystemLoader
from fetch_news import fetch_price
from fetch_market import fetch_fear_greed, fetch_trending, get_fear_greed_color
from build_page import parse_article, parse_market_section
from datetime import datetime


def load_archive():
    archive = []
    backup_files = sorted(glob.glob("backups/*.json"), reverse=True)
    for filepath in backup_files[1:31]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)
            articles = [parse_article(a) for a in content.get("articles", [])]
            archive.append({
                "date":          content.get("date", ""),
                "btc_price":     content.get("price", ""),
                "article_count": len(articles),
                "articles":      articles
            })
        except Exception as e:
            print(f"   Warning: could not load {filepath}: {e}")
    return archive


def build_news(today_articles, price_data, intro):
    print("Building news page...")

    fear_greed = fetch_fear_greed()
    trending   = fetch_trending()
    archive    = load_archive()

    change_class = "up" if "▲" in price_data["change"] else "down"

    env      = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("news_template.html")

    html = template.render(
        date             = datetime.today().strftime("%B %d, %Y"),
        update_time      = datetime.now().strftime("%H:%M UTC"),
        price            = price_data["price"],
        change           = price_data["change"],
        change_class     = change_class,
        intro            = intro,
        today_articles   = today_articles,
        archive          = archive,
        fear_greed       = fear_greed,
        fear_greed_color = get_fear_greed_color(fear_greed["value"]),
        trending         = trending,
    )

    with open("news.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ news.html built!")


if __name__ == "__main__":
    backup_files = sorted(glob.glob("backups/*.json"), reverse=True)

    if not backup_files:
        print("No backup files found. Run agent.py first.")
        exit()

    with open(backup_files[0], "r", encoding="utf-8") as f:
        content = json.load(f)

    articles   = [parse_article(a) for a in content["articles"]]
    price_data = fetch_price()

    build_news(articles, price_data, content.get("intro", ""))
    print("\n🌐 Open news.html to see the news page!")