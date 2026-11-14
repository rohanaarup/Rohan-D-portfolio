/* Portfolio additions: email assembled in the browser, and the booking-lock walkthrough. */
(function () {
  "use strict";

  // Email is built here so it never sits in the page source as plain text.
  document.querySelectorAll("a.rd-mail").forEach(function (a) {
    var addr = a.getAttribute("data-u") + "@" + a.getAttribute("data-h");
    a.setAttribute("href", "mailto:" + addr);
    if (a.hasAttribute("data-icon")) return;
    var b = a.querySelector("b");
    if (b) b.textContent = addr; else a.textContent = addr;
  });

  // Booking walkthrough
  var root = document.querySelector(".rd-ex");
  if (!root) return;
  var steps = [
    { cap: "Two students tap Book on Bed B at the same moment. Both requests reach the API together.", a: "Request in flight", b: "Request in flight", bed: "Available", tone: "" },
    { cap: "Student A's request opens a database transaction and locks the bed row with select_for_update.", a: "Transaction open, row locked", b: "Request in flight", bed: "Locked by A", tone: "is-locked" },
    { cap: "Student B's request uses SKIP LOCKED, sees the row is taken and is told the bed is no longer available. No waiting, no second booking.", a: "Creating the hold", b: "Told: bed unavailable", bed: "Locked by A", tone: "is-locked" },
    { cap: "A's transaction commits with an expiring bed hold. B can pick another bed.", a: "Hold created, with an expiry", b: "Choosing another bed", bed: "Held by A", tone: "is-held" },
    { cap: "If A does not pay before the hold expires, a background job releases it and the bed becomes available again.", a: "Hold expired", b: "Can try Bed B again", bed: "Available", tone: "" }
  ];
  var i = 0;
  var laneA = document.getElementById("ex-a"), laneB = document.getElementById("ex-b"), bed = document.getElementById("ex-bed");
  var cap = document.getElementById("ex-cap");
  var back = root.querySelector('[data-act="back"]'), next = root.querySelector('[data-act="next"]');
  function render() {
    var s = steps[i];
    laneA.querySelector(".rd-ex-state").textContent = s.a;
    laneB.querySelector(".rd-ex-state").textContent = s.b;
    bed.querySelector(".rd-ex-state").textContent = s.bed;
    bed.className = "rd-ex-bed " + s.tone;
    laneA.classList.toggle("is-active", i >= 1 && i <= 3);
    laneB.classList.toggle("is-active", i === 2);
    cap.innerHTML = "<b>Step " + (i + 1) + " of " + steps.length + ".</b>" + s.cap.replace(/&/g, "&amp;").replace(/</g, "&lt;");
    back.disabled = i === 0;
    next.disabled = i === steps.length - 1;
  }
  root.addEventListener("click", function (e) {
    var act = e.target && e.target.getAttribute && e.target.getAttribute("data-act");
    if (!act) return;
    if (act === "next" && i < steps.length - 1) i++;
    else if (act === "back" && i > 0) i--;
    else if (act === "reset") i = 0;
    render();
  });
  render();
})();

/* Reduced motion: no preloader, no scroll smoothing, content visible immediately. */
(function () {
  if (!window.matchMedia || !window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  document.documentElement.classList.add("rd-reduce");
  window.addEventListener("load", function () {
    try { if (window.ScrollSmoother && window.ScrollSmoother.get()) window.ScrollSmoother.get().kill(); } catch (e) { /* ignore */ }
  });
})();

/* ---------- In-page navigation ----------
   The template scrolls through GSAP ScrollSmoother, so native #hash jumps do not move the page.
   This handler scrolls through the smoother, closes the menu, keeps the URL hash in sync,
   supports back/forward and direct links, and moves keyboard focus to the target section. */
(function () {
  "use strict";
  var OFFSET = 110; // clears the sticky header
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isIndex = /(^|\/)(index\.html)?$/.test(location.pathname);

  function smoother() {
    try { return window.ScrollSmoother && window.ScrollSmoother.get ? window.ScrollSmoother.get() : null; } catch (e) { return null; }
  }
  function targetFor(hash) {
    if (!hash || hash === "#") return null;
    try { return document.querySelector(hash); } catch (e) { return null; }
  }
  function scrollToEl(el, animate) {
    var s = smoother();
    if (s) { s.scrollTo(el, animate && !reduce, "top " + OFFSET + "px"); return; }
    var y = el.getBoundingClientRect().top + window.pageYOffset - OFFSET;
    window.scrollTo({ top: Math.max(0, y), behavior: animate && !reduce ? "smooth" : "auto" });
  }
  function scrollTop(animate) {
    var s = smoother();
    if (s) s.scrollTo(0, animate && !reduce); else window.scrollTo({ top: 0, behavior: animate && !reduce ? "smooth" : "auto" });
  }
  function focusEl(el) {
    if (!el.hasAttribute("tabindex")) el.setAttribute("tabindex", "-1");
    try { el.focus({ preventScroll: true }); } catch (e) { /* ignore */ }
  }
  function closeMenu() {
    var area = document.querySelector(".tw-offcanvas-2-area");
    if (area && area.classList.contains("opened")) {
      var btn = document.querySelector(".tw-offcanvas-2-close-btn");
      if (btn) btn.click(); else area.classList.remove("opened");
    }
  }
  function go(hash, animate, push) {
    var el = targetFor(hash);
    if (hash === "#home" || (!el && (!hash || hash === "#"))) { scrollTop(animate); if (push) history.pushState(null, "", hash || location.pathname); return true; }
    if (!el) return false;
    scrollToEl(el, animate);
    if (push) history.pushState(null, "", hash);
    focusEl(el);
    return true;
  }

  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
    if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || a.target === "_blank") return;
    var href = a.getAttribute("href");
    var m = href.match(/^(?:index\.html)?(#[\w-]*)$/);
    if (!m) return;
    if (/^index\.html/.test(href) && !isIndex) return;   // from another page: let the browser load index.html#section
    if (m[1] === "#") return;                  // "#" = back-to-top button, handled by the template
    if (!targetFor(m[1]) && m[1] !== "#home") return;
    e.preventDefault();
    closeMenu();
    go(m[1], true, true);
  }, true);

  window.addEventListener("popstate", function () { go(location.hash, true, false); });
  // Direct link such as index.html#works: wait for the preloader, then jump.
  if (location.hash && targetFor(location.hash)) {
    var tries = 0;
    var t = setInterval(function () {
      var pre = document.querySelector(".preloader");
      var done = !pre || getComputedStyle(pre).display === "none" || pre.getBoundingClientRect().bottom < 0;
      if (done || ++tries > 60) { clearInterval(t); setTimeout(function () { go(location.hash, false, false); }, 150); }
    }, 100);
  }
})();

/* ---------- Scroll progress bar (GSAP ScrollTrigger, already on the page) ---------- */
(function () {
  var bar = document.querySelector(".rd-progress");
  if (!bar || !window.gsap || !window.ScrollTrigger) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) { bar.style.display = "none"; return; }
  window.gsap.to(bar, { scaleX: 1, ease: "none", scrollTrigger: { start: 0, end: "max", scrub: 0.3 } });
})();
