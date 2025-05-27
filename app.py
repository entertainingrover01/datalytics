from flask import Flask, render_template, abort, jsonify
import os
import markdown
import re
import datetime
from datetime import timedelta
import feedparser
import threading
import time
# import requests # Not strictly needed if only using feedparser for RSS
# from bs4 import BeautifulSoup # Not strictly needed if only using feedparser for RSS

app = Flask(__name__)

ARTICLES_DIR = 'articles'

# --- Configuration for External Highlights ---
# !!! CHANGE THIS TO THE DESIRED RSS FEED URL !!!
RSS_FEED_URL = 'https://www.kdnuggets.com/feed'
EXTERNAL_CACHE_DURATION_SECONDS = 3600

external_highlights_cache = {
    "articles": [],
    "last_updated": None
}

def load_articles():
    articles = []
    for filename in os.listdir(ARTICLES_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(ARTICLES_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

                front_matter_match = re.match(r'---\n(.*?)\n---(.*)', content, re.DOTALL)
                metadata = {}
                body = content
                if front_matter_match:
                    front_matter_str = front_matter_match.group(1)
                    body = front_matter_match.group(2).strip()

                    for line in front_matter_str.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip()

                html_content = markdown.markdown(body)

                if 'slug' not in metadata:
                    base_filename = os.path.splitext(filename)[0]
                    metadata['slug'] = base_filename.lower().replace(' ', '-')

                if 'date' in metadata:
                    try:
                        metadata['date_obj'] = datetime.datetime.strptime(metadata['date'], '%Y-%m-%d')
                    except ValueError:
                        metadata['date_obj'] = None
                else:
                    metadata['date_obj'] = None

                articles.append({
                    'metadata': metadata,
                    'html_content': html_content,
                    'filename': filename
                })

    articles.sort(key=lambda x: x['metadata'].get('date_obj', datetime.datetime.min), reverse=True)
    return articles

def fetch_and_cache_external_highlights():
    """Fetches articles from the external RSS feed and updates the cache."""
    global external_highlights_cache
    print(f"[{datetime.datetime.now()}] Attempting to fetch external RSS feed from: {RSS_FEED_URL}")
    try:
        feed = feedparser.parse(RSS_FEED_URL)
        print(feed)
        new_articles = []
        # Limit to 6 articles for display, consistent with the placeholder
        for entry in feed.entries[:6]:
            title = entry.title if hasattr(entry, 'title') else "No Title"
            summary = ""
            if hasattr(entry, 'summary'):
                summary = entry.summary
            elif hasattr(entry, 'description'):
                summary = entry.description

            summary_cleaned = re.sub('<.*?>', '', summary)
            if len(summary_cleaned) > 150:
                summary_cleaned = summary_cleaned[:150] + "..."

            link = entry.link if hasattr(entry, 'link') else "#"

            new_articles.append({
                "title": title,
                "summary": summary_cleaned,
                "url": link
            })

        external_highlights_cache["articles"] = new_articles
        external_highlights_cache["last_updated"] = datetime.datetime.now()
        print(f"[{datetime.datetime.now()}] External RSS feed fetched and cache updated successfully.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error fetching external RSS feed: {e}")
        if not external_highlights_cache["articles"]:
             external_highlights_cache["articles"] = []

def auto_update_external_cache():
    while True:
        fetch_and_cache_external_highlights()
        print(f"[{datetime.datetime.now()}] Next external highlights fetch in {EXTERNAL_CACHE_DURATION_SECONDS} seconds.")
        time.sleep(EXTERNAL_CACHE_DURATION_SECONDS)

all_articles = load_articles()

fetch_and_cache_external_highlights()

update_thread = threading.Thread(target=auto_update_external_cache)
update_thread.daemon = True
update_thread.start()

@app.route('/')
def home():
    latest_articles = all_articles[:3]
    return render_template("index.html", articles=latest_articles)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact_page():
    return render_template("contact.html")

@app.route('/blog')
def blog_list():
    return render_template('blog.html', articles=all_articles)

@app.route('/blog/<slug>')
def article_detail(slug):
    for article in all_articles:
        if article['metadata'].get('slug') == slug:
            return render_template('article.html', article=article)
    abort(404)

@app.route('/api/external-highlights')
def get_external_highlights():
    """API endpoint to serve cached external highlights to the frontend."""
    # This will return the articles that are updated by the background thread.
    # The caching logic ensures that the data is not fetched on every API call.
    return jsonify(external_highlights_cache["articles"])

if __name__ == '__main__':
    if not os.path.exists(ARTICLES_DIR):
        os.makedirs(ARTICLES_DIR)
        print(f"Created '{ARTICLES_DIR}' directory. Please add your Markdown articles there.")

    app.run(debug=True, port=8080)