---
name: loop-breaker
description: Detect loops; on 2 fails change a variable, do not retry.
version: 1.0.0
---

# Loop Breaker

When a task keeps failing on the same step, STOP re-trying. Repeated identical attempts are how agents get stuck. This skill forces a hard reset of approach.

## The Loop Rule

**If you have made 2+ attempts that failed identically, you are looping.** Do not repeat the same command. Break the loop in this order:

### Step 1 — Notice and Declare
State plainly: "I'm looping. Same failure, 3 attempts. Changing approach." No more of the same thing.

### Step 2 — Diagnose the Real Block
Ask before acting:
- Is the failure in the tool, the environment, or my understanding?
- What does the actual error say vs. what I assumed?
- What changed since the first attempt?

### Step 3 — Change One Variable
Pick ONE different lever — not just retry:
- Different tool: terminal → web_extract → search → delegate_task
- Different path: absolute vs relative path, different package manager, different file location
- Different granularity: retry a single step vs. skip ahead entirely
- Ask the user: if no local lever works, surface the blocker with a crisp question

### Step 4 — Escalate or Pivot
- If it's an environment problem (missing package, no network, read-only fs), install/patch it once, then proceed.
- If it's a knowledge gap, search first — don't guess.
- If it's genuinely stuck, stop and report the blocker + the one option to unblock it. Do not loop forever.

## Anti-Loop Checklist (check every ~30s of work)
- [ ] Am I running the same command twice?
- [ ] Did I read the actual error, or just assume?
- [ ] Is my next step different, or just a retry?
- [ ] Would asking the user or switching tools break this?

## Example
Failing: pip install matplotlib times out repeatedly.
Loop fix: don't keep running the same pip command. Instead — run it in the background with a longer timeout, or install via apk, or skip plotting and proceed, or ask the user.

## Memory hook
Repeated failure is a signal to change, not a signal to try harder.
