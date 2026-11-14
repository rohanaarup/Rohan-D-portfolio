// Navigation tests. Usage: node dev/test_nav.js <baseUrl> <path-to-node_modules-with-puppeteer-core>
const base = process.argv[2] || "http://localhost:5000";
const puppeteer = require(require("path").join(process.argv[3], "puppeteer-core"));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const results = [];
const ok = (name, pass, info = "") => { results.push({ name, pass, info }); console.log((pass ? "PASS " : "FAIL ") + name + (info ? "  [" + info + "]" : "")); };

async function open(b, url, w = 1440, h = 900, mobile = false) {
  const p = await b.newPage();
  await p.setViewport({ width: w, height: h, isMobile: mobile, hasTouch: mobile });
  const errs = []; p.on("pageerror", (e) => errs.push(String(e).slice(0, 150)));
  p.on("console", (m) => { if (m.type() === "error" && !/404/.test(m.text())) errs.push(m.text().slice(0, 150)); });
  p._errs = errs;
  await p.goto(base + url, { waitUntil: "networkidle0", timeout: 60000 });
  await sleep(5200); // template preloader
  return p;
}
const topOf = (p, sel) => p.evaluate((s) => { const e = document.querySelector(s); return e ? Math.round(e.getBoundingClientRect().top) : null; }, sel);
const menuOpen = (p) => p.evaluate(() => !!document.querySelector(".tw-offcanvas-2-area.opened"));

(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", args: ["--no-sandbox"] });
  const items = [["#home", "#home"], ["#about", "#about"], ["#services", "#services"], ["#works", "#works"], ["#experience", "#experience"], ["#contact", "#contact"]];

  for (const [label, w, h, mobile] of [["desktop", 1440, 900, false], ["mobile", 390, 844, true]]) {
    for (const [href, sel] of items) {
      const p = await open(b, "/index.html", w, h, mobile);
      await p.click("button.tw-offcanvas-open-btn"); await sleep(1200);
      const opened = await menuOpen(p);
      await p.evaluate((hr) => { const a = Array.from(document.querySelectorAll(".tw-main-menu-mobile a")).find((x) => x.getAttribute("href") === hr); if (!a) throw new Error("menu link missing " + hr); a.click(); }, href);
      await sleep(3500);
      const closed = !(await menuOpen(p));
      const hash = await p.evaluate(() => location.hash);
      const top = sel === "#home" ? await p.evaluate(() => window.scrollY) : await topOf(p, sel);
      const inView = sel === "#home" ? top < 40 : top !== null && top >= 0 && top <= 220;
      ok(`${label} menu "${href}" opens, scrolls, closes, sets hash`, opened && closed && hash === href && inView, `opened=${opened} closed=${closed} hash=${hash} top=${top}`);
      await p.close();
    }
  }

  // CTAs
  {
    const p = await open(b, "/index.html");
    const ctas = await p.evaluate(() => ["a.tw-hover-btn", ".header-three-button a", ".footer-three-middile a"].flatMap((s) => Array.from(document.querySelectorAll(s)).map((a) => [a.textContent.trim().replace(/\s+/g, " "), a.getAttribute("href")])));
    console.log("CTA inventory:", JSON.stringify(ctas));
    const exp = { "view projects": "#works", "get in touch": "#contact" };
    for (const [t, hr] of ctas) { const k = t.toLowerCase(); if (exp[k]) ok(`CTA "${t}" -> ${hr}`, hr === exp[k]); }
    await p.evaluate(() => document.querySelector(".header-three-button a").click()); await sleep(3500);
    ok("header 'get in touch' lands on Contact", (await topOf(p, "#contact")) >= -5 && (await topOf(p, "#contact")) <= 220 && (await p.evaluate(() => location.hash)) === "#contact");
    await p.evaluate(() => scrollTo(0, 0)); await sleep(500);
    await p.close();
  }

  // back / forward
  {
    const p = await open(b, "/index.html");
    const go = async (hr) => { await p.evaluate((h) => document.querySelector(`.header-three-social ~ * a[href="${h}"], a[href="${h}"]`).click(), hr); await sleep(3200); };
    await p.evaluate(() => document.querySelector('a[href="#about"]').click()); await sleep(3200);
    await p.evaluate(() => document.querySelector('a[href="#works"]').click()); await sleep(3200);
    await p.goBack(); await sleep(3200);
    const h1 = await p.evaluate(() => location.hash), t1 = await topOf(p, "#about");
    ok("browser Back returns to #about and scrolls there", h1 === "#about" && t1 !== null && t1 >= 0 && t1 <= 220, `hash=${h1} top=${t1}`);
    await p.goForward(); await sleep(3200);
    const h2 = await p.evaluate(() => location.hash), t2 = await topOf(p, "#works");
    ok("browser Forward returns to #works and scrolls there", h2 === "#works" && t2 !== null && t2 >= 0 && t2 <= 220, `hash=${h2} top=${t2}`);
    await p.close();
  }

  // direct links + refresh
  for (const id of ["works", "experience", "contact"]) {
    const p = await open(b, "/index.html#" + id);
    await sleep(1500);
    let t = await topOf(p, "#" + id);
    ok(`direct URL index.html#${id} lands on section`, t !== null && t >= -5 && t <= 220, `top=${t}`);
    await p.reload({ waitUntil: "networkidle0" }); await sleep(7000);
    t = await topOf(p, "#" + id);
    ok(`refresh on #${id} stays on section`, t !== null && t >= -5 && t <= 220, `top=${t}`);
    await p.close();
  }

  // keyboard focus after navigation + skip link
  {
    const p = await open(b, "/index.html");
    await p.evaluate(() => document.querySelector('a[href="#experience"]').click()); await sleep(3200);
    const f = await p.evaluate(() => document.activeElement && document.activeElement.id);
    ok("focus moves to the target section after navigation", f === "experience", "active=" + f);
    await p.close();
  }

  // project pages: load, menu links go back to index sections, contact works on the page
  for (const page of ["hostel-hunt", "eskoolia", "nxdesk"]) {
    const p = await open(b, `/${page}.html`);
    const h1 = await p.evaluate(() => document.querySelector("h1") && document.querySelector("h1").textContent.trim());
    ok(`${page}.html loads with its title`, !!h1, h1);
    ok(`${page}.html has no console errors`, p._errs.length === 0, p._errs.join(" | "));
    await p.evaluate(() => document.querySelector(".header-three-button a").click()); await sleep(3200);
    const t = await topOf(p, "#contact");
    ok(`${page}.html 'get in touch' scrolls to its Contact section`, t !== null && t >= -5 && t <= 220, `top=${t}`);
    await p.evaluate(() => document.querySelector('.tw-main-menu-mobile a[href="index.html#about"]').click());
    await sleep(6500);
    const url = await p.evaluate(() => location.pathname + location.hash), tt = await topOf(p, "#about");
    ok(`${page}.html menu 'About' navigates to index.html#about and lands`, /index\.html#about$/.test(url) && tt !== null && tt >= -5 && tt <= 220, `url=${url} top=${tt}`);
    await p.close();
  }

  // work cards open the right pages
  {
    const p = await open(b, "/index.html");
    const hrefs = await p.evaluate(() => Array.from(document.querySelectorAll(".portfolio-three-item a[href]")).map((a) => a.getAttribute("href")));
    const uniq = [...new Set(hrefs)].sort();
    ok("work cards link only to existing project pages", uniq.every((u) => /^(hostel-hunt|eskoolia|nxdesk)\.html(#owner)?$/.test(u)), uniq.join(", "));
    const dead = await p.evaluate(async () => { const out = []; for (const a of document.querySelectorAll("a[href]")) { const h = a.getAttribute("href"); if (/^(#|mailto:|https?:)/.test(h) || h === "") continue; const u = h.split("#")[0]; if (u && !(await fetch(u)).ok) out.push(h); } return out; });
    ok("every internal link target exists", dead.length === 0, dead.join(", "));
    const bad = await p.evaluate(() => Array.from(document.querySelectorAll('a[href="#"]')).map((a) => a.className.slice(0, 40)));
    console.log('Links that are just "#":', JSON.stringify(bad));
    await p.close();
  }

  await b.close();
  const fails = results.filter((r) => !r.pass);
  console.log(`\n${results.length - fails.length}/${results.length} passed`);
  process.exit(fails.length ? 1 : 0);
})().catch((e) => { console.error("TEST ERROR", e); process.exit(2); });
