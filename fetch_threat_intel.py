import feedparser
import datetime
import re

# ── Feed Sources ─────────────────────────────────────────────────────────────
FEEDS = [
    {
        "name": "Krebs on Security",
        "url": "https://krebsonsecurity.com/feed/",
        "emoji": "🔐"
    },
    {
        "name": "Bleeping Computer",
        "url": "https://www.bleepingcomputer.com/feed/",
        "emoji": "💻"
    },
    {
        "name": "The Hacker News",
        "url": "https://feeds.feedburner.com/TheHackersNews",
        "emoji": "🗞️"
    },
    {
        "name": "CISA Alerts",
        "url": "https://www.cisa.gov/news.xml",
        "emoji": "🚨"
    },
]

MAX_ARTICLES_PER_SOURCE = 10  # How many articles to show per source

def clean_html(text):
    """Strip HTML tags from summary text."""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean[:300] + "..." if len(clean) > 300 else clean

def format_date(entry):
    """Try to extract and format the published date."""
    try:
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            dt = datetime.datetime(*entry.published_parsed[:6])
            return dt.strftime("%B %d, %Y")
    except Exception:
        pass
    return "Date unknown"

def fetch_feed(feed_info):
    """Fetch and parse a single RSS feed."""
    articles = []
    try:
        parsed = feedparser.parse(feed_info["url"])
        entries = parsed.entries[:MAX_ARTICLES_PER_SOURCE]
        for entry in entries:
            articles.append({
                "title": entry.get("title", "No title").strip(),
                "link":  entry.get("link", "#"),
                "date":  format_date(entry),
                "summary": clean_html(entry.get("summary", entry.get("description", "")))
            })
        print(f"  [+] {feed_info['name']}: {len(articles)} articles fetched")
    except Exception as e:
        print(f"  [-] {feed_info['name']}: Failed - {e}")
    return articles

def build_markdown(feed_data):
    """Build the full markdown output."""
    now = datetime.datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
    lines = []

    lines.append("# 🛡️ Threat Intelligence Feed\n")
    lines.append(f"> Last updated: **{now}**  \n")
    lines.append("> Auto-updated daily via GitHub Actions.\n")
    lines.append("")
    lines.append("---\n")

    # Table of contents
    lines.append("## 📚 Sources\n")
    for feed in feed_data:
        anchor = feed["name"].lower().replace(" ", "-")
        lines.append(f"- [{feed['emoji']} {feed['name']}](#{anchor})")
    lines.append("")
    lines.append("---\n")

    # Articles per source
    for feed in feed_data:
        anchor = feed["name"].lower().replace(" ", "-")
        lines.append(f"## {feed['emoji']} {feed['name']}\n")
        if not feed["articles"]:
            lines.append("_No articles fetched. Source may be temporarily unavailable._\n")
        else:
            for art in feed["articles"]:
                lines.append(f"### [{art['title']}]({art['link']})")
                lines.append(f"📅 {art['date']}\n")
                if art["summary"]:
                    lines.append(f"{art['summary']}\n")
                lines.append("")
        lines.append("---\n")

    lines.append("_This page is automatically generated. Do not edit manually._")
    return "\n".join(lines)

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Fetching threat intel feeds...")

    feed_data = []
    for feed_info in FEEDS:
        articles = fetch_feed(feed_info)
        feed_data.append({
            "name":     feed_info["name"],
            "emoji":    feed_info["emoji"],
            "articles": articles
        })

    markdown = build_markdown(feed_data)

    with open("THREAT-INTEL.md", "w", encoding="utf-8") as f:
        f.write(markdown)

    print("\n✅ THREAT-INTEL.md generated successfully.")
