---
name: osint-startme
description: Use when reading start.me OSINT pages; needs JS proxy.
---

# start.me OSINT research

- start.me pages are client-side rendered: raw HTTP fetch returns a ~4KB shell, no tool links. To read a page, use `curl https://r.jina.ai/<start.me-url>` from terminal (browser backend unavailable on this device).
- Some old community page IDs 404 — verify before citing (e.g. osintutopia `start.me/p/kz/...` is dead as of 2026-10).
- Working pages verified live: NixIntel `https://start.me/p/rx6Qj8/nixintel-s-osint-resource-list`, Bederov email `https://start.me/p/b5gEPe/email-osint`, NCSO phone `https://start.me/p/2p1x6J/15-phone-number-business-register`, NCSO index `https://start.me/p/BnrMKd/01-ncso`.
- Search start.me pages externally: Google dork `site:start.me "OSINT"`, or SMAT at smart.myosint.training (indexes start.me widgets; blocked from web_extract here — use browser or curl).
- tools.osintnewsletter.com serves GitBook markdown via `.md` suffix; email category is `email-address-osint.md` (not `email-osint.md`). Query interface: `?ask=<q>&goal=<g>`.
- Interaction model: start.me is a curated link dashboard, not a search engine — click tool links and enter identifiers; in-page Ctrl+F to navigate huge pages; pages can be followed/duplicated with a free account.
- Local open-source lookup tools already on device: Maigret (maigret-web, port 5001), SearXNG (8888), domain recon skill.
