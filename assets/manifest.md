# Asset manifest

Downloaded 2026-10-12 from the Dream Shop CDN (`cdn.mydreamshop.io`, still public) and from Google Drive (public links on `/certificates`).
CDN base for page images: `https://cdn.mydreamshop.io/source/private/stefanoff/pages/attachments/`

> **Licence warning:** every product photo and both videos look like **stock** (studio or styled shots, not the Stefanoff farm). Ask the client where they came from and whether the licence covers a new site. Either way, the redesign needs **real farm photography**: fields at Venchan and Klimentovo, harvest, drying, the press, packaging, the team. Authentic images are a large trust signal for B2B buyers (see audit F9).

## Logo

| File | Size | Bytes | Source | Notes |
|---|---|---|---|---|
| `logo/logo.png` | 180×60 | 4 KB | `…/application.themes.logo_header/A/1705222130988865a39ff2f1685377.png` | White rosehip line drawing in a white rounded square + "stefanoff" wordmark, for a purple background |
| `logo/logo@2x.png` | 360×120 | 8 KB | same, `@2x` | Largest available. **Ask for vector (SVG/AI/PDF)** |

## Images

| File | Size | Bytes | Used on | CDN file | What it shows | Reuse? |
|---|---|---|---|---|---|---|
| `images/rosehip-01-shipka.png` | 1200×800 | 2.0 MB | `/rosehip`, "Шипка" | `d3b70dd…/17046546836203659af75b9776842.png` | Full-frame fresh red rosehips | Usable as a texture or background (likely stock) |
| `images/rosehip-02-powder.png` | 1200×800 | 0.95 MB | `/rosehip`, "Шипка на прах" | `d3b70dd…/17046549653622659af87558737565.png` | Orange powder in a clay bowl, fresh hips, white background | Stock; usable as a placeholder |
| `images/rosehip-03-tea.png` | 1200×800 | 1.4 MB | `/rosehip`, "Чай от шипки" | `d3b70dd…/17046550754384659af8e36b0c1113.png` | Glass teapot on wood, moody styling | Stock or AI-like; drop |
| `images/rosehip-04-dried-flakes.png` | 1200×800 | 2.6 MB | `/rosehip`, "Сушена шипка" | `d3b70dd…/17046551713533659af9435643b464.png` | Dried whole hips in a dark tray, burlap, blue boards | Closest to the actual product; still stock |
| `images/rosehip-oil-01.png` | 1200×675 | 1.2 MB | `/rosehip-oil` block 2 | `2c08367…/1705227133599865a3b37d92720311.png` | Corked bottle of red oil with fresh hips on wood | Stock |
| `images/rosehip-oil-02.png` | 1200×675 | 1.2 MB | `/rosehip-oil` block 3 | `2c08367…/1705230929700265a3c251ac059201.png` | Three essential-oil vials, candle, amber (spa mood) | Off-brand for B2B; drop |
| `images/rosehip-oil-03.png` | 1200×675 | 0.96 MB | `/rosehip-oil` block 4 | `2c08367…/1705231320883965a3c3d8d7ccb109.png` | Oil bottle with twine, dried hips in a wooden scoop | Stock |
| `images/lavender-01-flowers.png` | 1200×800 | 1.7 MB | `/lavender` | `7a5620e…/17046548009375659af7d0e4e6410.png` | Dried lavender buds in a white bowl with a wooden scoop, stems behind | Stock; usable as a placeholder |
| `images/project-BG-RRP-6.004-2420-C01.png` | 1200×800 | 135 KB | `/projects` block 1 | `ce36fd8…/175226166359696871641f91bca200.png` | RRF / NextGenerationEU publicity poster: beneficiary, title, contract, value 617,850.00 лв (282,827.75 лв grant), 25.06.2024–25.06.2025 | **Keep** (mandatory publicity). Rebuild its text in HTML |
| `images/project-BG06RDNP001-4.015-0286-C01.png` | 1200×800 | 211 KB | `/projects` block 2 | `ce36fd8…/17531263246737687e95b4a47e9224.png` | EAFRD / ПРСР 2014–2020 poster, sub-measure 4.2: public expenditure 2,574,828.47 лв, 03.08.2023–26.08.2025 | **Keep** |
| `images/project-BG06RDNP001-4.012-1695-C01.png` | 1200×800 | 274 KB | `/projects` block 3 | `ce36fd8…/17531252421266687e917a1f0e810.png` | EAFRD / ПРСР 2014–2020 poster, sub-measure 4.1: public expenditure 930,445.23 лв, 27.01.2023–25.08.2025 | **Keep** |

Note: the newer CDN files (projects) return 403 unless requested with `Referer: https://stefanoff.bg/` (hotlink protection).

## Video

| File | Size | Length | Bytes | Used on | CDN file | Notes |
|---|---|---|---|---|---|---|
| `video/home-hero.mp4` | 1800×1000 | 11.8 s loop | 8.4 MB | Home hero (embedded **twice**: once visible, once in a hidden duplicate block) | `783df04…/17046290178393659a9319cced7178.mp4` | Close-up of a spoon of glossy rosehips over a bed of hips. Strong visual; re-encode to H.264/WebM under 2 MB and add a poster frame |
| `video/rosehip-oil-hero.mp4` | 1200×674 | — | 4.6 MB | `/rosehip-oil` top | `2c08367…/1705226830574665a3b24e8c4d4896.mp4` | Oil poured into a glass jar, dried hips, white seamless background. Clean; usable for the oil page |

## Certificates

| File | Pages | Source | Content |
|---|---|---|---|
| `certificates/certificate-organic-production-eu-2018-848.pdf` | 6 | Drive `1lviUaxP-SHclqaqnLjOmeehRsgBvE5aH` | EU organic certificate BG-BIO-22.100-0003115.2024.001, Nutramed (BG-BIO-22), valid 11.03.2024–**29.12.2024 (expired)**. BG + EN |
| `certificates/certificate-of-analysis-rosehip-24-000523.pdf` | 7 | Drive `1AqGnfI-Mvvm4a_Kyl75hDmpEmS5HeXYD` | Primoris Lab pesticide-residue analysis, organic rosehips, 30.01.2024, result: no residues ≥ reporting limit |
| `certificates/thumb-rosehip-analysis.png` | 500×625 | CDN `7ca9511…/1707073089082665bfde41142d3117.png` | Thumbnail of page 1 of the lab report |
| `certificates/thumb-organic-production.png` | 500×625 | CDN `7ca9511…/171070813110465f755a319650351.png` | Thumbnail of page 1 of the organic certificate |

## Not recovered (ask the client)

- Vector versions of the logo and of the EU / NextGenerationEU / EAFRD / "Една посока, много възможности" publicity logos
- Favicon and social share (OG) image. There is no `og:image` on any page
- Any original (non-stock) photography

## Chapter I era images (site/src/img/eras)

| File | Source | Licence | Credit shown on site |
|---|---|---|---|
| `era-1-palisade.jpg` | Drawn (`assets/eras/draw_eras.py`) | own | Илюстрация |
| `era-2-wall.jpg` | Drawn (`assets/eras/draw_eras.py`) | own | Илюстрация |
| `era-3-skorpil.jpg` | Wikimedia Commons, `BASA-3K-7-526-43-Karel Škorpil.jpg` (Bulgarian Archives State Agency; photographer Onorio Marcolesco), sepia-toned and cropped | Public domain | Карел Шкорпил. Държавна агенция „Архиви“, обществено достояние |
| `era-4-kamchia.jpg` | Wikimedia Commons, `Zashtitena zona Kamchiska planina.jpg` by Viatarko, cropped | CC BY-SA 4.0 | Защитена зона „Камчийска планина“. Viatarko, CC BY-SA 4.0 |

Natura 2000 map (`site/src/brand/natura-map.svg`): zone outlines from the EEA Natura2000Sites MapServer (layer 2), simplified; river and coast schematic. Script: `assets/natura/make_map.py`.

Update 2026-10-14: the drawn IV and V–VI c. images were replaced.
| `era-1-tabula.jpg` | Wikimedia Commons, `TabulaPeutingeriana.jpg` (Konrad Miller facsimile 1887/88), crop of Thrace, Pontus and Constantinople | Public domain | Tabula Peutingeriana, римска пътна карта (IV в.). Факсимиле К. Милер, 1887, обществено достояние |
| `era-2-hisarya.jpg` | Wikimedia Commons, `Hisarya-CityWallsOfDiocletianopol01.jpg` by Gitanes232 | CC BY-SA 4.0 | Късноантична стена от епохата (Диоклецианопол, дн. Хисаря). Gitanes232, CC BY-SA 4.0 |
Note: era 2 shows a contemporary late-antique wall elsewhere in Bulgaria, labelled as such; replace with a photo of the Хемски порти ruins when the client provides one.

## Chapter II map tour (replaces the step map, 2026-10-14)

| File | Source | Licence | Credit shown on site |
|---|---|---|---|
| `site/src/img/natura/kamchiyska-fields*.jpg` | Wikimedia Commons, `Panorama of Venelin village, Dolni Chiflik Municipality, Bulgaria (2026-05-16).jpg` by Webchillie, left third cropped | CC BY-SA 4.0 | Снимка: поле край Венелин, община Долни чифлик. Webchillie, CC BY-SA 4.0 |
| `site/src/brand/natura-tour.svg` | Bulgaria outline: Natural Earth 1:10m admin-0 (public domain). Zones: EEA Natura2000Sites MapServer. River Kamchia: OpenStreetMap via Overpass | PD / EEA reuse / ODbL | Граници: ЕАОС „Натура 2000“, Natural Earth. Река: © OpenStreetMap |

Script: `assets/natura/make_tour.py` (projects everything to km so the camera can zoom from the country to the zones). Replace the photo with a client photo of the Булаир fields when available.
