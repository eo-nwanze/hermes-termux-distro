# Anti-bot submission gates (reCAPTCHA)

When a page loads and the form is correct but submission fails (connection error, HTTP 500, or a "that doesn't look right" message), the POST is likely gated by reCAPTCHA. This is the decision table and a worked example.

## Decision table

| Signal | What it means | Do |
|--------|---------------|----|
| `typeof window.grecaptcha === 'object'` on load | reCAPTCHA widget is present | The POST needs a solved token. |
| Submit succeeds structurally but page is unchanged | Backend rejected the request | Solve CAPTCHA, then resubmit. |
| Raw POST returns HTTP 500 | Missing/invalid CSRF token, or no CAPTCHA token | Get a fresh token, or solve CAPTCHA. |
| Fetch of HTML returns the page but data is missing | JS/AJAX render behind the gate | Drive the real browser; don't curl. |
| Response itself is a 403/paywall interstitial | WAF/bot-wall on the HTML surface | Use `blocked-page-recovery` (archives, Jina, API pivot). |

## Why the same page can be fetchable but not submittable

The GET returns 200 (no WAF on the static surface), but the POST is a separate request the backend validates. Without a valid reCAPTCHA response token, the backend refuses it. The HTML/JS surface is healthy; only the write is gated.

## Worked example — VicRoads rego check

The Service Victoria "Check registration" page (`/check-registration/vehicle`) loads fine, but the "Continue" POST is gated by reCAPTCHA. When automated:
- The form is GET-shaped but the JS `form.submit()` fires an AJAX POST the backend validates against a CAPTCHA token.
- A raw `curl` POST without a solved CAPTCHA returns HTTP 500; a raw POST with a grabbed CSRF token but no CAPTCHA returns "Connection error".
- The backend endpoint URL is not in the page JS bundle (it is constructed at runtime), so you can't POST to it directly from curl.

Two ways forward:
- **One-off:** load the page, solve the checkbox on it, submit, read the result page (VIN, rego number, make, colour, body type, registration status, **expiry date**).
- **Recurring ("tell me when X expires"):** wire a CAPTCHA-solver API key so the solve is unattended, then script the periodic lookup and alert on the expiry date. This is the correct setup for recurring rego/reminder tasks — a manual checkbox solve does not survive automation.

## Solving reCAPTCHA

- **Human-in-the-loop (one-off):** `browser_exec` loads the page; the user ticks the checkbox in their session; you then submit and read the result.
- **Automated:** a CAPTCHA-solver service (e.g. 2Captcha, antiCAPTCHA) posts the site key and returns a solved token. Requires an API key; set it and point the solver at the loaded page. No key means the box stays unsolved — don't dress up that gap as "the site is down."

## Cloudflare / JavaScript challenge (page-load gate)

Some sites serve the page surface but hold a **Cloudflare JS challenge** at page load:
the body shows "Just a moment...", "Performing security verification", a Ray ID, or
"Performance and Security by Cloudflare". Unlike a reCAPTCHA POST gate, this blocks the
initial GET — the data never loads at all.

Diagnose it before assuming the site is broken:
- Body text contains "Cloudflare"/"security verification"/a Ray ID, AND
  `typeof window.grecaptcha === 'undefined'` with
  `document.querySelectorAll('iframe').length === 0` (no reCAPTCHA widget or its iframe).
- The challenge text persists across repeated waits (5s, 15s, 30s) — it does not clear.

Mechanism: the browser renders the challenge page but does not execute the proof-resolution
step Cloudflare requires, so the challenge never auto-clears; waiting longer does not help.
This is distinct from a reCAPTCHA widget (`typeof window.grecaptcha === 'object'`), and
either is solved by the local built-in browser or Camofox alone.

Handle it:
- One-off: human-in-the-loop — the user completes the challenge in their session, then you
  read the result page.
- Automated: a CAPTCHA/solver service, or a cloud browser with built-in stealth
  (Browser Use Cloud, Browserbase, Firecrawl) that clears the challenge server-side.
- If the challenge is a plain checkbox rather than a JS proof, clicking the checkbox
  element can clear it.