import sys
sys.stdout.reconfigure(encoding='utf-8')

import re
import json
import glob
from jinja2 import Environment, FileSystemLoader
from datetime import datetime


def strip_html(text):
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def parse_article(article_data):
    written  = article_data["written"]
    original = article_data["original"]

    # Extract title
    title = strip_html(original.get("title", ""))
    title_match = re.search(r'ARTICLE_TITLE:\s*(.+)', written)
    if title_match:
        candidate = strip_html(re.sub(r'\*+', '', title_match.group(1).strip()))
        if len(candidate) > 10:
            title = candidate

    # Extract body paragraphs
    paragraphs = []
    body_match = re.search(r'ARTICLE_BODY:\s*(.*?)(?=KEY_TAKEAWAY:|$)', written, re.DOTALL)
    if body_match:
        body_text = body_match.group(1).strip()
        body_text = re.sub(r'\*+', '', body_text)
        body_text = re.sub(r'^\d+\.\s*', '', body_text, flags=re.MULTILINE)
        raw = [strip_html(p.strip()) for p in body_text.split('\n\n') if p.strip()]
        paragraphs = [p for p in raw if len(p) > 40][:3]

    # If no good paragraphs found try splitting by single newline
    if not paragraphs and body_match:
        body_text = strip_html(body_match.group(1).strip())
        sentences = [s.strip() for s in body_text.split('.') if len(s.strip()) > 40]
        if sentences:
            paragraphs = ['. '.join(sentences[:3]) + '.']

    # Final fallback use clean summary
    if not paragraphs:
        clean_summary = strip_html(original.get("summary", ""))
        if clean_summary:
            paragraphs = [clean_summary[:500]]
        else:
            paragraphs = [f"Read the full article about {title} at the original source."]

    # Extract takeaway
    takeaway = ""
    takeaway_match = re.search(r'KEY_TAKEAWAY:\s*(.+)', written, re.DOTALL)
    if takeaway_match:
        takeaway = strip_html(re.sub(r'\*+', '', takeaway_match.group(1).strip().split('\n')[0]).strip())
        if len(takeaway) < 10:
            takeaway = ""

    return {
        "title":      title,
        "paragraphs": paragraphs,
        "takeaway":   takeaway,
        "source":     strip_html(original.get("source", "")),
        "link":       original.get("link", "")
    }


def parse_market_section(market_text):
    mood  = ""
    watch = ""

    mood_match = re.search(r'MARKET_MOOD:\s*(.*?)(?=WATCH_TOMORROW:|$)', market_text, re.DOTALL)
    if mood_match:
        mood = strip_html(mood_match.group(1).strip())

    watch_match = re.search(r'WATCH_TOMORROW:\s*(.*?)$', market_text, re.DOTALL)
    if watch_match:
        watch = strip_html(watch_match.group(1).strip())

    return mood, watch


def build_page(content):
    parsed_articles = [parse_article(a) for a in content["articles"]]
    change_class    = "up" if "UP" in content.get("change", "") or "▲" in content.get("change", "") else "down"

    env      = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("index_template.html")

    html = template.render(
        date             = content["date"],
        price            = content["price"],
        change           = content["change"],
        change_class     = change_class,
        intro            = strip_html(content.get("intro", "")),
        articles         = parsed_articles,
        top_coins        = [],
        fear_greed       = {"value": 50, "label": "Neutral", "history": []},
        fear_greed_color = "#f7931a",
        trending         = [],
        overview         = {
            "total_mcap_fmt":   "N/A",
            "total_volume_fmt": "N/A",
            "btc_dominance":    0,
            "eth_dominance":    0,
            "active_coins":     "N/A",
            "mcap_change_24h":  0
        },
        whales   = [],
        btc_high = "N/A",
        btc_low  = "N/A",
        btc_ath  = "N/A",
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("index.html built successfully!")
    return html


if __name__ == "__main__":
    backup_files = sorted(glob.glob("backups/*.json"), reverse=True)
    if not backup_files:
        print("No backup files found.")
        exit()

    with open(backup_files[0], "r", encoding="utf-8") as f:
        content = json.load(f)

    build_page(content)
    print("Done!")