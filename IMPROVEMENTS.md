# ScanDriver — Summary of Improvements (v1 → v2)

**Standard applied:** same brand, instantly recognisable — clearly upgraded execution.

## 0. Cinematic video hero (homepage)
- The homepage hero now plays a **muted, looping night-drive film** (black sedan gliding through a lit city) behind the headline — the footage's black + warm-gold palette is the brand palette, so it reads as a custom brand film.
- Headline updated to **"Your ride, your journey."** with the gold gradient accent; the original tagline "Your driver, one scan away" is preserved in the page title and the scan-to-book card.
- Engineered, not just embedded: AI watermark removed from the footage, audio stripped, compressed to **2.2 MB** (H.264, `faststart` for instant streaming), poster frame preloaded for instant paint, **scrim gradients** keep every word legible, and the film melts into the page with a fade — no hard edge.
- **Light theme** keeps the dark cinematic band while hero text stays cream/gold (scoped token overrides).
- **Accessibility & performance**: `prefers-reduced-motion` users get the static poster instead of motion; video is `aria-hidden` (decorative), `playsinline` for iOS, Picture-in-Picture/remote-playback disabled, autoplay-safe (muted).

## 1. Brand & trust restoration
- The v1 shell shipped without the real logo (text wordmark fallback) and without the driver photo. v2 restores the **original brand logo** (trimmed, optimized 9 KB, retina-sharp), a **light-theme ink variant** so the wordmark never disappears on cream backgrounds, and the **original driver photo** (compressed 67 KB, progressive).
- New: full **favicon set** (16→512 px + ICO + Apple touch icon) cropped from the brand shield emblem — the browser tab now carries the brand.
- New: branded **1200x630 Open Graph image** (gold glow, logo, tagline) — shared links on WhatsApp/LinkedIn/Twitter now preview like a premium brand, not a blank card.

## 2. Typography (identity reconnect)
- Body/UI text switched to **Manrope — the font the original site uses** — reconnecting the rebuild to the original's typographic identity. Bricolage Grotesque remains for display headlines, keeping the rebuild's editorial personality.
- Fluid heading scale, balanced text wrapping, tabular numerals on stats/pricing, refined letter-spacing.

## 3. Visual elevation
- Ambient **gold radial glows** (dark + light) give depth without changing the identity palette (#080808 / #c9a24b).
- **Gold gradient accents** on key headline phrases ("one scan away.", "We verify them.", …) and gradient gold buttons with a hover shine sweep + lift.
- Editorial **kickers** (small gold uppercase labels) above major section headings.
- Panels, testimonial cards (decorative quote marks, hover lift + gold ring), service rows (hover tint + arrow nudge), steps (gradient number coins) all refined.
- Footer gains a gold hairline top gradient; custom scrollbar + gold selection color.

## 4. Motion & micro-interactions (all respect prefers-reduced-motion)
- Scroll-triggered **staggered reveals** on every section.
- **Count-up animation** on stats (500+, <2 min, 1,000+).
- Hero QR **"pass" card**: floats gently, scan line loops, **3D tilt** follows the pointer on desktop.
- **Trust marquee**: verification badges auto-scroll on wide screens, pause on hover.
- Sticky header **elevates on scroll**; nav links get sliding gold underlines; mobile menu links indent on hover.

## 5. Conversion & UX additions
- **WhatsApp floating button** (desktop) — reinforces the WhatsApp-first brand promise; **back-to-top** button appears on long pages.
- Full-width CTA buttons on small phones; larger, more confident header logo (matching the original's brand presence).

## 6. SEO & performance
- Every page: **canonical URL, og:title/description/image/url, Twitter large-image card**.
- **sitemap.xml + robots.txt** (with sitemap reference); enriched **Organization JSON-LD** (url + logo).
- Header logo **preloaded with explicit dimensions** (no CLS), images compressed, fonts load with `display=swap` + preconnect, CSS/JS are single small files with zero dependencies.

## 7. Verified working (browser-tested, desktop 1440px + mobile 390px)
- All 11 pages return 200; navigation, breadcrumbs, theme toggle (persists), mobile menu, skip-link, focus states OK.
- **Booking form end-to-end**: validation (car-type check confirmed), live summary, WhatsApp handoff with full pre-filled booking details verified.
- Both dark (default) and light themes render correctly with correct logo variant per theme.
