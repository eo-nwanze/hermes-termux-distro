# Case Study: Full-site business scrape of incogni.com (Termux, 2026-10)

Goal: scrape a competitor's whole site and extract their business model (pricing, funnel, positioning) for a rival business plan.

## What worked (step-by-step recipe)

1. **Recon first:** fetch `/robots.txt` (allowed all + `Sitemap:` directive) and `/sitemap.xml` directly with `Fetcher.get()`. Incogni's sitemap listed exactly 7 pages — no need for blind BFS crawling.
2. **SitemapSpider with explicit catch-all rule** (critical — empty `rules()` silently drops everything):
   ```python
   class SiteSpider(SitemapSpider):
       sitemap_urls = ["https://target.com/sitemap.xml"]
       allowed_domains = {"target.com"}
       concurrent_requests = 2
       download_delay = 0.5
       robots_txt_obey = True
       def configure_sessions(self, manager):
           manager.add("fast", FetcherSession(impersonate="chrome"))
       def rules(self):
           return [CrawlRule(LinkExtractor(allow=()), callback=self.parse)]
       async def parse(self, response):
           yield {...}  # plain dict only — str values, never Path objects
   ```
3. **Per-page extraction:** `page.css("title::text").get()`, `meta[name=description]::attr(content)`, `h1/h2/h3::text`, `li::text`, `a::attr(href)`, `page.get_all_text()` for regex price extraction (`\$\d[\d,]*\.?\d*`), and `page.markdown(main_content_only=True)` for a clean LLM-ready copy of each page. Saved one `.md` per page + a consolidated `extracted.json`.
4. **Pricing teardown:** regex over full-page text catches every price variant on marketing pages (monthly/annual toggles show BOTH prices in static HTML: e.g. `$7.99/month` annual-effective + `Billed at ~~$191.76~~ **$95.88** annually` strikethroughs — grep for `Billed at` to separate annual from monthly cleanly).
5. **Funnel discovery:** the sitemap's `/am-i-exposed` page = the free scanner lead magnet; `/affiliate` + `/referral` = growth programs. Footer link lists (opt-out guides, programs) reveal the whole SEO strategy — Incogni's footer links to dozens of `blog.incogni.com/{broker}-opt-out-guide/` pages = their primary organic channel.

## Pitfalls hit (and fixes)

- **Empty rules = 0 items, no error.** Always provide the catch-all CrawlRule (above).
- **`Path` in yielded dict → engine TypeError every page.** `OUT / (slug + ".md")` then `str(md_path)`.
- **JS-only SPA page** (incogni.com/affiliate): static fetch returned a 9 KB React shell ("enable JavaScript"). Fixed by fetching the lazy route chunk `/assets/index-3e4f9fd1.js` from the route import map and grepping the minified bundle for commission strings; also cross-checked via web search for the referral terms (40% bounty, cap $120).
- **`page.markdown()` and `.css()` all work fine inside spider callbacks** — Response objects support the full Selector API.

## Reusable output shape
One `.md` per page (title + markdown), one JSON with `{url, title, meta_description, h1/h2/h3, price_hits, dollar_amounts, bullets, links, md_file}` per page — that's enough to write a competitor's business plan from.
