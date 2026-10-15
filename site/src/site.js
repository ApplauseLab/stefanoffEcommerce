(() => {
  const root = document.documentElement;
  const reduced = root.classList.contains("reduced");
  const P = root.dataset.base || "";   // site sub-path when hosted under one (GitHub Pages), set by build.py --base

  // Interface strings, by page language (the page copy itself is translated at build time, see i18n.py)
  const L = {
    bg: { menu: "Меню", close: "Затвори",
      errProduct: "Изберете продукт.", errQty: "Въведете количество.", errQtyPos: "Въведете число, например 2,5.",
      errCountry: "Въведете държава на доставка.", errCompany: "Въведете име на фирмата.", errEmail: "Въведете имейл.",
      errEmailBad: "Проверете имейла, например name@firma.bg.", errConsent: "Нужно е съгласие, за да отговорим.",
      fixFields: (n) => (n === 1 ? "Остава 1 поле." : `Остават ${n} полета.`),
      mProduct: "Продукт", mForm: "Форма / спецификация", mQty: "Количество", mCountry: "Държава на доставка", mCompany: "Фирма",
      mName: "Лице за контакт", mEmail: "Имейл", mPhone: "Телефон", mSubject: "Запитване",
      copied: "Копирано", copyFail: "Копирайте ръчно",
      added: "Добавено", remove: "Премахнете", fewer: "По-малко", more: "Повече", packs: "Брой опаковки",
      lineSub: (f, q, pk) => `${f}, ${q} × ${pk}`, packTotal: (q, pk, u, s) => `${q} × ${pk} = ${u}, ${s}`,
      bagLabel: (n) => (n ? `Запитване: ${n} ${n === 1 ? "продукт" : "продукта"}` : "Запитване: няма продукти"),
      count: (n) => (n === 1 ? "1 продукт" : `${n} продукта`), edit: "Редактирайте", inBag: "Продукти в запитването",
      estimate: "Ориентировъчно, без ДДС", mLines: "Продукти", mTotal: "Ориентировъчна стойност (примерни цени, без ДДС)",
      sampleMsg: "Бихме искали мостра." },
    en: { menu: "Menu", close: "Close",
      errProduct: "Choose a product.", errQty: "Enter a quantity.", errQtyPos: "Enter a number, for example 2.5.",
      errCountry: "Enter the delivery country.", errCompany: "Enter the company name.", errEmail: "Enter your email.",
      errEmailBad: "Check the email, for example name@company.com.", errConsent: "We need your consent to reply.",
      fixFields: (n) => (n === 1 ? "1 field left." : `${n} fields left.`),
      mProduct: "Product", mForm: "Form / specification", mQty: "Quantity", mCountry: "Delivery country", mCompany: "Company",
      mName: "Contact person", mEmail: "Email", mPhone: "Phone", mSubject: "Enquiry",
      copied: "Copied", copyFail: "Copy it by hand",
      added: "Added", remove: "Remove", fewer: "Fewer", more: "More", packs: "Number of packs",
      lineSub: (f, q, pk) => `${f}, ${q} × ${pk}`, packTotal: (q, pk, u, s) => `${q} × ${pk} = ${u}, ${s}`,
      bagLabel: (n) => (n ? `Enquiry: ${n} ${n === 1 ? "product" : "products"}` : "Enquiry: no products"),
      count: (n) => (n === 1 ? "1 product" : `${n} products`), edit: "Edit", inBag: "Products in the enquiry",
      estimate: "Estimate, VAT excluded", mLines: "Products", mTotal: "Estimated value (example prices, VAT excluded)",
      sampleMsg: "We would like a sample." },
  }[root.lang === "en" ? "en" : "bg"];

  // Scroll lock for the menu, chat and bag. Hiding the scrollbar would widen the page and shift everything behind the
  // drawer, so the scrollbar's width is measured first and given back as padding to the page and the fixed bars.
  const locks = new Set();
  const lockScroll = (who, on) => {
    if (on && !locks.size) root.style.setProperty("--lock-pad", `${Math.max(0, innerWidth - root.getBoundingClientRect().width)}px`);
    on ? locks.add(who) : locks.delete(who);
    root.classList.toggle("scroll-locked", locks.size > 0);
  };

  // Smooth, weighted wheel scroll (touch stays native). Off under reduced motion.
  let lenis = null;
  if (!reduced && window.Lenis) {
    lenis = new Lenis({ lerp: 0.1, wheelMultiplier: 0.7, gestureOrientation: "vertical", smoothWheel: true, syncTouch: false });
    const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
    document.addEventListener("click", (e) => {
      const a = e.target.closest('a[href^="#"]');
      if (!a) return;
      const id = a.getAttribute("href");
      if (id.length < 2) return;
      const target = id === "#top" ? 0 : document.querySelector(id);
      if (target === null) return;
      e.preventDefault();
      lenis.scrollTo(target, { offset: id === "#top" ? 0 : -104, duration: 1.6, easing: (t) => 1 - Math.pow(1 - t, 4) });
      if (id !== "#main") history.replaceState(null, "", id);
    });
  }

  // Nav: scrim and centred mark once the hero has left (inner pages: after a small scroll)
  const nav = document.getElementById("nav");
  const hero = document.querySelector(".hero");
  if (nav) {
    if (hero && "IntersectionObserver" in window) {
      new IntersectionObserver(([e]) => nav.classList.toggle("scrolled", !e.isIntersecting), { rootMargin: "-88px 0px 0px 0px" }).observe(hero);
    } else {
      const onS = () => nav.classList.toggle("scrolled", scrollY > 24);
      addEventListener("scroll", onS, { passive: true }); onS();
    }
  }

  // Hide the nav while scrolling down; show it on scroll up, near the top, when the pointer reaches the top
  // edge (or hovers the nav), on keyboard focus, and whenever the menu or chat is open. On the home page it
  // stays put until the emblem has finished flying into it (one screen of scroll).
  if (nav) {
    const peek = document.querySelector(".nav-peek");
    let lastY = scrollY, hovering = false, ticking2 = false;
    const pinned = () => hovering || nav.contains(document.activeElement) || nav.classList.contains("menu-open") || document.documentElement.classList.contains("chat-open") || document.body.classList.contains("chat-open");
    const floor = () => (nav.classList.contains("is-home") ? innerHeight : 0) + 120;
    const evaluate = () => {
      ticking2 = false;
      const y = scrollY, dy = y - lastY;
      if (Math.abs(dy) < 6 && y > floor()) return;
      if (y <= floor() || dy < 0 || pinned()) nav.classList.remove("nav-hidden");
      else if (dy > 0) nav.classList.add("nav-hidden");
      lastY = y;
    };
    addEventListener("scroll", () => { if (!ticking2) { ticking2 = true; requestAnimationFrame(evaluate); } }, { passive: true });
    const show = () => { hovering = true; nav.classList.remove("nav-hidden"); };
    const leave = () => { hovering = false; };
    if (peek) peek.addEventListener("pointerenter", show);
    nav.addEventListener("pointerenter", show);
    nav.addEventListener("pointerleave", leave);
    nav.addEventListener("focusin", () => nav.classList.remove("nav-hidden"));
  }

  // Emblem flight (home): one element, large in the middle of the hero, shrinking into the centre
  // of the nav over one viewport of scroll. Same curve as the reference: ease-out, position and
  // scale on the same progress. Inner pages and reduced motion: the emblem simply sits in the nav.
  const fly = document.getElementById("logoFly");
  const isHome = nav && nav.classList.contains("is-home");
  let flyOn = false, restY = 0, restH = 1, startS = 1, lastY = -1;
  const measure = () => {
    fly.style.setProperty("--fly-y", "0px"); fly.style.setProperty("--fly-s", "1");
    const r = fly.getBoundingClientRect();
    restY = r.top + r.height / 2; restH = r.height;
    const target = Math.min(innerHeight * 0.46, innerWidth * 0.72, 27.5 * parseFloat(getComputedStyle(document.documentElement).fontSize));
    startS = Math.max(1, target / restH);
    lastY = -1;
  };
  const flyFrame = () => {
    if (!flyOn) return;
    const y = scrollY;
    if (y !== lastY) {
      lastY = y;
      const t = Math.min(1, Math.max(0, y / innerHeight));
      const q = 1 - (1 - t) * (1 - t);
      fly.style.setProperty("--fly-y", ((innerHeight / 2 - restY) * (1 - q)).toFixed(2) + "px");
      fly.style.setProperty("--fly-s", (startS + (1 - startS) * q).toFixed(4));
    }
    requestAnimationFrame(flyFrame);
  };
  if (fly && isHome && !reduced) {
    measure();
    flyOn = true; requestAnimationFrame(flyFrame);
    requestAnimationFrame(() => fly.classList.add("ready"));
    addEventListener("resize", measure);
  }

  // Card arrows: transitions.dev icon swap, chevron (a) to arrow (b) while the card is hovered or focused
  document.querySelectorAll(".banner").forEach((card) => {
    const sw = card.querySelector(".t-icon-swap");
    if (!sw) return;
    const set = (s) => () => sw.setAttribute("data-state", s);
    card.addEventListener("pointerenter", set("b"));
    card.addEventListener("pointerleave", set("a"));
    card.addEventListener("focus", set("b"));
    card.addEventListener("blur", set("a"));
  });

  // Nav CTA rosehips: grow on hover / keyboard focus only
  const grow = document.querySelector("[data-cta-grow]");
  if (grow && !reduced) {
    let hold = false, timer = 0;
    const on = () => { hold = true; clearTimeout(timer); grow.classList.add("is-grown"); };
    const off = () => { hold = false; grow.classList.remove("is-grown"); };
    grow.addEventListener("pointerenter", on);
    grow.addEventListener("pointerleave", off);
    grow.addEventListener("focusin", on);
    grow.addEventListener("focusout", off);
  }

  // Language switch (transitions.dev "Tabs sliding"): the pill slides to the chosen language, the page fades out,
  // and the other language opens where the reader was: same section, same position inside it.
  const sw = document.querySelector("[data-lang-switch]");
  if (sw) {
    const pill = sw.querySelector(".t-tabs-pill"), tabs = [...sw.querySelectorAll(".t-tab")];
    const moveTo = (tab, animate) => {
      if (!animate) {
        const prev = pill.style.transition;
        pill.style.transition = "none";
        pill.style.transform = `translateX(${tab.offsetLeft}px)`;
        pill.style.width = `${tab.offsetWidth}px`;
        void pill.offsetWidth;
        pill.style.transition = prev;
      } else {
        pill.style.transform = `translateX(${tab.offsetLeft}px)`;
        pill.style.width = `${tab.offsetWidth}px`;
      }
    };
    const active = () => tabs.find((t) => t.getAttribute("aria-current") === "true") || tabs[0];
    requestAnimationFrame(() => { moveTo(active(), false); sw.classList.add("is-ready"); });
    addEventListener("resize", () => moveTo(active(), false));
    // where the reader is: the section at the top of the screen (pages share their structure across languages)
    const blocks = () => [...document.querySelectorAll("main section, main > div > section, footer")];
    const here = () => {
      const list = blocks(), top = 0.25 * innerHeight;
      const i = list.findIndex((el) => { const r = el.getBoundingClientRect(); return r.bottom > top; });
      if (i < 0) return { i: -1, f: 0 };
      const r = list[i].getBoundingClientRect();
      return { i, f: Math.max(0, (top - r.top) / Math.max(1, r.height)) };
    };
    const dur = parseFloat(getComputedStyle(root).getPropertyValue("--tabs-dur")) || 250;
    tabs.forEach((tab) => tab.addEventListener("click", (e) => {
      if (tab.getAttribute("aria-current") === "true") { e.preventDefault(); return; }
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;   // new tab / window: leave it to the browser
      e.preventDefault();
      try { sessionStorage.setItem("langSwitch", JSON.stringify({ ...here(), y: scrollY })); } catch (_) {}
      tabs.forEach((t) => t.setAttribute("aria-current", t === tab ? "true" : "false"));
      moveTo(tab, true);
      if (!reduced) root.classList.add("lang-leaving");
      setTimeout(() => { location.href = tab.href; }, reduced ? 0 : dur);
    }));
    addEventListener("pageshow", (e) => { if (e.persisted) root.classList.remove("lang-leaving"); moveTo(active(), false); });
    // the BG/EN pair in the mobile menu hands off through the same switch (fade, same scroll position)
    document.querySelectorAll(".menu-lang-tab").forEach((t) => t.addEventListener("click", (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
      e.preventDefault();
      sw.querySelector(`.t-tab[data-lang="${t.dataset.lang}"]`)?.click();
    }));
    // arrival: put the reader back in the same section, then let the fade-in play
    let saved = null;
    try { saved = JSON.parse(sessionStorage.getItem("langSwitch") || "null"); sessionStorage.removeItem("langSwitch"); } catch (_) {}
    if (saved) {
      if ("scrollRestoration" in history) history.scrollRestoration = "manual";
      const list = blocks(), el = list[saved.i];
      const y = el ? el.getBoundingClientRect().top + scrollY + saved.f * el.offsetHeight - 0.25 * innerHeight : saved.y;
      const go = Math.max(0, Math.round(y));
      lenis ? lenis.scrollTo(go, { immediate: true, force: true }) : scrollTo(0, go);
      setTimeout(() => root.classList.remove("lang-arriving"), 450);
    }
  }

  // Mobile menu
  const btn = document.querySelector(".nav-menu-btn");
  const menu = document.getElementById("menu");
  let closeMenu = () => {};
  if (btn && menu) {
    menu.setAttribute("inert", "");
    const set = (open) => {
      menu.classList.toggle("open", open);
      menu.toggleAttribute("inert", !open);
      btn.setAttribute("aria-expanded", String(open));
      btn.textContent = open ? L.close : L.menu;
      lockScroll("menu", open);
      if (lenis) open ? lenis.stop() : lenis.start();
      nav.classList.toggle("menu-open", open);
      if (open) menu.querySelector("a")?.focus({ preventScroll: true });
    };
    closeMenu = () => { if (menu.classList.contains("open")) set(false); };
    btn.addEventListener("click", () => set(!menu.classList.contains("open")));
    menu.addEventListener("click", (e) => { if (e.target.closest("a")) set(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && menu.classList.contains("open")) { set(false); btn.focus(); } });
    matchMedia("(min-width: 1300px)").addEventListener("change", (m) => { if (m.matches) set(false); });
  }

  // Videos: decorative loops, playing only while on screen. Reduced motion keeps the poster.
  document.querySelectorAll("[data-video] video").forEach((video) => {
    if (reduced) { video.pause(); return; }
    if (!("IntersectionObserver" in window)) return void video.play().catch(() => {});
    new IntersectionObserver(([e]) => (e.isIntersecting ? video.play().catch(() => {}) : video.pause()), { threshold: 0.2 }).observe(video.closest("[data-video]"));
  });

  // Statement: letters for the screen, full sentence for screen readers
  document.querySelectorAll("[data-letters]").forEach((p) => {
    const full = p.textContent.replace(/\s+/g, " ").trim();
    const wrap = (node) => {
      if (node.nodeType === 3) {
        const frag = document.createDocumentFragment();
        node.textContent.split(/(\s+)/).forEach((part) => {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(" ")); return; }
          const w = document.createElement("span"); w.style.whiteSpace = "nowrap";
          [...part].forEach((c) => { const s = document.createElement("span"); s.className = "ch"; s.textContent = c; w.appendChild(s); });
          frag.appendChild(w);
        });
        node.replaceWith(frag);
      } else if (node.nodeType === 1) [...node.childNodes].forEach(wrap);
    };
    [...p.childNodes].forEach(wrap);
    p.setAttribute("aria-label", full);
    [...p.children].forEach((c) => c.setAttribute("aria-hidden", "true"));
  });

  // Scroll-linked effects: one rAF-throttled listener, active only while targets are visible
  const letters = [...document.querySelectorAll("[data-letters]")].map((el) => ({ el, chars: [...el.querySelectorAll(".ch")] }));
  const grows = [...document.querySelectorAll("[data-grow]")];
  // Chapter I eras: the stage is pinned (CSS sticky); scroll progress picks the era and drives the rail
  const eras = [...document.querySelectorAll("[data-eras]")].map((el) => ({
    el, items: [...el.querySelectorAll(".era")], pics: [...el.querySelectorAll(".era-pic")], btns: [...el.querySelectorAll(".eras-rail button")], cur: -1 }));
  const setEra = (E, i) => {
    if (i === E.cur) return; E.cur = i;
    E.items.forEach((x, k) => x.classList.toggle("is-on", k === i));
    E.pics.forEach((x, k) => x.classList.toggle("is-on", k === i));
    E.btns.forEach((x, k) => { x.classList.toggle("is-on", k === i); x.classList.toggle("is-past", k < i); x.setAttribute("aria-current", k === i ? "step" : "false"); });
    E.el.style.setProperty("--age", (1 - i / Math.max(1, E.items.length - 1)).toFixed(3));
  };
  eras.forEach((E) => {
    setEra(E, 0);
    E.btns.forEach((btn, i) => btn.addEventListener("click", () => {
      const r = E.el.getBoundingClientRect(), span = r.height - innerHeight;
      const y = scrollY + r.top + span * ((i + 0.3) / E.items.length);
      lenis ? lenis.scrollTo(y, { duration: 1.2 }) : scrollTo({ top: y, behavior: "smooth" });
    }));
  });
  // Chapter II, after klimtwine.com: one pinned, scroll-scrubbed shot over a landscape photo. Bulgaria draws
  // itself, then the camera flies into the Kamchia zones. Map units are km; the camera maps them to screen px.
  const tours = [...document.querySelectorAll("[data-tour]")].map((el) => {
    const svg = el.querySelector(".tmap"), cam = svg.querySelector(".tm-cam");
    const box = (k) => { const [a, b, c, d] = cam.dataset[k].split(",").map(Number); return { x: a, y: b, w: c - a, h: d - b }; };
    return { el, svg, cam, country: box("country"), zones: box("zones") };
  });
  const clamp01 = (v) => Math.min(1, Math.max(0, v));
  const ease = (p, a, b) => { const t = clamp01((p - a) / (b - a)); return t * t * (3 - 2 * t); };
  const layoutTour = (T) => {
    const W = T.svg.clientWidth, H = T.svg.clientHeight, wide = W > 900;
    T.svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    // screen regions the two shots are framed into: left of the copy column on desktop, above it on phones
    const R = wide ? { x: W * 0.05, y: H * 0.16, w: W * 0.5, h: H * 0.7 } : { x: W * 0.05, y: H * 0.12, w: W * 0.9, h: H * 0.42 };
    if (reduced) { R.y += H * 0.1; R.h -= H * 0.1; }   // static final frame sits below the title
    const fit = (b, pad) => { const z = Math.min(R.w / b.w, R.h / b.h) / pad; return { z, cx: b.x + b.w / 2, cy: b.y + b.h / 2 }; };
    T.k0 = fit(T.country, 1.08); T.k1 = fit(T.zones, wide ? 1.25 : 1.15); T.R = R;
  };
  const renderTour = (T, p) => {
    const s = T.el.style, set = (k, v) => s.setProperty(k, v.toFixed(3));
    set("--title", 1 - ease(p, 0.08, 0.2));
    set("--kb", 1.12 - 0.12 * p);
    set("--shade", ease(p, 0.16, 0.3));
    set("--dark", ease(p, 0.12, 0.3));
    set("--draw-c", ease(p, 0.16, 0.42));
    set("--wide", ease(p, 0.3, 0.42) * (1 - ease(p, 0.5, 0.6)));
    set("--pin", ease(p, 0.34, 0.44));
    set("--pa", ease(p, 0.2, 0.3) * (1 - ease(p, 0.48, 0.55)));
    set("--draw-r", ease(p, 0.6, 0.78));
    set("--draw-z", ease(p, 0.64, 0.84));
    set("--fill", ease(p, 0.76, 0.9));
    set("--close", ease(p, 0.8, 0.9));
    set("--pb", ease(p, 0.6, 0.7));
    // camera: zoom geometrically while the zones' centre glides to the centre of the frame
    const e = ease(p, 0.48, 0.82), a = T.k0, b = T.k1, R = T.R;
    const z = a.z * Math.pow(b.z / a.z, e);
    const sx0 = R.x + R.w / 2 + (b.cx - a.cx) * a.z, sy0 = R.y + R.h / 2 + (b.cy - a.cy) * a.z;
    const sx = sx0 + (R.x + R.w / 2 - sx0) * e, sy = sy0 + (R.y + R.h / 2 - sy0) * e;
    T.cam.setAttribute("transform", `translate(${(sx - z * b.cx).toFixed(2)} ${(sy - z * b.cy).toFixed(2)}) scale(${z.toFixed(4)})`);
    T.svg.style.setProperty("--z", z.toFixed(4));
  };
  tours.forEach((T) => { layoutTour(T); renderTour(T, reduced ? 1 : 0); });
  addEventListener("resize", () => tours.forEach((T) => { layoutTour(T); T.last = -1; onScroll(); if (reduced) renderTour(T, 1); }));

  // Photo rows, as on restaurantsem.com: each column has its own rate (spread evenly from 0 to RATE_MAX px per scrolled px),
  // offset measured from the moment the row top is 60 % up the viewport. So the row enters stepped down to
  // the right, is level at 60 %, and leaves stepped up to the right; every gap changes on its own.
  const RATE_MAX = 0.52;  // last column's rate; the others are spread evenly from 0
  const rows = [...document.querySelectorAll("[data-drift-row]")].map((el) => ({ el, cells: [...el.children], col: [] }));
  const layoutRows = () => rows.forEach((r) => {
    r.cells.forEach((c) => c.style.setProperty("--dy", "0px"));
    const lefts = [...new Set(r.cells.map((c) => Math.round(c.offsetLeft)))].sort((a, b) => a - b);
    r.col = r.cells.map((c) => lefts.indexOf(Math.round(c.offsetLeft)));
    r.cols = lefts.length;
    r.k = innerWidth > 900 ? 1 : 0.4;
  });
  const active = new Set();
  let ticking = false;
  const update = () => {
    ticking = false;
    const vh = innerHeight;
    letters.forEach(({ el, chars }) => {
      if (!active.has(el)) return;
      const r = el.getBoundingClientRect();
      const n = Math.round(Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height + vh * 0.35))) * chars.length);
      chars.forEach((c, i) => c.classList.toggle("on", i < n));
    });
    rows.forEach((r) => {
      if (!active.has(r.el)) return;
      const d = r.el.getBoundingClientRect().top - vh * 0.4;
      r.cells.forEach((c, i) => c.style.setProperty("--dy", (d * (r.cols > 1 ? r.col[i] / (r.cols - 1) : 0) * RATE_MAX * r.k).toFixed(1) + "px"));
    });
    eras.forEach((E) => {
      if (!active.has(E.el)) return;
      const r = E.el.getBoundingClientRect();
      const p = Math.min(1, Math.max(0, -r.top / (r.height - vh)));
      const n = E.items.length, idx = Math.min(n - 1, Math.floor(p * n)), within = p * n - idx;
      setEra(E, idx);
      E.el.style.setProperty("--p", Math.min(1, (idx + within) / (n - 1)).toFixed(3));
    });
    tours.forEach((T) => {
      if (!active.has(T.el)) return;
      const r = T.el.getBoundingClientRect();
      const p = Math.min(1, Math.max(0, -r.top / (r.height - vh)));
      if (Math.abs(p - (T.last ?? -1)) < 0.0005) return;
      T.last = p; renderTour(T, p);
    });
    grows.forEach((g) => {
      if (!active.has(g)) return;
      const r = g.getBoundingClientRect();
      g.style.setProperty("--p", Math.min(1, Math.max(0, -r.top / ((r.height - vh) * 0.7))).toFixed(3));
    });
  };
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };

  if (!reduced && "IntersectionObserver" in window) {
    const watch = new IntersectionObserver((es) => { es.forEach((e) => (e.isIntersecting ? active.add(e.target) : active.delete(e.target))); onScroll(); });
    letters.forEach(({ el }) => watch.observe(el));
    grows.forEach((g) => watch.observe(g));
    eras.forEach((E) => watch.observe(E.el));
    tours.forEach((T) => watch.observe(T.el));
    layoutRows();
    rows.forEach((r) => watch.observe(r.el));
    addEventListener("resize", () => { layoutRows(); onScroll(); });
    if (hero) watch.observe(hero);
    addEventListener("scroll", onScroll, { passive: true });
    addEventListener("resize", onScroll);
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    document.querySelectorAll(".rv, .img-rv").forEach((el) => io.observe(el));
  } else {
    document.querySelectorAll(".rv, .img-rv").forEach((el) => el.classList.add("in"));
    grows.forEach((g) => g.style.setProperty("--p", "1"));
  }

  // Dropdowns (transitions.dev "Menu dropdown"): every <select data-dd> gets a button + listbox. The select keeps the
  // value (and works without JS); arrows / Home / End / typing move, Enter / Space pick, Esc / Tab close.
  const ddCloseMs = parseFloat(getComputedStyle(root).getPropertyValue("--dropdown-close-dur")) || 150;
  const dds = [...document.querySelectorAll("select[data-dd]")].map((sel) => {
    const wrap = document.createElement("div"); wrap.className = "dd";
    sel.parentNode.insertBefore(wrap, sel); wrap.appendChild(sel);
    const id = sel.id || `dd-${Math.random().toString(36).slice(2, 7)}`;
    sel.id = `${id}-native`; sel.tabIndex = -1; sel.setAttribute("aria-hidden", "true");
    const trig = document.createElement("button");
    trig.type = "button"; trig.id = id; trig.className = "dd-trigger t-input";
    trig.setAttribute("aria-haspopup", "listbox"); trig.setAttribute("aria-expanded", "false");
    const lbl = document.querySelector(`label[for="${id}"]`);
    if (lbl) trig.setAttribute("aria-labelledby", `${id}-lbl ${id}`), (lbl.id = `${id}-lbl`);
    else if (sel.getAttribute("aria-label")) trig.setAttribute("aria-label", sel.getAttribute("aria-label"));
    trig.innerHTML = `<span class="dd-value"></span><span class="ico" style="--i:url(${P}/icons/caret-down.svg)" aria-hidden="true"></span>`;
    const list = document.createElement("ul");
    list.className = "dd-list t-dropdown"; list.id = `${id}-list`; list.setAttribute("role", "listbox"); list.tabIndex = -1;
    if (lbl) list.setAttribute("aria-labelledby", `${id}-lbl`);
    trig.setAttribute("aria-controls", list.id);
    const opts = [...sel.options].map((o, i) => {
      const li = document.createElement("li");
      li.className = "dd-opt" + (o.value === "" ? " is-placeholder" : ""); li.id = `${id}-o${i}`; li.setAttribute("role", "option");
      li.innerHTML = `<span></span><span class="ico" style="--i:url(${P}/icons/check.svg)" aria-hidden="true"></span>`;
      li.firstChild.textContent = o.text; li.dataset.i = i;
      list.appendChild(li); return li;
    });
    wrap.append(trig, list);
    const real = () => opts.filter((li) => !li.classList.contains("is-placeholder"));
    let active = -1, typed = "", typedT = 0;
    const sync = () => {
      const o = sel.options[sel.selectedIndex];
      trig.querySelector(".dd-value").textContent = o ? o.text : "";
      trig.classList.toggle("is-empty", !sel.value);
      opts.forEach((li, i) => li.setAttribute("aria-selected", String(i === sel.selectedIndex)));
    };
    const setActive = (li) => {
      opts.forEach((x) => x.classList.toggle("is-active", x === li));
      active = li ? +li.dataset.i : -1;
      if (li) { trig.setAttribute("aria-activedescendant", li.id); li.scrollIntoView({ block: "nearest" }); } else trig.removeAttribute("aria-activedescendant");
    };
    const isOpen = () => wrap.classList.contains("is-open");
    const open = () => {
      if (isOpen()) return;
      dds.forEach((d) => d !== api && d.close());
      const r = trig.getBoundingClientRect();
      list.dataset.origin = innerHeight - r.bottom < 300 && r.top > 300 ? "bottom-left" : "top-left";
      list.classList.remove("is-closing"); list.classList.add("is-open");
      wrap.classList.add("is-open"); trig.setAttribute("aria-expanded", "true");
      setActive(opts[sel.selectedIndex] && sel.value ? opts[sel.selectedIndex] : real()[0]);
    };
    const close = () => {
      if (!isOpen()) return;
      list.classList.remove("is-open"); list.classList.add("is-closing");
      setTimeout(() => list.classList.remove("is-closing"), ddCloseMs);
      wrap.classList.remove("is-open"); trig.setAttribute("aria-expanded", "false"); setActive(null);
    };
    const pick = (li) => {
      sel.selectedIndex = +li.dataset.i; sync();
      sel.dispatchEvent(new Event("change", { bubbles: true }));
      close(); trig.focus();
    };
    trig.addEventListener("click", () => (isOpen() ? close() : open()));
    list.addEventListener("pointerdown", (e) => e.preventDefault());           // keep focus on the trigger
    list.addEventListener("click", (e) => { const li = e.target.closest(".dd-opt"); if (li) pick(li); });
    list.addEventListener("pointermove", (e) => { const li = e.target.closest(".dd-opt"); if (li && +li.dataset.i !== active) setActive(li); });
    trig.addEventListener("keydown", (e) => {
      const r = real(), pos = r.findIndex((li) => +li.dataset.i === active);
      const go = (k) => { if (!isOpen()) open(); setActive(r[Math.max(0, Math.min(r.length - 1, k))]); };
      if (e.key === "ArrowDown") { e.preventDefault(); isOpen() ? go(pos + 1) : open(); }
      else if (e.key === "ArrowUp") { e.preventDefault(); isOpen() ? go(pos - 1) : open(); }
      else if (e.key === "Home" && isOpen()) { e.preventDefault(); go(0); }
      else if (e.key === "End" && isOpen()) { e.preventDefault(); go(r.length - 1); }
      else if ((e.key === "Enter" || e.key === " ") && isOpen()) { e.preventDefault(); if (active >= 0) pick(opts[active]); }
      else if (e.key === "Escape" && isOpen()) { e.preventDefault(); close(); }
      else if (e.key === "Tab") close();
      else if (e.key.length === 1 && /\S/.test(e.key)) {          // type-ahead
        clearTimeout(typedT); typed += e.key.toLowerCase(); typedT = setTimeout(() => (typed = ""), 600);
        const hit = r.find((li) => li.textContent.trim().toLowerCase().startsWith(typed));
        if (hit) { if (!isOpen()) open(); setActive(hit); }
      }
    });
    document.addEventListener("pointerdown", (e) => { if (!wrap.contains(e.target)) close(); });
    sel.addEventListener("change", sync);
    sync();
    const api = { sel, trig, wrap, close, sync };
    return api;
  });
  const control = (el) => (el && el.tagName === "SELECT" && el.closest(".dd") ? el.closest(".dd").querySelector(".dd-trigger") : el);

  // Images: a pulsing frame while each photo loads, then it fades in out of a slight blur (after transitions.dev 14)
  document.querySelectorAll(".img img, .portrait img, .aside-photo img, .era-pic img, .project > img, .figures-media img").forEach((img) => {
    const box = img.closest(".img, .portrait, .aside-photo, .era-pic") || img;
    if (img.complete && img.naturalWidth) return;
    box.classList.add("is-img-loading", "img-loaded-fx");
    const done = () => box.classList.remove("is-img-loading");
    img.addEventListener("load", done, { once: true });
    img.addEventListener("error", done, { once: true });
  });

  // Store (quote cart): example prices from the page's #shop-data; the bag lives in localStorage as ids only, so names
  // follow the page language. Nothing is paid: the bag is sent as one enquiry through the form.
  const SHOP = (() => { try { return JSON.parse(document.getElementById("shop-data").textContent); } catch (_) { return null; } })();
  const EN = root.lang === "en";
  const BASE = P + (EN ? "/en" : "");
  const fmtMoney = new Intl.NumberFormat(EN ? "en-GB" : "bg-BG", { style: "currency", currency: "EUR" });
  const fmtNum = new Intl.NumberFormat(EN ? "en-GB" : "bg-BG", { maximumFractionDigits: 2 });
  const money = (v) => fmtMoney.format(v);
  const ico = (n) => `<span class="ico" style="--i:url(${P}/icons/${n}.svg)" aria-hidden="true"></span>`;
  const bag = (() => {
    const KEY = "stefanoff.bag";
    let lines = [];
    try { lines = JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (_) {}
    const P = (s) => SHOP && SHOP.products[s];
    lines = Array.isArray(lines) ? lines.filter((l) => P(l.s) && P(l.s).forms[l.f] != null && P(l.s).packs[l.p] != null && l.q > 0) : [];
    const subs = new Set();
    const save = () => { try { localStorage.setItem(KEY, JSON.stringify(lines)); } catch (_) {} subs.forEach((fn) => fn()); };
    const unitPrice = (s, units) => { const t = P(s).tiers; let v = t[0][1]; t.forEach(([from, price]) => { if (units >= from) v = price; }); return v; };
    const units = (l) => P(l.s).packs[l.p] * l.q;
    const lineSum = (l) => units(l) * unitPrice(l.s, units(l));
    return {
      P, unitPrice, units, lineSum,
      get lines() { return lines; },
      total: () => lines.reduce((a, l) => a + lineSum(l), 0),
      add(s, f, p, q) {
        const hit = lines.find((l) => l.s === s && l.f === f && l.p === p);
        if (hit) hit.q = Math.min(999, hit.q + q); else lines.push({ s, f, p, q });
        save();
      },
      set(i, q) { if (!lines[i]) return; lines[i].q = Math.max(1, Math.min(999, q)); save(); },
      remove(i) { lines.splice(i, 1); save(); },
      clear() { lines = []; save(); },
      on(fn) { subs.add(fn); },
      describe(l) { const pr = P(l.s); return { name: pr.name, sub: L.lineSub(pr.forms[l.f], l.q, pr.packLabels[l.p]), pack: pr.packLabels[l.p], unit: pr.unit } },
    };
  })();
  // Bag outside of SHOP-less pages is a no-op
  if (SHOP) {
    // count badge in the nav (transitions.dev "Notification badge"), bumped on every add
    const badges = [...document.querySelectorAll(".bag-badge")];
    const openers = [...document.querySelectorAll(".nav-bag")];
    let lastCount = bag.lines.length;
    const paintBadge = () => {
      const n = bag.lines.length;
      badges.forEach((b) => {
        b.querySelector("[data-bag-count]").textContent = n;
        b.dataset.open = String(n > 0);
        if (n > lastCount) { b.classList.remove("is-bump"); void b.offsetWidth; b.classList.add("is-bump"); }
      });
      openers.forEach((o) => o.setAttribute("aria-label", L.bagLabel(n)));
      lastCount = n;
    };
    paintBadge(); bag.on(paintBadge);

    // drawer
    const bd = document.getElementById("bag");
    const linesEl = bd.querySelector("[data-bag-lines]"), emptyEl = bd.querySelector("[data-bag-empty]"), footEl = bd.querySelector("[data-bag-foot]");
    const stepper = (i, q) => `<div class="stepper" role="group" aria-label="${L.packs}"><button type="button" data-line-step="-1" data-i="${i}" aria-label="${L.fewer}"${q <= 1 ? " disabled" : ""}>${ico("minus")}</button><input type="text" inputmode="numeric" value="${q}" data-line-q="${i}" aria-label="${L.packs}"><button type="button" data-line-step="1" data-i="${i}" aria-label="${L.more}">${ico("plus")}</button></div>`;
    const paintBag = () => {
      const n = bag.lines.length;
      linesEl.innerHTML = bag.lines.map((l, i) => {
        const d = bag.describe(l), pr = bag.P(l.s);
        return `<li class="bag-line"><img src="${P}/img/${pr.img}" alt="" width="64" height="80"><div><p class="bl-name"><a href="${BASE}/produkti/${l.s}.html"></a></p><p class="bl-sub"></p></div><p class="bl-sum">${money(bag.lineSum(l))}</p>
          <div class="bl-row">${stepper(i, l.q)}<button class="bl-remove" type="button" data-line-remove="${i}">${ico("trash")}${L.remove}</button></div></li>`;
      }).join("");
      [...linesEl.children].forEach((li, i) => { const d = bag.describe(bag.lines[i]); li.querySelector(".bl-name a").textContent = d.name; li.querySelector(".bl-sub").textContent = d.sub; });
      emptyEl.hidden = n > 0; footEl.hidden = n === 0;
      bd.querySelector("[data-bag-total]").textContent = money(bag.total());
    };
    paintBag(); bag.on(paintBag);
    linesEl.addEventListener("click", (e) => {
      const st = e.target.closest("[data-line-step]"), rm = e.target.closest("[data-line-remove]");
      if (st) { const i = +st.dataset.i; bag.set(i, bag.lines[i].q + +st.dataset.lineStep); linesEl.querySelector(`[data-line-step="${st.dataset.lineStep}"][data-i="${i}"]`)?.focus(); }
      if (rm) {
        const i = +rm.dataset.lineRemove, li = rm.closest(".bag-line");
        li.classList.add("is-leaving");
        setTimeout(() => { bag.remove(i); (linesEl.querySelector("[data-line-remove]") || bd.querySelector(".bag-empty a, .chat-close")).focus(); }, reduced ? 0 : 220);
      }
    });
    linesEl.addEventListener("change", (e) => { const q = e.target.closest("[data-line-q]"); if (q) bag.set(+q.dataset.lineQ, parseInt(q.value, 10) || 1); });
    const behindBag = [...document.body.children].filter((el) => !el.matches("#bag, .bag-scrim, script, .toast"));
    let bagOpen = false, bagFocus = null;
    const setBag = (next) => {
      if (next === bagOpen) return;
      bagOpen = next;
      if (next) bagFocus = document.activeElement;   // before the page behind goes inert and drops focus
      root.classList.toggle("bag-open", next);
      bd.inert = !next;
      behindBag.forEach((el) => { el.inert = next; });
      openers.forEach((o) => o.setAttribute("aria-expanded", String(next)));
      lockScroll("bag", next);
      if (lenis) next ? lenis.stop() : lenis.start();
      if (next) {
        hideToast();
        const x = bd.querySelector(".chat-close");
        x.focus({ preventScroll: true });
        requestAnimationFrame(() => { if (bagOpen && !bd.contains(document.activeElement)) x.focus({ preventScroll: true }); });
      }
      else { const back = bagFocus?.isConnected && !bagFocus.closest("#bag, .toast") ? bagFocus : openers.find((o) => o.offsetParent); back?.focus({ preventScroll: true }); }
    };
    document.addEventListener("click", (e) => {
      if (e.target.closest("[data-bag-open]")) { e.preventDefault(); setBag(true); }
      else if (e.target.closest("[data-bag-close]")) setBag(false);
    });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && bagOpen) setBag(false); });

    // toast (transitions.dev "Toast")
    const toast = document.querySelector("[data-toast]");
    let toastT = 0;
    function hideToast() { clearTimeout(toastT); toast.classList.remove("is-open"); root.classList.remove("toast-on"); }
    const showToast = (name, pack) => {
      const m = toast.querySelector("[data-toast-msg]");
      m.replaceChildren(Object.assign(document.createElement("strong"), { textContent: name }), Object.assign(document.createElement("span"), { textContent: `${L.added}, ${pack}` }));
      root.classList.add("toast-on");
      toast.classList.remove("is-open"); void toast.offsetWidth; toast.classList.add("is-open");
      clearTimeout(toastT); toastT = setTimeout(hideToast, 3600);
    };
    toast.addEventListener("pointerenter", () => clearTimeout(toastT));
    toast.addEventListener("pointerleave", () => { toastT = setTimeout(hideToast, 1600); });
    const addAndTell = (s, f, p, q) => { bag.add(s, f, p, q); const pr = bag.P(s); showToast(pr.name, `${q} × ${pr.packLabels[p]}`); };
    const flash = (btn, swap) => {
      btn.classList.add("is-added"); swap?.setAttribute("data-state", "b");
      clearTimeout(btn._t); btn._t = setTimeout(() => { btn.classList.remove("is-added"); swap?.setAttribute("data-state", "a"); }, 1600);
    };

    // quick add on tiles: default form and pack, one pack
    document.querySelectorAll("[data-add]").forEach((btn) => btn.addEventListener("click", () => {
      const s = btn.dataset.add, pr = bag.P(s);
      addAndTell(s, 0, pr.def, 1);
      flash(btn, btn.querySelector(".t-icon-swap"));
    }));

    // product page: form and pack pills, quantity, live price (number pop-in when the tier changes)
    const buy = document.querySelector("form[data-buy]");
    if (buy) {
      const s = buy.dataset.buy, pr = bag.P(s);
      const qIn = buy.querySelector('[name="qty"]'), minus = buy.querySelector('[data-step="-1"]');
      const priceEls = document.querySelectorAll("[data-unit-price]"), packEl = document.querySelector("[data-pack-total]");
      const tiersEls = [...document.querySelectorAll("[data-tier]")];
      const addBtn = buy.querySelector(".buy-add");
      const pick = (n) => +(buy.querySelector(`[name="${n}"]:checked`)?.value || 0);
      const qty = () => Math.max(1, Math.min(999, parseInt(qIn.value, 10) || 1));
      let shown = "";
      const setDigits = (el, str) => {
        el.classList.remove("is-animating"); el.replaceChildren();
        [...str].forEach((ch, i, a) => { const sp = document.createElement("span"); sp.className = "t-digit"; sp.textContent = ch; if (i === a.length - 2) sp.dataset.stagger = "1"; else if (i === a.length - 1) sp.dataset.stagger = "2"; el.append(sp); });
        void el.offsetHeight; el.classList.add("is-animating");
      };
      const paint = () => {
        const q = qty(), u = pr.packs[pick("pack")] * q, price = bag.unitPrice(s, u), str = money(price);
        priceEls.forEach((el) => { if (el.classList.contains("t-digit-group")) { if (str !== shown && shown) setDigits(el, str); else if (!shown) el.textContent = str; } else el.textContent = str; });
        shown = str;
        let ti = 0; pr.tiers.forEach(([from], i) => { if (u >= from) ti = i; });
        tiersEls.forEach((li, i) => li.classList.toggle("is-on", i === ti));
        packEl.textContent = L.packTotal(q, pr.packLabels[pick("pack")], `${fmtNum.format(u)} ${pr.unit}`, money(u * price));
        minus.disabled = q <= 1;
      };
      buy.addEventListener("change", paint);
      qIn.addEventListener("input", () => { qIn.value = qIn.value.replace(/\D/g, "").slice(0, 3); paint(); });
      qIn.addEventListener("blur", () => { qIn.value = qty(); paint(); });
      buy.querySelectorAll("[data-step]").forEach((b) => b.addEventListener("click", () => { qIn.value = Math.max(1, Math.min(999, qty() + +b.dataset.step)); paint(); }));
      buy.addEventListener("submit", (e) => {
        e.preventDefault();
        addAndTell(s, pick("form"), pick("pack"), qty());
        flash(addBtn, addBtn.querySelector(".t-icon-swap"));
        const a = addBtn.querySelector("[data-label-add]"), d = addBtn.querySelector("[data-label-done]");
        a.hidden = true; d.hidden = false; clearTimeout(addBtn._l); addBtn._l = setTimeout(() => { a.hidden = false; d.hidden = true; }, 1600);
      });
      paint();
      // mobile bar: price + add, out of the way while the real button is on screen
      const sb = document.querySelector("[data-sticky-buy]");
      if (sb) {
        sb.querySelector("[data-buy-proxy]").addEventListener("click", () => { buy.requestSubmit(); });
        if ("IntersectionObserver" in window) new IntersectionObserver(([en]) => sb.classList.toggle("is-hidden", en.isIntersecting || en.boundingClientRect.top > 0)).observe(addBtn);
      }
    }

    // gallery: thumbnails swap the main shot
    const gal = document.querySelector(".gallery");
    if (gal) gal.querySelectorAll(".thumb").forEach((t) => t.addEventListener("click", () => {
      gal.querySelectorAll(".thumb").forEach((x) => { x.classList.toggle("is-on", x === t); x.setAttribute("aria-pressed", String(x === t)); });
      gal.querySelectorAll(".shot").forEach((x) => x.classList.toggle("is-on", x.dataset.shot === t.dataset.shot));
    }));

    // products page: floating chapter bar (transitions.dev "Tabs sliding"), follows the chapter on screen
    const cbar = document.querySelector("[data-chapter-bar]");
    if (cbar) {
      const pill = cbar.querySelector(".t-tabs-pill"), tabs = [...cbar.querySelectorAll(".t-tab")];
      const chapters = tabs.map((t) => document.getElementById(t.dataset.chapterTab));
      let cur = -1;
      const move = (i, animate = true) => {
        if (i === cur) return; cur = i;
        tabs.forEach((t, k) => (k === i ? t.setAttribute("aria-current", "true") : t.removeAttribute("aria-current")));
        if (i < 0) return;
        if (!animate) pill.style.transition = "none";
        pill.style.transform = `translateX(${tabs[i].offsetLeft}px)`; pill.style.width = `${tabs[i].offsetWidth}px`;
        if (!animate) { void pill.offsetWidth; pill.style.transition = ""; }
        if (cbar.scrollWidth > cbar.clientWidth) cbar.scrollTo({ left: tabs[i].offsetLeft - 12, behavior: reduced ? "auto" : "smooth" });
      };
      const sync = () => {
        const mid = innerHeight * 0.45;
        let i = chapters.findIndex((c) => { const r = c.getBoundingClientRect(); return r.top <= mid && r.bottom > mid; });
        if (i < 0 && chapters[0].getBoundingClientRect().top > mid) i = 0;
        const first = chapters[0].getBoundingClientRect(), last = chapters[chapters.length - 1].getBoundingClientRect();
        cbar.classList.toggle("is-shown", first.top < innerHeight * 0.8 && last.bottom > innerHeight * 0.3);
        if (i >= 0) move(i, cur >= 0);
      };
      addEventListener("scroll", sync, { passive: true });
      addEventListener("resize", () => { const c = cur; cur = -1; move(c, false); });
      tabs.forEach((t, i) => t.addEventListener("click", (e) => {
        e.preventDefault(); move(i);
        if (lenis) lenis.scrollTo(chapters[i], { offset: -24 }); else chapters[i].scrollIntoView({ behavior: reduced ? "auto" : "smooth" });
        history.replaceState(null, "", `#${t.dataset.chapterTab}`);
      }));
      requestAnimationFrame(sync);
    }
  }

  // Quote form: inline validation; on send a short loading state, the pre-filled email, then a summary panel
  const form = document.querySelector("form.quote");
  if (form) {
    const F = (n) => form.querySelector(`[name="${n}"]`);   // by name: the dropdown buttons reuse the select ids
    const product = new URLSearchParams(location.search).get("product");
    if (product) { const sel = F("product"); if ([...sel.options].some((o) => o.value === product)) { sel.value = product; sel.dispatchEvent(new Event("change")); } }
    if (new URLSearchParams(location.search).get("mostra") && !F("message").value) F("message").value = L.sampleMsg;
    // with products in the bag, they replace the product and quantity fields
    const fg = form.querySelector(".fgroup");
    const sumBox = document.createElement("div");
    sumBox.className = "bag-sum"; sumBox.hidden = true;
    fg.querySelector("legend").after(sumBox);
    const viaBag = () => SHOP && bag.lines.length > 0;
    const paintSum = () => {
      const on = viaBag();
      sumBox.hidden = !on;
      F("product").closest(".field").hidden = on;
      F("quantity").closest(".field").hidden = on;
      if (!on) { sumBox.innerHTML = ""; return; }
      sumBox.innerHTML = `<div class="bag-sum-head"><p class="t-small">${L.inBag}</p><button class="link-btn" type="button" data-bag-open>${L.edit}</button></div><ul></ul><div class="bag-total"><span>${L.estimate}</span><strong>${money(bag.total())}</strong></div>`;
      const ul = sumBox.querySelector("ul");
      bag.lines.forEach((l) => { const d = bag.describe(l), li = document.createElement("li"); li.innerHTML = `<span><strong></strong><span class="bl-sub"></span></span><span class="bl-sum">${money(bag.lineSum(l))}</span>`; li.querySelector("strong").textContent = d.name; li.querySelector(".bl-sub").textContent = d.sub; ul.append(li); });
    };
    if (SHOP) { paintSum(); bag.on(paintSum); }
    const status = form.querySelector(".form-status");
    const done = form.parentElement.querySelector(".form-done");
    const submit = form.querySelector("[data-submit]");
    const rules = {
      product: (v) => (viaBag() || v ? "" : L.errProduct),
      quantity: (v) => (viaBag() ? "" : !v.trim() ? L.errQty : Number(v.trim().replace(",", ".")) > 0 ? "" : L.errQtyPos),
      country: (v) => (v.trim() ? "" : L.errCountry),
      company: (v) => (v.trim() ? "" : L.errCompany),
      email: (v) => (!v.trim() ? L.errEmail : /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) ? "" : L.errEmailBad),
      consent: (_, el) => (el.checked ? "" : L.errConsent),
    };
    const check = (name) => {
      const el = F(name);
      const field = el.closest(".field");
      const msg = rules[name](el.value, el);
      field.classList.toggle("invalid", !!msg);
      control(el).setAttribute("aria-invalid", msg ? "true" : "false");
      const m = field.querySelector(".err .msg"); if (m) m.textContent = msg;
      return !msg;
    };
    // error ids for screen readers
    Object.keys(rules).forEach((n) => {
      const el = F(n), err = el.closest(".field").querySelector(".err");
      if (err) { err.id = `${n}-err`; control(el).setAttribute("aria-describedby", err.id); }
    });
    let tried = false;
    const left = () => Object.keys(rules).filter((n) => F(n).closest(".field").classList.contains("invalid")).length;
    const refresh = () => { if (!tried) return; const k = left(); status.className = "form-status" + (k ? " bad" : ""); status.textContent = k ? L.fixFields(k) : ""; };
    Object.keys(rules).forEach((n) => {
      const el = F(n);
      // leaving a filled field: say only if its format is wrong (e.g. an email without a domain)
      (control(el) || el).addEventListener("blur", () => {
        if (el.tagName === "SELECT" && el.closest(".dd").classList.contains("is-open")) return;
        if (tried || (el.type !== "checkbox" && el.value.trim())) check(n);
        refresh();
      });
      // while correcting: clear as soon as it is right; never add new errors mid-typing
      ["input", "change"].forEach((ev) => el.addEventListener(ev, () => {
        if (el.closest(".field").classList.contains("invalid")) { check(n); refresh(); }
      }));
    });
    let mailHref = "", mailBody = "";
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (submit.classList.contains("is-loading")) return;
      tried = true;
      const bad = Object.keys(rules).filter((n) => !check(n));
      refresh();
      if (bad.length) { control(F(bad[0])).focus(); return; }
      const f = new Proxy({}, { get: (_, n) => (n === "unit" ? form.querySelector('[name="unit"]:checked') : F(n)) });
      const fromBag = viaBag();
      const label = fromBag ? L.count(bag.lines.length) : f.product.options[f.product.selectedIndex].text;
      const what = fromBag
        ? [[L.mLines, L.count(bag.lines.length)], [L.mTotal, money(bag.total())]]
        : [[L.mProduct, label], [L.mQty, `${f.quantity.value} ${f.unit.value}`]];
      const rows = [
        ...what, [L.mForm, f.form_detail.value], [L.mCountry, f.country.value],
        [L.mCompany, f.company.value], [L.mName, f.name.value], [L.mEmail, f.email.value], [L.mPhone, f.phone.value],
      ].filter(([, v]) => v && v.trim());
      const list = fromBag ? bag.lines.map((l) => { const d = bag.describe(l); return `- ${d.name}: ${d.sub} (${fmtNum.format(bag.units(l))} ${d.unit}), ~${money(bag.lineSum(l))}`; }).join("\n") + "\n\n" : "";
      mailBody = list + rows.map(([k, v]) => `${k}: ${v}`).join("\n") + (f.message.value ? `\n\n${f.message.value}` : "");
      mailHref = `mailto:office@stefanoff.bg?subject=${encodeURIComponent(`${L.mSubject}: ${fromBag ? label : `${label}, ${f.quantity.value} ${f.unit.value}`}`)}&body=${encodeURIComponent(mailBody)}`;
      submit.classList.add("is-loading"); submit.setAttribute("aria-busy", "true"); submit.disabled = true;
      setTimeout(() => {
        location.href = mailHref;
        const sum = done.querySelector(".done-sum");
        sum.innerHTML = "";
        rows.slice(0, 5).forEach(([k, v]) => { const dt = document.createElement("dt"), dd = document.createElement("dd"); dt.textContent = k; dd.textContent = v; sum.append(dt, dd); });
        done.querySelector("[data-mailto]").href = mailHref;
        if (fromBag) bag.clear();
        form.classList.add("is-leaving");
        setTimeout(() => {
          form.hidden = true; form.classList.remove("is-leaving");
          submit.classList.remove("is-loading"); submit.removeAttribute("aria-busy"); submit.disabled = false;
          done.hidden = false; form.parentElement.classList.add("is-done"); done.focus({ preventScroll: true });
          const c = done.querySelector(".t-success-check");
          c.setAttribute("data-state", "out"); void c.offsetWidth; c.setAttribute("data-state", "in");
          const top = form.parentElement.getBoundingClientRect().top;
          if (top < 0) (lenis ? lenis.scrollTo(form.parentElement, { offset: -120 }) : form.parentElement.scrollIntoView({ behavior: "smooth" }));
        }, reduced ? 0 : 250);
      }, reduced ? 0 : 650);
    });
    done.querySelector("[data-copy]").addEventListener("click", async (e) => {
      const btn = e.currentTarget, lab = btn.querySelector(".btn-label"), was = lab.textContent;
      try { await navigator.clipboard.writeText(`office@stefanoff.bg\n\n${mailBody}`); lab.textContent = L.copied; }
      catch (_) { lab.textContent = L.copyFail; }
      setTimeout(() => (lab.textContent = was), 2200);
    });
    done.querySelector("[data-reset]").addEventListener("click", () => {
      form.reset(); dds.forEach((d) => d.sync()); tried = false;
      form.querySelectorAll(".field.invalid").forEach((x) => x.classList.remove("invalid"));
      status.className = "form-status"; status.textContent = "";
      done.hidden = true; form.hidden = false; form.parentElement.classList.remove("is-done"); if (SHOP) paintSum(); control(F("product")).focus();
    });
  }

  // Chat: a drawer that slides in from the right when the header chat icon is pressed. Inside it sits the client's Tidio chat,
  // loaded on first open and docked into the drawer body: its bubble hidden, its colours, corners and
  // font set to ours through its own CSS variables. Once a visitor has used the chat, later pages load it
  // quietly, so a reply from the team opens the drawer. If Tidio can't load, the drawer offers phone and email.
  const drawer = document.getElementById("chat");
  if (drawer) {
    const toggles = document.querySelectorAll("[data-chat][aria-controls]");
    const top = drawer.querySelector(".chat-top");
    const wait = drawer.querySelector(".chat-wait");
    const fail = drawer.querySelector(".chat-fail");
    const closeBtn = drawer.querySelector(".chat-close");
    const behind = [...document.body.children].filter((el) => !el.matches("#chat, .chat-scrim, script"));
    const OUT_MS = reduced ? 0 : 440;
    const CHAT_KEY = "stefanoff.chat";
    const DOCK = `
      #tidio-chat-root { left: auto !important; right: 0 !important; top: var(--chat-top) !important; bottom: 0 !important;
        width: var(--chat-w) !important; max-width: none !important; height: auto !important; margin: 0 !important; display: block !important;
        --custom-action-color: #674EA7 !important; --radius-surface: 0px !important; --radius-component: 4px !important;
        --radius-small-component: 4px !important; --operator-message: #F7F4F2 !important; --border-color: #E0D3CC !important; }
      #tidio-chat-root .chat { position: absolute !important; inset: 0 !important; width: 100% !important; height: 100% !important;
        max-height: none !important; border-radius: 0 !important; box-shadow: none !important; transition: none !important; animation: none !important; }
      #tidio-chat-root .chat > div:nth-child(2) { width: 100% !important; height: 100% !important; }
      #tidio-chat-root .chat-header { height: auto !important; min-height: 0 !important; }
      #tidio-chat-root .chat-header + div { max-height: none !important; }
      #tidio-chat-root button:has(#ic_close) { display: none !important; }   /* ours closes it */
      #tidio-chat-root .chat-header h2, #tidio-chat-root .chat-header h2 ~ * { display: none !important; }
      #button { display: none !important; }
      #tidio-chat-root, #tidio-chat-root * { font-family: Manrope, system-ui, sans-serif !important; }`;
    const used = () => { try { return localStorage.getItem(CHAT_KEY) === "1"; } catch { return false; } };
    const markUsed = () => { try { localStorage.setItem(CHAT_KEY, "1"); } catch {} };
    const measure = () => root.style.setProperty("--chat-top", top.offsetHeight + "px");
    if ("ResizeObserver" in window) new ResizeObserver(measure).observe(top);
    let open = false, api = null, chat = null, lastFocus = null, outTimer = 0;

    const loadChat = () => chat ||= new Promise((resolve, reject) => {
      document.addEventListener("tidioChat-ready", () => {
        const t = window.tidioChatApi;
        const shadow = document.getElementById("tidio-chat")?.shadowRoot;
        if (shadow) { const css = document.createElement("style"); css.textContent = DOCK; shadow.append(css); }
        t.setColorPalette?.("#0B0807");
        t.hide();
        t.on("open", () => { if (!open) { t.close(); t.hide(); } });   // no pop-ups of its own
        t.on("close", () => { if (open) setOpen(false, true); });
        t.on("messageFromOperator", () => { if (!open) setOpen(true); });
        api = t;
        resolve(t);
      }, { once: true });
      document.tidioChatLang = "bg";
      const s = document.createElement("script");
      s.src = "https://code.tidio.co/n1ksixcega3fitxecwcwrsc6mr5rgwa2.js";
      s.async = true;
      s.onerror = reject;
      document.body.append(s);
      setTimeout(reject, 12000);
    }).catch((e) => { chat = null; throw e; });

    const setOpen = (next, fromTidio = false) => {
      if (next === open) return;
      open = next;
      clearTimeout(outTimer);
      root.classList.toggle("chat-open", open);
      drawer.inert = !open;
      behind.forEach((el) => { el.inert = open; });
      toggles.forEach((b) => b.setAttribute("aria-expanded", String(open)));
      lockScroll("chat", open);
      if (lenis) open ? lenis.stop() : lenis.start();
      if (open) {
        closeMenu();
        lastFocus = document.activeElement;
        measure();
        closeBtn.focus({ preventScroll: true });
        fail.hidden = true;
        wait.hidden = false;
        loadChat().then((t) => {
          if (!open) return;
          markUsed();
          t.show();
          t.open();
        }, () => {
          wait.hidden = true;
          fail.hidden = false;
        });
      } else {
        const back = lastFocus?.isConnected && !lastFocus.closest("#chat") ? lastFocus : [...toggles].find((b) => b.offsetParent);
        back?.focus({ preventScroll: true });
        // The docked chat slides out with the drawer; fold it away once it's off screen.
        outTimer = setTimeout(() => {
          if (open || !api) return;
          if (!fromTidio) api.close();
          api.hide();
        }, OUT_MS);
      }
    };

    // Tidio's phone mode puts back the scroll lock it found when it opened (ours), after it has closed.
    new MutationObserver(() => {
      if (!open && document.body.style.overflow === "hidden" && !menu?.classList.contains("open")) document.body.style.overflow = "";
    }).observe(document.body, { attributes: true, attributeFilter: ["style"] });

    document.addEventListener("click", (e) => {
      if (e.target.closest("[data-chat]")) setOpen(true);
      else if (e.target.closest("[data-chat-close]")) setOpen(false);
    });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && open) setOpen(false); });
    if (used()) (window.requestIdleCallback || setTimeout)(() => loadChat().catch(() => {}));
  }
})();
