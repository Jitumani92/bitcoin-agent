import json
from build_page import build_page
from datetime import datetime

# Load today's backup
with open("backups/content_2026-04-18.json", "r", encoding="utf-8") as f:
    content = json.load(f)

build_page(content)
print("Done!")