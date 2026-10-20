# ScanDriver — Premium Rebuild (v2, elevated)

Static site: plain HTML + CSS + vanilla JS. No framework, no build step, no backend.
Same brand identity as scandriver.in — refined execution, premium polish.

## What changed in v2 (elevation layer)

- **Brand assets restored**: the real ScanDriver logo (optimized + light-theme ink variant), driver photo, favicon set, Apple touch icon, and a branded 1200x630 og-image for social sharing.
- **Typography**: Manrope (the original brand font) now handles body/UI text; Bricolage Grotesque stays for display headlines. Fluid type scale, tabular numerals for stats.
- **Motion**: scroll-triggered reveals with stagger, count-up stats, floating QR "pass" card with 3D tilt, looping scan animation, auto-scrolling trust marquee (pauses on hover), animated nav underlines, button shine sweeps, hover lifts on cards/services, header elevation shadow on scroll.
- **New touches**: desktop WhatsApp floating action button + back-to-top, gold gradient headline accents, editorial kickers above section headings, custom scrollbar + selection color, ambient gold glow backgrounds.
- **SEO**: canonical + Open Graph + Twitter large-card meta on every page, sitemap.xml, robots.txt with sitemap reference, richer Organization JSON-LD.
- **Accessibility & performance**: prefers-reduced-motion fully respected (all effects disable), keyboard-safe, preloaded header logo with dimensions (no layout shift), compressed images, font display swap.

All original content, copy, phone numbers, links, and both themes (dark default + light) are preserved. Booking and enquiry forms still hand off to WhatsApp exactly as before.

## Pages

| File | What it is |
|---|---|
| `index.html` | Home: hero with real WhatsApp QR, services, steps, verification, reviews |
| `services.html` | All services, car types, pricing and extra charges |
| `how-it-works.html` | 3 steps, sample WhatsApp chat, key pointers |
| `why-us.html` | Story, mission and vision, verification, values, reviews |
| `join-driver.html` | Driver benefits and WhatsApp apply |
| `contact.html` | Enquiry form (opens WhatsApp) |
| `booking.html` | Booking form: layout changes per trip type, live summary, opens WhatsApp |
| `terms.html`, `privacy-policy.html`, `cancellation-and-refund-policy.html` | Legal pages |
| `404.html` | Not-found page |

## Deploy (pick one — both take under 2 minutes)

### Netlify (fastest)
1. Go to app.netlify.com → **Add new site → Deploy manually**.
2. Drag the **whole project folder** onto the drop zone.
3. Done. Rename the site in Site settings if you want a cleaner URL.

### Vercel
1. Push this folder to a GitHub repo (see below), then vercel.com → **Add New → Project → Import**.
2. Framework preset: **Other**. Build command: *(empty)*. Output directory: `.` (root). Deploy.

Or with the Vercel CLI: `npm i -g vercel && vercel --prod` from this folder.

### GitHub repo (for the "source code repository" handover)
    cd scandriver-site
    git init && git add -A && git commit -m "ScanDriver premium rebuild v2"
    git branch -M main
    git remote add origin https://github.com/<you>/scandriver.git
    git push -u origin main

## SEO note
Canonical URLs, og:url and sitemap.xml currently point to `https://scandriver.in/...`.
If you deploy under a different domain, find-and-replace that domain across the HTML files and `robots.txt`/`sitemap.xml`.

## How the forms work
Booking and enquiry forms validate in the browser, then open WhatsApp with the details
pre-filled to +91 97174 98198. Nothing is stored on a server. Trip types and their field
order are set at the top of `js/forms.js` (`LAYOUTS`).

## Editing
Styles: `css/style.css`. Behaviour: `js/main.js` (theme, menu, reveals, marquee, tilt,
FABs) and `js/forms.js` (form logic). `tools/build.py` generated v1 and is kept for
reference only — v2 edits were made directly to the HTML, so do **not** re-run it
(it would overwrite the upgrades).
