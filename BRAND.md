# West Street Baptist Church — Brand Reference

**Canonical source:** [`west-street-baptist-brand-sheet.html`](./west-street-baptist-brand-sheet.html).
This file is a quick text mapping of that sheet into the code. When the brand sheet
changes, update [`website/static/website/css/tokens.css`](./website/static/website/css/tokens.css)
and the SVG assets in `website/static/website/img/` to match.

- **Church:** West Street Baptist Church — Pueblo, Colorado
- **Tagline / scripture line:** *Bible Teaching Verse by Verse*

## Palette (brand sheet §05 — drawn from the original roadside sign)

| Token          | Hex       | Use |
|----------------|-----------|-----|
| `--sunday-blue`| `#2E5DA6` | Wordmark, headlines, links, primary buttons |
| `--ink`        | `#1C2733` | Body text, dark surfaces, reverse logo bg |
| `--parchment`  | `#F2EEE3` | Page background |
| `--sky`        | `#8FB4D4` | Accents, sign borders, reverse wordmark |
| `--slate`      | `#5C6C7C` | Muted text, eyebrows, captions |

Derived surfaces: `--paper #F7F4EB`, `--paper-2 #F9F6EE`, `--hairline rgba(28,39,51,.09)`.

## Type (brand sheet §07)

- **Asap** — weights 400 / 500 / 600 / 700, plus 400/600 italic (loaded from Google Fonts).
- Wordmark & headlines: **Asap 700**. Tagline & scripture lines: **Asap 600 italic**.

## Logo assets (brand sheet §01–04, copied verbatim as SVG)

- `website/static/website/img/logo-lockup.svg` — primary lockup (Sunday Blue on light).
- `website/static/website/img/logo-lockup-reverse.svg` — reverse (Sky on ink).
- `website/static/website/img/mark.svg` — standalone cross + circle mark.
- `website/static/website/img/favicon.svg` — favicon (cross + circle on ink).

## Service times (brand sheet §06 sign panel)

- Sunday School — **10 AM**
- Worship — **11 AM & 6 PM**
- Wednesday Bible Study & Prayer — **7 PM**
