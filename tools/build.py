#!/usr/bin/env python3
"""Generates the static ScanDriver site into the project root.

You do NOT need to run this to deploy: the finished .html files are already in the
project root. Run it only if you want to change shared parts (nav, footer, copy):

    pip install segno
    python3 tools/build.py
"""
import io
import json
import os
import re

import segno

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CUSTOMER_TEL = "+919717498198"
CUSTOMER_DISPLAY = "+91 97174 98198"
DRIVER_TEL = "+919718181498"
DRIVER_DISPLAY = "+91 97181 81498"
EMAIL = "care@scandriver.in"
GRIEVANCE = "grievance@scandriver.in"
WA_CUSTOMER = "https://wa.me/919717498198"
WA_BOOK_TEXT = "https://wa.me/919717498198?text=Hi%20ScanDriver!%20I%20need%20a%20driver."
WA_DRIVER_APPLY = "https://wa.me/919718181498?text=Hi%20ScanDriver!%20I%20want%20to%20join%20as%20a%20driver."
FACEBOOK = "https://www.facebook.com/profile.php?id=61590935150854"
INSTAGRAM = "https://www.instagram.com/scan_driver/"

FONT_URL = (
    "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:"
    "opsz,wdth,wght@12..96,75..100,200..800&display=swap"
)

# ---------------------------------------------------------------- icons

ICONS = {
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "chat": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9z"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "close": '<path d="M18 6 6 18M6 6l12 12"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "rupee": '<path d="M6 3h12M6 8h12M6 13l8.5 8M6 13h3M9 13c6.667 0 6.667-10 0-10"/>',
    "trend": '<path d="m22 7-8.5 8.5-5-5L2 17"/><path d="M16 7h6v6"/>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
}


def ic(name, cls="icon"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


def sprite():
    symbols = "".join(
        f'<symbol id="i-{n}" viewBox="0 0 24 24">{p}</symbol>' for n, p in ICONS.items()
    )
    return (
        '<svg width="0" height="0" style="position:absolute" aria-hidden="true" '
        f'focusable="false">{symbols}</svg>'
    )


def qr_svg(data, label):
    q = segno.make(data, error="m")
    svg = q.svg_inline(dark="#17140d", light=None, border=0)
    # segno emits a fixed width/height; swap for a viewBox so CSS can scale it
    svg = re.sub(r'width="(\d+)" height="(\d+)"', r'viewBox="0 0 \1 \2" shape-rendering="crispEdges"', svg, count=1)
    return svg.replace("<svg ", f'<svg role="img" aria-label="{label}" ', 1)


# ---------------------------------------------------------------- content

SERVICES = [
    ("hourly", "Hourly driver", "Book a driver by the hour for errands, appointments, or short trips across Delhi NCR."),
    ("monthly", "Monthly driver", "Dedicated personal driver for the entire month. Consistent, trusted, and always on time."),
    ("weekly", "Weekly driver", "Need a driver just for the week? Our weekly packages are flexible and hassle-free."),
    ("outstation", "Outstation driver", "Long-distance trips, city-to-city travel, or hill station trips, handled by experienced outstation drivers."),
    ("corporate", "Corporate driver", "Professional chauffeurs for executives and corporate fleets. Uniformed, punctual, discreet."),
    ("airport", "Airport transfer", "On-time pickups and drops to Delhi IGI Airport. Track your flight, stress-free transfer guaranteed."),
    ("event", "Event &amp; wedding driver", "Elegantly dressed, reliable drivers for weddings, social events, and ceremonies across NCR."),
]

ALSO = [
    ("daily", "Daily driver services"),
    ("school", "School pickup &amp; drop driver services"),
]

CARS = [
    ("Hatchback", "Alto, WagonR, i20"),
    ("Sedan", "Dzire, Ciaz, Amaze"),
    ("SUV", "Innova, Ertiga, Creta"),
    ("Luxury", "BMW, Audi, Mercedes"),
]

TESTIMONIALS = [
    (
        "Got a driver within 2 hours of messaging on WhatsApp. He was polite, punctual and very professional. Highly recommend ScanDriver for monthly hiring.",
        "Rahul Sharma", "Sector 50, Gurgaon",
    ),
    (
        "Used ScanDriver for my company's executive travel. The driver was in uniform, arrived early, and drove impeccably. Will continue using for corporate needs.",
        "Priya Mehta", "Connaught Place, Delhi",
    ),
    (
        "Booked for my daughter's wedding. The driver showed up perfectly on time, was respectful throughout and handled outstation too. Great experience overall.",
        "Sunita Agarwal", "Noida Sector 18",
    ),
]

NAV = [
    ("services.html", "Services", "services"),
    ("how-it-works.html", "How it works", "how"),
    ("why-us.html", "Why us", "why"),
    ("join-driver.html", "Join as a driver", "join"),
    ("contact.html", "Contact", "contact"),
]

LEGAL = [
    ("terms.html", "Terms &amp; conditions", "terms"),
    ("privacy-policy.html", "Privacy policy", "privacy"),
    ("cancellation-and-refund-policy.html", "Cancellation &amp; refund", "cancel"),
]


# ---------------------------------------------------------------- shell

THEME_INIT = (
    "try{if(localStorage.getItem('sd-theme')==='light')"
    "document.documentElement.setAttribute('data-theme','light')}catch(e){}"
)


def cur(key, active):
    return ' aria-current="page"' if key == active else ""


def header(active):
    links = "".join(
        f'<a class="nav__link" href="{href}"{cur(key, active)}>{label}</a>'
        for href, label, key in NAV
    )
    explore = "".join(
        f'<a href="{href}"{cur(key, active)}>{label}</a>' for href, label, key in NAV
    )
    legal = "".join(
        f'<a href="{href}"{cur(key, active)}>{label}</a>' for href, label, key in LEGAL
    )
    book_cur = cur("booking", active)
    return f"""
<header class="site-header">
  <div class="wrap site-header__bar">
    <a class="brand" href="index.html" aria-label="ScanDriver home"><img src="assets/logo-sd.png" alt="ScanDriver" height="34" data-fallback="wordmark"></a>
    <nav class="nav" aria-label="Main">{links}</nav>
    <div class="header-actions">
      <a class="icon-btn header-actions__contact" href="tel:{CUSTOMER_TEL}" aria-label="Call ScanDriver">{ic("phone")}</a>
      <a class="icon-btn header-actions__contact" href="{WA_CUSTOMER}" target="_blank" rel="noopener" aria-label="Message ScanDriver on WhatsApp">{ic("chat")}</a>
      <button class="icon-btn theme-toggle" type="button" data-theme-toggle aria-pressed="false" aria-label="Switch to light mode">{ic("sun", "icon icon--sun")}{ic("moon", "icon icon--moon")}</button>
      <a class="btn btn--gold btn--sm header-book" href="booking.html">Book now</a>
      <button class="icon-btn menu-btn" type="button" data-menu-toggle aria-expanded="false" aria-controls="menu-panel" aria-label="Open menu">{ic("menu", "icon icon--open")}{ic("close", "icon icon--close")}</button>
    </div>
  </div>
  <div class="menu-panel" id="menu-panel" hidden>
    <div class="wrap menu-panel__inner">
      <div class="menu-group"><p class="menu-group__title">Explore</p>{explore}</div>
      <div class="menu-group"><p class="menu-group__title">Book</p><a href="booking.html"{book_cur}>Book a driver</a></div>
      <div class="menu-group"><p class="menu-group__title">Legal</p>{legal}</div>
    </div>
  </div>
</header>"""


def action_bar(kind):
    if kind == "driver":
        return f"""<div class="action-bar">
  <a class="btn btn--line" href="tel:{DRIVER_TEL}">{ic("phone")}Call</a>
  <a class="btn btn--line" href="https://wa.me/919718181498" target="_blank" rel="noopener">{ic("chat")}WhatsApp</a>
  <a class="btn btn--gold" href="{WA_DRIVER_APPLY}" target="_blank" rel="noopener">Apply</a>
</div>"""
    return f"""<div class="action-bar">
  <a class="btn btn--line" href="tel:{CUSTOMER_TEL}">{ic("phone")}Call</a>
  <a class="btn btn--line" href="{WA_CUSTOMER}" target="_blank" rel="noopener">{ic("chat")}WhatsApp</a>
  <a class="btn btn--gold" href="booking.html">Book now</a>
</div>"""


def footer(bar="customer"):
    svc = "".join(
        f'<li><a href="booking.html?service={k}">{n}</a></li>' for k, n, _ in SERVICES
    )
    legal = "".join(f'<li><a href="{h}">{l}</a></li>' for h, l, _ in LEGAL)
    return f"""
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="index.html" aria-label="ScanDriver home"><img src="assets/logo-sd.png" alt="ScanDriver" height="34" loading="lazy" data-fallback="wordmark"></a>
        <p>Delhi NCR's most trusted on-demand verified driver service. Professional drivers for every need, no app required.</p>
        <div class="footer-social">
          <a href="{FACEBOOK}" target="_blank" rel="noopener">Facebook</a>
          <a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a>
          <a href="{WA_CUSTOMER}" target="_blank" rel="noopener">WhatsApp</a>
        </div>
      </div>
      <div class="footer-col"><h2>Services</h2><ul>{svc}</ul></div>
      <div class="footer-col"><h2>Company</h2><ul>
        <li><a href="why-us.html">Why ScanDriver</a></li>
        <li><a href="how-it-works.html">How it works</a></li>
        <li><a href="join-driver.html">Join as a driver</a></li>
        <li><a href="contact.html">Contact</a></li>
      </ul></div>
      <div class="footer-col"><h2>Legal</h2><ul>{legal}</ul></div>
      <div class="footer-col"><h2>Contact</h2><ul>
        <li><a href="tel:{CUSTOMER_TEL}">Customer: 97174 98198</a></li>
        <li><a href="tel:{DRIVER_TEL}">Driver: 97181 81498</a></li>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li><a href="mailto:{GRIEVANCE}">Grievance@scandriver.in</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2026 Scan Driver Private Limited. All rights reserved.</p>
      <p>Delhi NCR, India</p>
    </div>
  </div>
</footer>
{action_bar(bar)}"""


def page(filename, title, desc, body, active=None, scripts=("js/main.js",), jsonld=None, bar="customer"):
    og_title = title
    ld = ""
    if jsonld:
        ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>'
    script_tags = "".join(f'<script src="{s}" defer></script>' for s in scripts)
    html = f"""<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#080808">
<meta property="og:site_name" content="ScanDriver">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{desc}">
<meta name="twitter:card" content="summary">
<script>{THEME_INIT}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONT_URL}">
<link rel="stylesheet" href="css/style.css">
{ld}
</head>
<body>
{sprite()}
<a class="skip-link" href="#main">Skip to content</a>
{header(active)}
<main id="main">
{body}
</main>
{footer(bar)}
{script_tags}
</body>
</html>
"""
    with open(os.path.join(ROOT, filename), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", filename)


# ---------------------------------------------------------------- shared blocks


def service_rows(with_desc=True):
    rows = []
    for key, name, desc in SERVICES:
        plain = name.replace("&amp;", "and")
        rows.append(
            f"""<li class="service">
  <h3>{name}</h3>
  <p>{desc}</p>
  <a class="link service__go" href="booking.html?service={key}" aria-label="Book {plain.lower()}">Book now</a>
</li>"""
        )
    return '<ul class="service-list">' + "".join(rows) + "</ul>"


def steps():
    return """<ol class="steps">
  <li class="step"><span class="step__n" aria-hidden="true">1</span><div>
    <h3>Scan or message</h3>
    <p>Scan the QR code or directly WhatsApp us. Tell us your date, time, and driver requirement.</p>
    <p class="step__note">Your driver, just 1 scan away</p>
  </div></li>
  <li class="step"><span class="step__n" aria-hidden="true">2</span><div>
    <h3>Get a verified driver</h3>
    <p>We assign you a verified, background-checked driver matched to your need, within minutes.</p>
  </div></li>
  <li class="step"><span class="step__n" aria-hidden="true">3</span><div>
    <h3>Ride safely</h3>
    <p>Your driver arrives on time. No app, no signup. Just safe, reliable, professional driving.</p>
  </div></li>
</ol>"""


def chat_mock():
    return """<div class="chat-wrap">
<figure class="chat" aria-label="Sample WhatsApp booking conversation">
  <div class="chat__bar"><span class="chat__avatar" aria-hidden="true">SD</span><div><b>ScanDriver</b><small>Online, typically replies instantly</small></div></div>
  <div class="chat__body">
    <div class="msg msg--out"><p>Hi! I need a driver for tomorrow 9am from Gurgaon Sector 50.</p><time>10:32 AM</time></div>
    <div class="msg msg--in"><p>&#128075; Hello! We have verified drivers available tomorrow morning.</p><p>Please share:<br>&#128205; Pickup location<br>&#128344; Exact time<br>&#128467;&#65039; Duration needed</p><time>10:32 AM</time></div>
    <div class="msg msg--out"><p>Sector 50, 9am, need for full day (8 hours)</p><time>10:33 AM</time></div>
    <div class="msg msg--in"><p>&#9989; Confirmed! Your verified driver <b>Ramesh K.</b> will arrive at 9:00 AM sharp.</p><p>&#128203; Driver ID shared. 8-hour rate: &#8377;800.<br>No app needed, we handle everything here.</p><time>10:33 AM</time></div>
  </div>
</figure>
<p class="chat__note">Sample conversation</p>
</div>"""


def pointers():
    return f"""<div class="panel">
  <h3>Good to know</h3>
  <ul class="tick-list">
    <li>{ic("check")}<span>Nearby verified driver at your doorstep within <b>60 minutes</b>.</span></li>
    <li>{ic("check")}<span>All drivers are experienced and background verified.</span></li>
    <li>{ic("check")}<span><b>Pay at the end of the trip.</b> No advance needed.</span></li>
    <li>{ic("check")}<span>No need to provide food or travel expenses to the driver.</span></li>
  </ul>
</div>"""


def pricing():
    return f"""<div class="panel">
  <h3>Pricing and extra charges</h3>
  <ul class="tick-list">
    <li>{ic("check")}<span><b>&#8377;8 per km</b> extra if actual distance exceeds your booked KM limit.</span></li>
    <li>{ic("check")}<span>Waiting period: <b>&#8377;40 every half hour</b> (after a 15-minute start delay exception).</span></li>
    <li>{ic("check")}<span>Driver return charges are <b>already included</b> in the package.</span></li>
    <li>{ic("check")}<span><b>&#8377;200 Night Travel Allowance (NTA)</b> applicable between 10:00 PM and 6:00 AM.</span></li>
  </ul>
</div>"""


def checks():
    items = [
        ("shield", "Aadhaar and licence verified", "Every driver's Aadhaar card and driving license is manually verified before onboarding."),
        ("shield", "Background and criminal record check", "Full criminal background check + minimum 2 reference verifications before any driver is onboarded."),
        ("shield", "Reference check", "Trusted references are verified before a driver joins our network."),
        ("shield", "5+ years experience required", "We only work with experienced, professional drivers. No rookies."),
    ]
    out = "".join(
        f'<li class="check">{ic(i)}<div><h3>{t}</h3><p>{d}</p></div></li>' for i, t, d in items
    )
    return f'<ul class="checks">{out}</ul>'


def testimonials():
    first = True
    out = []
    for text, name, place in TESTIMONIALS:
        cls = "quote quote--lead" if first else "quote"
        first = False
        initial = name[0]
        out.append(
            f"""<figure class="{cls}">
  <span class="stars" role="img" aria-label="5 out of 5 stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
  <blockquote>&ldquo;{text}&rdquo;</blockquote>
  <figcaption><b>{name}</b><span>{place}</span></figcaption>
</figure>"""
        )
    return '<div class="quotes">' + "".join(out) + "</div>"


def cta_block(title="Ready to book your driver?", text="Message us on WhatsApp and get a driver assigned in minutes."):
    return f"""<section class="section section--raised cta">
  <div class="wrap">
    <h2>{title}</h2>
    <p>{text}</p>
    <div class="cta__actions">
      <a class="btn btn--gold" href="booking.html">Book now</a>
      <a class="btn btn--line" href="tel:{CUSTOMER_TEL}">{ic("phone")}Call now</a>
    </div>
    <div class="contact-lines">
      <div><span>Customer</span><a href="tel:{CUSTOMER_TEL}">{CUSTOMER_DISPLAY}</a></div>
      <div><span>Driver signup</span><a href="tel:{DRIVER_TEL}">{DRIVER_DISPLAY}</a></div>
      <div><span>Email</span><a href="mailto:{EMAIL}">{EMAIL}</a></div>
    </div>
  </div>
</section>"""


def stats_three():
    return """<div class="wrap"><div class="stats">
  <div class="stat"><span class="stat__num">500+</span><span class="stat__label"><b>Our drivers</b>Verified &amp; active</span></div>
  <div class="stat"><span class="stat__num">&lt; 2 min</span><span class="stat__label"><b>Response time</b>WhatsApp reply</span></div>
  <div class="stat"><span class="stat__num">1,000+</span><span class="stat__label"><b>Happy customers</b>Across Delhi NCR</span></div>
</div></div>"""


def stats_four():
    return """<div class="stats stats--four">
  <div class="stat"><span class="stat__num">500+</span><span class="stat__label">Verified drivers in network</span></div>
  <div class="stat"><span class="stat__num">1K+</span><span class="stat__label">Happy customers served</span></div>
  <div class="stat"><span class="stat__num">24/7</span><span class="stat__label">WhatsApp support available</span></div>
  <div class="stat"><span class="stat__num">100%</span><span class="stat__label">Background checked drivers</span></div>
</div>"""


def head(title, intro, crumb=None, wide=False):
    cr = ""
    if crumb:
        cr = f'<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span aria-hidden="true">/</span><span>{crumb}</span></nav>'
    cls = "page-hero page-hero--wide" if wide else "page-hero"
    p = f"<p>{intro}</p>" if intro else ""
    return f'<section class="{cls}"><div class="wrap">{cr}<h1>{title}</h1>{p}</div></section>'


# ---------------------------------------------------------------- pages


def build_home():
    qr = qr_svg(WA_BOOK_TEXT, "QR code that opens a WhatsApp chat with ScanDriver")
    trust = "".join(
        f'<li>{ic("check")}{t}</li>'
        for t in [
            "Background verified, 2 refs",
            "Aadhaar checked",
            "Licence verified",
            "Reference checked",
            "Available 24/7",
            "No app needed",
            "Instant WhatsApp booking",
            "Delhi NCR coverage",
        ]
    )
    body = f"""
<section class="hero">
  <div class="wrap">
    <div class="hero__grid">
      <div>
        <p class="hero__status">{ic("pin")}Now serving across Delhi NCR</p>
        <h1>Your driver, one scan away.</h1>
        <p class="hero__lede">Verified, background-checked, and professionally trained drivers, available hourly, weekly, or monthly. No app needed. Just WhatsApp.</p>
        <div class="hero__cta">
          <a class="btn btn--gold" href="booking.html">Book now</a>
          <a class="btn btn--line" href="services.html">Explore services</a>
        </div>
      </div>
      <div class="pass-wrap">
        <div class="pass">
          <p class="pass__cap">Scan to book on WhatsApp</p>
          <div class="pass__qr">{qr}<span class="pass__scan" aria-hidden="true"></span></div>
          <p class="pass__sub">Quick, easy, no app needed</p>
        </div>
      </div>
    </div>
    <ul class="trust">{trust}</ul>
  </div>
</section>

{stats_three()}

<section class="section" id="services">
  <div class="wrap">
    <div class="section-head">
      <h2>Driver services built for every need</h2>
      <p>From a quick hourly ride to a full-time monthly driver, we've got you covered across Delhi NCR.</p>
    </div>
    {service_rows()}
    <p style="margin-top:28px"><a class="link" href="services.html">See all services, cars and pricing</a></p>
  </div>
</section>

<section class="section section--raised" id="how-it-works">
  <div class="wrap">
    <div class="section-head">
      <h2>Book a driver in 3 easy steps</h2>
    </div>
    <div class="steps-grid">
      {steps()}
      <div>{pointers()}<p style="margin-top:22px"><a class="link" href="how-it-works.html">See how WhatsApp booking works</a></p></div>
    </div>
  </div>
</section>

<section class="section" id="why-us">
  <div class="wrap two-col">
    <div class="section-head" style="margin-bottom:0">
      <h2>We don't just find drivers. We verify them.</h2>
      <p>Every ScanDriver driver goes through a multi-layer verification before they ever sit behind your wheel. Your safety isn't a feature, it's our foundation.</p>
      <div class="hero__cta"><a class="btn btn--gold" href="booking.html">Book now</a><a class="btn btn--line" href="why-us.html">Why ScanDriver</a></div>
    </div>
    {checks()}
  </div>
</section>

<section class="section section--raised">
  <div class="wrap">
    <div class="section-head"><h2>Trusted by families and professionals across Delhi NCR</h2></div>
    {testimonials()}
  </div>
</section>

<section class="section section--tight">
  <div class="wrap band">
    <div>
      <h2>Are you a professional driver? Join ScanDriver.</h2>
      <p>Earn on your schedule. Join Delhi NCR's fastest-growing verified driver network. We bring you trusted customers, you bring the skills.</p>
    </div>
    <a class="btn btn--gold" href="join-driver.html">Join as a driver</a>
  </div>
</section>

{cta_block()}
"""
    ld = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "ScanDriver",
        "legalName": "ScanDriver Private Limited",
        "description": "Delhi NCR's most trusted on-demand driver service. Verified, professional drivers booked via WhatsApp.",
        "areaServed": "Delhi NCR",
        "email": EMAIL,
        "telephone": CUSTOMER_TEL,
        "sameAs": [FACEBOOK, INSTAGRAM],
    }
    page(
        "index.html",
        "ScanDriver | Your driver, one scan away | Delhi NCR",
        "Delhi NCR's most trusted on-demand driver service. Hire verified, professional drivers hourly, weekly, monthly or for outstation. Book via WhatsApp instantly.",
        body,
        jsonld=ld,
    )


def build_services():
    cars = "".join(f'<li class="car"><b>{n}</b><span>{m}</span></li>' for n, m in CARS)
    also = "".join(
        f'<a class="chip chip--link" href="booking.html?service={k}">{n}</a>' for k, n in ALSO
    )
    body = f"""
{head("Driver services built for every need", "From a quick hourly ride to a full-time monthly driver, we've got you covered across Delhi NCR.", "Services")}

<section class="section" style="padding-top:0">
  <div class="wrap">
    {service_rows()}
    <div style="margin-top:36px">
      <h2 style="font-size:1.4rem;margin-bottom:14px">Also available</h2>
      <div class="chip-list">{also}</div>
    </div>
  </div>
</section>

<section class="section section--raised">
  <div class="wrap two-col">
    <div class="section-head" style="margin-bottom:0">
      <h2>Pick the car you drive</h2>
      <p>Tell us your car type when you book, and we match a driver who is comfortable with it.</p>
    </div>
    <ul class="cars">{cars}</ul>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    {pricing()}
    {pointers()}
  </div>
  <div class="wrap" style="margin-top:28px"><p>Full terms are in our <a class="link" href="terms.html">terms &amp; conditions</a> and <a class="link" href="cancellation-and-refund-policy.html">cancellation &amp; refund policy</a>.</p></div>
</section>

{cta_block()}
"""
    page(
        "services.html",
        "Driver services in Delhi NCR | Hourly, monthly, outstation | ScanDriver",
        "Hourly, weekly, monthly, corporate, airport, outstation and wedding drivers across Delhi NCR. Verified, background-checked, booked on WhatsApp.",
        body,
        active="services",
    )


def build_how():
    body = f"""
{head("Book a driver in 3 easy steps", "No app downloads. No long forms. No waiting. Book, track, and communicate with your driver entirely through WhatsApp, in under 2 minutes.", "How it works")}

<section class="section" style="padding-top:0">
  <div class="wrap steps-grid">
    {steps()}
    <div>
      {chat_mock()}
      <div class="chip-list" style="margin-top:18px"><span class="chip">No app</span><span class="chip">Replies in under 2 minutes</span><span class="chip">Verified drivers</span></div>
    </div>
  </div>
  <div class="wrap hero__cta" style="margin-top:36px">
    <a class="btn btn--gold" href="booking.html">Book now</a>
    <a class="btn btn--line" href="{WA_BOOK_TEXT}" target="_blank" rel="noopener">{ic("chat")}Message on WhatsApp</a>
  </div>
</section>

<section class="section section--raised">
  <div class="wrap split">
    {pointers()}
    {pricing()}
  </div>
</section>

{cta_block()}
"""
    page(
        "how-it-works.html",
        "How booking works | WhatsApp-first driver booking | ScanDriver",
        "Book a verified driver in three steps with no app and no signup. Scan the QR code or message us on WhatsApp and get a driver in minutes.",
        body,
        active="how",
    )


def build_why():
    differ = [
        ("Verified professionals", "Every driver is carefully screened before joining our platform, giving customers complete peace of mind."),
        ("Experienced network", "We work with skilled drivers who understand city routes, highway driving, corporate etiquette, and customer service."),
        ("Fast response", "Our team helps customers connect with available drivers in minutes through a simple WhatsApp-based booking process."),
        ("Transparent service", "No hidden procedures or complicated booking systems, just straightforward, dependable driver solutions."),
        ("Customer-first approach", "From families and working professionals to corporate clients and event organizers, we focus on delivering punctual, safe, and hassle-free experiences."),
    ]
    defs = "".join(f'<li class="def"><h3>{t}</h3><p>{d}</p></li>' for t, d in differ)
    values = [
        ("S", "Safety", "Our top priority. Ensuring multi-layer driver verification and secure rides for complete peace of mind."),
        ("C", "Care", "Empathy toward both drivers and customers, cultivating a supportive, respectful community."),
        ("A", "Accountability", "Owning our service quality, maintaining complete transparency, and standing by our bookings."),
        ("N", "Never settle", "Always refining our network, optimizing booking speed, and exceeding passenger expectations."),
    ]
    vals = "".join(
        f'<li class="value"><span class="value__letter" aria-hidden="true">{l}</span><div><h3>{l} &mdash; {t}</h3><p>{d}</p></div></li>'
        for l, t, d in values
    )
    solutions = [
        "Hourly driver services",
        "Daily driver services",
        "Weekly &amp; monthly driver hiring",
        "School pickup &amp; drop driver services",
        "Corporate driver solutions",
        "Airport pickup &amp; drop drivers",
        "Outstation drivers",
        "Event &amp; wedding chauffeurs",
    ]
    chips = "".join(f'<li class="chip">{s}</li>' for s in solutions)
    body = f"""
{head("We don't just find drivers. We verify them.", "Every ScanDriver driver goes through a multi-layer verification before they ever sit behind your wheel. Your safety isn't a feature, it's our foundation.", "Why us", wide=True)}

<section class="section" style="padding-top:0">
  <div class="wrap">
    {checks()}
    <div style="margin-top:32px"><a class="btn btn--gold" href="booking.html">Book now</a></div>
  </div>
</section>

<section class="section section--raised"><div class="wrap">{stats_four()}</div></section>

<section class="section" id="story">
  <div class="wrap two-col">
    <div class="section-head" style="margin-bottom:0">
      <h2>Your trusted driver partner in Delhi NCR</h2>
    </div>
    <div>
      <div class="prose-block">
        <h3>Our core philosophy</h3>
        <p>At ScanDriver, we believe that finding a professional and reliable driver should be simple, fast, and stress-free. We connect individuals, families, and businesses with thoroughly verified, experienced drivers for hourly, daily, monthly, corporate, airport, and outstation requirements.</p>
      </div>
      <div class="prose-block">
        <h3>Uncompromised safety</h3>
        <p>Every driver in our network goes through a multi-step verification process, including identity verification, driving licence validation, background checks, and reference screening. This ensures that every ride is backed by professionalism, safety, and accountability.</p>
      </div>
      <div class="prose-block">
        <h3>Why we started</h3>
        <p>Modern urban life moves quickly, but hiring a trustworthy driver often remains complicated and time-consuming. ScanDriver was created to simplify this process through a WhatsApp-first booking experience that eliminates unnecessary apps, lengthy paperwork, and endless phone calls.</p>
        <p>Whether you need a driver for a few hours, a weekend trip, daily office commute, or long-term personal assistance, we make the process quick and reliable.</p>
      </div>
      <div class="prose-block">
        <h3>Driven by trust</h3>
        <p>With a growing network of verified drivers and satisfied customers across Delhi NCR, ScanDriver continues to set new standards for reliability, professionalism, and customer support. We are committed to making every journey safer, smoother, and more comfortable, because the right driver can make all the difference.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section--raised">
  <div class="wrap">
    <div class="mv">
      <div><h3>Our mission</h3><p>To become India's most trusted driver aggregation platform by delivering safe, verified, and technology-enabled driver services while creating flexible earning opportunities for professional drivers.</p></div>
      <div><h3>Our vision</h3><p>To redefine on-demand driver hiring through trust, transparency, and convenience, making professional driving services accessible to every household and business.</p></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap two-col">
    <div class="section-head" style="margin-bottom:0">
      <h2>What makes us different</h2>
      <p>The safety protocols, response times, and customer-first focus that set ScanDriver apart.</p>
    </div>
    <ul class="defs">{defs}</ul>
  </div>
</section>

<section class="section section--raised">
  <div class="wrap two-col">
    <div class="section-head" style="margin-bottom:0">
      <h2>Our core values</h2>
      <p>Our actions are guided by a simple acronym representing our promise.</p>
    </div>
    <ul class="values">{vals}</ul>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>Comprehensive solutions we provide</h2></div>
    <ul class="chip-list">{chips}</ul>
  </div>
</section>

<section class="section section--raised">
  <div class="wrap">
    <div class="section-head"><h2>Trusted by families and professionals across Delhi NCR</h2></div>
    {testimonials()}
  </div>
</section>

{cta_block()}
"""
    page(
        "why-us.html",
        "Why ScanDriver | Verified drivers you can trust | Delhi NCR",
        "Aadhaar, licence, background and reference checks on every driver. Learn how ScanDriver verifies drivers and why Delhi NCR families and companies trust us.",
        body,
        active="why",
    )


def build_join():
    perks = [
        ("rupee", "Guaranteed earnings", "Weekly payouts with no delays. Transparent rate structure."),
        ("clock", "Flexible timing", "Work full-time, part-time, or hourly. You set the schedule."),
        ("shield", "Trusted platform", "Work only with verified, genuine customers. Zero harassment guarantee."),
        ("trend", "Career growth", "Top drivers get priority assignments, bonuses, and corporate client access."),
    ]
    items = "".join(
        f'<li class="check">{ic(i)}<div><h3>{t}</h3><p>{d}</p></div></li>' for i, t, d in perks
    )
    body = f"""
{head("Are you a professional driver? Join ScanDriver.", "Earn on your schedule. Join Delhi NCR's fastest-growing verified driver network. We bring you trusted customers, you bring the skills.", "Join as a driver", wide=True)}

<section class="section" style="padding-top:0">
  <div class="wrap join-grid">
    <div>
      <ul class="checks">{items}</ul>
      <div class="prose-block" style="margin-top:36px">
        <h3>Who we work with</h3>
        <p>We only work with experienced, professional drivers, with 5+ years of experience. Every driver goes through the same multi-layer verification: Aadhaar and licence checks, a criminal background check, and reference checks.</p>
      </div>
    </div>
    <div>
      <figure class="join-photo"><img src="assets/driver_pic.jpeg" alt="A ScanDriver driver" loading="lazy" data-fallback="hide"></figure>
      <div class="callout" style="margin-top:22px">
        <h3>Start earning today</h3>
        <p>Join 500+ verified drivers already earning with ScanDriver. WhatsApp us to apply now.</p>
        <span class="callout__label">Driver WhatsApp</span>
        <span class="callout__number">{DRIVER_DISPLAY}</span>
        <a class="btn btn--gold" href="{WA_DRIVER_APPLY}" target="_blank" rel="noopener">{ic("chat")}Apply as a driver</a>
      </div>
    </div>
  </div>
</section>

"""
    page(
        "join-driver.html",
        "Join ScanDriver as a driver | Earn on your schedule | Delhi NCR",
        "Professional drivers in Delhi NCR: join ScanDriver for weekly payouts, flexible timing and verified customers. Apply on WhatsApp.",
        body,
        active="join",
        bar="driver",
    )


def build_contact():
    body = f"""
{head("Have questions? Send an enquiry.", "Whether you need a monthly driver, corporate chauffeur, outstation round-trip, or have specific package queries, send us an enquiry. Our customer relationship team will reach out with customized quotes within 15 minutes.", "Contact", wide=True)}

<section class="section" style="padding-top:0">
  <div class="wrap form-grid form-grid--contact">
    <form id="enquiry-form" class="form" novalidate>
      <div class="field">
        <label for="e-name">Full name</label>
        <input class="input" id="e-name" name="name" type="text" autocomplete="name" required>
        <p class="error" hidden></p>
      </div>
      <div class="field">
        <label for="e-phone">Phone number</label>
        <input class="input" id="e-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="98765 43210" required>
        <p class="error" hidden></p>
      </div>
      <div class="field">
        <label for="e-message">Your message or service requirements <span class="opt">(optional)</span></label>
        <textarea class="textarea" id="e-message" name="message"></textarea>
      </div>
      <button class="btn btn--gold" type="submit">Send enquiry on WhatsApp</button>
      <p class="hint">Your enquiry opens in WhatsApp so our team can reply to you there.</p>
      <p class="form-status" id="enquiry-status" role="status" hidden></p>
    </form>
    <div>
      <ul class="checks">
        <li class="check">{ic("shield")}<div><h3>Dedicated relationship manager</h3><p>Assigned to handle all your bookings &amp; updates.</p></div></li>
        <li class="check">{ic("rupee")}<div><h3>Tailored custom quotes</h3><p>Customized billing options for long term requirements.</p></div></li>
      </ul>
      <div class="contact-lines" style="grid-template-columns:1fr">
        <div><span>Customer</span><a href="tel:{CUSTOMER_TEL}">{CUSTOMER_DISPLAY}</a></div>
        <div><span>Driver signup</span><a href="tel:{DRIVER_TEL}">{DRIVER_DISPLAY}</a></div>
        <div><span>Email</span><a href="mailto:{EMAIL}">{EMAIL}</a></div>
        <div><span>Grievances</span><a href="mailto:{GRIEVANCE}">{GRIEVANCE}</a></div>
      </div>
    </div>
  </div>
</section>
"""
    page(
        "contact.html",
        "Contact ScanDriver | Enquiries and custom quotes | Delhi NCR",
        "Send an enquiry for monthly, corporate or outstation drivers in Delhi NCR. Our relationship team replies with a custom quote within 15 minutes.",
        body,
        active="contact",
        scripts=("js/main.js", "js/forms.js"),
    )


def build_booking():
    trips = "".join(
        f"""<label class="choice"><input type="radio" name="trip" value="{v}"{" checked" if v == "Hourly" else ""}><span><b>{v}</b></span></label>"""
        for v in ["Hourly", "One way", "Round trip", "Monthly", "Outstation"]
    )
    cars = "".join(
        f"""<label class="choice"><input type="radio" name="car" value="{n}" data-label="{n} ({m})"><span><b>{n}</b><small>{m}</small></span></label>"""
        for n, m in CARS
    )
    dist = "".join(f'<option value="{d}">{d} km</option>' for d in range(10, 75, 5))
    body = f"""
{head("Book a verified driver instantly", "Delhi NCR's most trusted on-demand driver service.", "Book now", wide=True)}

<section class="section" style="padding-top:0">
  <div class="wrap">
    <ul class="trust" style="margin:0 0 36px;padding:0;border:0">
      <li>{ic("check")}Background verified</li>
      <li>{ic("check")}Aadhaar KYC</li>
      <li>{ic("check")}Licence checked</li>
      <li>{ic("check")}No app required</li>
    </ul>
    <div class="form-grid">
      <form id="booking-form" class="form" novalidate>
        <input type="hidden" name="service" value="">
        <p class="service-note" id="service-note" hidden></p>

        <div class="two-up">
          <div class="field">
            <label for="name">Your name</label>
            <input class="input" id="name" name="name" type="text" autocomplete="name" required>
            <p class="error" hidden></p>
          </div>
          <div class="field">
            <label for="phone">WhatsApp number</label>
            <input class="input" id="phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="98765 43210" required>
            <p class="hint hint--lock">{ic("lock")}Your personal info is secured and will not be shared.</p>
            <p class="error" hidden></p>
          </div>
        </div>

        <fieldset class="field fieldset" data-field="trip">
          <legend>Trip type</legend>
          <div class="choices choices--trip">{trips}</div>
        </fieldset>

        <fieldset class="field fieldset" data-field="car">
          <legend>Car type</legend>
          <div class="choices">{cars}</div>
          <p class="error" hidden></p>
        </fieldset>

        <div class="fields">
          <div class="field" data-lf="hours">
            <label for="hours">Total hours required</label>
            <input class="input" id="hours" name="hours" type="number" inputmode="decimal" min="2" max="24" step="0.5" placeholder="e.g. 4 (min 2 hours)">
            <p class="error" hidden></p>
          </div>

          <div class="field" data-lf="interview" role="group" aria-labelledby="iv-title">
            <div class="notice">
              {ic("clock")}
              <div>
                <h3 id="iv-title">Monthly contract interview</h3>
                <p>We organize a face-to-face trial with the candidate. Select your preferred date &amp; time below.</p>
              </div>
            </div>
            <div class="date-pair">
              <div>
                <label for="idate">Interview date</label>
                <input class="input" id="idate" name="idate" type="date">
              </div>
              <div>
                <label for="itime">Start time</label>
                <input class="input" id="itime" name="itime" type="time">
              </div>
            </div>
            <p class="when-line" id="when-line"></p>
            <a class="btn btn--line btn--sm cal-link" id="cal-link" href="https://calendar.google.com/calendar/render?action=TEMPLATE" target="_blank" rel="noopener">Add interview to Google Calendar</a>
            <p class="error" hidden></p>
          </div>

          <div class="field" data-lf="days">
            <label for="days">Working days per month</label>
            <input class="input" id="days" name="days" type="number" inputmode="numeric" min="1" max="31" step="1" placeholder="e.g. 26">
            <p class="error" hidden></p>
          </div>

          <div class="field" data-lf="perday">
            <label for="perday">Hours per day</label>
            <input class="input" id="perday" name="perday" type="number" inputmode="decimal" min="1" max="24" step="0.5" placeholder="e.g. 10">
            <p class="error" hidden></p>
          </div>

          <div class="field" data-lf="pickup">
            <label for="pickup"><span id="pickup-label-text">Pickup location</span><span class="opt" id="pickup-opt"></span></label>
            <input class="input" id="pickup" name="pickup" type="text" autocomplete="street-address" placeholder="e.g. Sector 29, Gurgaon">
            <p class="error" hidden></p>
          </div>

          <div class="field" data-lf="drop">
            <label for="drop">Drop city / location</label>
            <input class="input" id="drop" name="drop" type="text" placeholder="e.g. Jaipur, Rajasthan">
            <p class="error" hidden></p>
          </div>

          <div class="field" data-lf="distance">
            <label for="distance">Estimated distance (one way)</label>
            <select class="select" id="distance" name="distance">
              <option value="">Select distance</option>
              {dist}
            </select>
            <p class="error" hidden></p>
          </div>

          <div class="field" data-lf="location">
            <span class="field__label">Share your location <span class="opt">(optional)</span></span>
            <div class="loc-row">
              <button class="btn btn--line loc-btn" type="button" id="share-location">{ic("pin")}<span>Share location</span></button>
              <p class="hint" id="location-hint">Not shared yet. Helps us dispatch the nearest driver faster.</p>
            </div>
          </div>

          <div class="field" data-lf="datetime" role="group" aria-labelledby="dt-label">
            <span class="field__label" id="dt-label">Date and time</span>
            <div class="date-pair">
              <input class="input" id="date" name="date" type="date" aria-label="Date">
              <input class="input" id="time" name="time" type="time" aria-label="Time">
            </div>
            <p class="error" hidden></p>
          </div>

          <div class="field" data-lf="comments">
            <label for="comments">Additional comments <span class="opt">(optional)</span></label>
            <textarea class="textarea" id="comments" name="comments" placeholder="Any special requests, automatic or manual transmission, preferred language..."></textarea>
          </div>
        </div>

        <section class="summary" aria-labelledby="sum-h">
          <h2 id="sum-h">Your booking</h2>
          <dl id="preview-list"></dl>
          <p class="summary__note">Check your details, then send. This updates as you fill in the form.</p>
        </section>

        <button class="btn btn--gold btn--block" type="submit">Send booking on WhatsApp</button>
        <p class="hint">Your details will be sent to our team via WhatsApp instantly.</p>
        <p class="form-status" id="booking-status" role="status" hidden></p>
      </form>

      <div class="aside-stack">
        {pricing()}
        {pointers()}
        <p class="hint">Full details are in our <a class="link" href="terms.html">terms &amp; conditions</a> and <a class="link" href="cancellation-and-refund-policy.html">cancellation &amp; refund policy</a>.</p>
      </div>
    </div>
  </div>
</section>
"""
    page(
        "booking.html",
        "Book a verified driver | ScanDriver | Delhi NCR",
        "Book a verified, background-checked driver in Delhi NCR. Choose your trip and car, then send the booking on WhatsApp. Pay at the end of the trip.",
        body,
        active="booking",
        scripts=("js/main.js", "js/forms.js"),
    )


# ---------------------------------------------------------------- legal


def render_blocks(blocks):
    out = []
    for kind, val in blocks:
        if kind == "p":
            out.append(f"<p>{val}</p>")
        elif kind == "h3":
            out.append(f"<h3>{val}</h3>")
        elif kind == "ul":
            out.append("<ul>" + "".join(f"<li>{i}</li>" for i in val) + "</ul>")
    return "".join(out)


def legal_page(filename, key, title, subtitle, updated, sections, desc, outro=None, contact_note=None):
    toc = "".join(f'<li><a href="#{sid}">{label}</a></li>' for sid, label, _ in sections)
    secs = "".join(
        f'<section id="{sid}"><h2>{label}</h2>{render_blocks(blocks)}</section>'
        for sid, label, blocks in sections
    )
    extra = f'<p style="margin-top:36px">{outro}</p>' if outro else ""
    body = f"""
{head(title, subtitle, title)}
<section class="section" style="padding-top:0">
  <div class="wrap legal">
    <nav class="toc" aria-label="On this page"><h2>Jump to section</h2><ol>{toc}</ol></nav>
    <div class="legal-body">
      <p class="legal__meta" style="margin:0 0 28px">{updated}</p>
      {secs}
      {extra}
    </div>
  </div>
</section>
<section class="section section--raised section--tight">
  <div class="wrap band">
    <div>
      <h2>Questions regarding our policies?</h2>
      <p>Our team is available 24/7 to clarify any questions regarding ScanDriver services, terms, or customer safety policies.</p>
    </div>
    <div class="cta__actions" style="margin:0">
      <a class="btn btn--line" href="mailto:{EMAIL}">Email legal support</a>
      <a class="btn btn--gold" href="{WA_CUSTOMER}" target="_blank" rel="noopener">WhatsApp customer support</a>
    </div>
  </div>
</section>
"""
    page(filename, f"{title} | ScanDriver", desc, body, active=key)


def build_terms():
    sections = [
        ("t1", "1. Acceptance of terms", [("p", "By contacting ScanDriver via WhatsApp, phone, or website, or by using any driver service provided by us, you agree to these Terms &amp; Conditions in full. If you do not agree, please discontinue use immediately.")]),
        ("t2", "2. Nature of service", [("p", "ScanDriver is a driver aggregation and placement platform. We connect verified drivers with customers requiring on-demand driving services. ScanDriver is not a transport company and does not own vehicles.")]),
        ("t3", "3. Driver verification", [("p", "All drivers on our platform undergo multi-layer verification including Aadhaar card, driving licence, criminal background check, and a minimum of two personal references.")]),
        ("t4", "4. Payments &amp; cancellations", [("p", "All payments are to be made directly to ScanDriver or as directed by our team. Cancellation within 2 hours of the confirmed booking time may attract a cancellation fee of up to &#8377;200.")]),
        ("t5", "5. Liability &amp; limitation", [("p", "ScanDriver's liability in any dispute is strictly limited to the service fee paid for that specific booking. We are not liable for damage to the customer's vehicle or accidents caused by the driver.")]),
        ("t6", "6. Customer obligations", [("p", "Customers must ensure their vehicle is in roadworthy condition with valid documents (RC, insurance, PUC), and treat the assigned driver with respect and dignity.")]),
        ("t7", "7. Privacy &amp; data", [("p", "Customer and driver information shared with ScanDriver is used solely for service delivery and communication purposes. We do not sell or share personal data with third parties. See our <a href=\"privacy-policy.html\">privacy policy</a>.")]),
        ("t8", "8. Governing law &amp; disputes", [("p", "These terms are governed by the laws of India. Any disputes shall be subject to the exclusive jurisdiction of the courts of Delhi, India.")]),
    ]
    legal_page(
        "terms.html", "terms", "Terms &amp; conditions",
        "The terms that apply when you use ScanDriver services in Delhi NCR.",
        "Last updated: May 2026. Applicable to all users of ScanDriver services in Delhi NCR.",
        sections,
        "Terms and conditions for ScanDriver driver services in Delhi NCR, including verification, payments, cancellations, liability and governing law.",
        outro=f'For any questions regarding these terms, contact us at <a href="mailto:{EMAIL}">{EMAIL}</a> or on <a href="{WA_CUSTOMER}">WhatsApp: +91 9717-498-198</a>. ScanDriver Private Limited, Delhi NCR, India.',
    )


def build_privacy():
    sections = [
        ("intro", "Introduction", [
            ("p", "At ScanDriver (&ldquo;ScanDriver&rdquo;, &ldquo;we&rdquo;, &ldquo;our&rdquo;, or &ldquo;us&rdquo;), we value your privacy and are committed to protecting your personal information."),
            ("p", "This Privacy Policy explains how we collect, use, store, disclose and protect your information when you access or use our website, mobile applications (if any), WhatsApp services, customer support channels and any other services provided by ScanDriver (collectively, the &ldquo;Platform&rdquo;)."),
            ("p", "By using our Platform, you consent to the collection and use of your information as described in this Privacy Policy."),
        ]),
        ("p1", "1. Information we collect", [
            ("p", "Depending on the services you use, we may collect the following information:"),
            ("h3", "Personal information"),
            ("ul", ["Full name", "Mobile number", "Email address", "Residential city", "Pickup address", "Drop location", "Vehicle details (where applicable)"]),
            ("h3", "Driver partner information"),
            ("ul", ["Name &amp; mobile number", "Driving licence", "Aadhaar / identity proof &amp; PAN card", "Address proof &amp; photograph", "Bank account details", "Vehicle information &amp; verification documents"]),
            ("h3", "Technical information"),
            ("ul", ["IP address &amp; browser type", "Device information &amp; OS", "Device ID &amp; application version", "Log files &amp; crash reports"]),
            ("h3", "Location information"),
            ("p", "With your permission, location data is collected to allocate nearby Driver Partners, improve booking accuracy, assist navigation, and enhance customer support."),
        ]),
        ("p2", "2. How we collect information", [
            ("p", "Information may be collected when you:"),
            ("ul", ["Visit our website", "Submit a booking request", "Contact customer support", "Register as a customer", "Register as a Driver Partner", "Upload verification documents", "Communicate through WhatsApp", "Respond to surveys or promotions", "Make payments", "Interact with our Platform"]),
            ("p", "We may also receive information from trusted third-party service providers involved in payment processing, verification, analytics and communication services."),
        ]),
        ("p3", "3. How we use your information", [
            ("p", "We use your information for legitimate business purposes including:"),
            ("ul", ["Creating and managing your account and bookings.", "Allocating Driver Partners and verifying document compliance.", "Processing payments, issuing invoices, and delivering booking updates.", "Sending OTPs, security alerts, and preventing fraudulent activity.", "Complying with legal obligations, resolving disputes, and maintaining platform security."]),
            ("p", "Where permitted by law, we may also send promotional offers, service announcements and marketing communications. You may opt out of promotional communications at any time."),
        ]),
        ("p4", "4. Sharing of information", [
            ("p", "<strong>ScanDriver does NOT sell your personal information.</strong>"),
            ("p", "We may share information only where necessary with:"),
            ("ul", ["Driver Partners for fulfilling your booking.", "Payment gateway providers &amp; identity verification partners.", "Cloud hosting, SMS, WhatsApp, and customer support service providers.", "Analytics providers and law enforcement authorities where required by law."]),
        ]),
        ("p5", "5. Payment information", [("p", "Online payments are processed through secure third-party payment service providers. ScanDriver does not store complete debit card, credit card or UPI credentials on its own servers. Payment processing is governed by the privacy policies and security practices of the respective payment providers.")]),
        ("p6", "6. Cookies &amp; similar technologies", [
            ("p", "Our website may use cookies and similar technologies to improve website functionality, remember preferences, measure performance, and analyze visitor behaviour."),
            ("p", "You may disable cookies through your browser settings; however, certain website features may become unavailable or function less effectively."),
        ]),
        ("p7", "7. Data security", [
            ("p", "We implement commercially reasonable technical, administrative and organizational measures to protect personal information against unauthorized access, misuse, disclosure, alteration or destruction."),
            ("ul", ["Secure servers &amp; access controls", "Encrypted communications where applicable", "Internal security procedures &amp; periodic monitoring"]),
        ]),
        ("p8", "8. Account security", [("p", "You are responsible for maintaining the confidentiality of your login credentials and OTPs. You agree to notify ScanDriver immediately if you suspect unauthorized access to your account.")]),
        ("p9", "9. Data retention", [("p", "We retain personal information only for as long as reasonably necessary to provide services, meet legal obligations, resolve disputes, enforce agreements, and prevent fraud. Afterwards, data is securely deleted or anonymized.")]),
        ("p10", "10. Children's privacy", [("p", "The Platform is not intended for individuals below 18 years of age. We do not knowingly collect personal information from children.")]),
        ("p11", "11. Third-party links", [("p", "The Platform may contain links to third-party websites or services. ScanDriver does not control and is not responsible for the privacy practices or content of third-party websites.")]),
        ("p12", "12. Your rights", [
            ("p", "Subject to applicable law, you may have the right to:"),
            ("ul", ["Access your personal information.", "Request correction of inaccurate information.", "Request deletion of information where legally permissible.", "Withdraw consent for certain processing activities.", "Update account details &amp; opt out of promotional communications."]),
        ]),
        ("p13", "13. Policy updates", [("p", "ScanDriver may update this Privacy Policy from time to time to reflect changes in law, technology or business operations. Updated versions will be published on our Platform with the revised &ldquo;Last Updated&rdquo; date.")]),
        ("p14", "14. Contact us", [
            ("p", "For questions regarding this Privacy Policy or your personal information, please contact:"),
            ("p", f"ScanDriver Private Limited<br>Website: <a href=\"https://www.scandriver.in\">www.scandriver.in</a><br>Email: <a href=\"mailto:{EMAIL}\">{EMAIL}</a><br>Customer support: as published on the Platform."),
            ("h3", "Consent"),
            ("p", "By accessing or using the ScanDriver Platform, you acknowledge that you have read, understood and agreed to this Privacy Policy and consent to the collection, use and disclosure of your information as described herein."),
        ]),
    ]
    legal_page(
        "privacy-policy.html", "privacy", "Privacy policy",
        "How ScanDriver collects, uses, stores, discloses, and safeguards your personal data.",
        "Last updated: July 20, 2026",
        sections,
        "How ScanDriver collects, uses, stores, shares and protects your personal information, and the rights you have over it.",
    )


def build_cancel():
    sections = [
        ("c1", "1. Overview", [
            ("p", "This Cancellation &amp; Refund Policy (&ldquo;Policy&rdquo;) explains the circumstances under which ScanDriver (&ldquo;ScanDriver&rdquo;, &ldquo;we&rdquo;, &ldquo;our&rdquo;, or &ldquo;us&rdquo;) may process cancellations and refunds for bookings made through our website, WhatsApp, customer support channels, or any other official booking platform."),
            ("p", "By placing a booking with ScanDriver, you agree to this Policy."),
        ]),
        ("c2", "2. Booking cancellation by customer", [
            ("p", "Customers may request cancellation of a booking by contacting ScanDriver through our official support channels."),
            ("p", "Cancellation charges, if any, may depend upon:"),
            ("ul", ["Time remaining before the scheduled booking.", "Whether a Driver Partner has already been assigned.", "Whether the Driver Partner has commenced travel to the pickup location.", "Operational costs already incurred by ScanDriver."]),
            ("p", "Any applicable cancellation charges shall be communicated to the Customer at the time of cancellation, where reasonably practicable."),
        ]),
        ("c3", "3. Cancellation by ScanDriver", [
            ("p", "ScanDriver reserves the right to cancel a booking where:"),
            ("ul", ["A suitable Driver Partner is unavailable.", "Incorrect or incomplete booking information has been provided.", "Payment authorization fails.", "Fraudulent or suspicious activity is detected.", "Service cannot be safely or legally provided.", "Circumstances beyond our reasonable control prevent fulfilment of the booking."]),
            ("p", "Where payment has already been received for a booking cancelled by ScanDriver, the Customer shall generally be eligible for a refund in accordance with this Policy."),
        ]),
        ("c4", "4. Cancellation by driver partner", [
            ("p", "A Driver Partner may cancel a booking due to circumstances including, but not limited to:"),
            ("ul", ["Medical emergencies.", "Personal emergencies.", "Safety concerns.", "Vehicle access issues.", "Force majeure events."]),
            ("p", "Where reasonably possible, ScanDriver will attempt to assign another available Driver Partner. If no replacement Driver Partner can be arranged and payment has already been collected, the Customer may be eligible for a refund."),
        ]),
        ("c5", "5. Refund eligibility", [
            ("p", "Refunds may be considered in circumstances including:"),
            ("ul", ["Booking cancelled by ScanDriver.", "Driver could not be assigned.", "Duplicate or multiple payments for the same booking.", "Failed transaction resulting in debit without booking confirmation.", "Incorrect amount charged due to a technical error.", "Other situations determined by ScanDriver to warrant a refund."]),
            ("p", "Refunds are subject to verification and approval by ScanDriver."),
        ]),
        ("c6", "6. Non-refundable situations", [
            ("p", "Refunds may not be granted in circumstances including:"),
            ("ul", ["Customer no-show.", "Incorrect booking information provided by the Customer.", "Cancellation after the Driver Partner has reached the pickup location, where cancellation charges apply.", "Services already completed.", "Delays caused by traffic, weather, road conditions, or other circumstances beyond ScanDriver's reasonable control.", "Customer dissatisfaction not arising from any breach of ScanDriver's obligations."]),
            ("p", "Nothing in this section limits any rights available to Customers under applicable law."),
        ]),
        ("c7", "7. Refund request process", [
            ("p", "To request a refund, Customers should contact ScanDriver Customer Support through the official support email or other designated support channels."),
            ("p", "The refund request should include, where applicable:"),
            ("ul", ["Booking ID.", "Registered mobile number.", "Date of booking.", "Reason for the refund request.", "Supporting documents or screenshots, if available."]),
            ("p", "ScanDriver may request additional information to verify the claim before processing the refund."),
        ]),
        ("c8", "8. Refund processing", [
            ("p", "Where a refund request is approved, ScanDriver will make reasonable efforts to process the refund within <strong>7 to 10 business days</strong>."),
            ("p", "Refunds will generally be credited to the original payment method used for the booking unless otherwise required by law or mutually agreed."),
            ("p", "Actual credit timelines may vary depending upon the policies and processing times of banks, payment gateways, card issuers, UPI providers, or other financial institutions."),
        ]),
        ("c9", "9. Failed or pending transactions", [
            ("p", "If payment has been debited but no booking confirmation has been generated due to a technical issue, Customers are requested to contact ScanDriver Customer Support."),
            ("p", "Following verification, ScanDriver will make reasonable efforts to resolve the issue, including initiating a refund where appropriate."),
        ]),
        ("c10", "10. Chargebacks", [
            ("p", "Customers may have the right to initiate a chargeback through their card issuer or financial institution in accordance with the terms governing their payment method."),
            ("p", "Chargebacks are processed by the relevant financial institution and not by ScanDriver."),
            ("p", "Where a chargeback is initiated, ScanDriver reserves the right to investigate the related booking and temporarily suspend any associated account if fraudulent activity is reasonably suspected."),
        ]),
        ("c11", "11. Fraudulent claims", [
            ("p", "ScanDriver reserves the right to reject refund requests where:"),
            ("ul", ["False or misleading information has been provided.", "Fraudulent activity is suspected.", "The request is inconsistent with Platform records.", "Abuse of the refund process is detected."]),
            ("p", "Repeated misuse of the refund process may result in suspension or permanent termination of access to the Platform."),
        ]),
        ("c12", "12. Force majeure", [("p", "ScanDriver shall not be liable for delays in processing refunds arising from events beyond its reasonable control, including but not limited to: natural disasters, government restrictions, banking system outages, internet failures, payment gateway downtime, war, civil unrest, pandemics, or other force majeure events.")]),
        ("c13", "13. Changes to this policy", [("p", "ScanDriver reserves the right to modify this Cancellation &amp; Refund Policy at any time. Any updated version will be published on the Platform along with the revised &ldquo;Last Updated&rdquo; date. Continued use of the Platform after publication of the updated Policy constitutes acceptance of the revised Policy.")]),
        ("c14", "14. Contact us", [
            ("p", "For refund requests or questions relating to this Policy, please contact:"),
            ("p", f"ScanDriver Private Limited<br>Website: <a href=\"https://www.scandriver.in\">www.scandriver.in</a><br>Email: <a href=\"mailto:{EMAIL}\">{EMAIL}</a><br>Customer support: as published on the Platform."),
            ("p", "This Cancellation &amp; Refund Policy is effective from the date published on the ScanDriver Platform and forms an integral part of the ScanDriver Terms &amp; Conditions."),
        ]),
    ]
    legal_page(
        "cancellation-and-refund-policy.html", "cancel", "Cancellation &amp; refund policy",
        "Rules governing cancellations, refund eligibility, and request timelines for ScanDriver services.",
        "Last updated: July 20, 2026",
        sections,
        "ScanDriver cancellation terms, refund eligibility, processing times and how to request a refund for driver bookings in Delhi NCR.",
    )


def build_404():
    body = f"""
{head("That page isn't here", "The link may be old or mistyped. Head back to the home page, or book a driver right away.")}
<section class="section" style="padding-top:0">
  <div class="wrap hero__cta">
    <a class="btn btn--gold" href="index.html">Go to home page</a>
    <a class="btn btn--line" href="booking.html">Book a driver</a>
  </div>
</section>
"""
    page("404.html", "Page not found | ScanDriver", "This page could not be found.", body)


if __name__ == "__main__":
    build_home()
    build_services()
    build_how()
    build_why()
    build_join()
    build_contact()
    build_booking()
    build_terms()
    build_privacy()
    build_cancel()
    build_404()
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n")
    print("done")
