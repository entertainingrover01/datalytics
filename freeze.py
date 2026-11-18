"""Build the Datalytics Flask site into a static site for Cloudflare Pages.

Renders every route with Flask's test client into dist/:
  /                     -> dist/index.html
  /about                -> dist/about/index.html
  /contact              -> dist/contact/index.html
  /blog                 -> dist/blog/index.html
  /blog/category/<name> -> dist/blog/category/<name>/index.html
  /blog/<slug>          -> dist/blog/<slug>/index.html
and copies static/ -> dist/static/.

Run:  pip install -r requirement.txt && python freeze.py
Then deploy dist/ to Cloudflare Pages (see README.md).

The /api/external-highlights endpoint is intentionally NOT frozen: it is
served live by the Cloudflare Pages Function in functions/api/.
"""
import os
import shutil
import socket
from urllib.parse import unquote, urlparse

# Bound the KDnuggets RSS fetch that app.py does at import time so a slow
# feed can never hang the build.
socket.setdefaulttimeout(15)

from app import all_articles, app  # noqa: E402

OUTPUT_DIR = "dist"


def url_to_file(url_path):
    path = unquote(urlparse(url_path).path).strip("/")
    if not path:
        return os.path.join(OUTPUT_DIR, "index.html")
    return os.path.join(OUTPUT_DIR, path, "index.html")


def main():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    with app.test_request_context():
        from flask import url_for

        urls = [
            url_for("home"),
            url_for("about"),
            url_for("contact_page"),
            url_for("blog_list"),
        ]
        categories = sorted({a["metadata"]["category"] for a in all_articles})
        for category in categories:
            urls.append(
                url_for(
                    "articles_by_category",
                    category_name=category.lower().replace(" ", "-"),
                )
            )
        for article in all_articles:
            urls.append(url_for("article_detail", slug=article["metadata"]["slug"]))

    client = app.test_client()
    for url in urls:
        response = client.get(url)
        if response.status_code != 200:
            raise SystemExit(f"freeze failed: {url} returned {response.status_code}")
        filepath = url_to_file(url)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(response.data)
        print(f"wrote {filepath} ({len(response.data)} bytes)")

    # 404 page: Cloudflare Pages serves 404.html for unknown URLs.
    response = client.get("/blog/__page-not-found__")
    with open(os.path.join(OUTPUT_DIR, "404.html"), "wb") as f:
        f.write(response.data)
    print("wrote dist/404.html")

    if os.path.isdir("static"):
        shutil.copytree("static", os.path.join(OUTPUT_DIR, "static"))
        print("copied static/ -> dist/static/")

    print(f"Done. {len(urls)} pages frozen into {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
