/* ScanDriver: theme, menu, fallbacks + premium layer (reveals, count-up, marquee, tilt, FABs).
   Zero dependencies. Everything degrades gracefully without JS. */
(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  root.classList.add("js");

  /* ---- Theme ---- */
  var toggles = document.querySelectorAll("[data-theme-toggle]");

  function isLight() {
    return root.getAttribute("data-theme") === "light";
  }

  function syncToggles() {
    var light = isLight();
    toggles.forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(light));
      btn.setAttribute("aria-label", light ? "Switch to dark mode" : "Switch to light mode");
    });
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", light ? "#fbfaf7" : "#080808");
  }

  toggles.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var next = isLight() ? "dark" : "light";
      if (next === "light") root.setAttribute("data-theme", "light");
      else root.removeAttribute("data-theme");
      try { localStorage.setItem("sd-theme", next); } catch (e) { /* storage unavailable */ }
      syncToggles();
    });
  });
  syncToggles();

  /* ---- Mobile menu ---- */
  var menuBtn = document.querySelector("[data-menu-toggle]");
  var menuPanel = document.getElementById("menu-panel");

  function setMenu(open) {
    if (!menuBtn || !menuPanel) return;
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    menuPanel.hidden = !open;
  }

  if (menuBtn && menuPanel) {
    menuBtn.addEventListener("click", function () {
      setMenu(menuBtn.getAttribute("aria-expanded") !== "true");
    });
    menuPanel.addEventListener("click", function (e) {
      if (e.target.closest("a")) setMenu(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menuBtn.getAttribute("aria-expanded") === "true") {
        setMenu(false);
        menuBtn.focus();
      }
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth >= 900) setMenu(false);
    });
  }

  /* ---- Image fallbacks ----
     Brand links hold two stacked logos (dark-theme + light-theme ink).
     If either file is missing, swap the whole brand for the wordmark. */
  function wordmark() {
    var span = document.createElement("span");
    span.className = "wordmark";
    span.innerHTML = "Scan<span>Driver</span>";
    return span;
  }

  document.querySelectorAll(".brand").forEach(function (brand) {
    var first = brand.querySelector("img");
    if (!first) return;
    function fail() { first.replaceWith(wordmark()); brand.querySelectorAll("img").forEach(function (i) { i.remove(); }); }
    first.addEventListener("error", fail, { once: true });
    if (first.complete && first.naturalWidth === 0) fail();
  });
  document.querySelectorAll("img[data-fallback]:not(.brand img)").forEach(function (img) {
    img.addEventListener("error", function () {
      if (img.parentElement) img.parentElement.hidden = true;
    }, { once: true });
  });

  /* ---- Header elevation on scroll ---- */
  var header = document.querySelector(".site-header");
  var lastScrolled = false;
  function headerState() {
    var scrolled = window.scrollY > 8;
    if (scrolled !== lastScrolled) {
      lastScrolled = scrolled;
      if (header) header.classList.toggle("is-scrolled", scrolled);
    }
  }
  headerState();
  window.addEventListener("scroll", headerState, { passive: true });

  /* ---- Scroll reveals (auto-tagged; content visible without JS) ---- */
  var REVEAL_SELECTORS = [
    ".section-head", ".kicker", ".service", ".panel", ".quote", ".step", ".check",
    ".value", ".def", ".car", ".chip", ".mv > div", ".prose-block", ".join-photo",
    ".callout", ".band > div", ".band > .btn", ".contact-lines", ".chat",
    ".hero__status", ".hero h1", ".hero__lede", ".hero__cta", ".pass-wrap",
    ".stat", ".page-hero .crumbs", ".page-hero h1", ".page-hero p", ".trust", ".stats"
  ];

  function initReveals() {
    if (reduceMotion || !("IntersectionObserver" in window)) return;
    var targets = [];
    REVEAL_SELECTORS.forEach(function (sel) {
      document.querySelectorAll(sel).forEach(function (el) { targets.push(el); });
    });
    if (!targets.length) return;
    var groups = new Map();
    targets.forEach(function (el) {
      if (el.closest(".menu-panel")) return;
      var cls = el.classList.contains("pass-wrap") ? "rv-scale" : "rv";
      el.classList.add(cls);
      var parent = el.parentElement;
      if (!groups.has(parent)) groups.set(parent, 0);
      var idx = groups.get(parent);
      groups.set(parent, idx + 1);
      if (idx) el.style.setProperty("--rv-delay", Math.min(idx * 70, 420) + "ms");
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("rv-in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
    targets.forEach(function (el) { io.observe(el); });
  }

  /* ---- Stat count-up ---- */
  function initCountUp() {
    if (reduceMotion || !("IntersectionObserver" in window)) return;
    var nums = document.querySelectorAll(".stat__num");
    if (!nums.length) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        animate(entry.target);
      });
    }, { threshold: 0.5 });

    nums.forEach(function (el) {
      var raw = el.textContent.trim();
      var m = raw.match(/^([^\d]*)([\d.,]+)(.*)$/);
      if (!m) return;
      el.dataset.pre = m[1];
      el.dataset.value = m[2].replace(/,/g, "");
      el.dataset.post = m[3];
      io.observe(el);
    });

    function animate(el) {
      var target = parseFloat(el.dataset.value);
      if (!isFinite(target) || target === 0) return;
      var dur = 1300, start = null, decimals = (el.dataset.value.split(".")[1] || "").length;
      function frame(ts) {
        if (start === null) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        var val = target * eased;
        var shown = decimals ? val.toFixed(decimals) : Math.round(val).toLocaleString("en-IN");
        el.textContent = el.dataset.pre + shown + el.dataset.post;
        if (p < 1) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }
  }

  /* ---- Trust marquee (wide screens, motion allowed) ---- */
  function initMarquee() {
    var trust = document.querySelector(".trust");
    if (!trust || reduceMotion) return;
    var mq = window.matchMedia("(min-width: 900px)");
    var original = trust.innerHTML;
    function build() {
      if (mq.matches) {
        if (trust.classList.contains("trust--marquee")) return;
        trust.classList.add("trust--marquee");
        trust.innerHTML = '<div class="trust__track"><ul>' + original + '</ul><ul aria-hidden="true">' + original + "</ul></div>";
      } else {
        if (!trust.classList.contains("trust--marquee")) return;
        trust.classList.remove("trust--marquee");
        trust.innerHTML = original;
      }
    }
    mq.addEventListener ? mq.addEventListener("change", build) : mq.addListener(build);
    build();
  }

  /* ---- QR pass tilt (fine pointers only) ---- */
  function initTilt() {
    var pass = document.querySelector(".pass");
    if (!pass || reduceMotion || !window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
    var wrap = pass.closest(".pass-wrap") || pass;
    wrap.addEventListener("pointermove", function (e) {
      var r = pass.getBoundingClientRect();
      var px = (e.clientX - r.left) / r.width - 0.5;
      var py = (e.clientY - r.top) / r.height - 0.5;
      pass.style.setProperty("--tilt-y", (px * 10).toFixed(2) + "deg");
      pass.style.setProperty("--tilt-x", (-py * 8).toFixed(2) + "deg");
    });
    wrap.addEventListener("pointerleave", function () {
      pass.style.setProperty("--tilt-x", "0deg");
      pass.style.setProperty("--tilt-y", "0deg");
    });
  }

  /* ---- Floating action stack: WhatsApp + back-to-top (desktop) ---- */
  function initFabs() {
    if (window.innerWidth < 900) return;
    var stack = document.createElement("div");
    stack.className = "fab-stack";
    var wa = document.createElement("a");
    wa.className = "fab fab--wa";
    wa.href = "https://wa.me/919717498198";
    wa.target = "_blank";
    wa.rel = "noopener";
    wa.setAttribute("aria-label", "Chat with ScanDriver on WhatsApp");
    wa.innerHTML = '<svg class="icon" aria-hidden="true" focusable="false"><use href="#i-chat"/></svg>';
    var top = document.createElement("button");
    top.type = "button";
    top.className = "fab fab--top is-off";
    top.setAttribute("aria-label", "Back to top");
    top.innerHTML = '<svg class="icon" aria-hidden="true" focusable="false" viewBox="0 0 24 24" style="stroke-width:2"><path d="M12 19V5m-7 7 7-7 7 7"/></svg>';
    top.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
    });
    stack.appendChild(wa);
    stack.appendChild(top);
    document.body.appendChild(stack);
    requestAnimationFrame(function () { wa.classList.add("is-on"); });
    window.addEventListener("scroll", function () {
      top.classList.toggle("is-off", window.scrollY < 640);
    }, { passive: true });
  }

  function initHeroVideo() {
    if (!matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    document.querySelectorAll("video").forEach(function (v) {
      v.pause();
      v.removeAttribute("autoplay");
    });
  }

  function initAll() {
    initReveals();
    initCountUp();
    initMarquee();
    initTilt();
    initFabs();
    initHeroVideo();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAll);
  } else {
    initAll();
  }
})();
