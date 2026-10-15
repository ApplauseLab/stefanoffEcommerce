# Стефанов НП: website redesign (staging)

Redesign of [stefanoff.bg](https://stefanoff.bg) for Стефанов НП, a B2B supplier of organic rosehip, lavender and hawthorn from Bulgaria. Bulgarian first, with an English version at `/en/`. Products work as a quote bag: visitors add products and send them as one enquiry (no payment).

**Live staging:** https://applauselab.github.io/stefanoffEcommerce/ (not indexed by search engines).

## Build and run

Python 3.9+, standard library only.

```bash
cd site
python3 build.py          # writes site/dist/ (Bulgarian at /, English at /en/)
python3 serve.py 4175     # http://localhost:4175
```

## Deploy to GitHub Pages

```bash
cd site
./deploy.sh               # builds for /stefanoffEcommerce/, pushes site/dist to the gh-pages branch, rebuilds for local use
```

## Layout

- `site/`: page templates (`build.py`), English generation (`i18n.py`, `i18n/en.json`), styles and script (`src/`). See `site/README.md`.
- `redesign/build.py`: product, project and contact copy (single source), plus photos, videos and certificate PDFs in `redesign/src/`.
- `styleguide/tokens.css`: design tokens (colours, type, spacing).
- `assets/manifest.md`: image sources, credits and licences.

Values with a dotted underline on the site (prices, pack sizes, dates, some product facts) are placeholders awaiting the client's confirmation.
