"""English version of the built site, generated from the Bulgarian pages.

The Bulgarian copy stays the single source (build.py and redesign/build.py). After the Bulgarian pages are built,
every page is re-rendered into /en/ by swapping each Bulgarian string for its entry in i18n/en.json:
  "html": whole fragments with inline markup (applied first, for sentences whose word order changes in English)
  "text": text nodes, attribute values (alt, title, aria-label, placeholder, content, value) and strings inside JSON
          blocks (structured data and the store data the bag reads)
Any Cyrillic left after both passes is a missing translation and stops the build.
"""
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
CYR = re.compile(r"[А-Яа-яЁё]")
TOKENS = re.compile(r"(<script\b[^>]*>[\s\S]*?</script>|<style\b[^>]*>[\s\S]*?</style>|<!--[\s\S]*?-->|<[^>]+>)")
ATTRS = re.compile(r'\b(alt|title|aria-label|placeholder|content|value|label)="([^"]*)"')
ASSET = ("/img/", "/docs/", "/icons/", "/brand/", "/vendor/", "/video/", "/site.css", "/tokens.css", "/site.js", "/robots.txt", "/sitemap.xml", "/en/")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def load():
    d = json.loads((HERE / "i18n" / "en.json").read_text(encoding="utf-8"))
    frags = sorted(d.get("html", {}).items(), key=lambda kv: -len(kv[0]))
    return frags, {norm(k): v for k, v in d.get("text", {}).items()}


def _swap_text(s, T, missing, where):
    if not CYR.search(s):
        return s
    raw = html.unescape(s)
    key = norm(raw)
    if key not in T:
        missing.add((key, where))
        return s
    lead = raw[: len(raw) - len(raw.lstrip())]
    tail = raw[len(raw.rstrip()):]
    return lead + T[key] + tail


def _walk_json(v, T, missing):
    if isinstance(v, str):
        return _swap_text(v, T, missing, "json-ld")
    if isinstance(v, list):
        return [_walk_json(x, T, missing) for x in v]
    if isinstance(v, dict):
        return {k: _walk_json(x, T, missing) for k, x in v.items()}
    return v


def en_href(h):
    if not h.startswith("/") or h.startswith("//") or h.startswith(ASSET):
        return h
    return "/en" + h


def translate(page, frags, T, missing, where):
    for bg, en in frags:
        page = page.replace(bg, en)
    out = []
    for part in TOKENS.split(page):
        if not part:
            continue
        if part.startswith("<script"):
            m = re.match(r'(<script[^>]*type="application/(?:ld\+)?json"[^>]*>)([\s\S]*)(</script>)', part)
            if m:
                data = _walk_json(json.loads(m.group(2)), T, missing)
                part = m.group(1) + json.dumps(data, ensure_ascii=False) + m.group(3)
            out.append(part)
        elif part.startswith("<!--") or part.startswith("<style"):
            out.append(part)
        elif part.startswith("<"):
            part = ATTRS.sub(lambda m: f'{m.group(1)}="{html.escape(_swap_text(m.group(2), T, missing, where), quote=True)}"'
                             if CYR.search(m.group(2)) else m.group(0), part)
            if "data-lang" not in part and "data-alt" not in part:
                part = re.sub(r'\b(href|action)="([^"]*)"', lambda m: f'{m.group(1)}="{en_href(m.group(2))}"', part)
            out.append(part)
        else:
            out.append(html.escape(_swap_text(part, T, missing, where), quote=False) if CYR.search(part) else part)
    return "".join(out)


def to_english(page, frags, T, missing, where):
    page = translate(page, frags, T, missing, where)
    page = page.replace('<html lang="bg"', '<html lang="en"', 1).replace('content="bg_BG"', 'content="en_GB"', 1)
    page = re.sub(r'(<link rel="canonical" href="https://[^/"]+)(/[^"]*)"', r'\1/en\2"', page, count=1)
    page = re.sub(r'(<meta property="og:image" content="https://[^"]+")', r'\1', page)
    page = page.replace(' data-lang="bg" hreflang="bg" lang="bg" aria-current="true">', ' data-lang="bg" hreflang="bg" lang="bg">')
    page = page.replace(' data-lang="en" hreflang="en" lang="en">', ' data-lang="en" hreflang="en" lang="en" aria-current="true">')
    return page


def extract(pages):
    """Every Cyrillic string a set of built pages renders, for filling in i18n/en.json."""
    found = {}
    for name, page in pages.items():
        for part in TOKENS.split(page):
            if part.startswith("<script"):
                m = re.search(r'type="application/(?:ld\+)?json"[^>]*>([\s\S]*)</script>', part)
                if m:
                    def walk(v):
                        if isinstance(v, str) and CYR.search(v):
                            found.setdefault(norm(v), name)
                        elif isinstance(v, list):
                            [walk(x) for x in v]
                        elif isinstance(v, dict):
                            [walk(x) for x in v.values()]
                    walk(json.loads(m.group(1)))
            elif part.startswith("<"):
                for _, v in ATTRS.findall(part):
                    if CYR.search(v):
                        found.setdefault(norm(html.unescape(v)), name)
            elif CYR.search(part):
                found.setdefault(norm(html.unescape(part)), name)
    return found
