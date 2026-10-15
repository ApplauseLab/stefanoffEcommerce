# stefanoff.bg website (styleguide v1.0)

```bash
python3 build.py        # writes dist/
python3 serve.py 4175   # http://localhost:4175
```

- `build.py`: page templates. Product, project and contact copy is imported from `../redesign/build.py` (single source).
- `src/site.css`, `src/site.js`: components and behaviour. All values come from `../styleguide/tokens.css` (copied into dist on build).
- `src/icons/`: Phosphor Light SVGs, coloured through CSS masks.
- `src/vendor/lenis.min.js`: smooth scroll (lerp 0.1, wheelMultiplier 0.7; off under reduced motion).

Pages: home, products and 5 product pages, farm, certificates, EU projects, quote request, privacy, 404.
Values with a dotted underline await client confirmation. Photos are temporary stock until the farm shoot.
The emblem is two aligned PNG layers cut from `brand/stefanoff-logo-on-dark.png` (`stefanoff-logo-type.png`, and `stefanoff-logo-leaves.png` with the green 18 % darker), so on the home page the leaf star turns into place before the type rises in. Regenerate both from the SVG when it arrives.
On screens wider than 1374 px the type, text widths and container keep growing to SEM's proportions (content 1620 px wide at 1920); `--u` in `tokens.css` is the fluid pixel behind the text widths.
The logo is a temporary PNG extraction (`img/mark-line-*.png`); replace it with the SVG when it is ready.
Chat is the client's live Tidio account (key in `src/site.js`), so anything typed in it reaches the business. The chat icon beside the phone in the header (and the `[data-chat]` buttons in the contact lists) opens a black drawer from the right; Tidio loads on the first open and docks into the drawer body through CSS injected into its shadow root (`DOCK` in `site.js`): bubble and its own close hidden, colours, corners and font from its CSS variables, greeting hidden because the drawer has its own title. If Tidio renames `#tidio-chat-root`, `.chat` or `.chat-header`, the chat still works but falls back to Tidio's own layout. Once a visitor has opened it, later pages preload it so a reply opens the drawer. If it fails to load, the drawer shows phone, email and the quote form. Tidio skips headless Chrome; test it with a normal user agent. Greeting copy and offline hours are set in the Tidio dashboard.
Black bands (`.band`, `--black`) sit behind groups of photos: the home products and process rows, the products page and "Други продукти". `banners()` in `build.py` lays them out on 12 columns with mixed spans and one aspect ratio, after the Tsimbidi reference.
The quote form validates on the page and opens a pre-filled email to office@stefanoff.bg; connect a form endpoint before launch.

See "Store" below for the quote bag.

## Story (home page)
The home page reads as one story, from the client's text "Булаир – земя на древни порти и защитена природа":
hero → intro "От земя с история. С грижа за природата." → statement → I Хемските порти (text + timeline, sources) →
growing photo → II Защитена природа (3 Натура 2000 zones, honest note, sources) → III Как работим → IV Какво отглеждаме (5 products) →
numbers, how to order, EU projects, FAQ, closing CTA. Data lives in TIMELINE, ZONES, SOURCES in build.py.
Rules kept from the client text: no claim that the plot is inside BG0002045; Натура 2000 is not presented as "bio";
gate dates stay hedged; "food as medicine" only in the logo. Бял трън (`/produkti/bial-trun.html`) has a drawn placeholder
image (`redesign/src/img/bial-trun.jpg`) and its bio status marked as awaiting confirmation. Needed from the client: photos of the
Хемските порти ruins, the Булаир fields and hawthorn; the official Натура 2000 property check for 07034.17.10; a certificate covering hawthorn.

## Spacing

All margins, paddings and gaps use one scale, taken from IBM Carbon's published spacing scale (the same values as Atlassian's 8 px scale): 2, 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96, 160 px, as `--s-0` … `--s-40` in `styleguide/tokens.css`.
No fluid in-between values: layout spacing steps up at breakpoints (Carbon's rule), via `--section` (80 / 96 / 160), `--gutter` (16 / 24 / 40), `--inset` (24 / 48 / 64) and `--panel` (32 / 48 / 80) at 600 and 1100 px.
Offsets below the fixed nav are `var(--nav-h)` + a scale step. Above 1600 px the root size grows with the window, so the whole layout scales.

## English version

`build.py` builds every page twice: Bulgarian at `/`, English at `/en/` (same paths, e.g. `/en/fermata.html`).
The Bulgarian copy stays the single source. `i18n.py` re-renders each built page into English by looking up every text node and attribute in `i18n/en.json` (Bulgarian string → English).
If a Bulgarian string has no translation, the build stops and lists it in `i18n/missing.txt`: add the line to `en.json` and rebuild.
Interface strings in `site.js` (menu button, form errors, the composed email) switch on `<html lang>`.
The BG/EN switch links to the same page in the other language; pages carry `hreflang` alternates and the sitemap lists both languages.

## Store (quote bag)

The products work like a shop, but nothing is paid: visitors add products to a bag and send the whole bag as one enquiry. Layout after Awwwards e-commerce sites: Agrumea Farm (shop in chapters, few products), Morpho Water (price per unit, stepper joined to the add button, accordions), Deadly Ponies (gallery left, sticky buy column right).

- **Data:** `SHOP` in `build.py`, keyed by product slug: chapter (`CATS`), badge, forms, pack sizes, the pack quick add picks (`def`) and price tiers `(from quantity, € per unit)`. `FEATURED` lists the three products on the home page.
- **Every value in `SHOP` is a placeholder** (dotted underline on the page): prices (EUR, VAT excluded), forms, pack sizes and badges. Replace them when the client sends a price list.
- **Products page:** one chapter per category (Шипка, Лавандула, Бял трън). The floating bar at the bottom ("Tabs sliding") follows the chapter on screen.
- **Product page:** gallery with placeholder frames for the missing shots ("Отблизо", "Опаковка", "На полето"); buy column with live price per unit and per pack (the price pops in when the quantity reaches the next tier), form and pack pills, stepper, "Добавете към запитването", "Поискайте мостра" (opens the form with the product chosen and a sample request in the message).
- **Bag:** `bag` in `site.js`, stored in `localStorage` (`stefanoff.bag`) as ids only, so it survives page changes and the language switch, and names come from the page's `#shop-data` JSON (translated with the page). Nav icon with a count ("Notification badge"), drawer from the right, toast on add ("Toast").
- **Quote form:** with items in the bag, the bag replaces the product and quantity fields; the email lists every line with its estimate. The bag empties once the email is prepared.
- **English:** prices and pack sizes are generated, not typed into `en.json`: `price_txt()`, `qty_txt()` and `per_txt()` record their English in `AUTO_EN`, which the build adds to the translation table.
- **Client to-dos:** price list and minimum quantities, real pack sizes and forms, close-up, packaging and field photos for each product, hawthorn photo and organic status.
