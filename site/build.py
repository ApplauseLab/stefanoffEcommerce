#!/usr/bin/env python3
"""Build the stefanoff.bg website (styleguide v1.0) into ./dist."""
import html
import json
import re
import shutil
import string
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
PROJECT = ROOT.parent
SRC, DIST = ROOT / "src", ROOT / "dist"
sys.path.insert(0, str(PROJECT / "redesign"))
from build import PRODUCTS, PROJECTS, PHONE, PHONE_HREF, EMAIL, tbc  # noqa: E402  (single source of copy)

SITE = "https://stefanoff.bg"
YEAR = date.today().year
import time as _t
VER = str(int(_t.time()))  # cache-busting stamp for CSS and JS, new on every build
TRACES = "https://webgate.ec.europa.eu/tracesnt/directory/publication/organic-operator/BG-BIO-22.100-0003115.2024.001.pdf"


def esc(s):
    return html.escape(s, quote=True)


def strip(s):
    return re.sub(r"<[^>]+>", "", s)


def ico(name, extra=""):
    return f'<span class="ico{(" " + extra) if extra else ""}" style="--i:url(/icons/{name}.svg)" aria-hidden="true"></span>'


ARROW = ico("arrow-right", "arrow")

CREDS = [
    ("leaf", "Био сертификат", "ЕС 2018/848", "/sertifikati.html#bio"),
    ("spray-bottle-slash", "Без пестициди", "0 остатъци, ISO 17025", "/sertifikati.html#analiz"),
    ("list-magnifying-glass", "Публичен регистър", "TRACES, ЕС", "/sertifikati.html#proverka"),
    ("tractor", "ПРСР 2014–2020", "Подмерки 4.1 и 4.2", "/proekti.html#rdp-4015-0286"),
    ("trend-up", "Механизъм за възстановяване", "NextGenerationEU", "/proekti.html#rrp-6004-2420"),
]

FAQ = [
    ("Защо Булаир?", "Булаир е в подножието на Източна Стара планина, близо до Хемските порти. Землището му попада в две защитени зони от „Натура 2000“. Там отглеждаме шипка и бял трън, редом с природни местообитания."),
    ("Означава ли „Натура 2000“, че продуктът е био?", "Не. „Натура 2000“ е природозащитен статут на територията. „Био“ е отделна система с правила, контрол и сертификация. За всеки продукт посочваме кой сертификат го покрива."),
    ("Продавате ли на дребно?", "Не. Работим с фирми: производители на храни, чай и козметика, преработватели и търговци на едро. Ако ви трябва малко количество за проба, пишете ни."),
    ("Какво е минималното количество за поръчка?", f"Зависи от продукта и опаковката. Посочете нужното количество в запитването и ще го потвърдим в офертата. {tbc('Конкретните минимуми се уточняват.')}"),
    ("Доставяте ли извън България?", f"{tbc('Да, в рамките на ЕС.')} Условията на доставка и транспорта договаряме в офертата."),
    ("Може ли мостра преди поръчка?", f"{tbc('Да.')} Изпращаме мостра след запитване с посочени продукт, форма и количество."),
    ("Какви документи получавам?", "Био сертификат, анализ за остатъци от пестициди и спецификация на продукта. Сертификат за транзакция издаваме при поискване, според изискванията за био продукти."),
    ("Кога е реколтата?", f"Шипката се бере през септември и октомври, лавандулата през {tbc('юни и юли')}. Сушените продукти предлагаме през цялата година до изчерпване на реколтата."),
    ("Колко бързо отговаряте?", f"В работни дни отговаряме {tbc('до един работен ден')}. Ако е спешно, обадете се на {PHONE}."),
]

ERAS = [
    {"key": "stone", "img": "era-1-tabula.jpg", "alt": "Участък от римската пътна карта Tabula Peutingeriana с Тракия, Черно море и Константинопол", "credit": "Tabula Peutingeriana, римска пътна карта (IV в.). Факсимиле К. Милер, 1887, обществено достояние", "year": "IV век", "rail": "IV в.", "title": "Портите на Хемус",
     "text": "На мястото на централната крепост са открити следи от временни дървени съоръжения, преди каменния строеж. Името идва от Хемус, античното име на Стара планина: portae Haemi."},
    {"key": "ustav", "img": "era-2-hisarya.jpg", "alt": "Късноантична крепостна стена с редове от тухли и камък", "credit": "Късноантична стена от епохата (Диоклецианопол, дн. Хисаря). Gitanes232, CC BY-SA 4.0", "year": "V – VI век", "rail": "V–VI в.", "title": "Каменната преграда",
     "text": "Три крепости, свързани с преградна стена с дължина около 2,3 км, пазят прохода. Централната е известна като „Хармана“. Точното датиране на отделните етапи още се обсъжда."},
    {"key": "print", "img": "era-3-skorpil.jpg", "alt": "Портрет на археолога Карел Шкорпил", "credit": "Карел Шкорпил. Държавна агенция „Архиви“, обществено достояние", "year": "XIX – XX век", "rail": "XIX–XX в.", "title": "Първите описания",
     "text": "Братята Карел и Херман Шкорпил описват останките в местността Гермето, между Булаир и Голица."},
    {"key": "now", "img": "era-4-kamchia.jpg", "alt": "Широколистна гора в защитена зона „Камчийска планина“", "credit": "Защитена зона „Камчийска планина“. Viatarko, CC BY-SA 4.0", "year": "2005 – 2009", "rail": "2005–2009", "title": "Разкопките и днес",
     "text": "Разкопките през 2005, 2007 и 2009 г. дават по-точна картина за строежа. Днес руините свидетелстват за умението на древните строители, а земята наоколо е дом на нашите насаждения."},
]


def era_fonts_link():
    """Google Fonts for the three historical eras, subset to exactly the glyphs used (a few KB each)."""
    from urllib.parse import quote
    def glyphs(*texts):
        s = "".join(texts)
        return quote("".join(sorted(set(s + s.upper() + "0123456789 –.,:„“" + string.ascii_letters + "()'’;"))))
    by = {e["key"]: e for e in ERAS}
    fams = [("Cormorant+SC:wght@600", glyphs(by["stone"]["year"], by["stone"]["title"], by["stone"]["text"])),
            ("Monomakh", glyphs(by["ustav"]["year"], by["ustav"]["title"], by["ustav"]["text"])),
            ("Old+Standard+TT", glyphs(by["print"]["year"], by["print"]["title"], by["print"]["text"]))]
    return "".join(f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={f}&text={t}&display=swap">' for f, t in fams)



ZONES = [
    ("mountains", "BG0000133", "Камчийска и Еменска планина", "Местообитания и диви растения и животни на Източна Стара планина.", "Включва землището на Булаир"),
    ("bird", "BG0002044", "Камчийска планина", "Места за гнездене, хранене и почивка на дивите птици.", "Включва землището на Булаир"),
    ("bird", "BG0002045", "Комплекс Камчия", "Дивите птици по долното течение и крайбрежието на Камчия.", "В по-широкия Камчийски район"),
]



NAV_LEFT = [("/produkti.html", "Продукти", "produkti"), ("/fermata.html", "Фермата", "fermata"), ("/sertifikati.html", "Сертификати", "sertifikati")]
NAV_RIGHT = [("/proekti.html", "Проекти", "proekti")]
MENU = NAV_LEFT + NAV_RIGHT + [("/zapitvane.html#kontakt", "Контакти", "kontakt"), ("/zapitvane.html", "Запитване", "zapitvane")]


# --------------------------------------------------------------------------- layout
def emblem(cls="", alt=""):
    """The Stefanoff emblem for dark surfaces, as two aligned layers cut from stefanoff-logo-on-dark.png:
    the type, and the leaves (18 % darker than the original). On the home page the leaves turn in."""
    label = f' role="img" aria-label="{alt}"' if alt else ' aria-hidden="true"'
    return (f'<span class="emblem{(" " + cls) if cls else ""}"{label}>'
            f'<img class="emblem-type" src="/brand/stefanoff-logo-type.png" alt="" width="636" height="694">'
            f'<img class="emblem-leaves" src="/brand/stefanoff-logo-leaves.png" alt="" width="636" height="694"></span>')


def contact_icons(extra=""):
    """Chat and bag side by side in the nav below 1300 px (wide screens: the chat tab on the right edge, the bag in nav-right)."""
    return (f'<div class="nav-contact{(" " + extra) if extra else ""}"><button class="nav-chat" type="button" data-chat aria-controls="chat" aria-expanded="false" aria-label="Чат с нас">{ico("chat-circle-dots")}</button>'
            f'{bag_btn() if "nav-contact-m" in extra else ""}</div>')


def _inline(name):
    """Line drawings traced from the client's rosehip 3D scan (assets/rosehip3d): inlined so CSS can draw
    every stroke and fill. Returns the svg and the CSS variables that pin its stem base to an anchor point."""
    svg = (SRC / "brand" / f"{name}.svg").read_text()
    meta = json.loads((SRC / "brand" / f"{name}.json").read_text())
    svg = re.sub(r"<svg ", '<svg aria-hidden="true" focusable="false" ', svg, count=1)
    return svg, f"--bx:{meta['base_x_frac']};--by:{meta['base_y_frac']};--ar:{meta['aspect']}"


# corners: rosehip sprigs with leaves; edges: leaf sprays filling the space between them
_SPRIG, _SV = _inline("rosehip-drawing")
_SPRAY, _PV = _inline("leaf-spray")
SPRIGS = ("".join(f'<span class="sprig {c}" style="{_SV}">{_SPRIG}</span>' for c in ("tl", "tr", "bl", "br"))
          + "".join(f'<span class="sprig spray {c}" style="{_PV}">{_SPRAY}</span>' for c in ("et1", "et2", "eb1", "eb2")))
SVG_DEFS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
            '<radialGradient id="rh-hip" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#E5482F"/>'
            '<stop offset=".55" stop-color="#C02A1C"/><stop offset="1" stop-color="#7E1810"/></radialGradient>'
            # weathering for the era text: stronger the older the era
            '<filter id="wear-3" x="-5%" y="-20%" width="110%" height="140%"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3.2"/></filter>'
            '<filter id="wear-2" x="-5%" y="-20%" width="110%" height="140%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="1.6"/></filter>'
            '<filter id="wear-1" x="-5%" y="-20%" width="110%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="1.2" numOctaves="1" seed="11"/><feDisplacementMap in="SourceGraphic" scale=".7"/></filter>'
            '</defs></svg>')


def cur(k, key):
    return ' aria-current="page"' if k == key else ""


def layout(*, key, path, title, desc, body, hero=False, schema=None, og="/img/hero-poster.jpg", sticky=""):
    left = "".join(f'<a class="link" href="{h}"{cur(k, key)}>{t}</a>' for h, t, k in NAV_LEFT)
    right = "".join(f'<a class="link" href="{h}"{cur(k, key)}>{t}</a>' for h, t, k in NAV_RIGHT)
    menu = "".join(f'<a class="big" href="{h}"{cur(k, key)}>{t}</a>' for h, t, k in MENU)
    ld = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>' if schema else ""
    main_open = "<main id=\"main\">" if hero else '<main id="main" class="page-bg inner">'
    return f"""<!doctype html>
<html lang="bg" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{path}">
<link rel="alternate" hreflang="bg" href="{SITE}{path}" data-alt>
<link rel="alternate" hreflang="en" href="{SITE}/en{path}" data-alt>
<link rel="alternate" hreflang="x-default" href="{SITE}{path}" data-alt>
<meta property="og:type" content="website">
<meta property="og:locale" content="bg_BG">
<meta property="og:site_name" content="Стефанов НП">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}{og}">
<meta name="theme-color" content="#20124D">
<link rel="icon" type="image/png" href="/brand/favicon-64.png">
<link rel="apple-touch-icon" href="/brand/apple-touch-icon.png">
<script>document.documentElement.classList.replace("no-js","js");try{{if(sessionStorage.getItem("langSwitch"))document.documentElement.classList.add("lang-arriving")}}catch(e){{}}if(matchMedia("(prefers-reduced-motion: reduce)").matches)document.documentElement.classList.add("reduced");</script>
<link rel="stylesheet" href="/tokens.css?v={VER}">
<link rel="stylesheet" href="/site.css?v={VER}">
{era_fonts_link() if hero else ""}
{ld}
</head>
<body>
<a class="skip" href="#main">Към съдържанието</a>
{SVG_DEFS}
<div class="nav-peek" aria-hidden="true"></div>
<header class="nav{" is-home" if hero else " always"}" id="nav">
  <div class="nav-inner">
    <button class="nav-menu-btn" type="button" aria-expanded="false" aria-controls="menu">Меню</button>
    <div class="nav-side nav-left">{left}</div>
    <a class="nav-logo" href="/" aria-label="Стефанов НП, начало"><span class="logo-fly" id="logoFly">{emblem("", "Stefanoff")}</span></a>
    <div class="nav-side nav-right">{right}<span class="cta-grow" data-cta-grow>{SPRIGS}<a class="btn btn-primary nav-cta" href="/zapitvane.html">Поискайте оферта</a></span>{bag_btn()}</div>
    {contact_icons("nav-contact-m")}
  </div>
</header>
<nav class="menu" id="menu" aria-label="Мобилно меню">
  {menu}
  <div class="contact"><a href="{PHONE_HREF}">{PHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a></div>
  <div class="menu-lang" role="group" aria-label="Език"><a class="menu-lang-tab" href="{path}" data-lang="bg" hreflang="bg" lang="bg" aria-current="true">BG</a><a class="menu-lang-tab" href="/en{path}" data-lang="en" hreflang="en" lang="en">EN</a></div>
</nav>
<nav class="lang t-tabs" aria-label="Език" data-lang-switch><span class="t-tabs-pill" aria-hidden="true"></span><a class="t-tab" href="{path}" data-lang="bg" hreflang="bg" lang="bg" aria-current="true">BG</a><a class="t-tab" href="/en{path}" data-lang="en" hreflang="en" lang="en">EN</a></nav>
{main_open}
{body}
</main>
{footer()}
{sticky}
<button class="chat-tab" type="button" data-chat aria-controls="chat" aria-expanded="false"><span class="ico-wrap">{ico("chat-circle-dots")}</span><span class="chat-tab-label">Чат</span></button>
{chat_drawer()}
{bag_drawer()}
{shop_json()}
<script src="/vendor/lenis.min.js" defer></script>
<script src="/site.js?v={VER}" defer></script>
</body>
</html>
"""


def chat_drawer():
    """The drawer the header chat icon opens. Tidio docks into .chat-body (see site.js)."""
    return f"""<div class="chat-scrim" data-chat-close aria-hidden="true"></div>
<aside class="chat-drawer" id="chat" role="dialog" aria-labelledby="chat-h" inert>
  <div class="chat-top">
    <div class="chat-titles">
      <h2 id="chat-h" class="t-h3">Попитайте ни</h2>
      <p class="t-small">Отговаряме в работно време, понеделник – петък, 08:00 – 18:00. Спешно е? Обадете се на <a href="{PHONE_HREF}">{PHONE}</a>.</p>
    </div>
    <button class="chat-close" type="button" data-chat-close aria-label="Затворете чата">{ico("x")}</button>
  </div>
  <div class="chat-body">
    <p class="chat-wait" role="status"><span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>Зареждаме чата</p>
    <div class="chat-fail" role="alert" hidden>
      <p class="t-body">Чатът не се зареди. Възможно е да го спира разширение в браузъра. Свържете се с нас директно:</p>
      <dl class="contact-list">
        <div><dt class="t-small">Телефон</dt><dd><a href="{PHONE_HREF}">{PHONE}</a></dd></div>
        <div><dt class="t-small">Имейл</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
      </dl>
      <div><a class="btn btn-primary" href="/zapitvane.html">Поискайте оферта {ARROW}</a></div>
    </div>
  </div>
</aside>"""


def footer():
    prods = "".join(f'<li><a href="/produkti/{p["slug"]}.html">{p["name"]}</a></li>' for p in PRODUCTS)
    mini = "".join(f'<a href="{href}" aria-label="{t}" title="{t}">{ico(i)}</a>' for i, t, _, href in CREDS)
    return f"""<footer class="footer">
  <div class="wrap">
    <a class="footer-logo" href="/" aria-label="Стефанов НП, начало">{emblem("", "Stefanoff")}</a>
    <div class="footer-grid">
      <div>
        <p class="lbl">Адрес</p><p>с. Бозвелийско, общ. Провадия,<br>обл. Варна, България</p>
        <p class="lbl" style="margin-top:var(--s-6)">Контакт</p><p><a href="mailto:{EMAIL}">{EMAIL}</a><br><a href="{PHONE_HREF}">{PHONE}</a></p>
      </div>
      <div><p class="lbl">Работно време</p><p>Понеделник – петък<br>08:00 – 18:00</p></div>
      <div><p class="lbl">Продукти</p><ul>{prods}</ul></div>
      <div><p class="lbl">Компания</p><ul>
        <li><a href="/fermata.html">Фермата</a></li><li><a href="/sertifikati.html">Сертификати</a></li>
        <li><a href="/proekti.html">Проекти с ЕС</a></li><li><a href="/zapitvane.html">Запитване</a></li>
        <li><a href="https://facebook.com/stefanoff.bg" rel="noopener">Facebook</a></li></ul></div>
    </div>
    <div class="creds-mini">{mini}</div>
    <div class="legal"><span>© {YEAR} {tbc("Стефанов НП ООД")}</span><span><a href="/poveritelnost.html">Поверителност и условия</a></span></div>
  </div>
</footer>"""


# --------------------------------------------------------------------------- blocks
def creds():
    items = "".join(
        f'<a class="cred rv d{i % 3}" href="{href}"><span class="ring">{ico(icon)}</span><span class="t-label">{t}</span><span class="t-small">{s}</span></a>'
        for i, (icon, t, s, href) in enumerate(CREDS))
    return f'<div class="creds">{items}</div>'


# Equal columns out of 12 (wide, then below 900 px): every product gets the same weight.
# On scroll the columns drift as on restaurantsem.com (data-drift-row, site.js): stepped down to the
# right as the row enters, level when it is 60 % up the screen, stepped up to the right as it leaves.
SPANS = {3: ((4, 12),) * 3, 4: ((3, 6),) * 4, 5: (("2-4", 6),) * 5}

# Arrow inside the photo: transitions.dev "icon swap" (09). Resting state a = chevron, hover state b = arrow;
# the outgoing icon blurs and scales down while the incoming one sharpens in. data-state is set in site.js.
CARD_ARROW = ('<span class="card-go" aria-hidden="true"><span class="t-icon-swap" data-state="a">'
              '<span class="t-icon" data-icon="a"><svg viewBox="0 0 16 16" width="16" height="16"><path d="M6 3.5L10.5 8L6 12.5"/></svg></span>'
              '<span class="t-icon" data-icon="b"><svg viewBox="0 0 16 16" width="16" height="16"><path d="M2.5 8H13.5M9 3.5L13.5 8L9 12.5"/></svg></span>'
              '</span></span>')


def banners(items, subtext=True):
    """Photo row for black bands. items: (href, src, alt, width, height, title, text)."""
    cells = "".join(f"""<a class="banner rv d{i % 4}" href="{href}" style="--span:{s};--span-m:{m}">
  <span class="img img-rv"><img src="{src}" alt="{esc(alt)}" loading="lazy" width="{w}" height="{h}">{CARD_ARROW}</span>
  <span class="name t-sub">{title}</span>{f'<span class="t-small">{text}</span>' if subtext else ''}
</a>""" for i, ((href, src, alt, w, h, title, text), (s, m)) in enumerate(zip(items, SPANS[len(items)])))
    return f'<div class="wrap"><div class="banners" data-drift-row>{cells}</div></div>'


def product_banners(items, subtext=True):
    return banners([(f"/produkti/{p['slug']}.html", f"/img/{p['img']}", p["alt"], 1200, 800, p["name"], p["card"]) for p in items], subtext)


def faq_html(items):
    return "".join(f'<details class="rv"><summary>{q}{ico("plus")}</summary><div class="ans t-body"><p>{a}</p></div></details>' for q, a in items)


def cta():
    return f"""<section class="section" aria-labelledby="cta-h">
  <div class="wrap">
    <div class="cta">
      <div class="copy rv">
        <h2 id="cta-h" class="t-display">Кажете ни какво<br>ви <span class="accent">трябва</span></h2>
        <p class="t-body">Продукт, количество и държава на доставка. Ще върнем цена, спецификация и документи {tbc("до един работен ден")}. Без регистрация.</p>
        <div class="row-actions"><a class="btn btn-primary" href="/zapitvane.html">Поискайте оферта {ARROW}</a></div>
      </div>
      <div class="contact-lines rv d1">
        <a href="{PHONE_HREF}">{ico("phone")}{PHONE}</a>
        <a href="mailto:{EMAIL}">{ico("envelope-simple")}{EMAIL}</a>
        <button type="button" data-chat>{ico("chat-circle-dots")}Чат на сайта</button>
        <span>{ico("clock")}Понеделник – петък, 08:00 – 18:00</span>
        <span>{ico("map-pin")}с. Бозвелийско, област Варна</span>
      </div>
    </div>
  </div>
</section>"""


def figures(heading, note, items):
    """Numbers beside a looping field video. Label first in the DOM, number shown first."""
    rows = "".join(f'<div class="rv d{i % 2}"><dt class="t-body">{label}</dt><dd>{num}</dd></div>' for i, (num, label) in enumerate(items))
    return f"""<div class="figures">
  <div class="figures-media img-rv rv" data-video>
    <video muted loop playsinline preload="none" poster="/img/rose-leaves.jpg" aria-hidden="true"><source src="/video/rose-leaves.mp4" type="video/mp4"></video>
  </div>
  <div class="figures-copy">
    <div class="head rv"><h2 id="num-h" class="t-h2">{heading}</h2><p class="t-body">{note}</p></div>
    <dl class="tally">{rows}</dl>
  </div>
</div>"""


def docs():
    return f"""<div class="docs">
  <article class="doc panel rv" id="bio">
    <img src="/img/cert-organic.jpg" alt="Първа страница на био сертификата на Стефанов НП, издаден от Нутрамед" width="500" height="625" loading="lazy">
    <div class="body">
      <span class="status status-warn">{ico("clock")}{tbc("Актуален сертификат предстои")}</span>
      <h3 class="t-h3">Био сертификат</h3>
      <p class="t-body">Регламент (ЕС) 2018/848: производство, подготовка и разпространение на шипка и лавандула.</p>
      <dl>
        <dt>Номер</dt><dd>BG-BIO-22.100-0003115.2024.001</dd>
        <dt>Контролен орган</dt><dd>Нутрамед, BG-BIO-22</dd>
        <dt>Валидност</dt><dd>11.03.2024 – 29.12.2024</dd>
      </dl>
      <div class="actions">
        <a class="link-arrow" href="/docs/certificate-organic-production-eu-2018-848.pdf">{ico("file-pdf")}Изтегли PDF</a>
        <a class="link-arrow" href="{TRACES}" rel="noopener">Провери в TRACES {ico("arrow-up-right")}</a>
      </div>
    </div>
  </article>
  <article class="doc panel rv d1" id="analiz">
    <img src="/img/cert-lab.jpg" alt="Първа страница на протокол от анализ 24/000523 на лаборатория Приморис" width="500" height="625" loading="lazy">
    <div class="body">
      <span class="status status-ok">{ico("check-circle")}Няма открити остатъци</span>
      <h3 class="t-h3">Анализ за пестициди</h3>
      <p class="t-body">Многокомпонентен скрининг с газова и течна хроматография, по граници за био и детски храни.</p>
      <dl>
        <dt>Лаборатория</dt><dd>Приморис, Пловдив, EN ISO/IEC 17025</dd>
        <dt>Протокол</dt><dd>24/000523, 30.01.2024</dd>
        <dt>Проба</dt><dd>Био шипка</dd>
      </dl>
      <div class="actions"><a class="link-arrow" href="/docs/certificate-of-analysis-rosehip-24-000523.pdf">{ico("file-pdf")}Изтегли PDF</a></div>
    </div>
  </article>
</div>"""


# --------------------------------------------------------------------------- pages
def page_home():
    schema = {"@context": "https://schema.org", "@type": "Organization", "name": "Стефанов НП ООД", "url": SITE, "logo": f"{SITE}/brand/stefanoff-logo-colour.png",
              "email": EMAIL, "telephone": "+359888229537", "sameAs": ["https://facebook.com/stefanoff.bg"],
              "address": {"@type": "PostalAddress", "addressLocality": "с. Бозвелийско", "addressRegion": "Варна", "addressCountry": "BG"}}
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in FAQ]}
    body = f"""<section class="hero" aria-label="Стефанов НП" data-video>
  <video autoplay muted loop playsinline preload="metadata" poster="/img/hero-poster.jpg" aria-hidden="true"><source src="/video/hero.mp4" type="video/mp4"></video>
  <div class="hero-center">
  </div>
  <p class="hero-note">Булаир, Източна Стара планина<br>Шипка, бял трън и лавандула</p>
</section>

<div class="page-bg">
<section class="section" aria-labelledby="intro-h">
  <div class="wrap">
    <div class="intro">
      <div class="copy rv">
        <h1 id="intro-h" class="t-display">От земя с история.<br>С <span class="accent">грижа</span> за природата.</h1>
        <p class="t-sub">В подножието на Източна Стара планина, край село Булаир, историята и природата се срещат.</p>
        <p class="t-body">Недалеч от нашите насаждения се намират Хемските порти: древна отбранителна система, която столетия наред е охранявала пътищата през Балкана. Тук отглеждаме шипка и бял трън, а в област Варна и лавандула, с уважение към земята. За нас качеството започва от полето.</p>
        <div class="row-actions"><a class="btn btn-primary" href="/zapitvane.html">Поискайте оферта {ARROW}</a><a class="btn btn-secondary" href="#portite">Нашата история</a></div>
      </div>
      <div class="portrait img-rv rv d1"><img src="/img/rosehip-fresh.jpg" alt="Свежи червени шипки след прибиране" width="1200" height="800"></div>
    </div>
    {creds()}
  </div>
</section>

<section class="statement" aria-label="Нашият подход">
  <div class="wrap"><p class="t-statement" data-letters>Земя, която векове е <span class="acc">пазила проходите</span> през Балкана, днес е дом на нашите насаждения.</p></div>
</section>

<section class="story eras" id="portite" aria-labelledby="gates-h" data-eras style="--n:{len(ERAS)}">
  <div class="eras-stick">
    <div class="wrap eras-wrap">
      <header class="eras-top">
        <h2 id="gates-h" class="eras-h">Стражът на Източна Стара планина <span>Гермето, между Булаир и Голица</span></h2>
      </header>
      <div class="eras-grid">
        <div class="eras-pics">{"".join(f'<figure class="era-pic" data-era="{i}"><img src="/img/eras/{x["img"]}" alt="{esc(x["alt"])}" width="1000" height="1250" loading="lazy"><figcaption>{x["credit"]}</figcaption></figure>' for i, x in enumerate(ERAS))}</div>
        <div class="eras-stage">{"".join(f'<article class="era era-{x["key"]}" data-era="{i}"><p class="era-year">{x["year"]}</p><h3 class="era-title">{x["title"]}</h3><p class="era-text">{x["text"]}</p></article>' for i, x in enumerate(ERAS))}</div>
        <ol class="eras-rail" aria-label="Епохи">{"".join(f'<li><button type="button" data-go="{i}"><span class="dot" aria-hidden="true"></span>{x["rail"]}</button></li>' for i, x in enumerate(ERAS))}</ol>
      </div>
    </div>
  </div>
</section>


<section class="grow" data-grow aria-label="Булаир днес">
  <div class="sticky"><div class="frame"><img src="/img/rosehip-branch.jpg" alt="Зряла шипка на клон през есента" loading="lazy" width="2400" height="1800">
    <p class="caption t-h3">Днес тази земя е дом на нашите насаждения от шипка и бял трън.</p></div></div>
</section>

<section class="story tour" id="natura" aria-labelledby="nature-h" data-tour>
  <div class="tour-stick">
    <div class="tour-media"><img src="/img/natura/kamchiyska-fields.jpg" srcset="/img/natura/kamchiyska-fields-1200.jpg 1200w, /img/natura/kamchiyska-fields.jpg 2356w" sizes="100vw" alt="Поле и цъфнали храсти пред горите на Камчийска планина, община Долни чифлик" width="2356" height="1325" loading="lazy" decoding="async"></div>
    <div class="tour-shade" aria-hidden="true"></div>
    {(SRC / "brand" / "natura-tour.svg").read_text()}
    <div class="wrap tour-ui">
      <header class="tour-title">
        <h2 id="nature-h"><span class="l1">Булаир:</span> <span class="l2">две зони от „Натура 2000“</span></h2>
        <p class="tour-meta"><span>42°53′ с. ш., 27°27′ и. д.</span><span>Източна Стара планина</span></p>
      </header>
      <div class="tour-copy">
        <p class="tour-p tour-pa">Булаир е село в Източна Стара планина, югозападно от Варна. Тук нивите граничат с широколистни гори, тревни съобщества и храсталаци.</p>
        <p class="tour-p tour-pb">Землището на Булаир попада в две защитени зони от европейската мрежа „Натура 2000“: BG0000133 „Камчийска и Еменска планина“ за местообитанията и BG0002044 „Камчийска планина“ за дивите птици. В по-широкия Камчийски район е и третата, BG0002045 „Комплекс Камчия“.</p>
      </div>
      <p class="tour-credit">Снимка: поле край Венелин, община Долни чифлик. Webchillie, CC BY-SA 4.0. Граници: ЕАОС „Натура 2000“, Natural Earth. Река: © OpenStreetMap.</p>
    </div>
  </div>
</section>
<div class="band nmap-after"><div class="wrap"><p class="note-honest rv">{ico("leaf")}„Натура 2000“ е природозащитен статут на територията, а не сертификат за продукта. Био производството е отделна система с правила, контрол и сертификация.</p></div></div>

<section class="section band story" aria-labelledby="pillars-h">
  <div class="wrap">
    <div class="band-head">
      <div class="rv"><h2 id="pillars-h" class="t-h2">Качеството започва<br>от <span class="accent">полето</span></h2></div>
      <div class="rv d1"><p class="t-body">Съседството с природни местообитания подпомага опрашителите при цъфтежа на шипката. Пазим почвата и ограничаваме ненужните химични въздействия. Не препродаваме, затова знаем произхода на всяка партида.</p></div>
    </div>
  </div>
  {banners([
      ("/fermata.html", "/img/rose-bush.jpg", "Шипков храст с листа и неразпукнати пъпки", 1200, 1800, '<span class="accent">Собствени</span> насаждения', "Шипка и бял трън в Булаир и Климентово, лавандула с капково напояване във Венчан."),
      ("/produkti/shipka-sushena.html", "/img/rosehip-fresh.jpg", "Свежи червени шипки след прибиране", 1200, 800, '<span class="accent">Бавно</span> сушене', "При ниска температура, за да се запазят цветът, вкусът и съставът."),
      ("/produkti/maslo-ot-shipka.html", "/img/oil-scoop.jpg", "Масло от шипка и сушени шипки", 1200, 800, '<span class="accent">Студено</span> пресоване', "Маслото от семките се извлича само с налягане, в нашата база."),
  ])}
</section>

<section class="section tight band story" aria-labelledby="prod-h">
  <div class="wrap">
    <div class="band-head">
      <div class="rv"><h2 id="prod-h" class="t-h2">Шипка, бял трън<br>и лавандула, на едро</h2></div>
      <div class="rv d1"><p class="t-body">Пет продукта от собствена суровина. Всеки има спецификация, а с офертата изпращаме сертификат и анализ от последната реколта.</p><div class="row-actions"><a class="btn btn-primary" href="/produkti.html">Всички продукти {ARROW}</a></div></div>
    </div>
  </div>
  <div class="wrap"><div class="tiles tiles-3 tiles-snap" data-drift-row>{"".join(product_tile(BY_SLUG[s], i) for i, s in enumerate(FEATURED))}</div>
    <div class="tiles-more rv"><a class="btn btn-secondary" href="/produkti.html">Всички продукти <span class="count">{len(PRODUCTS)}</span> {ARROW}</a></div></div>
</section>

<section class="section tight" aria-labelledby="how-h">
  <div class="wrap">
    <div class="head rv"><h2 id="how-h" class="t-h2">Как да поръчате</h2></div>
    <div class="steps">
      <div class="step rv">{ico("envelope-simple")}<span class="t-sub">Изпратете запитване</span><p class="t-body">Продукт, количество и държава на доставка. Около две минути.</p></div>
      <div class="step rv d1">{ico("file-pdf")}<span class="t-sub">Получете оферта и документи</span><p class="t-body">Цена, спецификация, био сертификат и анализ от последната реколта.</p></div>
      <div class="step rv d2">{ico("check-circle")}<span class="t-sub">Мостра и доставка</span><p class="t-body">При нужда изпращаме {tbc("мостра")}. След потвърждение уточняваме опаковка и транспорт.</p></div>
    </div>
  </div>
</section>

<section class="section tight" aria-labelledby="faq-h">
  <div class="wrap">
    <div class="split">
      <div class="head rv"><h2 id="faq-h" class="t-h2">Често задавани<br>въпроси</h2><p class="t-body">Не намирате отговор? Обадете се на <a href="{PHONE_HREF}">{PHONE}</a> или пишете на <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div>
      <div class="faq">{faq_html(FAQ)}</div>
    </div>
  </div>
</section>
{cta()}
</div>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>"""
    return layout(key="home", path="/", hero=True, schema=schema, body=body,
                  title="Стефанов НП | Шипка, бял трън и лавандула от Булаир и област Варна",
                  desc="От земя с история, с грижа за природата. Шипка, бял трън и лавандула от Булаир, край Хемските порти, и от област Варна. На едро, със спецификация. Поискайте оферта.")


def page_products_wip():
    links = "".join(f'<li><a href="/produkti/{p["slug"]}.html"><span>{p["name"]}</span>{ico("arrow-right")}</a></li>' for p in PRODUCTS)
    body = f"""<section class="section tight"><div class="wrap">
  <div class="page-head wip rv">
    <p class="t-micro eyebrow wip-tag"><span class="wip-dot" aria-hidden="true"></span>В процес на разработка</p>
    <h1 class="t-display">Продукти</h1>
    <p class="t-body">Работим по тази страница. Дотогава можете да разгледате продуктите поотделно или да ни изпратите запитване.</p>
  </div>
  <ul class="wip-list rv d1">{links}</ul>
  <div class="row-actions rv d2"><a class="btn btn-primary" href="/zapitvane.html">Поискайте оферта {ARROW}</a><a class="btn btn-secondary" href="/">Към началото</a></div>
</div></section>"""
    return layout(key="produkti", path="/produkti.html", body=body, title="Продукти (в процес на разработка) | Стефанов НП",
                  desc="Био сушена шипка, шипка на прах, студено пресовано масло от шипкови семки, сушен лавандулов цвят и бял трън на едро.")


def page_products():
    if PRODUCTS_WIP:
        return page_products_wip()
    trust = "".join(f'<li>{ico(i)}<span>{t}</span></li>' for i, t in [("test-tube", tbc("Мостра при запитване")), ("files", "Спецификация и документи с всяка оферта"), ("clock", tbc("Отговор до един работен ден"))])
    tabs = "".join(f'<a class="t-tab" href="#{k}" data-chapter-tab="{k}">{n}</a>' for k, n, *_ in CATS)
    chapters = []
    for k, name, intro, mood, mood_alt in CATS:
        items = [p for p in PRODUCTS if SHOP[p["slug"]]["cat"] == k]
        n = len(items)
        count = f"{n} продукта" if n > 1 else "1 продукт"
        head = f'<header class="chapter-head"><h2 id="{k}-h" class="chapter-title rv">{name}</h2><div class="chapter-intro rv d1"><p class="t-body">{intro}</p><span class="t-micro chapter-count">{count}</span></div></header>'
        if n > 1:
            band = f'<div class="chapter-mood img-rv"><img src="/img/{mood}" alt="{esc(mood_alt)}" loading="lazy" width="1600" height="900"></div>' if mood else ""
            grid = f'<div class="tiles tiles-{min(n, 3)}">{"".join(product_tile(p, i) for i, p in enumerate(items))}</div>'
            chapters.append(f'<section class="shop-chapter" id="{k}" aria-labelledby="{k}-h">{head}{band}{grid}</section>')
        else:
            p = items[0]
            m = PRODUCT_MORE[p["slug"]]
            facts = "".join(f'<div class="fact"><dt>{lbl}</dt><dd>{val}</dd></div>' for val, lbl in m["facts"])
            solo = f"""<div class="chapter-solo">{product_tile(p, 0, "tile-lg")}
  <div class="solo-copy rv d1"><p class="t-sub">{p["short"]}</p><p class="t-body">{p["card"]}</p><dl class="facts facts-2">{facts}</dl>
    <a class="link-arrow" href="/produkti/{p["slug"]}.html">Вижте продукта {ico("arrow-right")}</a></div></div>"""
            chapters.append(f'<section class="shop-chapter" id="{k}" aria-labelledby="{k}-h">{head}{solo}</section>')
    body = f"""<section class="section tight"><div class="wrap">
  <div class="page-head rv"><h1 class="t-display">Продукти</h1><p class="t-body">Сушена шипка, шипка на прах, масло от шипкови семки, лавандулов цвят и бял трън. От собствена суровина, на едро. Добавете каквото ви трябва и изпратете всичко като едно запитване.</p></div>
  <ul class="trust rv d1">{trust}</ul>
</div></section>
<div class="shop" data-shop>
  <div class="wrap">{"".join(chapters)}
    <section class="shop-missing rv" aria-labelledby="miss-h"><h2 id="miss-h" class="t-h3">Не намирате нужното?</h2><p class="t-body">Друга форма, фракция, опаковка или по-голямо количество: пишете ни и ще проверим.</p><a class="btn btn-secondary" href="/zapitvane.html">Попитайте ни {ARROW}</a></section>
  </div>
  <div class="shop-bar"><nav class="t-tabs shop-tabs" aria-label="Категории" data-chapter-bar><span class="t-tabs-pill" aria-hidden="true"></span>{tabs}</nav></div>
</div>
{cta()}"""
    return layout(key="produkti", path="/produkti.html", body=body, title="Продукти | Стефанов НП",
                  desc="Био сушена шипка, шипка на прах, студено пресовано масло от шипкови семки, сушен лавандулов цвят и бял трън на едро.")

# --------------------------------------------------------------------------- product detail, beyond the spec table
# Only facts the client has stated (old site, certificate, projects); anything unconfirmed goes through tbc().
MONTHS = ["Яну", "Фев", "Мар", "Апр", "Май", "Юни", "Юли", "Авг", "Сеп", "Окт", "Ное", "Дек"]
_ROSEHIP_SEASON = [("Цъфтеж", 5, 7, False), ("Бране", 9, 10, False), ("Наличност", 1, 12, False)]
_DOCS_ROSEHIP = [("Спецификация на партидата", False), ("Био сертификат, ЕС 2018/848", True), ("Анализ за остатъци от пестициди", False), ("Сертификат за транзакция, при поискване", False)]
PRODUCT_MORE = {
    "shipka-sushena": {
        "facts": [("Rosa canina L.", "Ботаническо име"), ("Био", "ЕС 2018/848"), ("Сеп – окт", "Бране"), ("Бозвелийско", "Сушене и пакетиране")],
        "season": _ROSEHIP_SEASON,
        "process": [("hand-grabbing", "Бране", "В пълна зрялост, докато плодът е още твърд."),
                    ("thermometer-simple", "Бавно сушене", "При ниска температура, в нашата база в Бозвелийско."),
                    ("scissors", "Цял плод или люспи", "Според заявката: цял сушен плод или нарязани люспи."),
                    ("package", "Опаковане", tbc("В транспортна опаковка, по заявка."))],
        "docs": _DOCS_ROSEHIP,
    },
    "shipka-na-prah": {
        "facts": [("100% шипка", "Без добавки"), ("Био", "ЕС 2018/848"), ("Сеп – окт", "Бране"), ("Цял плод", "Смлян със семките")],
        "season": _ROSEHIP_SEASON,
        "process": [("hand-grabbing", "Бране", "В пълна зрялост, докато плодът е още твърд."),
                    ("thermometer-simple", "Бавно сушене", "Дълго и при ниска температура, вместо бързо и горещо."),
                    ("factory", "Смилане", "Целият плод, със семките, на фин прах."),
                    ("package", "Опаковане", tbc("Фракция и опаковка по заявка."))],
        "docs": _DOCS_ROSEHIP,
    },
    "maslo-ot-shipka": {
        "facts": [("Rosa Canina Seed Oil", "INCI"), ("Студено", "Пресоване"), ("Винтова преса", "В собствена база"), (tbc("По запитване"), "Рафинирано")],
        "season": [("Бране на плода", 9, 10, False), ("Наличност", 1, 12, True)],
        "process": [("hand-grabbing", "Бране", "Плодовете от нашите насаждения, в пълна зрялост."),
                    ("drop", "Семките", tbc("Семките се отделят при преработката на плода.")),
                    ("factory", "Студено пресоване", "С винтова преса, само с налягане, без добавена топлина."),
                    ("package", "Опаковане", tbc("По заявка."))],
        "docs": [("Спецификация на партидата", False), ("Био статус на маслото", True), ("Анализ на мастните киселини", True), ("Информационен лист за безопасност", True)],
    },
    "lavandula": {
        "facts": [(tbc("L. angustifolia"), "Вид"), ("Био", "ЕС 2018/848"), (tbc("Юни – юли"), "Прибиране"), ("Венчан", "Капково напояване")],
        "season": [("Цъфтеж и прибиране", 6, 7, True), ("Наличност", 1, 12, True)],
        "process": [("flower", "Прибиране", "При цъфтеж, от насажденията с капково напояване във Венчан."),
                    ("sun", "Естествено сушене", "Пъпките и стъблата запазват етеричното си масло и аромат."),
                    ("snowflake", "Хладилно съхранение", "Технология за охлаждане и съхранение на етеричномаслени култури."),
                    ("package", "Опаковане", "Насипно, запечатано в транспортна опаковка.")],
        "docs": [("Спецификация на партидата", False), ("Био сертификат, ЕС 2018/848", True), ("Анализ за остатъци от пестициди", True), ("Сертификат за транзакция, при поискване", False)],
    },
    "bial-trun": {
        "facts": [("Crataegus monogyna", "Ботаническо име"), (tbc("Предстои"), "Био статус"), (tbc("Май; сеп – окт"), "Цвят; плод"), ("Булаир", "Източна Стара планина")],
        "season": [("Цвят", 5, 5, True), ("Плод", 9, 10, True)],
        "process": [("flower", "Бране на цвета", tbc("През май, цвят с листа.")),
                    ("hand-grabbing", "Бране на плода", tbc("През септември и октомври.")),
                    ("thermometer-simple", "Сушене", tbc("В нашата база в Бозвелийско.")),
                    ("package", "Опаковане", tbc("По заявка."))],
        "docs": [("Спецификация на партидата", True), ("Био статус", True), ("Сертификат за транзакция, при поискване", True)],
    },
}
TERMS = [("truck", "Доставка", tbc("В рамките на ЕС, условията се договарят в офертата.")),
         ("package", "Опаковка и количество", tbc("По заявка. Минимумите се уточняват.")),
         ("test-tube", "Мостра", tbc("Изпращаме мостра след запитване с продукт, форма и количество.")),
         ("clock", "Отговор", tbc("До един работен ден, с цена, спецификация и документи."))]


# --------------------------------------------------------------------------- store: quote cart, example prices
# Everything here is a placeholder until the client confirms it: prices (EUR, VAT excluded), forms and pack sizes.
# The bag (site.js) reads the same data from the JSON block every page carries, so names follow the page language.
AUTO_EN = {}   # generated strings (prices, pack sizes) and their English, merged into the translation table at build time
_U_EN = {"кг": "kg", "л": "l"}


def money(v, lang="bg"):
    s = f"{v:,.2f}"
    return s.replace(",", " ").replace(".", ",") + " €" if lang == "bg" else "€" + s


def price_txt(v, unit, frm=False):
    bg = f"{'от ' if frm else ''}{money(v)} / {unit}"
    AUTO_EN[bg] = f"{'from ' if frm else ''}{money(v, 'en')} / {_U_EN[unit]}"
    return bg


def per_txt(unit):
    AUTO_EN[f"/ {unit}"] = f"/ {_U_EN[unit]}"
    return f"/ {unit}"


def qty_txt(n, unit, plus=False, upto=None):
    bg = f"{n}{'+' if plus else ''}{f' – {upto}' if upto else ''} {unit}"
    AUTO_EN[bg] = f"{n}{'+' if plus else ''}{f' – {upto}' if upto else ''} {_U_EN[unit]}"
    return bg


CATS = [("shipka", "Шипка", "Rosa canina от собствени био насаждения. Сушим бавно, мелим и пресоваме в нашата база в Бозвелийско.", "rosehip-sky.jpg", "Клонка шипка с червени плодове на фона на небето"),
        ("lavandula", "Лавандула", "Лавандулов цвят от насажденията с капково напояване във Венчан, сушен по естествен път.", "", ""),
        ("bial-trun", "Бял трън", "Плод и цвят от района на Булаир, в подножието на Източна Стара планина. Био статусът предстои.", "", "")]
# packs: (size in the product unit); "def": the pack chosen by quick add; tiers: (from quantity, example price per unit)
SHOP = {
    "shipka-sushena": {"cat": "shipka", "badge": "Нова реколта", "forms": ["Цял плод", "Люспи"], "unit": "кг", "packs": [1, 5, 25, 500], "def": 2, "tiers": [(1, 14.0), (25, 11.5), (500, 8.9)]},
    "shipka-na-prah": {"cat": "shipka", "badge": "Био", "forms": ["Фин прах"], "unit": "кг", "packs": [1, 5, 25, 500], "def": 2, "tiers": [(1, 18.0), (25, 15.2), (500, 12.4)]},
    "maslo-ot-shipka": {"cat": "shipka", "badge": "Студено пресовано", "forms": ["Нерафинирано", "Рафинирано"], "unit": "л", "packs": [1, 5, 25, 200], "def": 1, "tiers": [(1, 64.0), (25, 55.0), (200, 48.0)]},
    "lavandula": {"cat": "lavandula", "badge": "Био", "forms": ["Със стъбла", "Пъпки"], "unit": "кг", "packs": [1, 5, 25, 250], "def": 2, "tiers": [(1, 16.0), (25, 13.4), (250, 10.8)]},
    "bial-trun": {"cat": "bial-trun", "badge": "Скоро", "forms": ["Цвят", "Плод"], "unit": "кг", "packs": [1, 5, 25, 250], "def": 2, "tiers": [(1, 15.0), (25, 12.6), (250, 10.2)]},
}
FEATURED = ["shipka-sushena", "maslo-ot-shipka", "lavandula"]
PRODUCTS_WIP = True   # products listing unfinished: /produkti shows a work-in-progress page (set False to restore the store)
BY_SLUG = {p["slug"]: p for p in PRODUCTS}


def tier_rows(s):
    t, u = s["tiers"], s["unit"]
    return [(qty_txt(a, u, upto=t[i + 1][0] - 1) if i + 1 < len(t) else qty_txt(a, u, plus=True), price_txt(v, u)) for i, (a, v) in enumerate(t)]


def shop_json():
    data = {"cur": "EUR", "products": {slug: {"name": BY_SLUG[slug]["name"], "img": BY_SLUG[slug]["img"], "unit": s["unit"],
            "forms": s["forms"], "packs": s["packs"], "packLabels": [qty_txt(n, s["unit"]) for n in s["packs"]], "def": s["def"],
            "tiers": s["tiers"]} for slug, s in SHOP.items()}}
    return f'<script type="application/json" id="shop-data">{json.dumps(data, ensure_ascii=False)}</script>'


def product_tile(p, i=0, cls=""):
    s = SHOP[p["slug"]]
    href = f"/produkti/{p['slug']}.html"
    forms = '<span class="sep">, </span>'.join(f"<span>{f}</span>" for f in s["forms"])
    return f"""<article class="tile rv d{i % 4}{(' ' + cls) if cls else ''}">
  <div class="tile-frame">
  <a class="tile-media img-rv" href="{href}" tabindex="-1" aria-hidden="true">
    <img src="/img/{p['img']}" alt="" loading="lazy" width="1200" height="800">
    <span class="tile-badge">{s['badge']}</span>
    <span class="tile-view"><span>Вижте продукта</span>{ico("arrow-right")}</span>
  </a>
  <button class="tile-add" type="button" data-add="{p['slug']}" aria-label="Добавете към запитването: {esc(p['name'])}"><span class="t-icon-swap" data-state="a"><span class="t-icon" data-icon="a">{ico("plus")}</span><span class="t-icon" data-icon="b">{ico("check")}</span></span></button>
  </div>
  <div class="tile-meta"><h3 class="tile-name"><a href="{href}">{p['name']}</a></h3><p class="tile-price">{tbc(price_txt(s['tiers'][-1][1], s['unit'], frm=True))}</p></div>
  <p class="tile-forms">{forms}</p>
</article>"""


def bag_btn():
    return f'<button class="nav-bag" type="button" data-bag-open aria-controls="bag" aria-expanded="false" aria-label="Запитване: продукти">{ico("shopping-bag")}<span class="t-badge bag-badge" data-open="false" aria-hidden="true"><span class="t-badge-dot" data-bag-count>0</span></span></button>'


def bag_drawer():
    return f"""<div class="bag-scrim" data-bag-close aria-hidden="true"></div>
<aside class="bag-drawer" id="bag" role="dialog" aria-modal="true" aria-labelledby="bag-h" inert>
  <div class="bag-top">
    <div><h2 id="bag-h" class="t-h3">Запитване</h2><p class="t-small muted">Добавете продукти и ги изпратете като едно запитване. Без плащане.</p></div>
    <button class="chat-close" type="button" data-bag-close aria-label="Затворете">{ico("x")}</button>
  </div>
  <ul class="bag-lines" data-bag-lines></ul>
  <div class="bag-empty" data-bag-empty>
    <span class="bag-empty-ico">{ico("shopping-bag")}</span>
    <p class="t-body">Още нищо не сте добавили.</p>
    <a class="btn btn-secondary" href="/produkti.html">Разгледайте продуктите {ARROW}</a>
  </div>
  <div class="bag-foot" data-bag-foot hidden>
    <div class="bag-total"><span>Ориентировъчно, без ДДС</span><strong data-bag-total></strong></div>
    <p class="t-small muted">{tbc("Цените са примерни.")} Точната цена, спецификация и документи изпращаме в офертата.</p>
    <a class="btn btn-primary" href="/zapitvane.html">Изпратете запитването {ARROW}</a>
  </div>
</aside>
<div class="toast t-toast" role="status" aria-live="polite" data-toast><span class="toast-ico">{ico("check")}</span><span class="toast-msg" data-toast-msg></span><button class="link-btn" type="button" data-bag-open>Вижте</button></div>"""


def season_html(rows):
    head = "".join(f'<span class="m"><span class="ml">{m}</span><span class="ms">{m[0]}</span></span>' for m in MONTHS)
    body = "".join(
        f'<div class="cal-row"><span class="cal-lbl">{lbl}{" " + tbc("*") if unsure else ""}</span>'
        f'<span class="cal-track" style="--a:{a};--b:{b_}"><span class="cal-bar"></span></span></div>'
        for lbl, a, b_, unsure in rows)
    return f'<div class="cal" role="img" aria-label="{esc(", ".join(f"{l}: {MONTHS[a-1]}" + (f" – {MONTHS[b_-1]}" if b_ != a else "") for l, a, b_, _ in rows))}"><div class="cal-row cal-head"><span></span><span class="cal-months">{head}</span></div>{body}</div>'


def product_more(p):
    m = PRODUCT_MORE[p["slug"]]
    facts = "".join(f'<div class="fact"><dt>{lbl}</dt><dd>{val}</dd></div>' for val, lbl in m["facts"])
    steps = "".join(f'<li class="pstep rv d{i % 4}"><span class="pstep-ico">{ico(ic)}</span><h3 class="t-sub">{t}</h3><p class="t-small">{d}</p></li>' for i, (ic, t, d) in enumerate(m["process"]))
    terms = "".join(f'<div class="term">{ico(ic)}<dt>{t}</dt><dd>{d}</dd></div>' for ic, t, d in TERMS)
    return f"""<section class="section band pmore" aria-labelledby="proc-h">
  <div class="wrap">
    <div class="band-head"><div class="rv"><h2 id="proc-h" class="t-h2">От полето<br>до <span class="accent">доставката</span></h2></div>
      <div class="rv d1"><p class="t-body">Отглеждаме, берем и преработваме сами, затова знаем произхода на всяка партида.</p></div></div>
    <dl class="facts rv">{facts}</dl>
    <ol class="psteps">{steps}</ol>
    <div class="pgrid">
      <section class="panel rv" aria-labelledby="season-h"><p class="t-micro eyebrow">{ico("calendar-blank")}Сезон</p><h3 id="season-h" class="t-h3">Кога е реколтата</h3>{season_html(m["season"])}<p class="t-small muted">Сушените продукти предлагаме през цялата година до изчерпване на реколтата.</p></section>
      <section class="panel rv d1" aria-labelledby="terms-h"><p class="t-micro eyebrow">{ico("truck")}Условия</p><h3 id="terms-h" class="t-h3">Търговски условия</h3><dl class="terms-list">{terms}</dl></section>
    </div>
  </div>
</section>"""



def page_product(p):
    s = SHOP[p["slug"]]
    m = PRODUCT_MORE[p["slug"]]
    cat = next(n for k, n, *_ in CATS if k == s["cat"])
    rows = "".join(f"<tr><th scope=\"row\">{k}</th><td>{v}</td></tr>" for k, v in p["spec"])
    more = product_more(p)
    uses = "".join(f"<li>{ico(i.removeprefix('ph-'))}{t}</li>" for i, t in p["uses"])
    docs = "".join(f'<li>{ico("check")}<span>{tbc(t) if unsure else t}</span></li>' for t, unsure in m["docs"])
    about = "".join(f'<h3 class="t-label">{q}</h3><p>{a}</p>' for q, a in p["about"])
    others = [o for o in PRODUCTS if o["slug"] != p["slug"]]
    u = s["unit"]
    best = s["tiers"][0][1]
    tiers = "".join(f'<li data-tier="{i}"><span>{q}</span><span>{v}</span></li>' for i, (q, v) in enumerate(tier_rows(s)))
    forms = "".join(f'<label class="pill"><input type="radio" name="form" value="{i}"{" checked" if i == 0 else ""}><span>{f}</span></label>' for i, f in enumerate(s["forms"]))
    packs = "".join(f'<label class="pill"><input type="radio" name="pack" value="{i}"{" checked" if i == s["def"] else ""}><span>{qty_txt(n, u)}</span></label>' for i, n in enumerate(s["packs"]))
    organic = "Био статус предстои" if p["slug"] == "bial-trun" else "Био, Регламент (ЕС) 2018/848"
    shots = [("Отблизо", "Снимка предстои"), ("Опаковка", "Снимка предстои"), ("На полето", "Снимка предстои")]
    thumbs = (f'<button class="thumb is-on" type="button" data-shot="0" aria-label="Снимка 1" aria-pressed="true"><img src="/img/{p["img"]}" alt="" width="1200" height="800"></button>'
              + "".join(f'<button class="thumb thumb-ph" type="button" data-shot="{i + 1}" aria-label="{t}: {ph}" aria-pressed="false"><span>{t}</span></button>' for i, (t, ph) in enumerate(shots)))
    slides = (f'<figure class="shot is-on" data-shot="0"><img src="/img/{p["img"]}" alt="{esc(p["alt"])}" width="1200" height="800"></figure>'
              + "".join(f'<figure class="shot shot-ph" data-shot="{i + 1}"><img src="/img/mark-line-white.png" alt="" width="400" height="400"><figcaption><span class="t-label">{t}</span><span class="t-small">{ph}</span></figcaption></figure>' for i, (t, ph) in enumerate(shots)))
    schema = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "description": strip(p["lead"]),
              "image": f"{SITE}/img/{p['img']}", "brand": {"@type": "Brand", "name": "Стефанов НП"}, "countryOfOrigin": "BG"}
    sticky = f'''<div class="sticky-buy is-hidden" data-sticky-buy><span class="sb-price"><strong data-unit-price>{money(best)}</strong> {per_txt(u)}</span><button class="btn btn-primary" type="button" data-buy-proxy>Добавете {ico("plus")}</button></div>'''
    body = f"""<section class="section tight"><div class="wrap">
  <div class="pdp pdp-shop" data-pdp="{p['slug']}">
    <div class="gallery rv">
      <div class="shots">{slides}</div>
      <div class="thumbs" role="group" aria-label="Снимки">{thumbs}</div>
    </div>
    <div class="buy">
      <p class="t-micro eyebrow rv"><a href="/produkti.html#{s['cat']}">{cat}</a><span class="sep">, </span><span>{s['badge']}</span></p>
      <h1 class="t-h2 buy-title rv d1">{p['name']}</h1>
      <p class="t-body buy-short rv d1">{p['short']}</p>
      <div class="price rv d1">
        <p class="price-main"><span class="price-num t-digit-group" data-unit-price>{money(best)}</span> <span class="price-unit">{per_txt(u)}</span></p>
        <p class="price-pack t-small" data-pack-total></p>
        <ul class="tiers" aria-label="Цена според количеството">{tiers}</ul>
        <p class="t-micro price-note">{tbc("Примерни цени, без ДДС.")} Точната цена е в офертата.</p>
      </div>
      <form class="buy-form rv d2" data-buy="{p['slug']}">
        <fieldset class="pills"><legend class="t-small">Форма</legend><div class="pill-row">{forms}</div></fieldset>
        <fieldset class="pills"><legend class="t-small">Опаковка</legend><div class="pill-row">{packs}</div></fieldset>
        <div class="buy-row">
          <div class="stepper" role="group" aria-label="Брой опаковки"><button type="button" data-step="-1" aria-label="По-малко">{ico("minus")}</button><input name="qty" type="text" inputmode="numeric" value="1" aria-label="Брой опаковки"><button type="button" data-step="1" aria-label="Повече">{ico("plus")}</button></div>
          <button class="btn btn-primary buy-add" type="submit"><span class="t-icon-swap" data-state="a"><span class="t-icon" data-icon="a">{ico("plus")}</span><span class="t-icon" data-icon="b">{ico("check")}</span></span><span class="btn-label" data-label-add>Добавете към запитването</span><span class="btn-label" data-label-done hidden>Добавено</span></button>
        </div>
        <a class="btn btn-secondary buy-sample" href="/zapitvane.html?product={p['slug']}&amp;mostra=1">Поискайте мостра</a>
      </form>
      <ul class="buy-meta rv d2">
        <li>{ico("seal-check")}<span>{tbc(organic) if p["slug"] == "bial-trun" else organic}</span></li>
        <li>{ico("truck")}<span>{tbc("Доставка в ЕС, условията се договарят в офертата")}</span></li>
        <li>{ico("files")}<span>Спецификация и документи с офертата</span></li>
      </ul>
      <div class="faq buy-acc">
        <details open><summary>Описание{ico("plus")}</summary><div class="ans t-body"><p>{p['lead']}</p></div></details>
        <details><summary>Спецификация{ico("plus")}</summary><div class="ans"><table class="spec">{rows}</table><p class="t-small muted" style="margin-top:var(--s-4)">Пълна спецификация на партидата изпращаме с офертата.</p></div></details>
        <details><summary>Приложения{ico("plus")}</summary><div class="ans"><ul class="uses">{uses}</ul></div></details>
        <details><summary>Документи{ico("plus")}</summary><div class="ans"><ul class="docs-list">{docs}</ul><a class="link-arrow" href="/sertifikati.html">Сертификати и анализи {ico("arrow-right")}</a></div></details>
        <details><summary>За суровината{ico("plus")}</summary><div class="ans t-body about">{about}</div></details>
      </div>
    </div>
  </div>
</div></section>
{more}
<section class="section band" aria-labelledby="more-h">
  <div class="wrap"><div class="head rv"><h2 id="more-h" class="t-h2">Други продукти</h2></div>
    <div class="tiles tiles-4">{"".join(product_tile(o, i) for i, o in enumerate(others))}</div></div>
</section>{cta()}"""
    return layout(key="produkti", path=f"/produkti/{p['slug']}.html", body=body, schema=schema, og=f"/img/{p['img']}", sticky=sticky,
                  title=f"{p['name']} на едро, био | Стефанов НП", desc=strip(p["lead"])[:155])


def page_farm():
    eu = "".join(f"""<a class="rv" href="/proekti.html#{p['id']}"><span class="code">{p['code']}</span><span class="t-sub">{p['short']}</span><span class="amt">{p['amount_short']}</span>{ico('arrow-right')}</a>""" for p in PROJECTS)
    body = f"""<section class="section tight"><div class="wrap">
  <div class="intro" style="margin-bottom:var(--section)">
    <div class="copy rv">
      <h1 class="t-display">Фермер и<br>преработвател в едно</h1>
      <p class="t-sub">Стефанов НП отглежда шипка, бял трън и лавандула в Булаир и област Варна и сам ги преработва.</p>
      <p class="t-body">Фокусирани сме върху биологично отглеждане и преработка с методи, които пазят природата и биологичното разнообразие. Шипката берем в пълна зрялост и я сушим бавно. Лавандулата сушим по естествен път. Маслото от семките пресоваме студено. Използваме енергия от собствена соларна инсталация.</p>
    </div>
    <div class="portrait img-rv rv d1"><img src="/img/rosehip-fresh.jpg" alt="Свежи червени шипки след прибиране" width="1200" height="800"></div>
  </div>
  <div class="head rv"><h2 class="t-h2">Къде сме</h2></div>
  <div class="places" style="margin-bottom:var(--section)">
    <div class="place rv">{ico("mountains")}<span class="t-sub">Булаир</span><p class="t-small">Шипка и бял трън в подножието на Източна Стара планина, в близост до Хемските порти.</p></div>
    <div class="place rv d1">{ico("factory")}<span class="t-sub">Бозвелийско</span><p class="t-small">База за сушене, преработка и експедиция. Община Провадия.</p></div>
    <div class="place rv d1">{ico("flower")}<span class="t-sub">Венчан</span><p class="t-small">Лавандула с капково напояване. Община Провадия.</p></div>
    <div class="place rv d2">{ico("plant")}<span class="t-sub">Климентово</span><p class="t-small">Насаждения от шипка. Община Аксаково.</p></div>
  </div>
  <div style="margin-bottom:var(--section)">
    {figures('Реколта 2024<br>в <span class="accent">цифри</span>', f'По данни от био сертификата и лабораторния анализ. {tbc("Площите в преход се потвърждават.")}',
             [("55,8 ха", "шипка с био сертификат"), ("5,15 ха", "лавандула с био сертификат"), ("74,9 т", "прогнозна реколта шипка"), ("14,1 т", "прогнозна реколта лавандула"), ("0", "открити остатъци от пестициди"), ("2,3 км", "дължина на Хемските порти")])}
  </div>
  <section aria-labelledby="eu-h" style="margin-bottom:var(--section)">
    <div class="head rv"><h2 id="eu-h" class="t-h2">Инвестираме<br>в <span class="accent">капацитет</span></h2><p class="t-body">Около 3,79 млн. лв. публично съфинансиране за напояване, техника, хладилно съхранение, автоматизация и соларна енергия.</p></div>
    <div class="eu">{eu}</div>
  </section>
  <div class="people">
    <div class="copy rv">
      <h2 class="t-h2">Хората зад фермата</h2>
      <p class="t-body">{tbc("Историята на семейството: кога започват, защо шипка и лавандула, кой какво прави. Очаква се от клиента.")}</p>
      <div class="row-actions"><a class="btn btn-primary" href="/proekti.html">Проектите ни с ЕС {ARROW}</a></div>
    </div>
    <div class="photo rv d1"><p class="t-small">Портрет на семейството<br>4:5, естествена светлина, на полето</p></div>
  </div>
</div></section>{cta()}"""
    return layout(key="fermata", path="/fermata.html", body=body, title="Фермата | Стефанов НП, био шипка и лавандула",
                  desc="Стефанов НП отглежда и преработва шипка, бял трън и лавандула в Булаир, Бозвелийско, Венчан и Климентово.")


def page_certs():
    body = f"""<section class="section tight"><div class="wrap">
  <div class="page-head rv"><h1 class="t-display">Сертификати<br>и анализи</h1><p class="t-body">Документите, които получавате и с офертата. Био сертификатът е публичен и можете да го проверите сами.</p></div>
  {creds()}
  <div style="margin-top:var(--s-16)">{docs()}</div>
  <div class="prose rv" id="proverka" style="margin-top:var(--section)">
    <h2 class="t-h2">Как да проверите</h2>
    <p class="t-body">Всички био оператори в ЕС са публикувани в системата TRACES на Европейската комисия. Отворете „Провери в TRACES“ при сертификата или потърсете номера му в публичния регистър.</p>
    <p class="t-body">С всяка доставка на био продукт издаваме сертификат за транзакция при поискване.</p>
  </div>
</div></section>{cta()}"""
    return layout(key="sertifikati", path="/sertifikati.html", body=body, title="Сертификати и анализи | Стефанов НП",
                  desc="Био сертификат по Регламент (ЕС) 2018/848 и анализ за остатъци от пестициди от акредитирана лаборатория.")


def page_projects():
    items = "".join(f"""<article class="project" id="{p['id']}">
  <img class="img-rv rv" src="/img/{p['img']}" alt="Информационен плакат на проект {p['code']}: {esc(p['funding'])}; {esc(p['amount'])}; период {p['start']} – {p['end']}" width="1200" height="800" loading="lazy">
  <div class="copy rv d1">
    <p class="t-micro eyebrow">{p['code']}</p>
    <h2 class="t-h3">{p['title']}</h2>
    <dl class="meta"><dt>Програма</dt><dd>{p['programme']}</dd><dt>Финансиране</dt><dd>{p['amount']}</dd><dt>Период</dt><dd>{p['start']} – {p['end']}</dd><dt>Статус</dt><dd>{tbc("Приключил, резултатите се потвърждават")}</dd></dl>
    <p class="t-small">{p['text']}</p>
  </div>
</article>""" for p in PROJECTS)
    body = f"""<section class="section tight"><div class="wrap">
  <div class="page-head rv"><h1 class="t-display">Проекти с европейско<br>финансиране</h1><p class="t-body">Три инвестиции в напояване, техника, хладилно съхранение, автоматизация и соларна енергия, с общо около 3,79 млн. лв. публично съфинансиране.</p></div>
  {items}
</div></section>"""
    return layout(key="proekti", path="/proekti.html", body=body, title="Проекти с ЕС | Стефанов НП",
                  desc="Проекти BG-RRP-6.004-2420-C01, BG06RDNP001-4.015-0286-C01 и BG06RDNP001-4.012-1695-C01 на Стефанов НП.")


def page_quote():
    opts = "".join(f'<option value="{p["slug"]}">{p["name"]}</option>' for p in PRODUCTS) + '<option value="drugo">Друго или няколко продукта</option>'
    err = '<p class="err"><span class="msg"></span></p>'
    units = "".join(f'<label class="unit"><input type="radio" name="unit" value="{u}"{" checked" if u == "т" else ""}><span>{u}</span></label>' for u in ("кг", "т", "л"))
    body = f"""<section class="section tight"><div class="wrap">
  <div class="page-head rv"><h1 class="t-display">Запитване<br>за оферта</h1><p class="t-body">Кажете ни продукта и количеството. Ще върнем цена, спецификация и документи {tbc("до един работен ден")}.</p></div>
  <div class="form-wrap">
    <div class="quote-card rv">
      <form class="quote" novalidate>
        <fieldset class="fgroup">
          <legend class="fgroup-h">Какво ви трябва</legend>
          <div class="field"><label for="product">Продукт</label><select id="product" name="product" required data-dd><option value="">Изберете продукт</option>{opts}</select>{err}</div>
          <div class="field-row">
            <div class="field"><label for="quantity">Количество</label><div class="qty"><input id="quantity" name="quantity" type="text" inputmode="decimal" autocomplete="off" placeholder="2,5" required><span class="units" role="radiogroup" aria-label="Мерна единица">{units}</span></div>{err}</div>
            <div class="field"><label for="country">Държава на доставка</label><input id="country" name="country" type="text" autocomplete="country-name" value="България" required>{err}</div>
          </div>
          <div class="field"><label for="form_detail">Форма или спецификация <span class="opt">по желание</span></label><input id="form_detail" name="form_detail" type="text" autocomplete="off" placeholder="Цял плод, люспи 3–5 мм"></div>
        </fieldset>
        <fieldset class="fgroup">
          <legend class="fgroup-h">Как да се свържем с вас</legend>
          <div class="field-row">
            <div class="field"><label for="company">Фирма</label><input id="company" name="company" type="text" autocomplete="organization" required>{err}</div>
            <div class="field"><label for="name">Лице за контакт <span class="opt">по желание</span></label><input id="name" name="name" type="text" autocomplete="name"></div>
          </div>
          <div class="field-row">
            <div class="field"><label for="email">Имейл</label><input id="email" name="email" type="email" autocomplete="email" placeholder="name@firma.bg" required>{err}</div>
            <div class="field"><label for="phone">Телефон <span class="opt">по желание</span></label><input id="phone" name="phone" type="tel" autocomplete="tel"></div>
          </div>
          <div class="field"><label for="message">Съобщение <span class="opt">по желание</span></label><textarea id="message" name="message" rows="4" placeholder="Срок за доставка, опаковка, нужни документи, мостра"></textarea></div>
        </fieldset>
        <div class="field"><label class="check"><input type="checkbox" name="consent" required><span class="box" aria-hidden="true"><svg viewBox="0 0 16 16"><path d="M3.5 8.5l3 3 6-7"/></svg></span><span>Съгласен съм данните ми да се използват само за отговор на това запитване. <a href="/poveritelnost.html">Поверителност</a></span></label>{err}</div>
        <div class="form-foot"><button class="btn btn-primary" type="submit" data-submit><span class="btn-spin" aria-hidden="true"></span><span class="btn-label">Изпратете запитването</span> {ARROW}</button><p class="form-status" role="status" aria-live="polite"></p></div>
      </form>
      <div class="form-done" hidden tabindex="-1">
        <span class="t-success-check" data-state="out" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><circle cx="24" cy="24" r="22"/><path d="M14.5 24.5l6.5 6.5 13-14"/></svg></span>
        <h2 class="t-h3">Запитването е готово</h2>
        <p class="t-body">Отворихме имейла ви с попълненото запитване до {EMAIL}. Изпратете го оттам и ще отговорим {tbc("до един работен ден")}.</p>
        <dl class="done-sum"></dl>
        <div class="row-actions"><a class="btn btn-primary" data-mailto href="mailto:{EMAIL}">Отворете имейла отново {ARROW}</a><button class="btn btn-secondary" type="button" data-copy><span class="btn-label">Копирайте текста</span></button></div>
        <p class="t-small muted">Нищо не се отвори? Пишете ни на <a href="mailto:{EMAIL}">{EMAIL}</a> или се обадете на <a href="{PHONE_HREF}">{PHONE}</a>. <button class="link-btn" type="button" data-reset>Ново запитване</button></p>
      </div>
    </div>
    <aside class="aside" id="kontakt">
      <div class="aside-photo img-rv rv"><img src="/img/rosehip-sky.jpg" alt="Три зрели шипки на клонка срещу синьо небе" width="1200" height="1800" loading="lazy"></div>
      <section class="rv" aria-labelledby="talk-h"><h2 id="talk-h" class="t-h3">Предпочитате разговор?</h2>
        <dl class="contact-list">
          <div><dt class="t-small">Телефон</dt><dd><a href="{PHONE_HREF}">{PHONE}</a></dd></div>
          <div><dt class="t-small">Имейл</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
          <div><dt class="t-small">Чат</dt><dd><button type="button" data-chat>Пишете ни тук</button></dd></div>
          <div><dt class="t-small">Работно време</dt><dd>Понеделник – петък, 08:00 – 18:00</dd></div>
          <div><dt class="t-small">Адрес</dt><dd>с. Бозвелийско, общ. Провадия, обл. Варна</dd></div>
        </dl>
      </section>
      <section class="rv" aria-labelledby="next-h"><h2 id="next-h" class="t-h3">Какво следва</h2>
        <ol class="next"><li><span>Потвърждаваме наличност за реколтата.</span></li><li><span>Изпращаме цена, спецификация, сертификат и анализ.</span></li><li><span>При нужда изпращаме {tbc("мостра")}.</span></li></ol>
      </section>
    </aside>
  </div>
</div></section>"""
    return layout(key="zapitvane", path="/zapitvane.html", body=body, title="Запитване за оферта | Стефанов НП",
                  desc="Поискайте оферта за био шипка, шипка на прах, масло от шипкови семки или лавандулов цвят на едро.")


def page_privacy():
    body = f"""<section class="section tight"><div class="wrap">
  <div class="page-head"><h1 class="t-display">Поверителност<br>и условия</h1><p class="t-body">{tbc("Текстът се одобрява от клиента и юрист.")}</p></div>
  <div class="prose">
    <h2 class="t-h3">Какви данни събираме</h2><p class="t-body">Само данните, които въвеждате в запитването: фирма, лице за контакт, имейл, телефон и детайли за поръчката. Използваме ги единствено, за да отговорим на запитването ви.</p>
    <h2 class="t-h3">Чат</h2><p class="t-body">Чатът на сайта се предоставя от Tidio и се зарежда едва когато го отворите. Съобщенията и данните, които напишете в него, се съхраняват при Tidio и ги използваме само, за да ви отговорим.</p>
    <h2 class="t-h3">Колко дълго ги пазим</h2><p class="t-body">{tbc("До 24 месеца след последната кореспонденция, освен ако закон не изисква друго.")}</p>
    <h2 class="t-h3">Вашите права</h2><p class="t-body">Можете да поискате достъп, корекция или изтриване на данните си на {EMAIL}.</p>
    <h2 class="t-h3" id="usloviya">Условия за ползване</h2><p class="t-body">Информацията на сайта е с ориентировъчен характер. Цени, наличности и спецификации се потвърждават в писмена оферта.</p>
  </div>
</div></section>"""
    return layout(key="", path="/poveritelnost.html", body=body, title="Поверителност и условия | Стефанов НП", desc="Как Стефанов НП използва данните от запитванията.")


def page_404():
    links = "".join(f'<li><a href="/produkti/{p["slug"]}.html">{p["name"]}</a></li>' for p in PRODUCTS)
    body = f"""<section class="section tight"><div class="wrap"><div class="nf">
  <p class="t-micro eyebrow">Грешка 404</p>
  <h1 class="t-display">Тази страница<br>не съществува</h1>
  <p class="t-body muted">Възможно е адресът да е сгрешен или страницата да е преместена при новия сайт.</p>
  <div class="row-actions"><a class="btn btn-primary" href="/">Към началото {ARROW}</a><a class="btn btn-secondary" href="/zapitvane.html">Запитване за оферта</a></div>
  <ul class="t-body" style="margin:0;padding-left:1.2em">{links}</ul>
</div></div></section>"""
    return layout(key="", path="/404.html", body=body, title="Страницата не е намерена | Стефанов НП", desc="Страницата не е намерена.")


# --------------------------------------------------------------------------- build
def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    rsrc = PROJECT / "redesign" / "src"
    sg = PROJECT / "styleguide"
    shutil.copytree(rsrc / "img", DIST / "img")
    shutil.copytree(rsrc / "video", DIST / "video")
    shutil.copytree(SRC / "img", DIST / "img", dirs_exist_ok=True)
    shutil.copytree(SRC / "video", DIST / "video", dirs_exist_ok=True)
    shutil.copytree(rsrc / "docs", DIST / "docs")
    for f in ("mark-line-white.png", "mark-line-purple.png", "mark-line-ink.png", "wordmark-white.png", "wordmark-purple.png", "wordmark-ink.png"):
        shutil.copy(sg / "assets" / f, DIST / "img" / f)
    shutil.copy(sg / "tokens.css", DIST / "tokens.css")
    shutil.copytree(SRC / "icons", DIST / "icons")
    shutil.copytree(SRC / "brand", DIST / "brand")
    shutil.copytree(SRC / "vendor", DIST / "vendor")
    shutil.copy(SRC / "site.css", DIST / "site.css")
    shutil.copy(SRC / "site.js", DIST / "site.js")
    pages = {"index.html": page_home(), "produkti.html": page_products(), "fermata.html": page_farm(),
             "sertifikati.html": page_certs(), "proekti.html": page_projects(), "zapitvane.html": page_quote(),
             "poveritelnost.html": page_privacy(), "404.html": page_404()}
    for p in PRODUCTS:
        pages[f"produkti/{p['slug']}.html"] = page_product(p)
    for name, content in pages.items():
        out = DIST / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
    # English: every page again under /en/, translated from i18n/en.json (see i18n.py)
    import i18n
    frags, T = i18n.load()
    T.update({i18n.norm(k): v for k, v in AUTO_EN.items()})   # generated prices and pack sizes
    missing = set()
    for name, content in pages.items():
        out = DIST / "en" / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(i18n.to_english(content, frags, T, missing, name), encoding="utf-8")
    if missing:
        (ROOT / "i18n" / "missing.txt").write_text("\n".join(f"{w}\t{k}" for k, w in sorted(missing, key=lambda x: x[1])), encoding="utf-8")
        sys.exit(f"{len(missing)} strings have no English translation: see i18n/missing.txt")
    (ROOT / "i18n" / "missing.txt").unlink(missing_ok=True)
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    urls = "".join(f"<url><loc>{SITE}{pre}/{'' if n == 'index.html' else n}</loc></url>" for pre in ("", "/en") for n in pages if n != "404.html")
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', encoding="utf-8")
    base = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--base=")), "").rstrip("/")
    noindex = bool(base) or "--noindex" in sys.argv[1:]
    # Netlify: English 404 under /en/ (GitHub Pages and serve.py ignore this file)
    (DIST / "_redirects").write_text(f"{base}/en/*  {base}/en/404.html  404\n", encoding="utf-8")
    if base:
        rebase(base)
    if noindex:
        hide_from_search()
    print(f"built {len(pages)} pages in Bulgarian and English into {DIST}" + (f", for {base}/" if base else "") + (" (staging, noindex)" if noindex else ""))


def hide_from_search():
    """Staging and proof-of-concept copies: keep them out of search results so they never compete with stefanoff.bg."""
    for f in DIST.rglob("*.html"):
        s = f.read_text(encoding="utf-8")
        f.write_text(s.replace('<meta name="viewport"', '<meta name="robots" content="noindex, nofollow">\n<meta name="viewport"', 1), encoding="utf-8")
    (DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (DIST / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow\n", encoding="utf-8")


def rebase(base):
    """Staging copy served under a sub-path (GitHub Pages: /stefanoffEcommerce/). Prefixes every root-relative URL in the
    built pages and styles, and tells site.js the sub-path (<html data-base>)."""
    attr = re.compile(r'(\s(?:href|src|action|poster)=")/(?!/)')
    url = re.compile(r'url\((["\']?)/(?!/)')
    for f in DIST.rglob("*.html"):
        s = f.read_text(encoding="utf-8")
        s = attr.sub(lambda m: m.group(1) + base + "/", s)
        s = re.sub(r'srcset="([^"]*)"', lambda m: 'srcset="' + re.sub(r'(^|,\s*)/(?!/)', lambda k: k.group(1) + base + "/", m.group(1)) + '"', s)
        s = url.sub(lambda m: f"url({m.group(1)}{base}/", s)
        s = s.replace("<html ", f'<html data-base="{base}" ', 1)
        f.write_text(s, encoding="utf-8")
    for f in DIST.rglob("*.css"):
        f.write_text(url.sub(lambda m: f"url({m.group(1)}{base}/", f.read_text(encoding="utf-8")), encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")


if __name__ == "__main__":
    main()
