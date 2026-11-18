# Datalytics — Personal Portfolio & Blog

Personal portfolio and blog for Krishna Prasad Chapagain, at
[datalytics.work](https://datalytics.work). Articles are Markdown files in
`articles/`; the site renders them to HTML with Flask templates.

## How it is hosted

The site is a **static site on Cloudflare Pages**. There is no server:
`freeze.py` renders the Flask app to plain HTML at build time, and
Cloudflare Pages serves the result. Every push to `master` rebuilds and
redeploys automatically, so publishing a new article is just adding a
Markdown file and pushing.

## Run it locally (optional)

```bash
pip install -r requirement.txt
python app.py        # Flask dev server on http://localhost:8080
```

Or build the static site exactly as Cloudflare does:

```bash
pip install -r requirement.txt
python freeze.py     # renders everything into dist/
python -m http.server --directory dist 8080
```

## Cloudflare Pages setup (one time)

In the Cloudflare dashboard, **Workers & Pages → Create → Pages →
Connect to Git**, pick this repo, then use these build settings:

| Setting | Value |
| --- | --- |
| Framework preset | None |
| Build command | `pip install -r requirement.txt && python freeze.py` |
| Build output directory | `dist` |
| Environment variable | `PYTHON_VERSION` = `3.11` |

Then, in the Pages project, **Custom domains → Set up a custom domain →
`datalytics.work`** (and `www.datalytics.work` if you want it). The domain
already lives in this Cloudflare account, so DNS is configured
automatically.

## Publishing a new article

1. Add a `.md` file under `articles/` — put it in the subfolder for its
   category (create a new subfolder for a new category).
2. Start the file with front matter, e.g.:

   ```markdown
   ---
   title: My New Article
   date: 2026-11-18
   author: Krishna Prasad Chapagain
   summary: One or two lines shown on the home and blog pages.
   slug: my-new-article
   ---
   Your article text in Markdown...
   ```

   `slug` is optional — without it, the slug is the filename, lowercased
   with spaces turned into dashes.
3. Commit and push to `master`. Cloudflare Pages rebuilds and the article
   goes live in a minute or two — no other step needed.

## How the pieces fit

- `app.py` — the Flask app: routes, Markdown loading, front-matter parsing.
  Used only at build time (and for local dev); it does not run on
  Cloudflare.
- `freeze.py` — the build script: renders every route (home, about,
  contact, blog list, each category page, each article) to static HTML in
  `dist/`, plus a `404.html`, and copies `static/` across.
- `functions/api/external-highlights.js` — a Cloudflare Pages Function.
  The homepage "Latest Discoveries & Highlights" section fetches
  `/api/external-highlights`; this function fetches the KDnuggets RSS feed
  server-side and returns the same JSON the old Flask endpoint returned,
  cached at the edge for 1 hour. It deploys automatically with the site —
  no separate step.
- `templates/`, `static/` — Jinja templates and CSS/images.
- `articles/` — Markdown articles, grouped by category subfolder.

## Known gaps

- The profile photo (`static/xyz.jpeg`) and the LinkedIn/GitHub/Kaggle
  icons (`static/icons8-*.png`) referenced by the templates are **not in
  this repo**, so those images 404. Drop the files into `static/` and push
  — they will deploy with the next build.
- The contact form is display-only: it posts to `#` and was never wired
  to a backend (same as on the old AWS hosting). It can be connected to a
  Pages Function + an email service later if you want it to send mail.
