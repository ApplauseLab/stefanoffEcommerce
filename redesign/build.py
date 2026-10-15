#!/usr/bin/env python3
"""Build the stefanoff.bg redesign prototype into ./dist (static HTML)."""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SRC, DIST = ROOT / "src", ROOT / "dist"
YEAR = date.today().year
SITE = "https://stefanoff.bg"

PHONE, PHONE_HREF = "+359 888 229 537", "tel:+359888229537"
EMAIL = "office@stefanoff.bg"
TBC = "Потвърждава се от клиента"


def tbc(text):
    return f'<span class="tbc" title="{TBC}">{text}</span>'


def esc(s):
    return html.escape(s, quote=True)


# --------------------------------------------------------------------------- data
PRODUCTS = [
    {
        "slug": "shipka-sushena",
        "name": "Сушена шипка",
        "short": "Цял плод и люспи, бавно изсушени",
        "card": "Цели плодове и нарязани люспи за чай, смеси и екстракция.",
        "img": "rosehip-dried.jpg",
        "alt": "Сушени цели шипки в тъмен метален поднос върху дървени дъски",
        "tags": ["Цял плод", "Люспи"],
        "lead": "Плодове от шипка (Rosa canina), брани в пълна зрялост, докато са още твърди, и изсушени бавно при ниска температура в нашата база в Бозвелийско.",
        "spec": [
            ("Ботаническо име", "Rosa canina L."),
            ("Произход", "Област Варна, България"),
            ("Статус", "Био, Регламент (ЕС) 2018/848"),
            ("Форми", "Цял сушен плод, люспи"),
            ("Прибиране", "Септември – октомври"),
            ("Срок на годност", tbc("До 12 месеца на сухо място")),
            ("Опаковка", tbc("По заявка, транспортна опаковка")),
            ("Минимално количество", tbc("По запитване")),
        ],
        "uses": [("ph-coffee", "Чай и билкови смеси"), ("ph-flask", "Екстракти и сиропи"), ("ph-factory", "Хранителна преработка"), ("ph-bowl-food", "Мюсли и сухи смеси")],
        "about": [
            ("Как берем и сушим", "Шипката цъфти от май до юли, а плодовете узряват през септември и октомври. Берем ги, когато са узрели, но още твърди, защото омекналите плодове губят голяма част от витамините си. Сушим бавно, без висока температура."),
            ("Приготвяне на чай", "Една супена лъжица сушени шипки се вари в 250 мл вода около 10 минути и се прецежда. За по наситен вкус две супени лъжици се оставят в термос с половин литър вода от 60 до 70 °C за няколко часа."),
        ],
    },
    {
        "slug": "shipka-na-prah",
        "name": "Шипка на прах",
        "short": "100% цял плод, смлян след сушене",
        "card": "Фин прах от целия плод за храни, напитки, козметика и фуражи.",
        "img": "rosehip-powder.jpg",
        "alt": "Оранжев шипков прах в глинена купа до свежи плодове на шипка",
        "tags": ["Прах", "Цял плод"],
        "lead": "Целият плод на шипката, изсушен бавно и смлян на фин прах. Без добавки: съставът е 100% шипка.",
        "spec": [
            ("Състав", "100% плод на шипка (Rosa canina)"),
            ("Произход", "Област Варна, България"),
            ("Статус", "Био, Регламент (ЕС) 2018/848"),
            ("Обработка", "Бавно сушене, смилане на целия плод"),
            ("Фракция", tbc("По заявка")),
            ("Опаковка", tbc("По заявка")),
            ("Минимално количество", tbc("По запитване")),
        ],
        "uses": [("ph-bread", "Хлебни и сладкарски изделия"), ("ph-coffee", "Напитки и смутита"), ("ph-sparkle", "Козметика: маски и ексфолианти"), ("ph-cow", "Фуражни добавки")],
        "about": [
            ("Защо бавно сушене", "Сушим плода дълго и при ниска температура, вместо бързо и горещо. Така прахът запазва цвета, вкуса и състава на плода по добре. След сушене смиламе целия плод, със семките."),
            ("Вкус и приложение", "Прахът е леко кисел, с плодов аромат. Добавя се към тесто заедно с друго брашно, към студени и топли напитки и към сухи смеси. В козметиката финият прах се използва като мек ексфолиант в маски и почистващи продукти."),
        ],
    },
    {
        "slug": "maslo-ot-shipka",
        "name": "Масло от шипкови семки",
        "short": "Студено пресовано в собствена база",
        "card": "Студено пресовано масло за козметика, по запитване и рафинирано.",
        "img": "oil-bottle.jpg",
        "alt": "Стъклено шишенце с червено масло от шипка и свежи шипки върху стара дървена маса",
        "tags": ["Студено пресовано", "Рафинирано"],
        "lead": "Масло, извлечено от семките на шипката чрез механично студено пресоване в нашата база. При поискване доставяме и рафинирано масло с неутрален цвят и аромат.",
        "spec": [
            ("INCI", "Rosa Canina Seed Oil"),
            ("Метод", "Студено пресоване с винтова преса"),
            ("Варианти", "Нерафинирано" + ", " + tbc("рафинирано")),
            ("Есенциални мастни киселини", tbc("Не по малко от 80%")),
            ("Био статус", tbc("По запитване")),
            ("Опаковка", tbc("По заявка")),
            ("Минимално количество", tbc("По запитване")),
        ],
        "uses": [("ph-drop", "Серуми и масла за лице"), ("ph-hand-heart", "Продукти за тяло"), ("ph-flask", "Масло носител в рецептури"), ("ph-scissors", "Грижа за коса")],
        "about": [
            ("Студено и рафинирано", "При студеното пресоване маслото се извлича само с налягане, без добавена топлина. Добивът е по нисък, а маслото запазва естествения си оранжев цвят и аромат. Рафинираното масло е светложълто, почти без мирис, и не влияе на цвета и аромата на крайния продукт."),
            ("Безопасност", "Както при всяко козметично масло, препоръчваме тест върху малък участък кожа преди употреба."),
        ],
    },
    {
        "slug": "lavandula",
        "name": "Лавандулов цвят",
        "short": "Сушен по естествен път, със стъбла",
        "card": "Сушен цвят със стъбла, на едро, запечатан за аромат.",
        "img": "lavender.jpg",
        "alt": "Сушени лавандулови пъпки в бяла купа с дървена лопатка, стръкове лавандула отзад",
        "tags": ["Цвят", "Със стъбла"],
        "lav": True,
        "lead": "Лавандула от собствени насаждения с капково напояване във Венчан. Изсушаваме я по естествен път, така че пъпките и стеблата запазват етеричното си масло и аромат.",
        "spec": [
            ("Ботаническо име", tbc("Lavandula angustifolia")),
            ("Произход", "с. Венчан, област Варна, България"),
            ("Статус", "Био, Регламент (ЕС) 2018/848"),
            ("Форма", "Сушен цвят със стъбла"),
            ("Прибиране", tbc("Юни – юли")),
            ("Опаковка", "Насипно, запечатано в транспортна опаковка"),
            ("Минимално количество", tbc("По запитване")),
        ],
        "uses": [("ph-coffee", "Билков чай и смеси"), ("ph-flower", "Ароматни саше и възглавнички"), ("ph-gift", "Декорация и подаръци"), ("ph-t-shirt", "Защита на дрехи от молци")],
        "about": [
            ("Аромат, който се запазва", "При естественото сушене пъпките не губят, а засилват аромата си. Затова цветът е подходящ за ароматни продукти, ръчно изработени саше и малки подаръци за сватби и празници."),
            ("В кухнята", "Лавандулата е позната подправка от провансалската кухня. Използва се умерено в десерти, печива и смеси от подправки."),
        ],
    },
    {
        "slug": "bial-trun",
        "name": "Бял трън",
        "short": "От подножието на Източна Стара планина",
        "card": "Сушен плод и цвят от Булаир, по запитване.",
        "img": "bial-trun.jpg",
        "alt": "Място за снимка на бял трън: рисунка на клонка с червени плодове",
        "tags": ["Плод", "Цвят"],
        "lead": "Бял трън (Crataegus monogyna) от нашите насаждения край Булаир, в подножието на Източна Стара планина. Предлагаме сушен плод и цвят с листа, по запитване.",
        "spec": [
            ("Ботаническо име", "Crataegus monogyna Jacq."),
            ("Произход", "с. Булаир, Източна Стара планина, България"),
            ("Статус", tbc("Био статусът се потвърждава")),
            ("Форми", tbc("Сушен плод; цвят с листа")),
            ("Прибиране", tbc("Цвят: май; плод: септември – октомври")),
            ("Опаковка", tbc("По заявка")),
            ("Минимално количество", tbc("По запитване")),
        ],
        "uses": [("ph-coffee", "Чай и билкови смеси"), ("ph-flask", "Екстракти и тинктури"), ("ph-factory", "Хранителна преработка"), ("ph-flower", "Цвят за билкови смеси")],
        "about": [
            ("Растението", "Белият трън е бодлив храст или ниско дърво от семейство Розоцветни, роднина на шипката. Цъфти с бели цветове през май, а червените му плодове узряват през есента."),
            ("От Булаир", "Отглеждаме го край Булаир, в подножието на Източна Стара планина, където земеделските площи съседстват с природни местообитания."),
        ],
    },
]

PROJECTS = [
    {
        "id": "rrp-6004-2420",
        "code": "BG-RRP-6.004-2420-C01",
        "short": "Технологична модернизация и цифровизация",
        "title": "„Инвестиции в технологична модернизация и цифровизация на „Стефанов НП“ ООД за устойчиво селско стопанство“",
        "programme": "Механизъм за възстановяване и устойчивост, Компонент „Устойчиво земеделие“, процедура BG-RRP-6.004",
        "amount": "617 850,00 лв. обща стойност, от които 282 827,75 лв. безвъзмездно",
        "amount_short": "282 827,75 лв. безвъзмездно",
        "start": "25.06.2024", "end": "25.06.2025",
        "text": "На 25.06.2024 г. СТЕФАНОВ НП ООД сключи договор за финансиране BG-RRP-6.004-2420-C01 от Механизма за възстановяване и устойчивост за изпълнение на инвестиция по Компонент „Устойчиво земеделие“, Инвестиция „Фонд за насърчаване на технологичния и екологичен преход на селското стопанство“. Изпълнението на инвестицията ще допринесе за технологично и екологично осъвременяване на средствата за производство, повишаване на конкурентоспособността и устойчивостта на стопанството и ускоряване на неговата адаптация към климатичните промени, екологизацията на производството и цифровата трансформация.",
        "img": "project-BG-RRP-6.004-2420-C01.jpg",
        "funding": "Финансирано от Европейския съюз, NextGenerationEU",
    },
    {
        "id": "rdp-4015-0286",
        "code": "BG06RDNP001-4.015-0286-C01",
        "short": "Автоматизация и ВЕИ в базата за преработка",
        "title": "Инвестиции, свързани с автоматизация и опазване на околната среда, включително ВЕИ, за обект за преработка на билки и плодове (шипки) в ПИ 05102.128.63, с. Бозвелийско, община Провадия, област Варна",
        "programme": "Програма за развитие на селските райони 2014 – 2020, подмярка 4.2 „Инвестиции в преработка/маркетинг на селскостопански продукти“",
        "amount": "2 574 828,47 лв. публични разходи",
        "amount_short": "2 574 828,47 лв. публични разходи",
        "start": "03.08.2023", "end": "26.08.2025",
        "text": "На 03.08.2023 г. СТЕФАНОВ НП ООД сключи договор за финансиране № BG06RDNP001-4.015-0286-C01 по процедура чрез подбор на проектни предложения по подмярка 4.2 „Инвестиции в преработка/маркетинг на селскостопански продукти“ от мярка 4 „Инвестиции в материални активи“. След реализацията на инвестицията „Стефанов НП“ ООД ще постигне висока икономическа ефективност и повишена конкурентоспособност чрез много добро използване на факторите за производство и добавяне на стойност към преработената от дружеството земеделска продукция.",
        "img": "project-BG06RDNP001-4.015-0286-C01.jpg",
        "funding": "Европейски земеделски фонд за развитие на селските райони: Европа инвестира в селските райони",
    },
    {
        "id": "rdp-4012-1695",
        "code": "BG06RDNP001-4.012-1695-C01",
        "short": "Капково напояване, техника и хладилно съхранение",
        "title": "Изграждане на система за капково напояване за насаждения от лавандула, закупуване на земеделска техника и иновативно оборудване",
        "programme": "Програма за развитие на селските райони 2014 – 2020, подмярка 4.1 „Инвестиции в земеделски стопанства“",
        "amount": "930 445,23 лв. публични разходи",
        "amount_short": "930 445,23 лв. публични разходи",
        "start": "27.01.2023", "end": "25.08.2025",
        "text": "На 27.01.2023 г. СТЕФАНОВ НП ООД сключи договор за финансиране № BG06RDNP001-4.012-1695-C01 по подмярка 4.1 „Инвестиции в земеделски стопанства“ от мярка 4 „Инвестиции в материални активи“. Новата земеделска техника и системите за напояване ще подобрят цялостната дейност на стопанството, ще намалят производствените разходи и ще гарантират устойчиви добиви и високо качество на продукцията. Модернизацията включва иновативна технология за интензивно охлаждане и съхранение на етеричномаслените култури, за да се запазят най летливите им вещества, и енергийна независимост чрез автономна соларна инсталация.",
        "img": "project-BG06RDNP001-4.012-1695-C01.jpg",
        "funding": "Европейски земеделски фонд за развитие на селските райони: Европа инвестира в селските райони",
    },
]

NAV = [
    ("/produkti.html", "Продукти", "produkti"),
    ("/za-nas.html", "За нас", "za-nas"),
    ("/sertifikati.html", "Сертификати", "sertifikati"),
    ("/proekti.html", "Проекти", "proekti"),
    ("/zapitvane.html#kontakt", "Контакти", "kontakt"),
]

# --------------------------------------------------------------------------- layout
def layout(*, key, title, desc, body, path, schema=None, og_img="/img/hero-poster.jpg"):
    links = "".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if k == key else ""}>{label}</a></li>' for href, label, k in NAV
    )
    big = "".join(
        f'<li><a class="big" href="{href}"{" aria-current=\"page\"" if k == key else ""}>{label}</a></li>' for href, label, k in NAV
    ) + f'<li><a class="big" href="/zapitvane.html"{" aria-current=\"page\"" if key == "zapitvane" else ""}>Запитване</a></li>'
    schema_tag = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>' if schema else ""
    return f"""<!doctype html>
<html lang="bg" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:locale" content="bg_BG">
<meta property="og:site_name" content="Стефанов НП">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}{og_img}">
<meta name="theme-color" content="#F7F3EC">
<link rel="icon" type="image/png" href="/img/mark.png">
<script>document.documentElement.classList.replace("no-js","js");if(matchMedia("(prefers-reduced-motion: reduce)").matches)document.documentElement.classList.add("reduced");</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&subset=cyrillic&display=swap" rel="stylesheet">
<script src="https://unpkg.com/@phosphor-icons/web@2.1.1"></script>
<link rel="stylesheet" href="/styles.css">
{schema_tag}
</head>
<body>
<a class="skip" href="#main">Към съдържанието</a>
<div class="nav-wrap">
  <nav class="nav" aria-label="Основна навигация">
    <a class="brand" href="/" aria-label="Стефанов НП, начало"><img src="/img/mark.png" alt="" width="32" height="32">stefanoff</a>
    <ul class="nav-links">{links}</ul>
    <a class="btn btn-primary nav-cta-desktop" href="/zapitvane.html">Поискайте оферта</a>
    <button class="burger" type="button" aria-expanded="false" aria-controls="menu" aria-label="Отвори менюто"><span></span><span></span></button>
  </nav>
</div>
<div class="overlay" id="menu">
  <ul>{big}</ul>
  <div class="overlay-contact t-base">
    <a href="{PHONE_HREF}">{PHONE}</a>
    <a href="mailto:{EMAIL}">{EMAIL}</a>
  </div>
</div>
<main id="main">
{body}
</main>
{footer()}
<script src="/main.js" defer></script>
</body>
</html>
"""


def footer():
    prods = "".join(f'<li><a href="/produkti/{p["slug"]}.html">{p["name"]}</a></li>' for p in PRODUCTS)
    return f"""<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div style="display:grid;gap:var(--s-200);align-content:start">
        <a class="brand" href="/"><img src="/img/mark.png" alt="" width="32" height="32">stefanoff</a>
        <p>Био шипка и лавандула от област Варна. Отглеждане, сушене и преработка в една ферма.</p>
      </div>
      <div><h2>Продукти</h2><ul>{prods}</ul></div>
      <div><h2>Компания</h2><ul>
        <li><a href="/za-nas.html">За нас</a></li><li><a href="/sertifikati.html">Сертификати</a></li>
        <li><a href="/proekti.html">Проекти с ЕС</a></li><li><a href="/zapitvane.html">Запитване за оферта</a></li></ul></div>
      <div><h2>Контакт</h2><ul>
        <li><a href="{PHONE_HREF}">{PHONE}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li>с. Бозвелийско, общ. Провадия, обл. Варна</li><li>Понеделник – петък, 08:00 – 18:00</li></ul></div>
    </div>
    <div class="legal">
      <span>© {YEAR} {tbc("Стефанов НП ООД")}</span>
      <span style="display:flex;gap:var(--s-300);flex-wrap:wrap"><a href="/poveritelnost.html">Поверителност</a><a href="/poveritelnost.html#usloviya">Условия за ползване</a><a href="https://facebook.com/stefanoff.bg" rel="noopener">Facebook</a></span>
    </div>
  </div>
</footer>"""


def proto_note():
    return f"""<div class="container"><p class="proto-note reveal"><i class="ph ph-info" aria-hidden="true"></i><span>Прототип на редизайна, октомври {YEAR}. Данните с <span class="tbc" title="{TBC}">пунктирана линия</span> се потвърждават от клиента. Снимките са временни, до фотосесия във фермата.</span></p></div>"""


def product_card(p, i=0):
    tags = "".join(f'<span class="tag{" tag-lav" if p.get("lav") else ""}">{t}</span>' for t in p["tags"])
    return f"""<article class="card reveal d{i % 4}">
  <div class="card-img"><img src="/img/{p['img']}" alt="{esc(p['alt'])}" loading="lazy" width="1200" height="800"></div>
  <div class="card-body">
    <h3><a href="/produkti/{p['slug']}.html">{p['name']}</a></h3>
    <p>{p['card']}</p>
    <div class="tags">{tags}</div>
  </div>
</article>"""


def docs_block():
    return f"""<div class="docs">
  <article class="doc reveal">
    <img src="/img/cert-organic.jpg" alt="Първа страница на био сертификата на Стефанов НП, издаден от Нутрамед" width="500" height="625" loading="lazy">
    <div class="body">
      <span class="status status-warn"><i class="ph ph-clock-counter-clockwise" aria-hidden="true"></i>{tbc("Актуален сертификат за " + str(YEAR) + " предстои")}</span>
      <h3>Био сертификат по Регламент (ЕС) 2018/848</h3>
      <dl>
        <dt>Номер</dt><dd>BG-BIO-22.100-0003115.2024.001</dd>
        <dt>Контролен орган</dt><dd>Нутрамед, BG-BIO-22</dd>
        <dt>Дейности</dt><dd>Производство, подготовка, разпространение</dd>
        <dt>Продукти</dt><dd>Шипка, лавандула</dd>
        <dt>Валидност</dt><dd>11.03.2024 – 29.12.2024</dd>
      </dl>
      <div class="actions">
        <a class="link-arrow" href="/docs/certificate-organic-production-eu-2018-848.pdf"><i class="ph ph-file-pdf" aria-hidden="true"></i>Изтегли PDF</a>
        <a class="link-arrow" href="https://webgate.ec.europa.eu/tracesnt/directory/publication/organic-operator/BG-BIO-22.100-0003115.2024.001.pdf" rel="noopener">Провери в TRACES<i class="ph ph-arrow-up-right" aria-hidden="true"></i></a>
      </div>
    </div>
  </article>
  <article class="doc reveal d1">
    <img src="/img/cert-lab.jpg" alt="Първа страница на протокол от анализ 24/000523 на лаборатория Приморис" width="500" height="625" loading="lazy">
    <div class="body">
      <span class="status status-ok"><i class="ph ph-check-circle" aria-hidden="true"></i>Няма открити остатъци</span>
      <h3>Анализ за остатъци от пестициди</h3>
      <dl>
        <dt>Лаборатория</dt><dd>Приморис, Пловдив</dd>
        <dt>Акредитация</dt><dd>EN ISO/IEC 17025</dd>
        <dt>Протокол</dt><dd>24/000523, 30.01.2024</dd>
        <dt>Проба</dt><dd>Био шипка</dd>
        <dt>Метод</dt><dd>Многокомпонентен скрининг с газова и течна хроматография, граници за био и детски храни</dd>
      </dl>
      <div class="actions">
        <a class="link-arrow" href="/docs/certificate-of-analysis-rosehip-24-000523.pdf"><i class="ph ph-file-pdf" aria-hidden="true"></i>Изтегли PDF</a>
      </div>
    </div>
  </article>
</div>"""


def cta_band():
    return f"""<section class="section" aria-labelledby="cta-h">
  <div class="container">
    <div class="cta-band reveal">
      <div style="display:grid;gap:var(--s-200)">
        <h2 id="cta-h" class="h2">Кажете ни какво ви трябва.<br>Ще върнем цена и спецификация.</h2>
        <p class="t-lg">Запитването отнема около две минути и не изисква регистрация. Отговаряме в {tbc("рамките на един работен ден")}.</p>
        <div><a class="btn btn-primary" href="/zapitvane.html">Поискайте оферта <i class="ph ph-arrow-right" aria-hidden="true"></i></a></div>
      </div>
      <div class="contact-lines">
        <a href="{PHONE_HREF}"><i class="ph ph-phone" aria-hidden="true"></i>{PHONE}</a>
        <a href="mailto:{EMAIL}"><i class="ph ph-envelope-simple" aria-hidden="true"></i>{EMAIL}</a>
        <span style="display:inline-flex;gap:var(--s-100);align-items:center"><i class="ph ph-clock" aria-hidden="true" style="font-size:1.25rem;color:#F2B8AE"></i>Понеделник – петък, 08:00 – 18:00</span>
      </div>
    </div>
  </div>
</section>"""


# --------------------------------------------------------------------------- pages
def page_home():
    cards = "".join(product_card(p, i) for i, p in enumerate(PRODUCTS))
    words = "От нашето поле до вашата производствена линия, без посредник между тях.".split()
    accent = {"без", "посредник"}
    tag = " ".join(f'<span class="w{" accent" if w.strip(",.") in accent else ""}">{w}</span>' for w in words)
    eu = "".join(
        f'<a class="reveal d{i}" href="/proekti.html#{p["id"]}"><span class="code">{p["code"]}</span><span class="ttl">{p["short"]}</span><span class="amt">{p["amount_short"]}</span></a>'
        for i, p in enumerate(PROJECTS)
    )
    faq = [
        ("Продавате ли на дребно?", "Не. Работим с фирми: производители на храни, чай и козметика, преработватели и търговци на едро. Ако ви трябва малко количество за проба, пишете ни."),
        ("Какво е минималното количество за поръчка?", f"Зависи от продукта и опаковката. Посочете нужното количество в запитването и ще го потвърдим в офертата. {tbc('Конкретни минимуми се уточняват с клиента.')}"),
        ("Доставяте ли извън България?", f"{tbc('Да, в рамките на ЕС')}. Условията на доставка и транспорта договаряме в офертата."),
        ("Може ли мостра преди поръчка?", f"{tbc('Да.')} Изпращаме мостра след запитване с посочени продукт, форма и количество."),
        ("Какви документи получавам?", "Био сертификат, анализ за остатъци от пестициди и спецификация на продукта. Сертификат за транзакция издаваме при поискване, според изискванията за био продукти."),
        ("Кога е реколтата?", f"Шипката се бере през септември и октомври, лавандулата през {tbc('юни и юли')}. Сушените продукти предлагаме през цялата година до изчерпване на реколтата."),
        ("Как са опаковани сушените продукти?", f"На едро, запечатани в транспортна опаковка, за да се запазят аромат и качество. Размера на опаковката уточняваме в офертата. {tbc('Стандартни размери предстоят.')}"),
        ("Колко бързо отговаряте?", f"В работни дни отговаряме {tbc('до един работен ден')}. Ако е спешно, обадете се на {PHONE}."),
    ]
    faq_html = "".join(
        f'<details class="reveal"><summary>{q}<i class="ph ph-plus" aria-hidden="true"></i></summary><div class="ans"><p>{a}</p></div></details>' for q, a in faq
    )
    schema = {
        "@context": "https://schema.org", "@type": "Organization", "name": "Стефанов НП ООД", "url": SITE,
        "logo": f"{SITE}/img/mark.png", "email": EMAIL, "telephone": "+359888229537",
        "address": {"@type": "PostalAddress", "addressLocality": "с. Бозвелийско", "addressRegion": "Варна", "addressCountry": "BG"},
        "sameAs": ["https://facebook.com/stefanoff.bg"],
    }
    faq_schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in faq]}
    body = f"""{proto_note()}
<section class="hero" aria-labelledby="hero-h">
  <div class="container hero-grid">
    <div class="hero-copy">
      <span class="eyebrow reveal"><i class="ph ph-seal-check" aria-hidden="true"></i>Био производител от област Варна</span>
      <h1 id="hero-h" class="reveal d1">Био шипка и лавандула<br>от собствени полета</h1>
      <p class="sub reveal d2">Отглеждаме, сушим и преработваме шипка и лавандула край Провадия. Доставяме на едро сушен плод, прах и студено пресовано масло за производители на храни, чай и козметика.</p>
      <div class="hero-actions reveal d3">
        <a class="btn btn-primary" href="/zapitvane.html">Поискайте оферта <i class="ph ph-arrow-right" aria-hidden="true"></i></a>
        <a class="btn btn-secondary" href="/produkti.html">Вижте продуктите</a>
      </div>
      <div class="hero-proof reveal d3">
        <span><i class="ph ph-certificate" aria-hidden="true"></i>Сертификат по Регламент (ЕС) 2018/848</span>
        <span><i class="ph ph-flask" aria-hidden="true"></i>0 открити остатъци от пестициди</span>
      </div>
    </div>
    <div class="media-card reveal d2">
      <video autoplay muted loop playsinline preload="metadata" poster="/img/hero-poster.jpg" aria-label="Видео: шипки в лъжица на фона на прясно набрани плодове">
        <source src="/video/hero.mp4" type="video/mp4">
      </video>
      <div class="media-badge"><i class="ph ph-plant" aria-hidden="true"></i><span><strong>Шипка от Варненско</strong>Прибиране септември – октомври</span></div>
      <button class="video-toggle" type="button" aria-label="Спри видеото"><i class="ph ph-pause"></i></button>
    </div>
  </div>
</section>

<section aria-label="Ключови факти">
  <div class="container">
    <div class="stats reveal">
      <div class="stat"><span class="num">55,8 ха</span><span class="lbl">шипка с био сертификат, 2024</span></div>
      <div class="stat"><span class="num">74,9 т</span><span class="lbl">прогнозна реколта шипка, 2024</span></div>
      <div class="stat"><span class="num">0</span><span class="lbl">открити остатъци от пестициди, анализ 2024</span></div>
      <div class="stat"><span class="num">3</span><span class="lbl">инвестиционни проекта с европейско финансиране</span></div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="prod-h">
  <div class="container">
    <div class="section-head reveal">
      <h2 id="prod-h" class="h2">Какво доставяме</h2>
      <p class="t-lg">Четири продукта от собствена суровина. Всеки има спецификация и бутон за запитване на една страница.</p>
    </div>
    <div class="grid-4">{cards}</div>
  </div>
</section>

<section class="tagline" aria-label="Нашият подход">
  <div class="container"><p>{tag}</p></div>
</section>

<section class="section" aria-labelledby="farm-h" style="padding-top:0">
  <div class="container split">
    <div class="split-img reveal"><img src="/img/rosehip-fresh.jpg" alt="Свежи червени шипки, събрани след прибиране" loading="lazy" width="1200" height="800"></div>
    <div style="display:grid;gap:var(--s-400)">
      <div class="section-head reveal" style="margin:0"><h2 id="farm-h" class="h2">Целият път на суровината е при нас</h2>
        <p class="t-lg">Не препродаваме. Отглеждаме, берем, сушим и преработваме сами, затова знаем произхода на всяка партида.</p></div>
      <ul class="checklist">
        <li class="reveal"><span class="ic"><i class="ph ph-plant" aria-hidden="true"></i></span><span><strong>Собствени насаждения</strong><span class="d">Шипка в Климентово, община Аксаково, и лавандула във Венчан, община Провадия.</span></span></li>
        <li class="reveal d1"><span class="ic"><i class="ph ph-drop" aria-hidden="true"></i></span><span><strong>Капково напояване</strong><span class="d">За равномерни добиви и качество при лавандулата.</span></span></li>
        <li class="reveal d2"><span class="ic"><i class="ph ph-snowflake" aria-hidden="true"></i></span><span><strong>Хладилно съхранение</strong><span class="d">Бързо охлаждане на етеричномаслените култури, за да се запазят летливите им вещества.</span></span></li>
        <li class="reveal d3"><span class="ic"><i class="ph ph-factory" aria-hidden="true"></i></span><span><strong>Преработка в Бозвелийско</strong><span class="d">Бавно сушене, смилане и студено пресоване в собствена база, захранвана и от соларна инсталация.</span></span></li>
      </ul>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="how-h" style="padding-top:0">
  <div class="container">
    <div class="section-head reveal"><h2 id="how-h" class="h2">Как да поръчате</h2><p class="t-lg">Три стъпки от запитване до доставка.</p></div>
    <div class="grid-3">
      <div class="step reveal"><span class="n">1</span><h3>Изпратете запитване</h3><p>Продукт, количество и държава на доставка. Отнема около две минути.</p></div>
      <div class="step reveal d1"><span class="n">2</span><h3>Получете оферта и документи</h3><p>Цена, спецификация, био сертификат и анализ от последната реколта.</p></div>
      <div class="step reveal d2"><span class="n">3</span><h3>Мостра и доставка</h3><p>При нужда изпращаме {tbc("мостра")}. След потвърждение уточняваме опаковка и транспорт.</p></div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="docs-h" style="padding-top:0">
  <div class="container">
    <div class="section-head reveal"><h2 id="docs-h" class="h2">Документи, които можете да проверите</h2>
      <p class="t-lg">Сертификатът е публикуван в европейската система TRACES. Анализът е от акредитирана лаборатория.</p></div>
    {docs_block()}
  </div>
</section>

<section class="section" aria-labelledby="eu-h" style="padding-top:0">
  <div class="container">
    <div class="section-head reveal"><h2 id="eu-h" class="h2">Инвестираме в капацитет</h2>
      <p class="t-lg">Около 3,79 млн. лв. публично съфинансиране за напояване, техника, хладилно съхранение, автоматизация и соларна енергия.</p></div>
    <div class="eu">{eu}</div>
  </div>
</section>

<section class="section" aria-labelledby="faq-h" style="padding-top:0">
  <div class="container">
    <div class="section-head reveal"><h2 id="faq-h" class="h2">Често задавани въпроси</h2></div>
    <div class="faq">{faq_html}</div>
  </div>
</section>
{cta_band()}
<script type="application/ld+json">{json.dumps(faq_schema, ensure_ascii=False)}</script>"""
    return layout(key="home", path="/", title="Стефанов НП | Био шипка и лавандула на едро от България",
                  desc="Био сертифицирана шипка и лавандула от собствени насаждения в област Варна. Сушен плод, прах и студено пресовано масло за производители. Поискайте оферта.",
                  body=body, schema=schema)


def page_products():
    cards = "".join(product_card(p, i) for i, p in enumerate(PRODUCTS))
    body = f"""<section class="section" style="padding-top:var(--s-400)"><div class="container">
  <nav class="crumbs" aria-label="Път"><ol><li><a href="/">Начало</a></li><li aria-current="page">Продукти</li></ol></nav>
  <div class="page-head reveal"><h1>Продукти</h1><p>Сушена шипка, шипка на прах, масло от шипкови семки и лавандулов цвят. Всичко от собствени био насаждения в област Варна, на едро.</p></div>
  <div class="grid-4">{cards}</div>
</div></section>{cta_band()}"""
    return layout(key="produkti", path="/produkti.html", title="Продукти | Стефанов НП",
                  desc="Био сушена шипка, шипка на прах, студено пресовано масло от шипкови семки и сушен лавандулов цвят на едро.", body=body)


def page_product(p):
    rows = "".join(f'<div class="row"><dt>{k}</dt><dd>{v}</dd></div>' for k, v in p["spec"])
    uses = "".join(f'<li><i class="ph {ic}" aria-hidden="true"></i>{t}</li>' for ic, t in p["uses"])
    about = "".join(
        f'<details class="reveal"><summary>{t}<i class="ph ph-plus" aria-hidden="true"></i></summary><div class="ans"><p>{d}</p></div></details>' for t, d in p["about"]
    )
    others = "".join(product_card(o, i) for i, o in enumerate([o for o in PRODUCTS if o["slug"] != p["slug"]]))
    schema = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "description": re.sub("<[^>]+>", "", p["lead"]),
              "image": f"{SITE}/img/{p['img']}", "brand": {"@type": "Brand", "name": "Стефанов НП"}, "countryOfOrigin": "BG"}
    body = f"""<section class="section" style="padding-top:var(--s-400)"><div class="container">
  <nav class="crumbs" aria-label="Път"><ol><li><a href="/">Начало</a></li><li><a href="/produkti.html">Продукти</a></li><li aria-current="page">{p['name']}</li></ol></nav>
  <div class="pdp">
    <div class="pdp-media reveal"><div class="main"><img src="/img/{p['img']}" alt="{esc(p['alt'])}" width="1200" height="800"></div></div>
    <div class="pdp-info">
      <span class="eyebrow reveal"{' style="background:var(--lavender-tint);color:var(--lavender)"' if p.get('lav') else ''}><i class="ph ph-seal-check" aria-hidden="true"></i>{p['short']}</span>
      <h1 class="reveal d1">{p['name']}</h1>
      <p class="lead reveal d2">{p['lead']}</p>
      <div class="pdp-actions reveal d2">
        <a class="btn btn-primary" href="/zapitvane.html?product={p['slug']}">Поискайте оферта за {p['name'].lower() if p['slug'] != 'maslo-ot-shipka' else 'маслото'} <i class="ph ph-arrow-right" aria-hidden="true"></i></a>
        <a class="btn btn-secondary" href="/sertifikati.html">Сертификат и анализ</a>
      </div>
      <section class="spec reveal" aria-labelledby="spec-h"><h2 id="spec-h"><i class="ph ph-list-checks" aria-hidden="true"></i>Спецификация</h2><dl>{rows}</dl></section>
      <section class="reveal" aria-labelledby="uses-h" style="display:grid;gap:var(--s-200)"><h2 id="uses-h" class="h3">Приложения</h2><ul class="uses">{uses}</ul></section>
      <section aria-labelledby="about-h" style="display:grid;gap:var(--s-200)"><h2 id="about-h" class="h3 reveal">За суровината</h2><div class="faq">{about}</div></section>
      <p class="note"><i class="ph ph-info" aria-hidden="true"></i>Пълна спецификация на партидата, сертификат и анализ изпращаме с офертата.</p>
    </div>
  </div>
  <div class="sticky-cta"><a class="btn btn-primary" href="/zapitvane.html?product={p['slug']}">Поискайте оферта <i class="ph ph-arrow-right" aria-hidden="true"></i></a>
  </div>
</div></section>
<section class="section" aria-labelledby="more-h" style="padding-top:0"><div class="container">
  <div class="section-head reveal"><h2 id="more-h" class="h2">Други продукти</h2></div>
  <div class="grid-3">{others}</div>
</div></section>{cta_band()}"""
    return layout(key="produkti", path=f"/produkti/{p['slug']}.html", title=f"{p['name']} на едро, био | Стефанов НП",
                  desc=f"{re.sub('<[^>]+>', '', p['lead'])[:150]}", body=body, schema=schema, og_img=f"/img/{p['img']}")


def page_about():
    body = f"""<section class="section" style="padding-top:var(--s-400)"><div class="container">
  <nav class="crumbs" aria-label="Път"><ol><li><a href="/">Начало</a></li><li aria-current="page">За нас</li></ol></nav>
  <div class="page-head reveal"><h1>Фермер и преработвател в едно</h1>
    <p>Стефанов НП отглежда шипка и лавандула в област Варна и сам ги преработва. Затова можем да отговорим за всяка партида, от полето до опаковката.</p></div>
  <div class="split" style="margin-bottom:var(--s-900)">
    <div class="split-img reveal"><img src="/img/rosehip-fresh.jpg" alt="Свежи червени шипки, събрани след прибиране" width="1200" height="800"></div>
    <div class="prose reveal">
      <h2 style="margin-top:0">Как работим</h2>
      <p>Фокусирани сме върху биологично отглеждане и преработка на билки и етеричномаслени култури с методи, които пазят природата и биологичното разнообразие. Използваме възобновяема енергия от собствена соларна инсталация.</p>
      <p>Шипката берем в пълна зрялост и я сушим бавно. Лавандулата сушим по естествен път. Маслото от шипкови семки пресоваме студено в нашата база в Бозвелийско.</p>
      <p>{tbc("История на фирмата, година на основаване и екип: очакват се от клиента.")}</p>
    </div>
  </div>
  <div class="section-head reveal"><h2 class="h2">Къде сме</h2></div>
  <div class="places" style="margin-bottom:var(--s-900)">
    <div class="place reveal"><i class="ph ph-factory" aria-hidden="true"></i><strong>Бозвелийско</strong><span class="muted t-base">База за сушене, преработка и експедиция. Община Провадия.</span></div>
    <div class="place reveal d1"><i class="ph ph-flower" aria-hidden="true"></i><strong>Венчан</strong><span class="muted t-base">Насаждения от лавандула с капково напояване. Община Провадия.</span></div>
    <div class="place reveal d2"><i class="ph ph-plant" aria-hidden="true"></i><strong>Климентово</strong><span class="muted t-base">Насаждения от шипка. Община Аксаково.</span></div>
  </div>
  <div class="section-head reveal"><h2 class="h2">В цифри</h2><p class="t-lg">По данни от био сертификата за 2024 г.</p></div>
  <div class="stats reveal">
    <div class="stat"><span class="num">55,8 ха</span><span class="lbl">шипка с био сертификат</span></div>
    <div class="stat"><span class="num">5,15 ха</span><span class="lbl">лавандула с био сертификат</span></div>
    <div class="stat"><span class="num">74,9 т</span><span class="lbl">прогнозна реколта шипка</span></div>
    <div class="stat"><span class="num">14,1 т</span><span class="lbl">прогнозна реколта лавандула</span></div>
  </div>
  <p class="note" style="margin-top:var(--s-200)"><i class="ph ph-info" aria-hidden="true"></i>{tbc("Старият сайт посочва 900 дка шипка и 220 дка лавандула, включително млади насаждения. Площите в преход се потвърждават от клиента.")}</p>
</div></section>{cta_band()}"""
    return layout(key="za-nas", path="/za-nas.html", title="За нас | Стефанов НП, био ферма в област Варна",
                  desc="Стефанов НП отглежда и преработва био шипка и лавандула в Бозвелийско, Венчан и Климентово, област Варна.", body=body)


def page_certs():
    body = f"""<section class="section" style="padding-top:var(--s-400)"><div class="container">
  <nav class="crumbs" aria-label="Път"><ol><li><a href="/">Начало</a></li><li aria-current="page">Сертификати</li></ol></nav>
  <div class="page-head reveal"><h1>Сертификати и анализи</h1><p>Документите, които получавате и с офертата. Био сертификатът е публичен и можете да го проверите сами.</p></div>
  {docs_block()}
  <div class="prose reveal" style="margin-top:var(--s-800)">
    <h2>Как да проверите био сертификата</h2>
    <p>Всички био оператори в ЕС са публикувани в системата TRACES на Европейската комисия. Отворете връзката „Провери в TRACES“ при сертификата или потърсете номера му в публичния регистър.</p>
    <p>С всяка доставка на био продукт издаваме сертификат за транзакция при поискване.</p>
  </div>
</div></section>{cta_band()}"""
    return layout(key="sertifikati", path="/sertifikati.html", title="Сертификати и анализи | Стефанов НП",
                  desc="Био сертификат по Регламент (ЕС) 2018/848 и анализ за остатъци от пестициди от акредитирана лаборатория.", body=body)


def page_projects():
    items = "".join(f"""<article class="project reveal" id="{p['id']}">
  <img src="/img/{p['img']}" alt="Информационен плакат на проект {p['code']}: {esc(p['funding'])}; {esc(p['amount'])}; период {p['start']} – {p['end']}" width="1200" height="800" loading="lazy">
  <div style="display:grid;gap:var(--s-200)">
    <span class="eyebrow">{p['code']}</span>
    <h2 class="h3">{p['title']}</h2>
    <dl class="meta"><dt>Програма</dt><dd>{p['programme']}</dd><dt>Финансиране</dt><dd>{p['amount']}</dd><dt>Период</dt><dd>{p['start']} – {p['end']}</dd><dt>Статус</dt><dd>{tbc("Приключил, резултатите се потвърждават")}</dd></dl>
    <p class="muted t-base">{p['text']}</p>
  </div>
</article>""" for p in PROJECTS)
    body = f"""<section class="section" style="padding-top:var(--s-400)"><div class="container">
  <nav class="crumbs" aria-label="Път"><ol><li><a href="/">Начало</a></li><li aria-current="page">Проекти</li></ol></nav>
  <div class="page-head reveal"><h1>Проекти с европейско финансиране</h1><p>Три инвестиции в напояване, техника, хладилно съхранение, автоматизация и соларна енергия, с общо около 3,79 млн. лв. публично съфинансиране.</p></div>
  {items}
</div></section>"""
    return layout(key="proekti", path="/proekti.html", title="Проекти с ЕС | Стефанов НП",
                  desc="Проекти BG-RRP-6.004-2420-C01, BG06RDNP001-4.015-0286-C01 и BG06RDNP001-4.012-1695-C01 на Стефанов НП.", body=body)


def page_quote():
    opts = "".join(f'<option value="{p["slug"]}">{p["name"]}</option>' for p in PRODUCTS) + '<option value="drugo">Друго или няколко продукта</option>'
    def err(): return '<p class="err" aria-live="polite"><i class="ph ph-warning-circle" aria-hidden="true"></i><span></span></p>'
    body = f"""<section class="section" style="padding-top:var(--s-400)"><div class="container">
  <nav class="crumbs" aria-label="Път"><ol><li><a href="/">Начало</a></li><li aria-current="page">Запитване</li></ol></nav>
  <div class="page-head reveal"><h1>Запитване за оферта</h1><p>Кажете ни продукта и количеството. Ще върнем цена, спецификация и документи {tbc("до един работен ден")}.</p></div>
  <div class="form-wrap">
    <form class="quote reveal" novalidate>
      <div class="field"><label for="product">Продукт</label>
        <select id="product" name="product" required aria-describedby="product-err"><option value="">Изберете продукт</option>{opts}</select>
        <div id="product-err">{err()}</div></div>
      <div class="field"><label for="form_detail">Форма или спецификация <span class="opt">(по желание)</span></label>
        <input id="form_detail" name="form_detail" type="text" autocomplete="off">
        <p class="hint">Например: цял плод, люспи 3 до 5 мм, нерафинирано масло.</p></div>
      <div class="field-row">
        <div class="field"><label for="quantity">Количество</label>
          <div class="qty"><input id="quantity" name="quantity" type="number" min="0" step="any" inputmode="decimal" required>
          <select name="unit" aria-label="Мерна единица"><option>кг</option><option selected>т</option><option>л</option></select></div>{err()}</div>
        <div class="field"><label for="country">Държава на доставка</label>
          <input id="country" name="country" type="text" autocomplete="country-name" required value="България">{err()}</div>
      </div>
      <div class="field-row">
        <div class="field"><label for="company">Фирма</label><input id="company" name="company" type="text" autocomplete="organization" required>{err()}</div>
        <div class="field"><label for="name">Лице за контакт <span class="opt">(по желание)</span></label><input id="name" name="name" type="text" autocomplete="name"></div>
      </div>
      <div class="field-row">
        <div class="field"><label for="email">Имейл</label><input id="email" name="email" type="email" autocomplete="email" required>{err()}</div>
        <div class="field"><label for="phone">Телефон <span class="opt">(по желание)</span></label><input id="phone" name="phone" type="tel" autocomplete="tel" inputmode="tel"></div>
      </div>
      <div class="field"><label for="message">Съобщение <span class="opt">(по желание)</span></label><textarea id="message" name="message" rows="4"></textarea>
        <p class="hint">Срок за доставка, опаковка, нужни документи, мостра.</p></div>
      <div class="field check-field"><label class="check"><input type="checkbox" name="consent" required>
        <span>Съгласен съм данните ми да се използват само за отговор на това запитване. <a href="/poveritelnost.html">Поверителност</a></span></label>{err()}</div>
      <div class="form-status" role="status" aria-live="polite"></div>
      <div><button class="btn btn-primary" type="submit">Изпратете запитването <i class="ph ph-paper-plane-tilt" aria-hidden="true"></i></button></div>
    </form>
    <aside style="display:grid;gap:var(--s-300)" id="kontakt">
      <div class="aside-card reveal"><h2>Предпочитате разговор?</h2>
        <a class="line" href="{PHONE_HREF}"><i class="ph ph-phone" aria-hidden="true"></i>{PHONE}</a>
        <a class="line" href="mailto:{EMAIL}"><i class="ph ph-envelope-simple" aria-hidden="true"></i>{EMAIL}</a>
        <p class="muted t-base">Понеделник – петък, 08:00 – 18:00<br>с. Бозвелийско, общ. Провадия, обл. Варна</p></div>
      <div class="aside-card reveal d1"><h2>Какво следва</h2>
        <ol style="margin:0;padding-left:var(--s-300);display:grid;gap:var(--s-75)" class="t-base muted">
          <li>Потвърждаваме наличност за реколтата.</li><li>Изпращаме цена, спецификация, сертификат и анализ.</li><li>При нужда изпращаме {tbc("мостра")}.</li></ol></div>
    </aside>
  </div>
</div></section>"""
    return layout(key="zapitvane", path="/zapitvane.html", title="Запитване за оферта | Стефанов НП",
                  desc="Поискайте оферта за био шипка, шипка на прах, масло от шипкови семки или лавандулов цвят на едро.", body=body)


def page_privacy():
    body = f"""<section class="section" style="padding-top:var(--s-400)"><div class="container">
  <nav class="crumbs" aria-label="Път"><ol><li><a href="/">Начало</a></li><li aria-current="page">Поверителност</li></ol></nav>
  <div class="page-head"><h1>Поверителност и условия</h1><p>{tbc("Текстът е чернова за прототипа и се одобрява от клиента и юрист.")}</p></div>
  <div class="prose">
    <h2>Какви данни събираме</h2>
    <p>Само данните, които въвеждате в запитването: фирма, лице за контакт, имейл, телефон и детайли за поръчката. Използваме ги единствено, за да отговорим на запитването ви.</p>
    <h2>Колко дълго ги пазим</h2><p>{tbc("До 24 месеца след последната кореспонденция, освен ако закон не изисква друго.")}</p>
    <h2>Вашите права</h2><p>Можете да поискате достъп, корекция или изтриване на данните си на {EMAIL}.</p>
    <h2 id="usloviya">Условия за ползване</h2><p>Информацията на сайта е с ориентировъчен характер. Цени, наличности и спецификации се потвърждават в писмена оферта.</p>
  </div>
</div></section>"""
    return layout(key="", path="/poveritelnost.html", title="Поверителност и условия | Стефанов НП", desc="Как Стефанов НП използва данните от запитванията.", body=body)


def page_404():
    links = "".join(f'<li><a href="/produkti/{p["slug"]}.html">{p["name"]}</a></li>' for p in PRODUCTS)
    body = f"""<section class="section"><div class="container"><div class="nf">
  <span class="code">ГРЕШКА 404</span>
  <h1 class="h2">Тази страница не съществува</h1>
  <p class="muted t-lg">Възможно е адресът да е сгрешен или страницата да е преместена при новия сайт.</p>
  <div class="hero-actions"><a class="btn btn-primary" href="/">Към началото</a><a class="btn btn-secondary" href="/zapitvane.html">Запитване за оферта</a></div>
  <div><p class="t-base muted" style="margin-bottom:var(--s-75)">Продукти:</p><ul style="margin:0;padding-left:var(--s-300)" class="t-base">{links}</ul></div>
  <p class="t-base muted">Или ни пишете на <a href="mailto:{EMAIL}">{EMAIL}</a>, телефон <a href="{PHONE_HREF}">{PHONE}</a>.</p>
</div></div></section>"""
    return layout(key="", path="/404.html", title="Страницата не е намерена | Стефанов НП", desc="Страницата не е намерена.", body=body)


# --------------------------------------------------------------------------- build
def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for sub in ("img", "video", "docs"):
        shutil.copytree(SRC / sub, DIST / sub)
    shutil.copy(SRC / "styles.css", DIST / "styles.css")
    shutil.copy(SRC / "main.js", DIST / "main.js")
    pages = {
        "index.html": page_home(), "produkti.html": page_products(), "za-nas.html": page_about(),
        "sertifikati.html": page_certs(), "proekti.html": page_projects(), "zapitvane.html": page_quote(),
        "poveritelnost.html": page_privacy(), "404.html": page_404(),
    }
    for p in PRODUCTS:
        pages[f"produkti/{p['slug']}.html"] = page_product(p)
    for name, content in pages.items():
        out = DIST / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    urls = "".join(f"<url><loc>{SITE}/{'' if n == 'index.html' else n}</loc></url>" for n in pages if n != "404.html")
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', encoding="utf-8")
    print(f"built {len(pages)} pages into {DIST}")


if __name__ == "__main__":
    main()
