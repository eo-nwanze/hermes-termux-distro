---
name: loop-finder
description: Scan my AI coding agent chat history to discover recurring patterns, then grill me into precise, implementable workflow specs.
disable-model-invocation: true
argument-hint: "Optionally specify an agent type (pi/codex/claude-code/opencode/hermes), or leave blank to auto-discover all"
---

## Phase 1: Discover Sessions

Search for chat history files in these common locations, in priority order:

| Agent | Session Path |
|---|---|
| pi | `~/.pi/agent/sessions/` — `*.jsonl` files |
| Codex | `~/.codex/sessions/` — `*.jsonl` files |
| Claude Code | `~/.claude/sessions/` or `~/.claude/projects/` — `*.jsonl` files |
| opencode | `~/.opencode/` or `~/.config/opencode/` — session files |
| Hermes | `~/.hermes/` — session files |

If the user specifies an agent, search only that one.

**Completion criterion**: every known path for the targeted agent(s) has been checked. If no session files are found anywhere, ask the user: "I couldn't find session files at: [list paths tried]. Where does your AI assistant store chat history?"

## Phase 2: Extract User Messages

Read every session file found. The JSONL format varies by agent — read the first few lines of each file to detect its structure before parsing. Typical formats:

- `{"type":"message","message":{"role":"user","content":[...]}}` (pi)
- `{"role":"user","content":"..."}` (simpler agents)
- Adapt to whatever format is found.

Extract all text content from user messages. Ignore system messages, tool calls, and assistant replies.

**Deduplicate**: merge semantically identical or near-identical messages (e.g. five consecutive "继续" counts as one pattern, not five).

**Completion criterion**: every line of every discovered session file has been read and classified. Confirm: "Read X sessions, Y user messages across Z workspaces."

## Phase 3: Identify Loops

Analyze the extracted messages for these signals — **exhaustively**, not until the first few hits:

1. **Repeated instructions**: identical or similar commands appearing across multiple sessions ("review the code quality", "optimize this page", "check for remaining issues")
2. **"Continue" chains**: sessions where the user says "continue" / "继续" / "go on" / "keep going" / "next" multiple times — marks friction where the agent stops too often
3. **Reversal / rollback**: user says "revert", "restore", "the original was better", "undo" — signals poor decision quality or communication
4. **Toolchain maintenance**: user says "update", "upgrade", "sync", "install" — periodic maintenance patterns
5. **Multi-step tasks**: sessions where the user gives multiple sequential instructions that form a flow

For each candidate loop, output:
- Name
- Pattern description (with evidence from actual messages)
- Occurrence count
- Estimated automation ROI (High / Medium / Low)

**Completion criterion**: all user messages have been analyzed. No pattern that appears 3+ times has been missed. State: "Exhaustive scan complete. Found X candidate loops."

## Phase 4: Propose to User

Present the candidate loops:

```
Found X candidate loops:

1. [Name] — Y occurrences
   Pattern: [description with evidence]
   ROI: High / Medium / Low
   Suggestion: [one-line recommendation]

2. ...
```

Ask the user which loop to design, or "all" to design every one.

## Phase 5: Grill the Spec

Once the user selects a loop, enter the **grilling** — a **relentless** interview, one question at a time, that stops only when the spec is done.

**Grilling discipline**:

- **One question at a time. Never ask multiple questions at once.** Asking several is bewildering.
- **Every question carries a recommended answer.** Base it on the patterns you observed in Phase 2–3 — the user's own history is the best evidence.
- **Wait for the user's response before asking the next.** They may agree with your recommendation or give a different answer.
- **Good questions shrink uncertainty.** Push on fuzzy boundaries, quantify where the user is vague, surface hidden exceptions. A bad question asks about something the user already implied. A good question exposes a decision they didn't know they needed to make.

**Vocabulary** — reach for these terms only when the workflow calls for them; never as a checklist:

- **Trigger** — what fires each run: an **event** (new PR, new email) or a **schedule** (every morning). Event-triggering is usually more efficient.
- **Checkpoint** — a human-in-the-loop point where the user verifies or decides. Some workflows have none.
- **Push right** — defer the checkpoint as far as it will go. Do maximal work before involving the human.
- **Brief** — what a checkpoint presents: a tight, decision-ready summary, never raw output. Speed of review is imperative.

**Definition of done**: a workflow spec is done when an implementer agent could build it without asking a single question. After every answer, ask yourself: "Could an implementer build this now?" If the answer is no, the grilling continues. Nothing is done while a question remains.

## Phase 6: Write Artifacts

When the spec is complete, write these files relative to the current workspace:

1. `workflows/[workflow-name].md` — the full workflow spec (source of truth)
2. `NOTES.md` — append new terms and patterns surfaced during this session
3. If the current agent supports a system-instruction file, append the core rules:
   - pi → `~/.pi/agent/AGENTS.md`
   - Codex → `~/.codex/AGENTS.md`
   - Claude Code → `~/.claude/CLAUDE.md` or project-level `CLAUDE.md`
   - If the agent type is unknown or unsupported, skip this step but tell the user where the spec lives so they can copy it manually.

## Workspace

- `workflows/*.md` — one spec per workflow
- `NOTES.md` — raw notes on the user's world: tools, channels, terminology. When empty or thin, interview the user about their world before specifying anything.

## Cross-Agent Compatibility

- **Never hardcode any agent's file paths.** Always search first; ask the user if nothing is found.
- **Detect JSONL format, don't assume.** Read the first few lines to determine the structure.
- **When writing AGENTS.md / CLAUDE.md**, only write to the agent currently in use. Do not assume the user has every agent installed.
- **If the current agent has no system-instruction mechanism**, skip the write step but inform the user where the workflow spec lives.