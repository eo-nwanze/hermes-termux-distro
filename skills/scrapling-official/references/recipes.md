# Real-world recipes & case studies

These are worked examples from pages that fail naive scraping. They teach the
*method*, not copy-paste code — adapt the field names to the target.

---

## Recipe 1: Stateful MVC form (the VicRoads case)

**Problem:** A government portal (`https://www.vicroads.vic.gov.au/.../vehicle-registration-enquiry/`)
that silently returns the *unchanged form* when you POST with a bare `Fetcher()`.

**Symptom:** `Fetcher().get()` then `Fetcher().post()` returns an identical 200 page,
no visible error, and the data never appears.

**Root cause:** The page is an ASP.NET MVC form. The server binds
`__RequestVerificationToken` to a cookie set on the GET. A bare `Fetcher().post()`
starts a brand-new session with no matching cookie → antiforgery fails → server
returns the untouched form. This is the classic "silent same-page POST" trap.

**Correct method — a cookie-persisting `FetcherSession`:**

```python
from scrapling.fetchers import FetcherSession
import re

url = "https://www.vicroads.vic.gov.au/registration/buy-sell-or-transfer-a-vehicle/check-vehicle-registration/vehicle-registration-enquiry/"

with FetcherSession(impersonate="chrome") as session:
    # 1) GET the form. Cookies (ASP.NET_SessionId, __RequestVerificationToken,
    #    __cf_bm, etc.) are captured and attached to every later request.
    page = session.get(url, stealthy_headers=True)
    assert page.status == 200

    # 2) Extract hidden fields (token + state-machine ids) from the form.
    form_html = page.body.decode() if isinstance(page.body, bytes) else page.body
    fields = {
        m.group(1): (m.group(2) if m.group(2) else "")
        for m in re.finditer(
            r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"',
            form_html,
        )
    }

    # 3) Determine which input fields are actually active.
    #    The form uses data-show-when-rule="..." to toggle fields per vehicle type.
    #    Read those rules to map them to field indices:
    #      permitNumberNotSelected       -> InputFields[1]
    #      permitNumberSelected          -> InputFields[2]  (permit number)
    #      registrationCarSelected       -> InputFields[3]  (rego, maxlen 6)   <-- our target
    #      registrationMotorcycleSelected-> InputFields[4]  (rego, maxlen 5)
    #      registrationCaravanSelected   -> InputFields[5]  (rego, maxlen 6)
    #      vinSelected                   -> InputFields[6]  (VIN, maxlen 17)
    #      chassisNumberSelected         -> InputFields[7]  (chassis, maxlen 20)
    data = dict(fields)
    data["FormApplicationItem.Forms[0].Sections[0].InputFields[0].Value"] = "car"          # vehicle type
    data["FormApplicationItem.Forms[0].Sections[0].InputFields[1].Value"] = "registration"  # identifier type
    data["FormApplicationItem.Forms[0].Sections[0].InputFields[3].Value"] = "AGU621"        # active rego field
    # every other InputFields[N].Value -> "" (empty, since only #3 is active for car+registration)

    # 4) POST on the SAME session. Cookies/token carry across, so antiforgery validates.
    resp = session.post(url, data=data, stealthy_headers=True)
    out = resp.body.decode() if isinstance(resp.body, bytes) else resp.body
    # Response is now the RESULTS page (redirect target: .../vehicle-registration-enquiry-results?details=...),
    # not the form. Parse the <dt>/<dd> pairs for the vehicle details.
```

**Result (AGU621, verified):**
- Registration status: **Current — expires 23/12/2026**
- Serial: 3230260 · Year: 2015 · Make: MAZDA · Body: SEDAN · Colour: BLUE
- VIN: JM0BM527810205937 · Engine: PE20721045 · Compliance: 12/2015
- Sanctions: None · Goods carrying: No · Transfer in dispute: No

**Key takeaways**
1. **Always reuse one `FetcherSession`** for any stateful page (GET then POST).
2. **Inspect `data-show-when-rule`** (or equivalent JS) to know which fields are live.
   Filling a field whose rule isn't selected — or sending hidden fields as non-empty —
   changes the response silently.
3. **A "silent same-page POST" is a token/session error**, not "the site blocked me".
   Fix the session, don't blindly switch to stealth mode.
4. **If the POST truly is AJAX/JS**, the real endpoint lives in the framework JS
   (inspect `mvc-form-concat.js` for `fetch(`/`$.post(`/`JSON.stringify` + a URL).
   On VicRoads it was actually a normal POST — the session was the only problem.

---

## Recipe 2: Quick pattern for simpler stateful pages (login, search-with-token)

Same idea, smaller form — no need to read per-vehicle-type rules:

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate="chrome") as session:
    page = session.get("https://site.example/login", stealthy_headers=True)
    data = {
        m.group(1): (m.group(2) or "")
        for m in re.finditer(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', page.body)
    }
    data["username"] = "user"
    data["password"] = "pass"
    resp = session.post("https://site.example/login", data=data, stealthy_headers=True)
    # now authenticated; subsequent session.get() calls carry the login cookie
    account = session.get("https://site.example/account", stealthy_headers=True)
```

---

## Recipe 3: Parser-only (no network) — works everywhere

When you already have HTML (from the CLI, a saved file, or another tool):

```python
from scrapling.parser import Selector

page = Selector("<html>... <div class='quote'>...</div></html>")
quotes = [e.text for e in page.css('.quote .text')]
```

`Selector` needs no fetcher and works on Android. Use it for offline parsing and for
turning CLI-fetched HTML into structured data.

---

## Recipe 4: The method is correct but the server crashes (crash-vs-rejection)

**Problem:** A stateful form POST that worked in an earlier run starts returning
`errorpage?error=An+unhandled+exception+occurred.` on every attempt — including when
the payload is byte-identical to a request that succeeded moments before. This is
exactly what happened to the VicRoads vehicle-registration enquiry (WSL162): the same
`FetcherSession` method returned AGU621's results hours earlier, then every subsequent
WSL162 POST returned the same error page.

**Do NOT rewrite the method on first failure.** First distinguish three outcomes
(see SKILL.md → "Classifying a FAILED POST"):

1. **Client-side rejection** — same form page + a *validation summary* ("This field is
   required", "Please enter a value"). Fix the field; the method is fine.
2. **Server-side crash** — an *error page* (title like `Error : <site>`, URL
   `errorpage?error=...`, "An unhandled exception", ASP.NET exception detail). The
   backend failed, not your request. **Retry; do not rewrite.**
3. **Results page** — different URL/title, contains the queried value + parsed fields.

**How to prove the method is correct when the server crashes (snapshot comparison):**
- Save the successful response HTML (e.g. to a file) after the first successful POST.
- When a later POST returns the error page, diff the two saved pages: compare byte size,
  title, whether the queried value appears, and whether the "unhandled"/error markers are
  present.
- If the earlier page is a *results* page and the current one is an *error* page, the
  method is correct — the failure is a transient backend outage. Retry or schedule a
  re-check instead of rewriting the approach.

**Diagnosis steps for this case:**
```python
from scrapling.fetchers import FetcherSession
import re, time

def parse(out):
    title = re.findall(r'<title>(.*?)</title>', out, re.S)
    title = re.sub('<[^>]+>', '', title[0]).strip() if title else '?'
    pairs = re.findall(r'<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>', out, re.S)
    good = [(re.sub('<[^>]+>','',d).rstrip(':').strip(),
             re.sub('<[^>]+>','',v).strip())
            for d,v in pairs if re.sub('<[^>]+>','',d) and re.sub('<[^>]+>','',v)]
    return {
        'title': title,
        'has_query_value': 'WSL162' in out,
        'has_results_marker': 'Results for' in out,
        'has_unhandled': 'unhandled' in out.lower(),
        'has_error_title': 'Error' in title,
        'dtdd_count': len(good),
        'fields': good,
    }

with FetcherSession(impersonate="chrome") as session:
    page = session.get(url, stealthy_headers=True)
    form_html = page.body.decode() if isinstance(page.body, bytes) else page.body
    fields = {m.group(1): (m.group(2) if m.group(2) else "")
              for m in re.finditer(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', form_html)}
    data = dict(fields)
    data["FormApplicationItem.Forms[0].Sections[0].InputFields[0].Value"] = "car"
    data["FormApplicationItem.Forms[0].Sections[0].InputFields[1].Value"] = "registration"
    data["FormApplicationItem.Forms[0].Sections[0].InputFields[3].Value"] = "WSL162"
    for i in [2,4,5,6,7]:
        data[f"FormApplicationItem.Forms[0].Sections[0].InputFields[{i}].Value"] = ""
    out = session.post(url, data=data, stealthy_headers=True).body.decode()
    if isinstance(out, bytes): out = out.decode()
    info = parse(out)
    print(info['title'], '| has_query_value=', info['has_query_value'],
          '| has_results_marker=', info['has_results_marker'],
          '| has_unhandled=', info['has_unhandled'],
          '| has_error_title=', info['has_error_title'], '| dtdd=', info['dtdd_count'])
```
**Interpretation:** `has_results_marker=True` + `has_query_value=True` = success.
`has_error_title=True` + `has_unhandled=True` + `dtdd=0` = server-side crash — retry.
`has_query_value=False` + no error markers + same form as GET = client rejection — inspect fields.

**Lesson:** a crash page is evidence the backend received and processed the request
(but blew up handling it) — the request shape is correct. Only rewrite the method when
the response is the *unchanged form with a validation summary*, which is the only signal
that points at the client.

**Field notes (verified 2026-10-02, Termux/Android):**
- The enquiry GET issues `ASP.NET_SessionId`, `__RequestVerificationToken` and
  `shell#lang=en` — **no `__cf_bm` / Turnstile challenge is issued** on this page.
  Chrome TLS impersonation + stealthy headers is enough to pass their edge; a
  browser fetcher adds nothing here.
- To prove an outage is **site-wide, not rego-specific**, POST a *control* rego that
  succeeded in an earlier run (e.g. AGU621). If the control crashes identically,
  the backend is down for everyone — stop retrying and re-check later.
- VicRoads has had recurring multi-day outages around site upgrades (June 2026
  network overhaul; Oct 2026 POST handler crash). News search + a control POST are
  the two fastest ways to confirm "their problem, not ours".
